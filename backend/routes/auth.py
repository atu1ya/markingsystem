import os

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.session_store import create_session

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    session_id: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    expected_password = os.getenv("ASET_APP_PASSWORD")
    if expected_password is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: ASET_APP_PASSWORD not set",
        )

    if payload.password != expected_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    session_id = create_session()
    return LoginResponse(session_id=session_id)
