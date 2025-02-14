"""DATABASE
MongoDB, Firebase, PostgreSQL, and Redis initialization.
"""

import os
from collections.abc import AsyncGenerator, AsyncIterator, Generator

import firebase_admin
import redis.asyncio as redis
from firebase_admin import credentials, firestore
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import get_settings

settings = get_settings()

# PostgreSQL
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_database}"

ASYNC_RO_DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_ro_user}:{settings.postgres_ro_password}@{settings.postgres_host}/{settings.postgres_database}"

DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_database}"

RO_DATABASE_URL = f"postgresql://{settings.postgres_ro_user}:{settings.postgres_ro_password}@{settings.postgres_host}/{settings.postgres_database}"

async_engine_rw = create_async_engine(
    url=ASYNC_DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=5,
    max_overflow=20,
    pool_pre_ping=True,
)
rw_sessionmaker = async_sessionmaker(
    async_engine_rw, class_=AsyncSession, autoflush=False, expire_on_commit=False
)

async_engine_ro = create_async_engine(
    url=ASYNC_RO_DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=5,
    max_overflow=20,
    pool_pre_ping=True,
)
ro_sessionmaker = async_sessionmaker(
    async_engine_ro, class_=AsyncSession, autoflush=False, expire_on_commit=False
)

# Create SQLModel engine
engine = create_engine(url=DATABASE_URL)
ro_engine = create_engine(url=RO_DATABASE_URL)


def get_session() -> Generator[Session]:
    """Provide an sync sqlmodel session to the database."""
    with Session(engine) as session:
        yield session
        session.commit()


def get_read_only_session() -> Generator[Session]:
    """Provide an sync sqlmodel read-only session to the database."""
    with Session(ro_engine) as session:
        yield session


class AsyncSessionsTuple(BaseModel):
    """Tuple of async read-only and read-write sessions."""

    ro: AsyncSession
    rw: AsyncSession

    model_config = ConfigDict(arbitrary_types_allowed=True)


async def get_async_sessions() -> AsyncIterator[AsyncSessionsTuple]:
    """Provide async read-only and read-write sessions."""
    rw_session = rw_sessionmaker()
    ro_session = ro_sessionmaker()
    try:
        yield AsyncSessionsTuple(ro=ro_session, rw=rw_session)
        await rw_session.commit()
    except Exception:
        await rw_session.rollback()
        raise
    finally:
        await rw_session.close()
        await ro_session.close()


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Provides an async Redis client."""
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


# Firebase
firebase_app = None


def initialize_firebase():
    """Initialize Firebase."""

    global firebase_app
    if firebase_app is None:
        if os.path.exists("firebase_secret.json"):
            print("Initializing Firebase", flush=True)
            cred = credentials.Certificate("firebase_secret.json")
            firebase_app = firebase_admin.initialize_app(cred)
        else:
            print(
                "firebase_secret.json not found. Skipping Firebase initialization.",
                flush=True,
            )
            firebase_app = "mock_firebase_app"
    return firebase_app


def get_firebase_collection():
    """Get the Firebase collection."""

    app = initialize_firebase()
    if app == "mock_firebase_app":
        print("Using mock Firebase collection.", flush=True)
        return None
    db = firestore.client(app=app)
    return db.collection("users")


firebase_collection = get_firebase_collection()