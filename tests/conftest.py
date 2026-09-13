import uuid

import pytest
from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.user import User
from app.repositories.chat_repository import ChatRepository


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db):
    unique_id = uuid.uuid4().hex[:12]

    user = User(
        username=f"pytest_user_{unique_id}",
        email=f"pytest_{unique_id}@example.com",
        password_hash="pytest-password-hash",
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def test_session(db, test_user):
    repository = ChatRepository(db)

    return repository.create_session(
        user_id=test_user.id,
        title="Pytest Test Chat",
    )
