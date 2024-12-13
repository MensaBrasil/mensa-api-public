import subprocess
import time
from pathlib import Path
from unittest import mock

import psycopg2
import pytest
from fastapi.testclient import TestClient

from people_api.app import app
from people_api.auth import verify_firebase_token

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stats"
TEST_DB_DUMP_PATH = Path(__file__).parent / "test_db_dump.sql"


def wait_for_db(timeout=60):
    """Wait for the database to be ready, retrying until timeout"""
    start_time = time.time()
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            break
        except psycopg2.OperationalError:
            if time.time() - start_time > timeout:
                raise Exception("Timeout while waiting for the database to be ready.")
            time.sleep(2)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Set up the database before any tests run."""
    try:
        # Start the test database container
        subprocess.run(["docker", "compose", "up", "-d", "test-db"], check=True)
        wait_for_db()  # Ensure the DB is ready before proceeding

        # Drop and recreate the public schema
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            conn.commit()
        conn.close()

        # Apply existing migrations
        subprocess.run(
            ["alembic", "-c", "people_api/database/alembic.ini", "upgrade", "c4c4ea41ac02"],
            check=True,
        )

        # Populate the database with test data
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            with open(TEST_DB_DUMP_PATH) as dump_file:
                cur.execute(dump_file.read())
            conn.commit()
        conn.close()
    except (subprocess.CalledProcessError, psycopg2.Error) as e:
        pytest.exit(f"Failed to set up the database: {str(e)}")
    yield

    # Stop the database container
    subprocess.run(["docker", "compose", "down"], check=True)


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Reset the database before each test"""
    try:
        # Drop all data
        subprocess.run(["docker", "compose", "down", "--volumes", "--remove-orphans"], check=True)
        # Restart the test database
        subprocess.run(["docker", "compose", "up", "-d", "test-db"], check=True)
        wait_for_db()  # Ensure the DB is fully ready

        # Reapply migrations
        subprocess.run(
            ["alembic", "-c", "people_api/database/alembic.ini", "upgrade", "head"], check=True
        )

        # Reload test data
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            with open("tests/test_db_dump.sql") as dump_file:
                cur.execute(dump_file.read())
            conn.commit()
        conn.close()
    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to reset the database: {e}")
    yield


@pytest.fixture(scope="function")
def test_client():
    """Create a FastAPI test client, ensuring DB is connected"""
    wait_for_db()  # Ensure DB is ready before starting the test client
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function")
def mock_valid_token():
    """Mock the verify_firebase_token function to return a valid token"""

    def mock_verify_firebase_token():
        return {
            "name": "Fernando Diniz Souza Filho",
            "picture": "https://lh3.googleusercontent.com/a/ACg8ocLTbtfPMG0uE7NFMuxQxoNyYlQ0f_3WJDlpeX4wVnL3Gg=s96-c",
            "iss": "https://securetoken.google.com/carteirinhasmensa",
            "aud": "carteirinhasmensa",
            "auth_time": 1709996057,
            "user_id": "V3jqdbSNw3hQsbQMD5mcs2q88PJ3",
            "sub": "V3jqdbSNw3hQsbQMD5mcs2q88PJ3",
            "iat": 1722977514,
            "exp": 1722981114,
            "email": "fernando.filho@mensa.org.br",
            "email_verified": True,
            "firebase": {
                "identities": {
                    "google.com": ["101271401621105857573"],
                    "email": ["fernando.filho@mensa.org.br"],
                },
                "sign_in_provider": "google.com",
            },
        }

    # Override the dependency in the FastAPI app
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    yield
    # Clean up after test
    app.dependency_overrides.pop(verify_firebase_token, None)


@pytest.fixture(autouse=True)
def mock_firebase_initialization():
    with mock.patch("firebase_admin.initialize_app") as mock_initialize_app:
        with mock.patch("firebase_admin.credentials.Certificate") as mock_certificate:
            mock_certificate.return_value = mock.Mock()
            yield mock_initialize_app, mock_certificate


@pytest.fixture
def run_db_query():
    """Fixture to run arbitrary queries on the database."""

    def run_query(query):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()  # Commit for updates, inserts, etc.

                # Only fetch results for SELECT queries
                if query.strip().lower().startswith("select"):
                    return cur.fetchall()  # Return fetched results for SELECT queries
        finally:
            conn.close()  # Ensure the connection is closed after the query

    return run_query
