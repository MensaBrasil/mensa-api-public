"""Tests for member_email router endpoints."""


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


def test_update_email_invalid_format(test_client, mock_valid_token, run_db_query):
    """
    Test updating an email with an invalid email format.
    Expect a 422 validation error.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
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
    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (2, 5, 'alternative', 'oldemail@example.com')"
    )

    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Email",
        "email_address": "invalidemail",
        "email_type": "alternative",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/email/5/2", json=payload, headers=headers)
    assert response.status_code == 422, f"Expected 422 but got {response.status_code}"
