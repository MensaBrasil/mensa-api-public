"""Service for member onboarding operations."""

import json
import logging
import time
from datetime import date, datetime, timedelta

import aiohttp
import httpx
from fastapi import HTTPException, status
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.models import (
    MembershipPayments,
)
from people_api.database.models.pending_registration import (
    PendingRegistration,
    PendingRegistrationData,
)
from people_api.dbs import get_async_sessions
from people_api.models.asaas import AnuityType, PaymentChoice
from people_api.services.email_sending_service import EmailSendingService
from people_api.services.email_service import EmailTemplates
from people_api.services.workspace_service import WorkspaceService
from people_api.settings import get_asaas_settings, get_settings, get_smtp_settings

from .member_utils import convert_pending_to_member_models


class CalculatedPaymentResponse:
    """Class to represent the payment response structure."""

    def __init__(self, payment_value: float, expiration_date: date):
        self.payment_value = payment_value
        self.expiration_date = expiration_date

    def to_dict(self) -> dict:
        """Convert the payment response to a dictionary."""
        return {
            "payment_value": self.payment_value,
            "expiration_date": self.expiration_date.strftime("%Y-%m-%d"),
            "expiration_date_br_format": self.expiration_date.strftime("%d/%m/%Y"),
        }


def calculate_payment_value(payment: PaymentChoice) -> CalculatedPaymentResponse:
    """Calculate the payment value based on the payment type."""
    mes_ingresso = datetime.now().month
    VB = 139.00
    valor_vitalicio = 11855.00

    NPP = 13 - mes_ingresso
    PPR = NPP * 11.50

    if payment.anuityType == AnuityType.ONE_ANNUAL_FEE:
        payment_value = VB
        expiration_date = datetime(datetime.now().year + 1, 1, 31).date()
    elif payment.anuityType == AnuityType.ONE_ANNUAL_FEE_PLUS_PRO_RATA:
        payment_value = round(VB + PPR, 2)
        expiration_date = datetime(datetime.now().year + 2, 1, 31).date()
    elif payment.anuityType == AnuityType.FIVE_ANNUAL_FEES_PLUS_PRO_RATA:
        payment_value = round((VB * 5 * 0.95) + PPR, 2)
        expiration_date = datetime(datetime.now().year + 6, 1, 31).date()
    elif payment.anuityType == AnuityType.TEN_ANNUAL_FEES_PLUS_PRO_RATA:
        payment_value = round((VB * 10 * 0.9) + PPR, 2)
        expiration_date = datetime(datetime.now().year + 11, 1, 31).date()
    elif payment.anuityType == AnuityType.LIFETIME:
        payment_value = valor_vitalicio
        expiration_date = datetime(9999, 1, 31).date()

    return CalculatedPaymentResponse(payment_value, expiration_date)  # pylint: disable=E0606


