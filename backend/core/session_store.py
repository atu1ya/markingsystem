from typing import Any, Dict

from fastapi import Depends, HTTPException, Request, status
from uuid import uuid4

SESSION_STORE: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    """Create a new session and return its id."""
    session_id = str(uuid4())
    SESSION_STORE[session_id] = {
        "answer_keys": {},
        "concept_map": None,
    }
    return session_id


def get_session_id_from_header(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Session-ID header",
        )
    if session_id not in SESSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return session_id


def get_session(session_id: str = Depends(get_session_id_from_header)) -> Dict[str, Any]:
    """FastAPI dependency to retrieve the current session dict."""
    return SESSION_STORE[session_id]
