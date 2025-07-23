"""This module contains tests for the group endpoints."""

from typing import Any

import pytest


def test_get_can_participate_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving groups that the member can participate in with a valid token"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_can_participate", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 2
    assert all(item.get("group_name") != "MB | Mulheres" for item in response_data)
    assert isinstance(response_data, list)


def test_get_can_participate_include_mulheres_for_female(
    test_client: Any, get_valid_internal_token
) -> None:
    """Test that the 'MB | Mulheres' group is included for female members."""

    token = get_valid_internal_token(10)

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/get_can_participate", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert all(item.get("group_name") == "MB | Mulheres" for item in response_data)


def test_get_can_participate_invalid_token(test_client: Any) -> None:
    """Test retrieving groups that the member can participate in with an invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/get_can_participate", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_participate_in_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving groups that the member is participating in with a valid token"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_participate_in", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0


def test_get_participate_in_invalid_token(test_client: Any) -> None:
    """Test retrieving groups that the member is participating in with an invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/get_participate_in", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_pending_requests_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving pending group join requests with a valid token"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_pending_requests", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0


def test_get_pending_requests_invalid_token(test_client: Any) -> None:
    """Test retrieving pending group join requests with an invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/get_pending_requests", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_failed_requests_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving failed group join requests with a valid token"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_failed_requests", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0


def test_get_failed_requests_invalid_token(test_client: Any) -> None:
    """Test retrieving failed group join requests with an invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/get_failed_requests", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_participate_in_empty_participate_in(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test retrieving member groups when the member is not participating in any group"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    run_db_query(
        """
        DELETE FROM member_groups
        WHERE registration_id = 5
    """
    )
    response = test_client.get("/get_participate_in", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    result = run_db_query("SELECT COUNT(*) FROM member_groups WHERE registration_id = 5")
    assert result[0][0] == 0


def test_get_participate_in_date_format(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving member groups when the member is not participating in any group"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.get("/get_participate_in", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {"group_name": "Mensa Rio de Janeiro Regional", "entry_date": "19/10/2023"}
    ]


def test_get_pending_requests_empty_pending_requests(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test retrieving member groups when the member has no pending requests"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    run_db_query(
        """
        DELETE FROM group_requests
        WHERE registration_id = 5
    """
    )
    response = test_client.get("/get_pending_requests", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    result = run_db_query("SELECT COUNT(*) FROM group_requests WHERE registration_id = 5")
    assert result[0][0] == 0


def test_get_pending_requests_date_format(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving member groups when the member has no pending requests"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_pending_requests", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {
            "group_name": "Mensa Bahia Regional",
            "last_attempt": "25/09/2023",
            "no_of_attempts": 2,
        },
        {
            "group_name": "Mensa DF Regional",
            "last_attempt": "20/09/2023",
            "no_of_attempts": 1,
        },
        {
            "group_name": "Mensa Rio Grande do Sul Regional",
            "last_attempt": None,
            "no_of_attempts": 0,
        },
    ]


def test_get_failed_requests_empty_failed_requests(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test retrieving member groups when the member has no failed requests"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    run_db_query(
        """
        DELETE FROM group_requests
        WHERE registration_id = 5
    """
    )
    response = test_client.get("/get_failed_requests", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    result = run_db_query("SELECT COUNT(*) FROM group_requests WHERE registration_id = 5")
    assert result[0][0] == 0


def test_get_failed_requests_date_format(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving member groups when the member has no failed requests"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.get("/get_failed_requests", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {"group_name": "Grupos Regionais Mensa Brasil", "last_attempt": "01/10/2023"},
        {"group_name": "Mensampa Regional", "last_attempt": "05/09/2023"},
    ]


def test_request_join_group_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test a valid request to join a group"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}

    result = run_db_query(
        "SELECT COUNT(*) FROM group_requests WHERE registration_id = 5 AND group_id = 'abc'"
    )
    assert result[0][0] > 0


def test_request_join_group_invalid_token(test_client: Any) -> None:
    """Test request to join group with an invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_request_join_group_no_phone(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test requesting to join a group when the user has no phone number associated"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    run_db_query(
        """
        DELETE FROM phones
        WHERE registration_id = 5
    """
    )
    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Não há número de telefone registrado para o usuário."}

    result = run_db_query("SELECT COUNT(*) FROM phones WHERE registration_id = 5")
    assert result[0][0] == 0


def test_request_join_group_pending_request(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test requesting to join a group when there is already a pending request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    result = run_db_query(
        "SELECT fulfilled FROM group_requests WHERE registration_id = 5 AND group_id = '556184020538-1393452040@g.us'"
    )
    assert result[0][0] is False

    response = test_client.post(
        "/request_join_group",
        json={"group_id": "556184020538-1393452040@g.us"},
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe uma solicitação pendente para este grupo."}


def test_request_join_group_failed_request(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test requesting to join a group when there is a failed request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    result = run_db_query(
        "SELECT no_of_attempts, fulfilled FROM group_requests WHERE registration_id = 5 AND group_id = '120363150360123420@g.us'"
    )
    assert result[0][0] > 0
    assert result[0][1] is False

    response = test_client.post(
        "/request_join_group",
        json={"group_id": "120363150360123420@g.us"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}

    result = run_db_query(
        "SELECT fulfilled FROM group_requests WHERE registration_id = 5 AND group_id = '120363150360123420@g.us'"
    )
    assert result[0][0] is False


def test_request_join_group_new_request(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test requesting to join a group with a new request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    run_db_query("DELETE FROM group_requests WHERE registration_id = 5 AND group_id = 'abc'")

    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}

    result = run_db_query(
        "SELECT fulfilled FROM group_requests WHERE registration_id = 5 AND group_id = 'abc'"
    )
    assert result[0][0] is False


def test_get_authorization_status_valid_token(
    test_client: Any, get_valid_internal_token: Any
) -> None:
    """Test retrieving authorization status for a valid token."""
    token = get_valid_internal_token(7)
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert "authorizations" in response_data

    authorizations = response_data["authorizations"]
    assert any(
        "+552199876543" in data["authorized_numbers"]
        and data["authorized_numbers"]["+552199876543"] == "member"
        for data in authorizations.values()
    )
    assert any(
        "+5521955555551" in data["authorized_numbers"]
        and data["authorized_numbers"]["+5521955555551"] == "legal_rep"
        for data in authorizations.values()
    )
    assert any(
        "+5521955555552" in data["authorized_numbers"]
        and data["authorized_numbers"]["+5521955555552"] == "legal_rep"
        for data in authorizations.values()
    )


def test_get_authorization_status_invalid_token(test_client: Any) -> None:
    """Test retrieving authorization status with an invalid token."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_authorization_status_missing_token(test_client: Any) -> None:
    """Test retrieving authorization status without a token."""
    response = test_client.get("/get_authorization_status")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_get_authorization_none_authorized(
    test_client: Any, get_valid_internal_token: Any, run_db_query: Any
) -> None:
    """Test that authorization status shows empty authorized/pending lists when no phones are registered."""
    token = get_valid_internal_token(7)
    headers = {"Authorization": f"Bearer {token}"}

    run_db_query("DELETE FROM whatsapp_authorization WHERE phone_number = '+552199876543'")
    run_db_query("DELETE FROM whatsapp_authorization WHERE phone_number = '+5521955555551'")
    run_db_query("DELETE FROM whatsapp_authorization WHERE phone_number = '+5521955555552'")

    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 200
    response_data = response.json()

    assert isinstance(response_data, dict)
    assert "authorizations" in response_data

    assert len(response_data["authorizations"]) == 2

    for _, data in response_data["authorizations"].items():
        assert "authorized_numbers" in data
        assert "pending_authorization" in data
        assert len(data["authorized_numbers"]) == 0
        assert len(data["pending_authorization"]) == 3


@pytest.mark.parametrize("registration_id", [5, 6, 7, 8, 9, 10, 11])
def test_get_authorization_status_with_legal_rep_phone(
    test_client: Any, get_valid_internal_token: Any, registration_id: int, run_db_query
) -> None:
    """Test that authorization status includes all expected phones for members and their legal representatives."""
    token = get_valid_internal_token(registration_id)
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 200
    response_data = response.json()

    assert "authorizations" in response_data
    assert len(response_data["authorizations"]) > 0

    for _, data in response_data["authorizations"].items():
        assert "authorized_numbers" in data
        assert "pending_authorization" in data

        for _, type_value in data["authorized_numbers"].items():
            assert type_value in ["member", "legal_rep"]

        for _, type_value in data["pending_authorization"].items():
            assert type_value in ["member", "legal_rep"]

    result = run_db_query(
        f"SELECT phone_number FROM phones WHERE registration_id = {registration_id}"
    )
    if result and result[0][0]:
        member_phone = result[0][0]
        assert any(
            member_phone in data["authorized_numbers"]
            or member_phone in data["pending_authorization"]
            for data in response_data["authorizations"].values()
        )

    result = run_db_query(
        f"SELECT phone, alternative_phone FROM legal_representatives WHERE registration_id = {registration_id}"
    )
    for rep in result:
        if rep[0]:
            assert any(
                rep[0] in data["authorized_numbers"] or rep[0] in data["pending_authorization"]
                for data in response_data["authorizations"].values()
            )
        if rep[1]:
            assert any(
                rep[1] in data["authorized_numbers"] or rep[1] in data["pending_authorization"]
                for data in response_data["authorizations"].values()
            )


class TestWorkersEndpoints:
    """Tests for the workers endpoints."""

    @pytest.fixture
    def mock_valid_internal_token(self, get_valid_internal_token: Any, run_db_query: Any) -> str:
        """Fixture that maps SUPER.ADMIN role to registration_id 5 and returns a valid token."""
        run_db_query("""
            INSERT INTO iam_user_roles_map (role_id, registration_id)
            SELECT r.id, 5
            FROM iam_roles r
            WHERE r.role_name = 'SUPER.ADMIN'
            AND NOT EXISTS (
                SELECT 1 FROM iam_user_roles_map urm
                WHERE urm.role_id = r.id AND urm.registration_id = 5
            )
        """)
        return get_valid_internal_token(5)

    def test_get_workers_valid_permission(
        self, test_client: Any, mock_valid_internal_token: Any
    ) -> None:
        """Test retrieving workers with valid permission"""
        token = mock_valid_internal_token
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/get_workers", headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 2
        assert any(worker["worker_phone"] == "5521334456879" for worker in response_data)
        assert any(worker["worker_phone"] == "5521879455648" for worker in response_data)

    def test_get_workers_invalid_token(self, test_client: Any) -> None:
        """Test retrieving workers with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.get("/get_workers", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid Token"}

    def test_get_workers_no_permission(
        self, test_client: Any, get_valid_internal_token: Any
    ) -> None:
        """Test retrieving workers without proper permission"""
        token = get_valid_internal_token(6)
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/get_workers", headers=headers)
        assert response.status_code == 403

    def test_add_worker_valid_permission(
        self, test_client: Any, mock_valid_internal_token: Any, run_db_query: Any
    ) -> None:
        """Test adding a worker with valid permission"""
        token = mock_valid_internal_token
        headers = {"Authorization": f"Bearer {token}"}
        new_worker_phone = "5521999888777"

        response = test_client.post(f"/add_worker?worker_phone={new_worker_phone}", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Worker added successfully"}

        result = run_db_query(
            f"SELECT COUNT(*) FROM whatsapp_workers WHERE worker_phone = '{new_worker_phone}'"
        )
        assert result[0][0] == 1

    def test_add_worker_duplicate(self, test_client: Any, mock_valid_internal_token: Any) -> None:
        """Test adding a worker that already exists"""
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
        existing_worker_phone = "5521334456879"

        response = test_client.post(
            f"/add_worker?worker_phone={existing_worker_phone}", headers=headers
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_add_worker_empty_phone(self, test_client: Any, mock_valid_internal_token: Any) -> None:
        """Test adding a worker with empty phone number"""
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}

        response = test_client.post("/add_worker?worker_phone=", headers=headers)
        assert response.status_code == 400
        assert "phone number is required" in response.json()["detail"].lower()

    def test_add_worker_invalid_token(self, test_client: Any) -> None:
        """Test adding a worker with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.post("/add_worker?worker_phone=+5521999888777", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid Token"}

    def test_add_worker_no_permission(
        self, test_client: Any, get_valid_internal_token: Any
    ) -> None:
        """Test adding a worker without proper permission"""
        token = get_valid_internal_token(6)
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.post("/add_worker?worker_phone=+5521999888777", headers=headers)
        assert response.status_code == 403

    def test_remove_worker_valid_permission(
        self, test_client: Any, mock_valid_internal_token: Any, run_db_query: Any
    ) -> None:
        """Test removing a worker with valid permission"""
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
        worker_phone = "5521879455648"

        result = run_db_query(
            f"SELECT COUNT(*) FROM whatsapp_workers WHERE worker_phone = '{worker_phone}'"
        )
        assert result[0][0] == 1

        response = test_client.delete(
            f"/remove_worker?worker_phone={worker_phone}", headers=headers
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Worker removed successfully"}

        result = run_db_query(
            f"SELECT COUNT(*) FROM whatsapp_workers WHERE worker_phone = '{worker_phone}'"
        )
        assert result[0][0] == 0

    def test_remove_worker_not_found(
        self, test_client: Any, mock_valid_internal_token: Any
    ) -> None:
        """Test removing a worker that doesn't exist"""
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
        non_existent_phone = "+5521999000111"

        response = test_client.delete(
            f"/remove_worker?worker_phone={non_existent_phone}", headers=headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_worker_empty_phone(
        self, test_client: Any, mock_valid_internal_token: Any
    ) -> None:
        """Test removing a worker with empty phone number"""
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}

        response = test_client.delete("/remove_worker?worker_phone=", headers=headers)
        assert response.status_code == 400
        assert "phone number is required" in response.json()["detail"].lower()

    def test_remove_worker_invalid_token(self, test_client: Any) -> None:
        """Test removing a worker with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.delete("/remove_worker?worker_phone=+5521879455648", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid Token"}

    def test_remove_worker_no_permission(
        self, test_client: Any, get_valid_internal_token: Any
    ) -> None:
        """Test removing a worker without proper permission"""
        token = get_valid_internal_token(6)
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.delete("/remove_worker?worker_phone=+5521879455648", headers=headers)
        assert response.status_code == 403
