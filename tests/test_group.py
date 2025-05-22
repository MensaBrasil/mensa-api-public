"""This module contains tests for the group endpoints."""

from typing import Any


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
    assert isinstance(response_data, list)
    # Should include member phone
    assert any(
        p["phone_number"] == "+552199876543"
        and p["name"].startswith("Ana")
        and p["authorization_status"] is True
        and p["type"] == "member"
        for p in response_data
    )
    # Should include both legal representatives
    assert any(
        p["phone_number"] == "+5521955555551"
        and p["name"].startswith("Carlos")
        and p["authorization_status"] is True
        and p["type"] == "legal_representative"
        for p in response_data
    )
    assert any(
        p["phone_number"] == "+5521955555552"
        and p["name"].startswith("Ana")
        and p["authorization_status"] is True
        and p["type"] == "legal_representative"
        for p in response_data
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


def test_get_authorization_status_no_phones(
    test_client: Any, get_valid_internal_token: Any, run_db_query: Any
) -> None:
    """Test that authorization status includes all expected phones for the member and legal representatives."""
    token = get_valid_internal_token(5)
    headers = {"Authorization": f"Bearer {token}"}
    run_db_query("DELETE FROM whatsapp_authorization WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 200
    # Since there are no phones and the member is not a minor, should return only the member with phone_number None and authorization_status False
    assert response.json() == [
        {
            "type": "member",
            "name": "Fernando Filho",
            "phone_number": None,
            "authorization_status": False,
        }
    ]


def test_get_authorization_status_with_legal_rep_phone(
    test_client: Any, get_valid_internal_token: Any
) -> None:
    """Test that authorization status includes all expected phones for the member and legal representatives."""
    token = get_valid_internal_token(8)
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/get_authorization_status", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    numbers = {p["phone_number"] for p in response_data}
    assert "+552191234567" in numbers
    assert "+5521955555554" in numbers
    assert "+5521955555555" in numbers