class MemberOnboardingService:
    """Service class for member onboarding operations."""

    settings = get_asaas_settings()

    webclient = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=10.0),
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": settings.asaas_api_key,
        },
    )

    @classmethod
    async def _check_asaas_auth_token(cls, asaas_auth_token: str):
        """Check if the provided asaas_auth_token is valid."""
        if not asaas_auth_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not authenticated."
            )

        if asaas_auth_token != cls.settings.asaas_auth_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Invalid authentication token.",
            )

    @classmethod
    async def request_payment_link(cls, payment: PaymentChoice, session: AsyncSession):
        """Get or create a customer and request a payment link for member onboarding."""

        pending_member = (
            await session.exec(
                PendingRegistration.get_select_stmt_by_token(payment.externalReference)
            )
        ).first()

        if not pending_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid token.",
            )

        member_data = PendingRegistrationData.model_validate(pending_member.data)

        payload = {
            "name": member_data.full_name,
            "cpfCnpj": member_data.cpf,
            "email": member_data.email,
            "mobilePhone": member_data.phone_number,
            "address": member_data.address.street,
            "province": member_data.address.neighborhood,
            "postalCode": member_data.address.zip_code,
            "externalReference": payment.externalReference,
        }

        if not member_data.cpf:
            logging.error(
                "CPF is required for customer creation. Member data: %s",
                json.dumps(member_data.model_dump(), indent=2),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF is required for customer creation.",
            )

        try:
            result = await cls.webclient.get(
                url=f"{get_asaas_settings().asaas_customers_url}?cpfCnpj={member_data.cpf}"
            )
            result_json = result.json() if isinstance(result, dict) else result.json()
        except Exception as e:
            logging.error("Error communicating with Asaas API: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to communicate with Asaas API.",
            ) from e

        if result.status_code == 200 and result_json.get("totalCount") != 1:
            customer_response = await cls.webclient.post(
                url=get_asaas_settings().asaas_customers_url, json=payload
            )
            customer = customer_response.json()

            if customer_response.status_code != 200 or "id" not in customer:
                logging.error(
                    "Customer creation failed. Response: %s",
                    json.dumps(customer, indent=2),
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to create customer on Asaas.",
                )
        else:
            try:
                customer = result_json["data"][0]
            except (KeyError, IndexError) as e:
                logging.error(
                    "Customer lookup failed. Result: %s",
                    json.dumps(result_json, indent=2),
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found and could not be created.",
                ) from e

        payment_information = calculate_payment_value(payment).to_dict()

        payment_payload = {
            "billingType": "UNDEFINED",
            "customer": customer["id"],
            "value": payment_information.get("payment_value"),
            "dueDate": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "daysAfterDueDateToRegistrationCancellation": 0,
            "externalReference": json.dumps(
                {
                    "pending_token": payment.externalReference,
                    "expiration_date": payment_information.get("expiration_date"),
                }
            ),
            "description": (
                f"Pagamento de primeira anuidade para {member_data.full_name}, com validade até "
                f"{payment_information.get('expiration_date_br_format')}!"
            ),
        }

        payment_response = await cls.webclient.post(
            url=get_asaas_settings().asaas_payments_url, json=payment_payload
        )

        payment_result = payment_response.json()
        if payment_response.status_code != 200 or "invoiceUrl" not in payment_result:
            logging.error(
                "Payment creation failed. Response: %s",
                json.dumps(payment_result, indent=2),
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to create payment. Please try again later.",
            )

        return {"payment_link": payment_result["invoiceUrl"]}

    @classmethod
    async def process_member_onboarding(cls, asaas_auth_token: str, payload, session: AsyncSession):
        """Process member onboarding by validating the payment for pending members."""
        await cls._check_asaas_auth_token(asaas_auth_token)

        external_reference_raw = payload.get("payment", {}).get("externalReference")
        if not external_reference_raw:
            return {
                "message": "Request successfull. But no externalReference found in payment payload.",
                "error": "No externalReference found in payment payload.",
            }

        try:
            external_reference_data = json.loads(external_reference_raw)
            external_reference = external_reference_data.get("pending_token")
            expiration_date_str = external_reference_data.get("expiration_date")
            if not external_reference or not expiration_date_str:
                return {
                    "message": "Request successfull. But invalid externalReference format in payment payload.",
                    "error": "Invalid externalReference format in payment payload.",
                }
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()

        except Exception as e:
            logging.error(
                "Error parsing externalReference in payment payload: %s. Content: \n\n %s",
                str(e),
                json.dumps(payload, indent=2),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid externalReference format in payment payload.",
            ) from e

        pending_member = (
            await session.exec(PendingRegistration.get_select_stmt_by_token(external_reference))
        ).first()
        if not pending_member:
            logging.error(
                "Pending registration not found for externalReference: %s. Content: \n\n %s",
                external_reference,
                json.dumps(payload, indent=2),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pending registration not found for provided externalReference.",
            )

        if pending_member.member_effectivation_date:
            logging.info(
                "Member already activated for token: %s. Skipping onboarding process.",
                pending_member.token,
            )
            return {
                "message": "Member already activated. Skipping onboarding process.",
                "details": {
                    "member_name": pending_member.data.full_name,
                    "registration_id": pending_member.registration_id,
                },
            }

        try:
            member_data = PendingRegistrationData.model_validate(pending_member.data)

            (
                registration,
                address_obj,
                email_obj,
                phone_obj,
                rep_objs,
            ) = convert_pending_to_member_models(member_data)

            logging.info("Converting pending registration to member models")
            session.add(registration)
            await session.flush()

            logging.info("New registration created with ID: %s", registration.registration_id)
            reg_id = registration.registration_id

            logging.info("Processing address, email, phone, and representatives")
            address_obj.registration_id = reg_id
            email_obj.registration_id = reg_id
            phone_obj.registration_id = reg_id

            for rep in rep_objs:
                rep.registration_id = reg_id
                session.add(rep)

            session.add(address_obj)
            session.add(email_obj)
            session.add(phone_obj)

            logging.info(
                "Address, email, phone, and representatives processed for registration ID: %s",
                reg_id,
            )

            logging.info("Creating membership payment record")
            payment = payload.get("payment", {})
            payment_obj = MembershipPayments(
                registration_id=reg_id,
                payment_date=datetime.now(),
                expiration_date=expiration_date,
                amount_paid=payment.get("value"),
                observation=f"External Reference: {external_reference}",
                payment_method=payment.get("billingType"),
                transaction_id=payment.get("id"),
                payment_status=payment.get("status"),
            )
            session.add(payment_obj)
            await session.flush()
            logging.info("Membership payment record created for registration ID: %s", reg_id)

            logging.info("Pending registration deleted successfully")
            logging.info("Creating Mensa email for registration ID: %s", reg_id)
            mensa_email = await WorkspaceService.create_mensa_email(
                registration_id=reg_id, session=session
            )

            logging.info(
                "Mensa email created successfully for registration ID: %s\nEmail Address: %s",
                reg_id,
                mensa_email["user_data"]["email"],
            )
            email_address = mensa_email["user_data"]["email"]
            email_password = mensa_email["user_data"]["password"]

            sender = get_smtp_settings().smtp_username
            email_service = EmailSendingService()
            template_service = EmailTemplates()

            logging.info("Rendering welcome emails for registration ID: %s", reg_id)
            emails = template_service.render_welcome_emails_from_pending(
                pending_data=member_data,
                registration_id=reg_id,
                mensa_email=email_address,
                temp_email_password=email_password,
            )

            logging.info("Sending welcome emails for registration ID: %s", reg_id)
            for email in emails:
                email_service.send_email(
                    to_email=email["recipient_email"],
                    subject=email["subject"],
                    html_content=email["body"],
                    sender_email=sender,
                    reply_to="secretaria@mensa.org.br",
                )

            pending_member.member_effectivation_date = datetime.now()
            session.add(pending_member)

            return {
                "message": "Member onboarding processed successfully.",
                "details": {
                    "member_name": member_data.full_name,
                    "registration_id": reg_id,
                    "expiration_date": expiration_date.strftime("%Y-%m-%d"),
                    "email": {
                        "address": email_address,
                        "password": email_password,
                    },
                },
            }

        except Exception as e:
            logging.error("Error processing member onboarding...\n%s", str(e))

            try:
                async with aiohttp.ClientSession() as websession:
                    await websession.get(
                        url=get_settings().monitor_payment_validation_failed_url
                        + f"?status=down&msg={str(e)}\ntoken:{pending_member.token}&ping={time.time()}",
                        headers={"Content-Type": "application/json"},
                    )
                logging.info("Sent error notification to monitoring endpoint")
            except Exception as notify_error:
                logging.error("Failed to notify monitoring endpoint: %s", notify_error)

            async for sessions in get_async_sessions():
                logging.info("Resetting registration ID sequence after error.")
                await sessions.rw.execute(
                    text("""
                    SELECT setval('registration_registration_id_seq',
                                (SELECT MAX(registration_id) FROM registration));
                """)
                )
                logging.info("Registration ID sequence reset successfully.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process member onboarding.",
            ) from e


