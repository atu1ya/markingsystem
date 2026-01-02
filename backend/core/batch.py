import json
import zipfile
from io import BytesIO
from typing import Any, Dict, List

from .annotate import annotate_incorrect_bubbles, write_section_score
from .engine import mark_single_student_papers
from .pdf_tools import image_to_pdf_bytes, pdf_to_images
from .questions_qr_ar import QUESTIONS_AR, QUESTIONS_QR
from .questions_reading import QUESTIONS_READING


def process_batch_zip(
    zip_bytes: bytes,
    manifest: List[Dict[str, Any]],
    answer_keys: Dict[str, Any],
    concept_map: Dict[str, Any],
) -> BytesIO:
    input_zip = zipfile.ZipFile(BytesIO(zip_bytes), "r")
    out_buf = BytesIO()

    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for entry in manifest:
            student_name = entry.get("student_name")
            writing_score = entry.get("writing_score")
            reading_name = entry.get("reading_pdf")
            qr_ar_name = entry.get("qr_ar_pdf")

            if not all([student_name, reading_name, qr_ar_name]):
                raise ValueError("Manifest entries must include student_name, reading_pdf, qr_ar_pdf")

            reading_bytes = input_zip.read(reading_name)
            qr_ar_bytes = input_zip.read(qr_ar_name)

            result = mark_single_student_papers(
                reading_bytes,
                qr_ar_bytes,
                answer_keys,
                concept_map,
            )

            reading_img = pdf_to_images(reading_bytes)[0]
            qr_ar_img = pdf_to_images(qr_ar_bytes)[0]

            reading_img_annot = annotate_incorrect_bubbles(
                reading_img,
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

            qr_ar_img_annot = annotate_incorrect_bubbles(
                qr_ar_img,
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

            base = f"{student_name}/"

            out_zip.writestr(
                base + f"{student_name}_reading_annotated.pdf",
                image_to_pdf_bytes(reading_img_annot),
            )
            out_zip.writestr(
                base + f"{student_name}_qr_ar_annotated.pdf",
                image_to_pdf_bytes(qr_ar_img_annot),
            )
            payload = {
                "student_name": student_name,
                "writing_score": writing_score,
                **result,
            }
            out_zip.writestr(
                base + f"{student_name}_marking_data.json",
                json.dumps(payload, indent=2),
            )

    out_buf.seek(0)
    return out_buf
