"""Tests for member_email router endpoints."""

from unittest.mock import patch


def test_add_email_invalid_token(test_client, mock_valid_token):
    """
    Test adding an email with a token whose registration does not match the URL member ID.
    (Using member ID 2623 in the URL to trigger unauthorized access.)
    """
    payload = {
        "cpf": "22222222222",
        "full_name": "New Email",
        "email_address": "newemail@example.com",
        "email_type": "alternative",
    }

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/email/2623", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}


def test_add_email_success(test_client, mock_valid_token, run_db_query):
    """
    Test successfully adding an email for a member.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")
    run_db_query("DELETE FROM legal_representatives WHERE representative_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )

    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    payload = {
        "cpf": "22222222222",
        "full_name": "New Email",
        "email_address": "newemail@example.com",
        "email_type": "alternative",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/email/5", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    assert response.json() == {"message": "Email added successfully"}


def test_update_email_invalid_token(test_client, mock_valid_token, run_db_query):
    """
    Test updating an email when the URL member ID does not match the token's registration.
    (Using member ID 2623 in the URL to trigger unauthorized access.)
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")
    run_db_query("DELETE FROM legal_representatives WHERE representative_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )
    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Email",
        "email_address": "updated@example.com",
        "email_type": "main",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    # Use invalid member ID (2623) in the URL.
    response = test_client.put("/email/2623/1", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}


def test_update_email_success(test_client, mock_valid_token, run_db_query):
    """
    Test successfully updating an email for a member.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")
    run_db_query("DELETE FROM emails WHERE email_id = 2")
    run_db_query("DELETE FROM legal_representatives WHERE representative_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )

    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (2, 5, 'alternative', 'oldemail@example.com')"
    )

    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Email",
        "email_address": "updated@example.com",
        "email_type": "alternative",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/email/5/2", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Email updated successfully"}


def test_delete_email_invalid_token(test_client, mock_valid_token, run_db_query):
    """
    Test deleting an email when the URL member ID does not match the token's registration.
    (Using member ID 2623 in the URL to trigger unauthorized access.)
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )
    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    # Use an invalid member ID (2623) in the URL.
    response = test_client.delete("/email/2623/1", headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}


