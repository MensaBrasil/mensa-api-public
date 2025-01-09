"""Test cases for the member module"""

from typing import Any


def test_read_main(test_client: Any) -> None:
    """Test the read_main function"""
    response = test_client.get("/")
    assert response.status_code == 404


def test_set_pronouns_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test setting pronouns with a valid token"""
    headers = {"Authorization": "Bearer mock-valid-token"}
    response = test_client.patch("/pronouns", json={"pronouns": "Ela/dela"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Pronouns set successfully"}


def test_set_pronouns_invalid_pronouns(test_client: Any, mock_valid_token: Any) -> None:
    """Test setting pronouns with an invalid pronouns value"""
    headers = {"Authorization": "Bearer mock-valid-token"}
    response = test_client.patch("/pronouns", json={"pronouns": "Invalid"}, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Pronouns must be Ele/dele, Ela/dela or Elu/delu or Nenhuma das opções"
    }


def test_get_missing_fields_all_fields_present(test_client: Any, mock_valid_token: Any) -> None:
    """Test when all fields (CPF, birth_date) are present"""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/missing_fields", headers=headers)
    assert response.status_code == 200
    assert response.json() == []  # Expecting an empty list if no fields are missing


def test_get_missing_fields_missing_cpf(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test when the CPF is missing"""
    # Delete CPF from the member with the email 'calvin@mensa.org.br'
    run_db_query("""
        UPDATE registration
        SET cpf = NULL
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/missing_fields", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["cpf"]


def test_get_missing_fields_missing_birth_date(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test when the birth_date is missing"""
    # Delete birth_date from the member with the email 'calvin@mensa.org.br'
    run_db_query("""
        UPDATE registration
        SET birth_date = NULL
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/missing_fields", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        "birth_date"
    ]  # Expecting 'birth_date' to be in the list of missing fields


def test_get_missing_fields_missing_both_fields(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test when both CPF and birth_date are missing"""
    # Delete both CPF and birth_date from the member with the email 'calvin@mensa.org.br'
    run_db_query("""
        UPDATE registration
        SET cpf = NULL, birth_date = NULL
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/missing_fields", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        "cpf",
        "birth_date",
    ]  # Expecting both 'cpf' and 'birth_date' to be in the list of missing fields


def test_get_missing_fields_invalid_token(test_client: Any) -> None:
    """Test when the token is invalid"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/missing_fields", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_set_missing_fields_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test setting missing fields (CPF and birth_date) with valid data"""

    # Set up the member with missing fields (CPF and birth_date)
    run_db_query("""
    UPDATE registration
    SET cpf = NULL, birth_date = NULL
    WHERE registration_id IN (
        SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
    )
""")

    # Define the payload with valid CPF and birth_date
    payload = {"cpf": "12345678909", "birth_date": "1992-02-02"}

    # Make the request with valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    # Check the response status and message
    assert response.status_code == 200
    assert response.json() == {"message": "Missing fields set successfully"}

    # Verify that the member's fields were updated in the database
    updated_member = run_db_query("""
        SELECT cpf, birth_date FROM registration
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)
    assert [(cpf, birth_date.strftime("%Y-%m-%d")) for cpf, birth_date in updated_member] == [
        ("12345678909", "1992-02-02")
    ]


def test_set_missing_fields_invalid_cpf_format(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test setting missing fields with invalid cpf format"""

    # Set up the member with missing fields (CPF and birth_date)
    run_db_query(
        """
            UPDATE registration
            SET cpf = NULL
            WHERE registration_id IN (SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br')
        """
    )

    # Define the payload with invalid CPF
    payload = {"cpf": "1234567898"}

    # Make the request with valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid CPF"}


def test_set_missing_fields_invalid_cpf_number(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test setting missing fields with invalid data"""

    # Set up the member with missing fields (CPF and birth_date)
    run_db_query(
        """
            UPDATE registration
            SET cpf = NULL
            WHERE registration_id IN (SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br')
        """
    )

    # Define the payload with invalid CPF
    payload = {"cpf": "12345678905"}

    # Make the request with valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid CPF"}


def test_set_missing_fields_invalid_birth_date_format(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test setting missing fields with invalid birth_date"""
    # Set up the member with missing fields (birth_date)
    run_db_query(
        """
            UPDATE registration
            SET birth_date = NULL
            WHERE registration_id IN (SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br')
        """
    )

    # Define the payload with invalid birth)date
    payload = {"birth_date": "01-12-1980"}

    # Make the request with valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid birth_date format"}


def test_set_missing_fields_invalid_token(test_client: Any) -> None:
    """Test setting missing fields with an invalid token"""
    # Define the payload with CPF and birth_date
    payload = {"cpf": "12345678909", "birth_date": "1990-01-01"}

    # Make the request with an invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    # Check that the response returns a 401 status code
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_set_missing_fields_no_update_needed(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test setting missing fields when no update is needed"""

    # Ensure member already has CPF and birth_date set
    run_db_query("""
        UPDATE registration
        SET cpf = '12345678909', birth_date = '1990-01-01'
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)

    # Define the payload with the same CPF and birth_date
    payload = {"cpf": "12345678909", "birth_date": "1995-02-02"}

    # Make the request with valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/missing_fields", json=payload, headers=headers)

    # Check the response status and message (should still succeed)
    assert response.status_code == 200
    assert response.json() == {"message": "Missing fields set successfully"}

    # Ensure no changes were made in the database
    unchanged_member = run_db_query("""
        SELECT cpf, birth_date FROM registration
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """)
    assert [(cpf, birth_date.strftime("%Y-%m-%d")) for cpf, birth_date in unchanged_member] == [
        ("12345678909", "1990-01-01")
    ]


def test_update_fb_profession_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    # Define the payload with the updated profession and Facebook URL
    payload = {"profession": "Engineer", "facebook": "https://facebook.com/new_profile"}

    # Make the request with a valid authorization token
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/update_fb_profession/5", json=payload, headers=headers)

    # Check the response status and message
    assert response.status_code == 200
    assert response.json() == {"message": "Member updated successfully"}

    # Verify that the member's data was updated in the database
    updated_member = run_db_query("""
        SELECT profession, facebook FROM registration WHERE registration_id = 5
    """)
    assert updated_member == [("Engineer", "https://facebook.com/new_profile")]


def test_update_fb_profession_invalid_token(test_client: Any) -> None:
    """Test updating profession and Facebook URL with an invalid token"""
    payload = {"profession": "Engineer", "facebook": "https://facebook.com/new_profile"}
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.put("/update_fb_profession/1", json=payload, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_update_fb_profession_unauthorized_member(test_client: Any, mock_valid_token: Any) -> None:
    """Test updating profession and Facebook URL with unauthorized member"""

    # Define the payload with the updated profession and Facebook URL
    payload = {"profession": "Engineer", "facebook": "https://facebook.com/new_profile"}

    # Make the request with valid authorization but for the wrong member ID
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/update_fb_profession/1805", json=payload, headers=headers)

    # Expecting an unauthorized error since the token does not match the member ID
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
