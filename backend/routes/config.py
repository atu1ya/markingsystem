from typing import Dict, List, Literal

from fastapi import APIRouter, Depends, HTTPException, status  # noqa: F401
from pydantic import BaseModel, validator

from core.session_store import get_session

router = APIRouter(prefix="/config", tags=["config"])

Letter = Literal["A", "B", "C", "D", "E"]


class ReadingAnswerKey(BaseModel):
    __root__: Dict[str, Letter]

    @validator("__root__")
    def validate_keys(cls, value: Dict[str, Letter]) -> Dict[str, Letter]:  # noqa: D417
        for key in value:
            if not key.isdigit():
                raise ValueError("All question keys must be numeric strings")
        return value


class SubjectAnswerKey(BaseModel):
    __root__: Dict[str, Letter]

    @validator("__root__")
    def validate_keys(cls, value: Dict[str, Letter]) -> Dict[str, Letter]:  # noqa: D417
        for key in value:
            if not key.isdigit():
                raise ValueError("All question keys must be numeric strings")
        return value


class QrArAnswerKey(BaseModel):
    qr: SubjectAnswerKey
    ar: SubjectAnswerKey


class ConceptMap(BaseModel):
    __root__: Dict[str, Dict[str, List[int]]]


@router.post("/reading-key")
def set_reading_key(
    payload: ReadingAnswerKey,
    session: dict = Depends(get_session),
):
    session.setdefault("answer_keys", {})
    session["answer_keys"]["reading"] = payload.__root__
    return {"status": "ok", "message": "Reading answer key loaded"}


@router.post("/qr-ar-key")
def set_qr_ar_key(
    payload: QrArAnswerKey,
    session: dict = Depends(get_session),
):
    session.setdefault("answer_keys", {})
    session["answer_keys"]["qr_ar"] = payload.dict()
    return {"status": "ok", "message": "QR/AR answer key loaded"}


@router.post("/concepts")
def set_concepts(
    payload: ConceptMap,
    session: dict = Depends(get_session),
):
    session["concept_map"] = payload.__root__
    return {"status": "ok", "message": "Concept map loaded"}
