"""DATABASE
MongoDB, Firebase, PostgreSQL, and Redis initialization.
"""

import os
from collections.abc import AsyncGenerator

import firebase_admin
import redis.asyncio as redis
from firebase_admin import credentials, firestore
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlmodel import Session, create_engine, text

from .settings import get_settings

settings = get_settings()

# PostgreSQL
DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_database}"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_pre_ping=True)

# Create a Base class for our models
Base = declarative_base()

# Create the sessionmaker, scoped for thread safety
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
)


def get_session() -> Session:
    """Provides a synchronous database session for read-write operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()


def get_read_only_session() -> Session:
    """Provides a synchronous read-only database session."""
    db = SessionLocal()
    try:
        db.execute(text("SET TRANSACTION READ ONLY"))
        yield db
    finally:
        db.close()


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
    global firebase_app
    if firebase_app is None:
        if os.path.exists("firebase_secret.json"):
            print("Initializing Firebase", flush=True)
            cred = credentials.Certificate("firebase_secret.json")
            firebase_app = firebase_admin.initialize_app(cred)
        else:
            print("firebase_secret.json not found. Skipping Firebase initialization.", flush=True)
            firebase_app = "mock_firebase_app"
    return firebase_app


def get_firebase_collection():
    app = initialize_firebase()
    if app == "mock_firebase_app":
        print("Using mock Firebase collection.", flush=True)
        return None
    db = firestore.client(app=app)
    return db.collection("users")


firebase_collection = get_firebase_collection()
