"""Tests for member_legal_representative router endpoints."""

# --- API Key Endpoint Tests ---


def test_add_legal_representative_api_key_invalid_token(test_client):
    """
    Test adding a legal representative using API key authentication with an invalid token.
    """
    payload = {
        "token": "INVALID_API_KEY",
        "mb": "5",
        "birth_date": "01/01/2005",
        "cpf": "11111111111",
        "legal_representative": {
            "cpf": "22222222222",
            "full_name": "Legal Rep One",
            "email": "legalrep@example.com",
            "phone": "(11) 91234-5678",
            "alternative_phone": "(11) 91234-5678",
            "observations": "Test observation",
        },
    }
    response = test_client.post("/legal_representative_twilio", json=payload)
    assert response.status_code == 401, f"Expected status 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, f"Unexpected response: {response.json()}"


def test_add_legal_representative_api_key_success(test_client, run_db_query):
    """
    Test successfully adding a legal representative via API key.
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
        "VALUES (5, False, False, False, '2025-12-10', '11111111111', '2021-01-01')"
    )

    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    payload = {
        "token": "WHATSAPP_ROUTE_API_KEY",
        "mb": "5",
        "birth_date": "10/12/2025",
        "cpf": "11111111111",
        "legal_representative": {
            "cpf": "22222222222",
            "full_name": "Legal Rep Two",
            "email": "legalrep2@example.com",
            "phone": "(11) 91234-5678",
            "alternative_phone": "(11) 91234-5678",
            "observations": "Another test observation",
        },
    }

    response = test_client.post("/legal_representative_twilio", json=payload)

    assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
    assert response.json() == {"message": "Legal representative added successfully"}


# --- Member Token-Based Endpoints Tests ---


def test_add_legal_representative_invalid_token(test_client, mock_valid_token):
    """
    Test adding a legal representative with an invalid token (i.e. email not matching member's).
    """
    payload = {
        "cpf": "22222222222",
        "full_name": "Legal Rep Two",
        "email": "legalrep2@example.com",
        "phone": "(11) 91234-5678",
        "alternative_phone": "(11) 91234-5678",
        "observations": "Another test observation",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/legal_representative/2623", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, f"Unexpected response: {response.json()}"


def test_add_legal_representative_should_return_success(
    test_client, mock_valid_token, run_db_query
):
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
        "VALUES (5, False, False, False, '2025-12-10', '11111111111', '2021-01-01')"
    )

    run_db_query(
        "INSERT INTO emails (email_id, registration_id, email_type, email_address) "
        "VALUES (1, 5, 'main', 'fernando.filho@mensa.org.br')"
    )

    payload = {
        "cpf": "22222222222",
        "full_name": "Legal Rep Two",
        "email": "legalrep2@example.com",
        "phone": "+5511912345678",
        "alternative_phone": "+5511912345678",
        "observations": "Another test observation",
    }

    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.post("/legal_representative/5", json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Legal representative added successfully"}


def test_update_legal_representative_invalid_token(test_client, mock_valid_token):
    """
    Test updating a legal representative with an invalid token.
    """
    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Legal Rep",
        "email": "updated@example.com",
        "phone": "(11) 99876-5432",
        "alternative_phone": "(11) 99876-5432",
        "observations": "Updated observation",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/legal_representative/2623/11771", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, f"Unexpected response: {response.json()}"


def test_update_legal_representative_should_return_success(
    test_client, mock_valid_token, run_db_query
):
    """
    Test successfully updating a legal representative.
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

    run_db_query(
        "INSERT INTO legal_representatives (representative_id, registration_id, cpf, full_name, email, phone, alternative_phone, observations) "
        "VALUES (1, 5, '22222222222', 'Legal Rep Two', 'legalrep2@example.com', '(11) 91234-5678', '(11) 91234-5678', 'Observation')"
    )

    payload = {
        "cpf": "33333333333",
        "full_name": "Updated Legal Rep",
        "email": "updated@example.com",
        "phone": "(11) 99876-5432",
        "alternative_phone": "(11) 99876-5432",
        "observations": "Updated observation",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/legal_representative/5/1", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Legal representative updated successfully"}


def test_delete_legal_representative_invalid_token(test_client, mock_valid_token):
    """
    Test deleting a legal representative with an invalid token.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.delete("/legal_representative/2623/11771", headers=headers)
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, f"Unexpected response: {response.json()}"


def test_delete_legal_representative_should_return_success(
    test_client, mock_valid_token, run_db_query
):
    """
    Test successfully deleting a legal representative.
    """
    run_db_query("DELETE FROM emails WHERE registration_id = 5")
    run_db_query("DELETE FROM legal_representatives WHERE registration_id = 5")
    run_db_query("DELETE FROM member_groups WHERE registration_id = 5")
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query("DELETE FROM registration WHERE registration_id = 5")
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
        "INSERT INTO legal_representatives (representative_id, registration_id, cpf, full_name, email, phone, alternative_phone, observations) "
        "VALUES (1, 5, '22222222222', 'Legal Rep Two', 'legalrep2@example.com', '(11) 91234-5678', '(11) 91234-5678', 'Observation')"
    )

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.delete("/legal_representative/5/1", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Legal representative deleted successfully"}
