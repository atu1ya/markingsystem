from typing import Any, Dict

from .cv import detect_answers
from .marking_logic import compute_strengths_weaknesses, mark_section
from .pdf_tools import pdf_to_images
from .questions_qr_ar import QUESTIONS_AR, QUESTIONS_QR
from .questions_reading import QUESTIONS_READING


def mark_single_student_papers(
    reading_pdf_bytes: bytes,
    qr_ar_pdf_bytes: bytes,
    answer_keys: Dict[str, Any],
    concept_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Core engine for marking a single student's papers."""

    reading_images = pdf_to_images(reading_pdf_bytes)
    qr_ar_images = pdf_to_images(qr_ar_pdf_bytes)

    if not reading_images or not qr_ar_images:
        raise ValueError("PDF conversion returned no pages; ensure PDFs contain at least one page.")

    reading_image = reading_images[0]
    qr_ar_image = qr_ar_images[0]

    reading_answers = detect_answers(reading_image, QUESTIONS_READING)
    qr_answers = detect_answers(qr_ar_image, QUESTIONS_QR)
    ar_answers = detect_answers(qr_ar_image, QUESTIONS_AR)

    reading_key = answer_keys.get("reading", {})
    qr_ar_key = answer_keys.get("qr_ar", {})

    qr_key = qr_ar_key.get("qr") or {}
    ar_key = qr_ar_key.get("ar") or {}

    reading_results, reading_correct, reading_total = mark_section(reading_answers, reading_key)
    qr_results, qr_correct, qr_total = mark_section(qr_answers, qr_key)
    ar_results, ar_correct, ar_total = mark_section(ar_answers, ar_key)

    per_question_correct_by_subject = {
        "Reading": reading_results,
        "QR": qr_results,
        "AR": ar_results,
    }

    strengths_weaknesses = compute_strengths_weaknesses(per_question_correct_by_subject, concept_map)

    return {
        "reading": {
            "answers": reading_answers,
            "results": reading_results,
            "correct": reading_correct,
            "total": reading_total,
        },
        "qr": {
            "answers": qr_answers,
            "results": qr_results,
            "correct": qr_correct,
            "total": qr_total,
        },
        "ar": {
            "answers": ar_answers,
            "results": ar_results,
            "correct": ar_correct,
            "total": ar_total,
        },
        "strengths_weaknesses": strengths_weaknesses,
    }
