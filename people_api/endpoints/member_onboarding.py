"""Webhook endpoints for asaas service integration for member onboarding."""

from fastapi import APIRouter, Body, Depends, Header

from people_api.dbs import AsyncSessionsTuple, get_async_sessions
from people_api.models.asaas import AnuityType, PaymentChoice
from people_api.services.member_onboarding import (
    MemberOnboardingService,
    calculate_payment_value,
)

member_onboarding_router = APIRouter(prefix="/onboarding", tags=["member_onboarding"])


@member_onboarding_router.post(
    "/request_payment_link", description="Request payment link for member onboarding"
)
async def _request_payment_link(
    payment: PaymentChoice,
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await MemberOnboardingService.request_payment_link(payment, session.ro)


@member_onboarding_router.post(
    "/validate_payment", description="Validate payment for member onboarding"
)
async def _validate_payment(
    asaas_auth_token: str = Header(alias="asaas-access-token"),
    payload=Body(...),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await MemberOnboardingService.process_member_onboarding(
        asaas_auth_token, payload, session.rw
    )


@member_onboarding_router.get(
    "/payment_options",
    description="Get payment options for first membership payment",
)
async def _get_first_payment_options():
    options = []
    for option in AnuityType:
        calc = calculate_payment_value(PaymentChoice(anuityType=option, externalReference=""))
        options.append(
            {
                "name": option.value,
                "text": option.text,
                "price": calc.payment_value,
                "expiration_date": calc.expiration_date.strftime("%Y-%m-%d"),
            }
        )
    return options
