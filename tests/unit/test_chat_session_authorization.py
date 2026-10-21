from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.auth.chat_access import get_owned_chat_session


class FakeChatRepository:
    def __init__(self, session):
        self.session = session

    def get_session(self, session_id):
        return self.session if self.session and self.session.id == session_id else None


def test_owned_session_is_returned():
    user = SimpleNamespace(id=7)
    session = SimpleNamespace(id=12, user_id=7)

    result = get_owned_chat_session(12, user, FakeChatRepository(session))

    assert result is session


def test_foreign_session_is_hidden_as_not_found():
    user = SimpleNamespace(id=7)
    session = SimpleNamespace(id=12, user_id=99)

    with pytest.raises(HTTPException) as exc_info:
        get_owned_chat_session(12, user, FakeChatRepository(session))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Chat session not found"


def test_missing_session_returns_not_found():
    user = SimpleNamespace(id=7)

    with pytest.raises(HTTPException) as exc_info:
        get_owned_chat_session(12, user, FakeChatRepository(None))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Chat session not found"
