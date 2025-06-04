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
from people_api.models.asaas import AnuityType, PaymentChoice
from people_api.services.member_onboarding import (
    CalculatedPaymentResponse,
    MemberOnboardingService,
    calculate_payment_value,
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
        "cpf": "12345678909",
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


# End-to-end HTTP endpoint tests for member onboarding
class TestMemberOnboardingEndpoints:
    """Tests for the /onboarding endpoints using TestClient."""

    def test_request_payment_link_success(self, test_client, run_db_query, monkeypatch):
        # Insert pending registration
        token = "test-token-123"
        pending_data: dict = {
            "full_name": "Maria da Silva",
            "social_name": None,
            "birth_date": "1990-05-15",
            "cpf": "12345678909",
            "email": "maria.silva@asaas.com.br",
            "phone_number": "5531940028922",
            "profession": "Engineer",
            "address": {
                "street": "Rua das Flores",
                "neighborhood": "Jardim Primavera",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "04567890",
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
        # Load mock Asaas responses
        with open("tests/member_onboarding/customer_created.json", encoding="utf-8") as f:
            customer_json = json.load(f)
        with open("tests/member_onboarding/payment_created.json", encoding="utf-8") as f:
            payment_json = json.load(f)
        # Mock HTTP client
        from people_api.services.member_onboarding import MemberOnboardingService

        class DummyResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            async def json(self):
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
        # Call endpoint
        response = test_client.post(
            "/onboarding/request_payment_link",
            json={"anuityType": "1A", "externalReference": token},
        )
        assert response.status_code == 200
        assert response.json() == payment_json["invoiceUrl"]

    def test_request_payment_link_not_found(self, test_client):
        response = test_client.post(
            "/onboarding/request_payment_link",
            json={"anuityType": "1A", "externalReference": "no-such-token"},
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Invalid token."}

    def test_validate_payment_success(self, test_client, run_db_query, monkeypatch):
        # Load webhook event payload
        payload_path = "tests/member_onboarding/webhook_request.json"
        with open(payload_path, encoding="utf-8") as f:
            payload = json.load(f)
        ext_ref = json.loads(payload["payment"]["externalReference"])
        token = ext_ref["pending_token"]
        # Insert pending registration

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

        pending_data = {
            "full_name": "João das Neves Souza",
            "social_name": None,
            "birth_date": "1990-05-15",
            "cpf": "12345678909",
            "email": "joao.souza@example.com",
            "phone_number": "5511999999999",
            "profession": "Engineer",
            "address": {
                "street": "Some street",
                "neighborhood": "Some neighborhood",
                "city": "City",
                "state": "ST",
                "zip_code": "12345678",
            },
        }
        run_db_query(
            "INSERT INTO pending_registration (data, token) VALUES ('"
            + json.dumps(pending_data)
            + "'::json, '"
            + token
            + "')"
        )
        # Mock auth token

        dummy_settings = SimpleNamespace(asaas_auth_token="valid-token")
        monkeypatch.setattr(MemberOnboardingService, "settings", dummy_settings)
        # Call endpoint
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
        # Verify that the member registration was inserted into the database
        registration_id = data["details"]["registration_id"]
        # Check registration record
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
        # Check membership payment record
        pay_rows = run_db_query(
            f"SELECT expiration_date, amount_paid, payment_status"
            f" FROM membership_payments WHERE registration_id = {registration_id}"  # noqa: E999
        )
        assert len(pay_rows) == 1
        exp_date_val, amount_paid_val, status_val = pay_rows[0]
        # expiration_date matches the one in payload externalReference
        assert str(exp_date_val) == ext_ref["expiration_date"]
        assert amount_paid_val == payload["payment"]["value"]
        assert status_val == payload["payment"]["status"]
        # Ensure pending registration entry was removed
        pending_rows = run_db_query(f"SELECT * FROM pending_registration WHERE token = '{token}'")
        assert pending_rows == []
