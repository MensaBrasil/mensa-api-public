"""This module contains tests for the group endpoints."""

from typing import Any

from people_api.app import app
from people_api.auth import verify_firebase_token
from people_api.schemas import UserToken


def test_get_can_participate_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving groups that the member can participate in with a valid token"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/get_can_participate", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 2
    assert "MB | Mulheres" not in response_data
    assert isinstance(response_data, list)


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


def test_get_failed_requests_date_format(test_client: Any, mock_valid_token: Any) -> None:
    """Test retrieving member groups when the member has no failed requests"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.get("/get_failed_requests", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {"group_name": "Grupos Regionais Mensa Brasil", "last_attempt": "01/10/2023"},
        {"group_name": "Mensampa Regional", "last_attempt": "05/09/2023"},
    ]


def test_request_join_group_valid_data(test_client: Any, mock_valid_token: Any) -> None:
    """Test a valid request to join a group"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}


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


def test_request_join_group_pending_request(test_client: Any, mock_valid_token: Any) -> None:
    """Test requesting to join a group when there is already a pending request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post(
        "/request_join_group",
        json={"group_id": "556184020538-1393452040@g.us"},
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe uma solicitação pendente para este grupo."}


def test_request_join_group_failed_request(test_client: Any, mock_valid_token: Any) -> None:
    """Test requesting to join a group when there is a failed request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post(
        "/request_join_group",
        json={"group_id": "120363150360123420@g.us"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}


def test_request_join_group_new_request(test_client: Any, mock_valid_token: Any) -> None:
    """Test requesting to join a group with a new request"""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/request_join_group", json={"group_id": "abc"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Request to join group sent successfully"}


def test_get_can_participate_include_mulheres_for_female(test_client: Any) -> None:
    """Test that the 'MB | Mulheres' group is included for female members."""

    def mock_verify_firebase_token_female():
        return UserToken(
            iss="https://securetoken.google.com/carteirinhasmensa",
            aud="carteirinhasmensa",
            auth_time=1709996057,
            sub="female-sub",
            iat=1722977514,
            exp=1722981114,
            email="carla.ferreira@mensa.org.br",
            registration_id=10,
        )

    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token_female
    try:
        headers = {"Authorization": "Bearer female-token"}
        response = test_client.get("/get_can_participate", headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        print(response_data)
        assert any(item.get("group_name") == "MB | Mulheres" for item in response_data)
    finally:
        app.dependency_overrides.pop(verify_firebase_token, None)
