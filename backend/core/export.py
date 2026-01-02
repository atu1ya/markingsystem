import json
import zipfile
from io import BytesIO
from typing import Dict

from PIL import Image

from .pdf_tools import image_to_pdf_bytes


def build_output_zip(
    student_name: str,
    reading_img: Image.Image,
    qr_ar_img: Image.Image,
    result_payload: Dict,
) -> BytesIO:
    """Package annotated PDFs + JSON summary into a ZIP."""

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Annotated PDFs
        zf.writestr(
            f"{student_name}_reading_annotated.pdf",
            image_to_pdf_bytes(reading_img),
        )
        zf.writestr(
            f"{student_name}_qr_ar_annotated.pdf",
            image_to_pdf_bytes(qr_ar_img),
        )

        # Raw result payload for later student report generation
        zf.writestr(
            f"{student_name}_marking_data.json",
            json.dumps(result_payload, indent=2),
        )

    zip_buffer.seek(0)
    return zip_buffer
