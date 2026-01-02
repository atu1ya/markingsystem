from typing import Dict

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from core.annotate import annotate_incorrect_bubbles, write_section_score
from core.engine import mark_single_student_papers
from core.export import build_output_zip
from core.pdf_tools import pdf_to_images
from core.questions_qr_ar import QUESTIONS_AR, QUESTIONS_QR
from core.questions_reading import QUESTIONS_READING
from core.session_store import get_session

router = APIRouter(prefix="/mark", tags=["mark"])


@router.post("/single-student")
async def mark_single_student(
    student_name: str = Form(...),
    writing_score: str = Form(...),
    reading_pdf: UploadFile = File(...),
    qr_ar_pdf: UploadFile = File(...),
    session: Dict = Depends(get_session),
):
    if reading_pdf.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reading_pdf must be a PDF",
        )

    if qr_ar_pdf.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="qr_ar_pdf must be a PDF",
        )

    reading_bytes = await reading_pdf.read()
    qr_ar_bytes = await qr_ar_pdf.read()

    if "answer_keys" not in session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer keys not loaded for this session.",
        )

    try:
        reading_images = pdf_to_images(reading_bytes)
        qr_ar_images = pdf_to_images(qr_ar_bytes)
    except Exception as exc:  # pragma: no cover - pdf parsing errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process uploaded PDFs: {exc}",
        ) from exc

    if not reading_images or not qr_ar_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDFs must contain at least one page.",
        )

    reading_image = reading_images[0]
    qr_ar_image = qr_ar_images[0]

    try:
        result = mark_single_student_papers(
            reading_bytes,
            qr_ar_bytes,
            session["answer_keys"],
            session.get("concept_map") or {},
        )
    except Exception as exc:  # pragma: no cover - engine level errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Marking engine error: {exc}",
        ) from exc

    # Annotate reading sheet
    reading_img_annot = annotate_incorrect_bubbles(
        reading_image,
        result["reading"]["answers"],
        result["reading"]["results"],
        QUESTIONS_READING,
    )
    reading_img_annot = write_section_score(
        reading_img_annot,
        "Reading",
        result["reading"]["correct"],
        result["reading"]["total"],
    )

    # Annotate QR/AR sheet (apply sequentially to cover both subjects)
    qr_ar_img_annot = annotate_incorrect_bubbles(
        qr_ar_image,
        result["qr"]["answers"],
        result["qr"]["results"],
        QUESTIONS_QR,
    )
    qr_ar_img_annot = annotate_incorrect_bubbles(
        qr_ar_img_annot,
        result["ar"]["answers"],
        result["ar"]["results"],
        QUESTIONS_AR,
    )
    qr_ar_img_annot = write_section_score(
        qr_ar_img_annot,
        "QR/AR",
        result["qr"]["correct"] + result["ar"]["correct"],
        result["qr"]["total"] + result["ar"]["total"],
    )

    result_payload = {
        "student_name": student_name,
        "writing_score": writing_score,
        **result,
    }

    zip_buffer = build_output_zip(
        student_name,
        reading_img_annot,
        qr_ar_img_annot,
        result_payload,
    )

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{student_name}_annotated_output.zip"'
            )
        },
    )
