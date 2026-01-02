import io
import zipfile
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
    _ = session  # ensures dependency executes even though session not used yet
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

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{student_name}_reading_original.pdf", reading_bytes)
        zip_file.writestr(f"{student_name}_qr_ar_original.pdf", qr_ar_bytes)

        meta = f"Student: {student_name}\nWriting score: {writing_score}\n"
        zip_file.writestr("meta.txt", meta)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{student_name}_marked_stub.zip"'
            )
        },
    )
