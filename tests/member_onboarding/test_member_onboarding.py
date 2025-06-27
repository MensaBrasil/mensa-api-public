# pylint: skip-file
"""Tests for member onboarding service."""

import json
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.pending_registration import (
    PendingRegistration,
)
from people_api.dbs import get_async_sessions
from people_api.models.asaas import AnuityType, PaymentChoice
from people_api.services.email_service import EmailTemplates
from people_api.services.member_onboarding import (
    CalculatedPaymentResponse,
    MemberOnboardingService,
    calculate_payment_value,
    send_initial_payment_email,
)
from people_api.services.workspace_service import WorkspaceService


@pytest.fixture
def mock_settings():
    """Mock Asaas settings for the MemberOnboardingService."""
    with patch(
        "people_api.services.member_onboarding.get_asaas_settings"
    ) as mock_get_asaas_settings:
        settings = Mock()
        settings.asaas_api_key = "test_api_key"
        settings.asaas_auth_token = "test_auth_token"
        mock_get_asaas_settings.return_value = settings
        yield settings


@pytest.fixture
def mock_smtp_settings():
    """Mock SMTP settings for email sending during onboarding scan."""
    with patch("people_api.services.member_onboarding.get_smtp_settings") as mock_get_smtp_settings:
        settings = Mock()
        settings.smtp_username = "sender@example.com"
        mock_get_smtp_settings.return_value = settings
        yield settings


@pytest.fixture
def mock_session():
    """Mock AsyncSession for database operations."""
    session = AsyncMock(spec=AsyncSession)
    session.rw = session
    return session


@pytest.fixture
def pending_registration_data():
    """Mock data for a pending registration."""
    return {
        "full_name": "Maria da Silva",
        "social_name": None,
        "birth_date": "1990-05-15",
        "cpf": "12466302063",
        "gender": "Feminino",
        "admission_type": "test",
        "email": "maria.silva@asaas.com.br",
        "phone_number": "5531940028922",
        "profession": "Engineer",
        "address": {
            "street": "Rua das Flores",
            "number": "123",
            "complement": "Apto 45",
            "neighborhood": "Jardim Primavera",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "04567890",
            "country": "Brazil",
        },
        "legal_representatives": [
            {
                "name": "José Silva",
                "email": "jose.silva@example.com",
                "phone_number": "5511987654321",
            }
        ],
    }


@pytest.fixture
def pending_registration_model(pending_registration_data):
    """Mock PendingRegistration model instance."""
    pending_reg = PendingRegistration(
        token="e7b8c9d2-4f3a-4a1b-8c2d-1a2b3c4d5e6f", data=pending_registration_data
    )
    return pending_reg


@pytest.fixture
def payment_choice():
    """Mock PaymentChoice instance."""
    return PaymentChoice(
        anuityType=AnuityType.ONE_ANNUAL_FEE,
        externalReference="e7b8c9d2-4f3a-4a1b-8c2d-1a2b3c4d5e6f",
    )


