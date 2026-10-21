"""Authorization helpers for persisted chat sessions."""

from fastapi import HTTPException


def get_owned_chat_session(session_id: int, current_user, repository):
    """Return a chat session only when it belongs to the authenticated user.

    A 404 for both missing and foreign sessions avoids disclosing whether a
    particular session ID exists.
    """
    session = repository.get_session(session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session