async def send_initial_payment_email(
    session: AsyncSession, pending_registration: PendingRegistration
):
    """Scan the database for new pending payments and send email with payment url + token."""
    email_service = EmailSendingService()
    sender_email = get_smtp_settings().smtp_username

    try:
        payment_url = get_asaas_settings().initial_payment_url
        member_data = PendingRegistrationData.model_validate(pending_registration.data)

        complete_payment_url = f"{payment_url}?t={pending_registration.token}"

        subject = "Parabéns! Você foi aprovado na Mensa Brasil"
        html_content = EmailTemplates.render_pending_payment_email(
            full_name=member_data.full_name,
            admission_type=member_data.admission_type,
            complete_payment_url=complete_payment_url,
        )

        email_service.send_email(
            to_email=member_data.email,
            subject=subject,
            html_content=html_content,
            sender_email=sender_email,
            reply_to="secretaria@mensa.org.br",
        )

        if member_data.legal_representatives:
            for rep in member_data.legal_representatives:
                rep_subject = "Parabéns! Seu filho(a) foi aprovado(a) na Mensa Brasil"
                rep_html_content = EmailTemplates.render_pending_payment_email_legal_rep(
                    full_name=rep.name.title(),  # type: ignore
                    admission_type=member_data.admission_type,
                    complete_payment_url=complete_payment_url,
                )
                email_service.send_email(
                    to_email=rep.email,  # type: ignore
                    subject=rep_subject,
                    html_content=rep_html_content,
                    sender_email=sender_email,
                    reply_to="secretaria@mensa.org.br",
                )

        pending_registration.email_sent_at = date.today()
        session.add(pending_registration)

        logging.info(
            "Payment email sent to %s for registration %s",
            member_data.email,
            pending_registration.token,
        )

    except Exception as e:
        logging.error(
            "Failed to send payment email for pending_registration token:%s\nerro:%s",
            pending_registration.token,
            e,
        )

        try:
            async with aiohttp.ClientSession() as websession:
                await websession.get(
                    url=get_settings().monitor_initial_payment_failed_url
                    + f"?status=down&msg={str(e)}\ntoken:{pending_registration.token}&ping={time.time()}",
                    headers={"Content-Type": "application/json"},
                )
            logging.info("Sent error notification to monitoring endpoint")
        except Exception as notify_error:
            logging.error("Failed to notify monitoring endpoint: %s", notify_error)
