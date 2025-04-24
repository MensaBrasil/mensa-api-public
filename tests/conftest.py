"""Fixtures for the test suite."""

import subprocess
import time
import os
from pathlib import Path
from unittest import mock
from moto import mock_aws
import boto3   

import psycopg2
import pytest
from fastapi.testclient import TestClient

from collections.abc import Generator
from moto.server import ThreadedMotoServer

from people_api.app import app  # type: ignore
from people_api.auth import verify_firebase_token
from people_api.schemas import UserToken
from tests.router_config import test_router

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/stats"
TEST_DB_DUMP_PATH = Path(__file__).parent / "test_db_dump.sql"
AWS_ACCESS_KEY_ID = "testing"
AWS_SECRET_ACCESS_KEY = "testing"
AWS_SECURITY_TOKEN = "testing"
AWS_SESSION_TOKEN = "testing"
AWS_DEFAULT_REGION = "us-east-1"
MY_BUCKET_NAME = "mybucket"
AWS_S3_ENDPOINT_URL = "http://localhost"


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
        # Make sure composer is down before starting the test
        subprocess.run(["uv", "run", "docker", "compose", "down"], check=True)

        # Start the test database container
        subprocess.run(
            ["uv", "run", "docker", "compose", "up", "-d", "test-db", "redis"],
            check=True,
        )

        # Apply migrations
        subprocess.run(
            [
                "uv",
                "run",
                "alembic",
                "-c",
                "people_api/database/alembic.ini",
                "upgrade",
                "head",
            ],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to set up the database: {e}")

    # Create read-only user for database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute("CREATE USER mensa_ro WITH PASSWORD 'postgres';")
            cur.execute("GRANT CONNECT ON DATABASE stats TO mensa_ro;")
            cur.execute("GRANT USAGE ON SCHEMA public TO mensa_ro;")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO mensa_ro;")
            cur.execute(
                "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mensa_ro;"
            )
            conn.commit()
    except psycopg2.Error as e:
        if "already exists" not in str(e):
            pytest.exit(f"Failed to create read-only user: {e}")

    # Make sure composer is down after all tests
    yield
    try:
        subprocess.run(["uv", "run", "docker", "compose", "down"], check=True)
    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to tear down Docker containers: {e}")


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Reset the database before each test"""
    try:
        # Truncate all tables in the database
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute(
                """
                DO $$ DECLARE
                r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                        EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
                """
            )
            conn.commit()
            wait_for_db()
        # Populate the database with the initial data

        with open(TEST_DB_DUMP_PATH, encoding="utf-8") as f:
            sql = f.read()
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to reset the database: {e}")
    yield


@pytest.fixture(scope="session")
def test_client():
    """Create a FastAPI test client, ensuring DB is connected and test routes are included."""
    app.include_router(test_router)

    wait_for_db()
    with TestClient(app, base_url="http://localhost:5000") as c:
        yield c


@pytest.fixture(scope="function")
def mock_valid_token():
    """Mock the verify_firebase_token function to return a valid token"""

    def mock_verify_firebase_token():
        return UserToken(
            iss="https://securetoken.google.com/carteirinhasmensa",
            aud="carteirinhasmensa",
            auth_time=1709996057,
            sub="V3jqdbSNw3hQsbQMD5mcs2q88PJ3",
            iat=1722977514,
            exp=1722981114,
            email="fernando.filho@mensa.org.br",
            registration_id=5,
        )

    # Override the dependency in the FastAPI app
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    yield
    # Clean up after test
    app.dependency_overrides.pop(verify_firebase_token, None)


@pytest.fixture(autouse=True)
def mock_firebase_initialization():
    """Mock the Firebase Admin SDK initialization"""

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


@pytest.fixture
def mock_valid_token_auth():
    """Override verify_firebase_token to return a UserToken instance only for auth tests."""

    def override_verify_firebase_token():
        return UserToken(
            email="fernando.filho@mensa.org.br",
            permissions=["CREATE.EVENT", "WHATSAPP.BOT", "VOLUNTEER.CATEGORY.CREATE", "VOLUNTEER.CATEGORY.UPDATE", "VOLUNTEER.CATEGORY.DELETE", "VOLUNTEER.EVALUATION.UPDATE", "VOLUNTEER.EVALUATION.CREATE"],
            exp=1722981114,
            iat=1722977514,
            aud="carteirinhasmensa",
            iss="https://securetoken.google.com/carteirinhasmensa",
            sub="V3jqdbSNw3hQsbQMD5mcs2q88PJ3",
            auth_time=1709996057,
            registration_id=5,
        )

    app.dependency_overrides[verify_firebase_token] = override_verify_firebase_token
    yield
    app.dependency_overrides.pop(verify_firebase_token, None)


@pytest.fixture(scope="session", autouse=True)
def moto_server() -> Generator[str, None, None]:
    server = ThreadedMotoServer(port=4000)
    server.start()
    yield "http://localhost:4000"
    server.stop()


@pytest.fixture(scope="function")
def aws_resource():
    """
    Fixture to start the generic AWS mock (mock_aws) and create the test bucket.
    """
    bucket_name = os.environ.get("MY_BUCKET_NAME", "mybucket") 
    with mock_aws():
        s3 = boto3.resource(
            "s3",
            region_name="us-east-1",
            endpoint_url=os.environ.get("AWS_S3_ENDPOINT_URL"),
        )
        s3.create_bucket(Bucket=bucket_name)
        yield s3