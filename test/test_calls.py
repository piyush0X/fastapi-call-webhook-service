import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Call


# In-memory SQLite database for tests.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_duplicate_call_id_creates_only_one_record(client, db):
    payload = {
        "call_id": "abc123",
        "status": "answered",
        "duration_secs": 42,
    }

    # First request
    response1 = client.post("/call-ended", json=payload)

    # Second request with exactly the same call_id
    response2 = client.post("/call-ended", json=payload)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Both requests should return the same stored record.
    assert response1.json()["call_id"] == "abc123"
    assert response2.json()["call_id"] == "abc123"

    # Most important assertion:
    # There must be exactly ONE database record.
    record_count = (
        db.query(func.count(Call.id))
        .filter(Call.call_id == "abc123")
        .scalar()
    )

    assert record_count == 1