@pytest.fixture
def customer_created_response():
    """Mock response for customer creation."""
    with open("tests/member_onboarding/customer_created.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def payment_link_created_response():
    """Mock response for payment link creation."""
    with open("tests/member_onboarding/payment_created.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def webhook_response():
    """Mock response for webhook event."""
    with open("tests/member_onboarding/webhook_request.json", encoding="utf-8") as f:
        return json.load(f)


class TestCalculatedPaymentResponse:
    """Tests for CalculatedPaymentResponse model."""

    def test_init_and_to_dict(self):
        """Test initialization and conversion to dictionary."""
        payment_value = 139.0
        expiration_date = date(2025, 1, 31)

        response = CalculatedPaymentResponse(payment_value, expiration_date)

        assert response.payment_value == payment_value
        assert response.expiration_date == expiration_date

        response_dict = response.to_dict()
        assert response_dict["payment_value"] == payment_value
        assert response_dict["expiration_date"] == "2025-01-31"
        assert response_dict["expiration_date_br_format"] == "31/01/2025"


class TestCalculatePaymentValue:
    """Tests for calculate_payment_value function."""

    @pytest.mark.parametrize(
        "anuity_type, expected_value, expected_year",
        [
            (AnuityType.ONE_ANNUAL_FEE, 139.0, 1),
            (
                AnuityType.ONE_ANNUAL_FEE_PLUS_PRO_RATA,
                None,
                2,
            ),  # Value depends on current month
            (
                AnuityType.FIVE_ANNUAL_FEES_PLUS_PRO_RATA,
                None,
                6,
            ),  # Value depends on current month
            (
                AnuityType.TEN_ANNUAL_FEES_PLUS_PRO_RATA,
                None,
                11,
            ),  # Value depends on current month
            (
                AnuityType.LIFETIME,
                11855.0,
                9999 - datetime.now().year,
            ),  # Value is fixed
        ],
    )
    def test_calculate_payment_value(self, anuity_type, expected_value, expected_year):
        """Test calculate_payment_value with various anuity types."""
        payment = PaymentChoice(anuityType=anuity_type, externalReference="test-reference")

        result = calculate_payment_value(payment)

        assert isinstance(result, CalculatedPaymentResponse)
        if expected_value is not None:
            assert result.payment_value == expected_value
        assert result.expiration_date.year == datetime.now().year + expected_year
        assert result.expiration_date.month == 1
        assert result.expiration_date.day == 31

    def test_invalid_payment_type(self):
        """Test calculate_payment_value with an invalid payment type."""

        with pytest.raises(ValidationError):
            PaymentChoice(anuityType="INVALID", externalReference="test-reference")  # type: ignore


class TestMemberOnboardingService:
    """Tests for MemberOnboardingService methods."""

    @patch.object(MemberOnboardingService, "settings")
    @pytest.mark.asyncio
    async def test_check_asaas_auth_token_valid(self, mock_settings):
        """Test that valid authentication token does not raise an exception."""
        mock_settings.asaas_auth_token = "valid_token"
        await MemberOnboardingService._check_asaas_auth_token("valid_token")

    @patch.object(MemberOnboardingService, "settings")
    @pytest.mark.asyncio
    async def test_check_asaas_auth_token_invalid(self, mock_settings):
        """Test that invalid authentication token raises HTTPException."""
        mock_settings.asaas_auth_token = "valid_token"
        with pytest.raises(HTTPException) as excinfo:
            await MemberOnboardingService._check_asaas_auth_token("invalid_token")

        assert excinfo.value.status_code == 403
        assert "Invalid authentication token" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_process_member_onboarding_invalid_token(self, mock_settings):
        with patch.object(MemberOnboardingService, "settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await MemberOnboardingService.process_member_onboarding(
                    "invalid_token", {}, AsyncMock()
                )

            assert excinfo.value.status_code == 403
            assert "Invalid authentication token" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_process_member_onboarding_missing_external_reference(
        self, mock_settings, mock_session
    ):
        with patch.object(MemberOnboardingService, "settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await MemberOnboardingService.process_member_onboarding(
                    "test_auth_token", {"payment": {}}, mock_session
                )

            assert excinfo.value.status_code == 400
            assert "Missing externalReference" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_process_member_onboarding_invalid_external_reference_format(
        self, mock_settings, mock_session
    ):
        with patch.object(MemberOnboardingService, "settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await MemberOnboardingService.process_member_onboarding(
                    "test_auth_token",
                    {"payment": {"externalReference": "invalid-json"}},
                    mock_session,
                )

            assert excinfo.value.status_code == 400
            assert "Invalid externalReference format" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_process_member_onboarding_pending_registration_not_found(
        self, mock_settings, mock_session
    ):
        exec_result = Mock()
        exec_result.first.return_value = None
        mock_session.exec.return_value = exec_result

        external_reference = json.dumps(
            {"pending_token": "non-existent-token", "expiration_date": "2026-01-31"}
        )

        with patch.object(MemberOnboardingService, "settings", mock_settings):
            with pytest.raises(HTTPException) as excinfo:
                await MemberOnboardingService.process_member_onboarding(
                    "test_auth_token",
                    {"payment": {"externalReference": external_reference}},
                    mock_session,
                )

            assert excinfo.value.status_code == 404
            assert "Pending registration not found" in excinfo.value.detail


class TestMemberOnboardingEndpoints:
    """Tests for the /onboarding endpoints using TestClient."""

    def test_request_payment_link_success(self, test_client, run_db_query, monkeypatch):
        token = "test-token-123"
        pending_data: dict = {
            "full_name": "Maria da Silva",
            "social_name": None,
            "birth_date": "1990-05-15",
            "cpf": "12466302063",
            "gender": "Feminino",
            "email": "maria.silva@asaas.com.br",
            "admission_type": "test",
            "phone_number": "5531940028922",
            "profession": "Engineer",
            "address": {
                "street": "Rua das Flores",
                "neighborhood": "Jardim Primavera",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "04567890",
                "country": "Brazil",
            },
            "legal_representatives": [],
        }
        run_db_query(
            "INSERT INTO pending_registration (data, token) VALUES ('"
            + json.dumps(pending_data)
            + "'::json, '"
            + token
            + "')"
        )

        with open("tests/member_onboarding/customer_created.json", encoding="utf-8") as f:
            customer_json = json.load(f)
        with open("tests/member_onboarding/payment_created.json", encoding="utf-8") as f:
            payment_json = json.load(f)

        from people_api.services.member_onboarding import MemberOnboardingService

        class DummyResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            def json(self):
                return self._data

        class DummyClient:
            async def get(self, url):
                return DummyResponse(200, {"totalCount": 0, "data": []})

            async def post(self, url, json=None):
                if "customers" in url:
                    return DummyResponse(200, customer_json)
                if "payments" in url:
                    return DummyResponse(200, payment_json)
                return DummyResponse(404, {})

        monkeypatch.setattr(MemberOnboardingService, "webclient", DummyClient())
        response = test_client.post(
            "/onboarding/request_payment_link",
            json={"anuityType": "1A", "externalReference": token},
        )
        assert response.status_code == 200
        assert response.json() == {"payment_link": payment_json["invoiceUrl"]}

    def test_request_payment_link_not_found(self, test_client):
        response = test_client.post(
            "/onboarding/request_payment_link",
            json={"anuityType": "1A", "externalReference": "no-such-token"},
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Invalid token."}

    def test_validate_payment_success(self, test_client, run_db_query, monkeypatch):
        payload_path = "tests/member_onboarding/webhook_request.json"
        with open(payload_path, encoding="utf-8") as f:
            payload = json.load(f)
        ext_ref = json.loads(payload["payment"]["externalReference"])
        token = ext_ref["pending_token"]

        monkeypatch.setattr(
            WorkspaceService,
            "create_mensa_email",
            AsyncMock(
                return_value={
                    "message": "Mensa email created successfully",
                    "user_data": {
                        "email": "maria.silva@mensa.org.br",
                        "password": "mocked-password",
                    },
                    "information": "User will be prompted to change the password at the first login.",
                }
            ),
        )

        mock_email_service = Mock()
        mock_template_emails = [
            {
                "recipient_email": "joao.souza@example.com",
                "subject": "Welcome to Mensa Brazil",
                "body": "<html><body>Welcome email content</body></html>",
            }
        ]

        monkeypatch.setattr(
            "people_api.services.member_onboarding.EmailSendingService",
            Mock(return_value=mock_email_service),
        )

        monkeypatch.setattr(
            "people_api.services.member_onboarding.EmailTemplates",
            Mock(
                return_value=Mock(
                    render_welcome_emails_from_pending=Mock(return_value=mock_template_emails)
                )
            ),
        )
        monkeypatch.setattr(
            "people_api.services.member_onboarding.get_smtp_settings",
            Mock(return_value=SimpleNamespace(smtp_username="tescalvin@mensa.org.br")),
        )

        pending_data = {
            "full_name": "João das Neves Souza",
            "social_name": None,
            "birth_date": "1990-05-15",
            "cpf": "12466302063",
            "email": "joao.souza@example.com",
            "admission_type": "test",
            "phone_number": "5511999999999",
            "gender": "Masculino",
            "profession": "Engineer",
            "address": {
                "street": "Some street",
                "neighborhood": "Some neighborhood",
                "city": "City",
                "state": "ST",
                "zip_code": "12345678",
                "country": "Brazil",
            },
        }
        run_db_query(
            "INSERT INTO pending_registration (data, token) VALUES ('"
            + json.dumps(pending_data)
            + "'::json, '"
            + token
            + "')"
        )

        dummy_settings = SimpleNamespace(asaas_auth_token="valid-token")
        monkeypatch.setattr(MemberOnboardingService, "settings", dummy_settings)
        response = test_client.post(
            "/onboarding/validate_payment",
            headers={"asaas-access-token": "valid-token"},
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Member onboarding processed successfully."
        assert "details" in data
        assert data["details"]["member_name"] == pending_data["full_name"]
        assert isinstance(data["details"]["registration_id"], int)
        assert isinstance(data["details"]["expiration_date"], str)
        assert data["details"]["email"]["address"] == "maria.silva@mensa.org.br"
        assert data["details"]["email"]["password"] == "mocked-password"
        registration_id = data["details"]["registration_id"]
        reg_rows = run_db_query(
            f"SELECT name, cpf, birth_date, profession"
            f" FROM registration WHERE registration_id = {registration_id}"  # noqa: E999
        )
        assert len(reg_rows) == 1
        name, cpf_val, birth_date_val, profession_val = reg_rows[0]
        assert name == pending_data["full_name"]
        assert cpf_val == pending_data["cpf"]
        assert str(birth_date_val) == pending_data["birth_date"]
        assert profession_val == pending_data["profession"]
        pay_rows = run_db_query(
            f"SELECT expiration_date, amount_paid, payment_status"
            f" FROM membership_payments WHERE registration_id = {registration_id}"  # noqa: E999
        )
        assert len(pay_rows) == 1
        exp_date_val, amount_paid_val, status_val = pay_rows[0]
        assert str(exp_date_val) == ext_ref["expiration_date"]
        assert amount_paid_val == payload["payment"]["value"]
        assert status_val == payload["payment"]["status"]
        pending_rows = run_db_query(f"SELECT * FROM pending_registration WHERE token = '{token}'")
        assert pending_rows == []


class TestMemberOnboardingEmails:
    """Tests for email sending during member onboarding."""

    @pytest.mark.asyncio
    async def test_send_initial_payment_email_sends_email_and_updates_registration(
        self,
        mock_session,
        mock_settings,
        mock_smtp_settings,
        pending_registration_model,
    ):
        """Should send initial payment email to both member and legal rep and update pending registration."""
        mock_settings.initial_payment_url = "http://test-url"
        token = pending_registration_model.token

        with patch(
            "people_api.services.member_onboarding.EmailSendingService"
        ) as mock_email_svc_cls:
            email_svc_mock = Mock()
            mock_email_svc_cls.return_value = email_svc_mock

            with patch(
                "people_api.services.member_onboarding.EmailTemplates"
            ) as mock_email_templates:
                mock_email_templates.render_pending_payment_email.return_value = (
                    "member email content"
                )
                mock_email_templates.render_pending_payment_email_legal_rep.return_value = (
                    "legal rep email content"
                )

                await send_initial_payment_email(mock_session, pending_registration_model)

                # Verify emails were sent to both member and legal rep
                assert email_svc_mock.send_email.call_count == 2

                # Check the calls to send_email
                calls = email_svc_mock.send_email.call_args_list

                # First call should be to the member
                member_call = calls[0].kwargs
                assert member_call["to_email"] == pending_registration_model.data["email"]
                assert member_call["subject"] == "Parabéns! Você foi aprovado na Mensa Brasil"
                assert member_call["sender_email"] == mock_smtp_settings.smtp_username
                assert member_call["html_content"] == "member email content"
                assert member_call["reply_to"] == "secretaria@mensa.org.br"

                # Second call should be to the legal representative
                legal_rep_call = calls[1].kwargs
                legal_rep = pending_registration_model.data["legal_representatives"][0]
                assert legal_rep_call["to_email"] == legal_rep["email"]
                assert (
                    legal_rep_call["subject"]
                    == "Parabéns! Seu filho(a) foi aprovado(a) na Mensa Brasil"
                )
                assert legal_rep_call["sender_email"] == mock_smtp_settings.smtp_username
                assert legal_rep_call["html_content"] == "legal rep email content"
                assert legal_rep_call["reply_to"] == "secretaria@mensa.org.br"

                # Verify template rendering
                mock_email_templates.render_pending_payment_email.assert_called_once_with(
                    full_name=pending_registration_model.data["full_name"],
                    admission_type=pending_registration_model.data["admission_type"],
                    complete_payment_url=f"{mock_settings.initial_payment_url}?t={token}",
                )

                # Verify template rendering for legal representative
                mock_email_templates.render_pending_payment_email_legal_rep.assert_called_once_with(
                    full_name=legal_rep["name"].title(),
                    admission_type=pending_registration_model.data["admission_type"],
                    complete_payment_url=f"{mock_settings.initial_payment_url}?t={token}",
                )

        # Verify pending registration was updated
        assert pending_registration_model.email_sent_at == date.today()
        mock_session.add.assert_called_once_with(pending_registration_model)

    @pytest.mark.asyncio
    async def test_send_initial_payment_email_integration_sends_email_and_updates_db(
        self,
        run_db_query,
        mock_settings,
        mock_smtp_settings,
        monkeypatch,
    ):
        """Should send payment email for pending registration in DB and update flags."""
        data = {
            "full_name": "Test User",
            "social_name": "Tester",
            "email": "test.user@example.com",
            "birth_date": "2000-01-01",
            "cpf": "12466302063",
            "profession": "Developer",
            "gender": "Masculino",
            "phone_number": "5511999998888",
            "admission_type": "test",
            "address": {
                "street": "Test Street",
                "neighborhood": "Test Neighborhood",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345678",
                "country": "Brazil",
            },
            "legal_representatives": [],
        }
        token = "00000000-0000-0000-0000-000000000000"
        run_db_query(
            f"INSERT INTO pending_registration (data, token) VALUES ('{json.dumps(data)}'::json, '{token}')"
        )
        dummy_email_svc = SimpleNamespace(send_email=Mock())

        monkeypatch.setattr(
            "people_api.services.member_onboarding.EmailSendingService",
            lambda: dummy_email_svc,
        )
        mock_settings.initial_payment_url = "http://test-payment-url"
        async for sessions in get_async_sessions():
            result = await sessions.rw.exec(
                PendingRegistration.get_all_pending_registrations_with_no_email_sent()
            )
            for pending in result.all():
                await send_initial_payment_email(sessions.rw, pending)

        dummy_email_svc.send_email.assert_called_once()
        kwargs = dummy_email_svc.send_email.call_args.kwargs
        assert kwargs["to_email"] == data["email"]
        assert kwargs["subject"] == "Parabéns! Você foi aprovado na Mensa Brasil"
        assert kwargs["sender_email"] == mock_smtp_settings.smtp_username
        expected_html = EmailTemplates.render_pending_payment_email(
            full_name=data["full_name"],  # type: ignore
            admission_type=data["admission_type"],  # type: ignore
            complete_payment_url=f"{mock_settings.initial_payment_url}?t={token}",
        )
        assert kwargs["html_content"] == expected_html
        rows = run_db_query(
            f"SELECT email_sent_at FROM pending_registration WHERE token = '{token}'"
        )
        assert len(rows) == 1
        (email_sent_at,) = rows[0]
        assert email_sent_at == date.today()

    @pytest.mark.asyncio
    async def test_send_initial_payment_email_to_legal_representative(
        mock_session,
        mock_settings,
        mock_smtp_settings,
        pending_registration_model,
    ):
        """Test that emails are sent to legal representatives when present in member data."""
        mock_settings.initial_payment_url = "http://test-url"
        token = pending_registration_model.token

        with patch(
            "people_api.services.member_onboarding.EmailSendingService"
        ) as mock_email_svc_cls:
            email_svc_mock = Mock()
            mock_email_svc_cls.return_value = email_svc_mock

            with patch(
                "people_api.services.member_onboarding.EmailTemplates"
            ) as mock_email_templates:
                mock_email_templates.render_pending_payment_email.return_value = (
                    "member email content"
                )
                mock_email_templates.render_pending_payment_email_legal_rep.return_value = (
                    "legal rep email content"
                )

                await send_initial_payment_email(mock_session, pending_registration_model)  # type: ignore

                # Verify email sent to member
                assert (
                    email_svc_mock.send_email.call_count == 2
                )  # One for member, one for legal rep

                # Check the calls to send_email
                calls = email_svc_mock.send_email.call_args_list

                # First call should be to the member
                member_call = calls[0].kwargs
                assert member_call["to_email"] == pending_registration_model.data["email"]
                assert member_call["subject"] == "Parabéns! Você foi aprovado na Mensa Brasil"
                assert member_call["sender_email"] == mock_smtp_settings.smtp_username

                # Second call should be to the legal representative
                legal_rep_call = calls[1].kwargs
                legal_rep = pending_registration_model.data["legal_representatives"][0]
                assert legal_rep_call["to_email"] == legal_rep["email"]
                assert (
                    legal_rep_call["subject"]
                    == "Parabéns! Seu filho(a) foi aprovado(a) na Mensa Brasil"
                )
                assert legal_rep_call["sender_email"] == mock_smtp_settings.smtp_username

                # Verify template rendering for legal representative
                mock_email_templates.render_pending_payment_email_legal_rep.assert_called_once_with(
                    full_name=legal_rep["name"].title(),
                    admission_type=pending_registration_model.data["admission_type"],
                    complete_payment_url=f"{mock_settings.initial_payment_url}?t={token}",
                )

    @pytest.mark.asyncio
    async def test_send_initial_payment_email_no_legal_representative(
        mock_session,
        mock_settings,
        mock_smtp_settings,
    ):
        """Test that no emails are sent to legal representatives when not present in member data."""
        mock_settings.initial_payment_url = "http://test-url"

        # Create a pending registration without legal representatives
        pending_data: dict = {
            "full_name": "Test Child",
            "social_name": None,
            "birth_date": "2010-05-15",
            "cpf": "12466302063",
            "gender": "Masculino",
            "admission_type": "test",
            "email": "child@example.com",
            "phone_number": "5531940028922",
            "profession": "Student",
            "address": {
                "street": "Rua das Flores",
                "number": "123",
                "complement": "Apto 45",
                "neighborhood": "Jardim Primavera",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "04567890",
                "country": "Brazil",
            },
            "legal_representatives": [],  # Empty list, no legal representatives
        }

        pending_reg = PendingRegistration(token="test-token-123", data=pending_data)

        with patch(
            "people_api.services.member_onboarding.EmailSendingService"
        ) as mock_email_svc_cls:
            email_svc_mock = Mock()
            mock_email_svc_cls.return_value = email_svc_mock

            with patch(
                "people_api.services.member_onboarding.EmailTemplates"
            ) as mock_email_templates:
                mock_email_templates.render_pending_payment_email.return_value = (
                    "member email content"
                )

                await send_initial_payment_email(mock_session, pending_reg)  # type: ignore

                # Verify only one email is sent (to the member, not to any legal representative)
                assert email_svc_mock.send_email.call_count == 1

                # Check the call to send_email
                call_args = email_svc_mock.send_email.call_args.kwargs
                assert call_args["to_email"] == pending_data["email"]
                assert call_args["subject"] == "Parabéns! Você foi aprovado na Mensa Brasil"

                # Verify render_pending_payment_email_legal_rep was not called
                mock_email_templates.render_pending_payment_email_legal_rep.assert_not_called()