def test_delete_email_success(test_client, mock_valid_token, run_db_query):
    """
    Test successfully deleting an email for a member.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")
    run_db_query("DELETE FROM legal_representatives WHERE representative_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )
    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.delete("/email/5/1", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Email deleted successfully"}


def test_add_email_invalid_format(test_client, mock_valid_token, run_db_query):
    """
    Test adding an email with an invalid email format.
    Expect a 422 validation error.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    run_db_query("DELETE FROM emails WHERE email_id = 1")

    run_db_query(
        "INSERT INTO registration (registration_id, expelled, deceased, transferred, birth_date, cpf, join_date) "
        "VALUES (5, False, False, False, '2005-01-01', '11111111111', '2021-01-01')"
    )
    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    payload = {
        "cpf": "22222222222",
        "full_name": "New Email",
        "email_address": "invalidemail",
        "email_type": "alternative",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/email/5", json=payload, headers=headers)
    assert response.status_code == 422, f"Expected 422 but got {response.status_code}"


def test_update_email_invalid_format(test_client, mock_valid_token):
    """
    Test updating an email with an invalid email format.
    Expect a 422 validation error.
    """

    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Email",
        "email_address": "invalidemail",
        "email_type": "alternative",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/email/5/2", json=payload, headers=headers)
    assert response.status_code == 422, f"Expected 422 but got {response.status_code}"


## New tests for chatbot
def test_request_email_creation_member_already_have_email(test_client, mock_valid_internal_token):
    """
    Test requesting email creation when the member already has a Mensa email.
    Should return 400 with appropriate error message.
    """

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
    response = test_client.post("/emailrequest/", headers=headers)

    error_detail = (
        "Mensa email already exists for this member. Email Address: fernando.filho@mensa.org.br"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == error_detail


def test_request_email_creation_member_not_found(
    test_client, mock_valid_internal_token, run_db_query
):
    """
    Test requesting email creation when the member is not found.
    Should return 404 with appropriate error message.
    """

    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
    response = test_client.post("/emailrequest/", headers=headers)

    error_detail = "Member not found"
    assert response.status_code == 404
    assert response.json()["detail"] == error_detail


def test_request_email_creation_missing_name(test_client, mock_valid_internal_token, run_db_query):
    """
    Test requesting email creation when the member does not have a name.
    Should return 400 with appropriate error message.
    """

    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("UPDATE registration SET name = NULL WHERE registration_id = 5")

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}

    response = test_client.post("/emailrequest/", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Member name is required to create a Mensa email."


def test_request_email_creation_missing_first_or_last_name(
    test_client, mock_valid_internal_token, run_db_query
):
    """
    Test requesting email creation when the member does not have a first or last name.
    Should return 400 with appropriate error message.
    """

    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("UPDATE registration SET name = 'Fernando' WHERE registration_id = 5")

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}

    response = test_client.post("/emailrequest/", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Member name must contain at least a first and last name."


def test_request_email_creation_success(test_client, mock_valid_internal_token, run_db_query):
    """
    Test successfully requesting Mensa email creation.
    Should return 200 and the created email and password.
    """
    # Clean up and prepare DB state
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("UPDATE registration SET name = 'Fernando Filho' WHERE registration_id = 5")

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}

    # Patch WorkspaceService.create_mensa_email to simulate Google Workspace user creation
    with patch(
        "people_api.services.workspace_service.WorkspaceService.create_mensa_email",
        autospec=True,
    ) as mock_create_mensa_email:
        mock_create_mensa_email.return_value = {
            "message": "Mensa email created successfully",
            "user_data": {
                "email": "fernando.filho@mensa.org.br",
                "password": "mockedpass123",
            },
            "information": "User will be prompted to change the password at the first login.",
        }

        response = test_client.post("/emailrequest/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Mensa email created successfully"
        assert data["user_data"]["email"] == "fernando.filho@mensa.org.br"
        assert data["user_data"]["password"] == "mockedpass123"
        assert (
            data["information"]
            == "User will be prompted to change the password at the first login."
        )


def test_request_password_reset_success(test_client, mock_valid_internal_token):
    """
    Test successfully requesting a password reset for a Mensa email.
    Should return 200 and the reset password info.
    """
    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
    with patch(
        "people_api.services.workspace_service.WorkspaceService.reset_email_password",
        autospec=True,
    ) as mock_reset_password:
        mock_reset_password.return_value = {
            "message": "Password reset successfully",
            "user_data": {
                "email": "fernando.filho@mensa.org.br",
                "password": "resetpass123",
            },
            "information": "User will be prompted to change the password at the first login.",
        }
        response = test_client.post("/emailreset/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset successfully"
        assert data["user_data"]["email"] == "fernando.filho@mensa.org.br"
        assert data["user_data"]["password"] == "resetpass123"
        assert (
            data["information"]
            == "User will be prompted to change the password at the first login."
        )


def test_request_password_reset_no_mensa_email(
    test_client, mock_valid_internal_token, run_db_query
):
    """
    Test requesting password reset when the member does not have a Mensa email.
    Should return 404 with appropriate error message.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")

    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
    # Patch IamService.get_member_by_id to return a member without a Mensa email
    with patch(
        "people_api.services.iam_service.IamService.get_member_by_id", autospec=True
    ) as mock_get_member:
        member = type("Member", (), {"emails": []})()
        mock_get_member.return_value = member
        response = test_client.post("/emailreset/", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "No matching Mensa email found for this member"


def test_request_password_reset_invalid_email_format(
    test_client, mock_valid_internal_token, run_db_query
):
    """
    Test requesting password reset with a non-Mensa email.
    Should return 404 with appropriate error message.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query(
        """
        INSERT INTO emails (email_id, registration_id, email_type, email_address) VALUES (1, 5, 'mensa', 'fernando.diniz@gmail.com')
        """
    )
    # Patch token to use a non-Mensa email
    with patch("people_api.endpoints.member_email.verify_firebase_token") as mock_token:
        mock_token.return_value = type(
            "Token", (), {"email": "fernando.diniz@gmail.com", "registration_id": 5}
        )()
        headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
        response = test_client.post("/emailreset/", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "No matching Mensa email found for this member"


def test_request_password_reset_member_not_found(
    test_client, mock_valid_internal_token, run_db_query
):
    """
    Test requesting password reset when the member is not found.
    Should return 404 with appropriate error message.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM membership_payments WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
    headers = {"Authorization": f"Bearer {mock_valid_internal_token}"}
    with patch(
        "people_api.services.iam_service.IamService.get_member_by_id", autospec=True
    ) as mock_get_member:
        mock_get_member.side_effect = Exception("Member not found")
        response = test_client.post("/emailreset/", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "No matching Mensa email found for this member"
