"""Fixtures for the test suite."""

import os
import subprocess
import time
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import boto3
import psycopg2
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from moto import mock_aws
from moto.server import ThreadedMotoServer
from sqlmodel import Session
from twilio.request_validator import RequestValidator

from people_api.app import app  # type: ignore
from people_api.auth import create_token, verify_firebase_token
from people_api.dbs import engine
from people_api.schemas import UserToken
from people_api.settings import get_settings
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


@pytest.fixture(scope="session", autouse=True)
def ensure_env_and_keys() -> Generator[None, None, None]:
    """Ensure RSA keys exist for tests."""

    # The tests expect environment variables to be already configured via a
    # pre-existing ``.env`` file.  We therefore skip copying ``sample.env`` and
    # simply rely on the file being present.

    private_key = Path("private_key.pem")
    public_key = Path("public_key.pem")
    if not private_key.exists() or not public_key.exists():
        subprocess.run(["openssl", "genrsa", "-out", "private_key.pem", "4096"], check=True)
        subprocess.run(
            [
                "openssl",
                "rsa",
                "-in",
                "private_key.pem",
                "-pubout",
                "-out",
                "public_key.pem",
            ],
            check=True,
        )
        private_key.chmod(0o600)
        public_key.chmod(0o644)

    yield


def wait_for_db(timeout=60):
    """Wait for the database to be ready, retrying until timeout"""
    start_time = time.time()
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            break
        except psycopg2.OperationalError as e:
            if time.time() - start_time > timeout:
                raise Exception("Timeout while waiting for the database to be ready.") from e
            time.sleep(2)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Set up the database before any tests run."""
    use_docker = os.getenv("USE_DOCKER_POSTGRES_FOR_TESTS", "true").lower() == "true"
    try:
        if use_docker:
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
        if use_docker:
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

    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    yield
    app.dependency_overrides.pop(verify_firebase_token, None)


@pytest.fixture
def get_valid_internal_token(sync_rw_session):
    """
    Return a function that generates a valid JWT token for a given registration_id.
    Usage:
        token = get_valid_internal_token(registration_id)
    """

    def _get_token(registration_id):
        return create_token(registration_id=registration_id, ttl=3600, session=sync_rw_session)

    return _get_token


@pytest.fixture(scope="function")
def mock_valid_internal_token():
    """Mock the verify_internal_token function to return a valid token"""

    def mock_verify_internal_token():
        return UserToken(
            iss="mensa_api",
            sub="5",
            exp=int((datetime.now(tz=timezone.utc) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=timezone.utc).timestamp()),
            registration_id=5,
            email="fernando.filho@mensa.org.br",
            permissions=[
                "CREATE.EVENT",
                "WHATSAPP.BOT",
                "VOLUNTEER.CATEGORY.CREATE",
                "VOLUNTEER.CATEGORY.UPDATE",
                "VOLUNTEER.CATEGORY.DELETE",
                "VOLUNTEER.EVALUATION.UPDATE",
                "VOLUNTEER.EVALUATION.CREATE",
            ],
        )

    app.dependency_overrides[verify_firebase_token] = mock_verify_internal_token
    yield
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
            permissions=[
                "CREATE.EVENT",
                "WHATSAPP.BOT",
                "VOLUNTEER.CATEGORY.CREATE",
                "VOLUNTEER.CATEGORY.UPDATE",
                "VOLUNTEER.CATEGORY.DELETE",
                "VOLUNTEER.EVALUATION.UPDATE",
                "VOLUNTEER.ACTIVITY.CREATE",
                "VOLUNTEER.LEADERBOARD.VIEW",
                "VOLUNTEER.CATEGORY.LIST",
                "VOLUNTEER.EVALUATION.VIEW",
                "VOLUNTEER.EVALUATION.CREATE",
            ],
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


@pytest.fixture
def aws_resource():
    """Fixture to mock AWS S3 resource."""
    with mock_aws():
        s3 = boto3.resource("s3", region_name="us-east-1")
        yield s3


@pytest.fixture(scope="session", autouse=True)
def disable_otel_middleware():
    """Disable OpenTelemetry logging middleware during tests."""
    original_middleware = app.user_middleware.copy()

    app.user_middleware = [
        middleware
        for middleware in app.user_middleware
        if "otel_logging_middleware" not in str(middleware)
    ]

    yield

    app.user_middleware = original_middleware


@pytest.fixture
def sync_rw_session():
    """Yield a valid sync SQLModel session for tests."""

    with Session(engine) as session:
        yield session


@pytest.fixture
def sign_twilio_request():
    """
    Fixture to sign Twilio requests for endpoint testing.

    Usage:
        headers = sign_twilio_request(url, form_data)
        response = test_client.post(url, data=form_data, headers=headers)
    """

    def _sign(url, form_data, auth_token=None):
        # Use the configured Twilio auth token if not provided
        if auth_token is None:
            auth_token = get_settings().twilio_auth_token

        validator = RequestValidator(auth_token)
        signature = validator.compute_signature(url, form_data)
        return {
            "X-Twilio-Signature": signature,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    return _sign


@pytest_asyncio.fixture(autouse=True)
async def reset_async_db_engines():
    """Reset async DB engines after each test to avoid cross-loop issues."""
    yield
    from people_api import dbs

    if dbs.async_engine_rw is not None:
        await dbs.async_engine_rw.dispose()
    if dbs.async_engine_ro is not None:
        await dbs.async_engine_ro.dispose()

    dbs.async_engine_rw = None
    dbs.async_engine_ro = None
    dbs.rw_sessionmaker = None
    dbs.ro_sessionmaker = None
