"""Milestone 1 computer vision script for automated bubble sheet marking."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np
import fitz  # PyMuPDF

from questions_example import questions

TEMPLATE_IMAGE_PATH = "template.pdf"
STUDENT_IMAGE_PATH = "student.pdf"
RESULT_PATH = Path(__file__).parent / "result.txt"
MIN_FILL_DELTA = 12.0  # Minimum mean-intensity separation to treat a bubble as filled

ROI = Tuple[int, int, int, int]


def load_color_image(path: str) -> np.ndarray:
    print(f"Loading raster image: {path}")
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not load image at '{path}'.")
    return image


def load_pdf_first_page(path: str, dpi: int = 300) -> np.ndarray:
    print(f"Loading PDF (first page): {path}")
    if not Path(path).exists():
        raise FileNotFoundError(f"PDF not found at '{path}'.")

    with fitz.open(path) as doc:
        if doc.page_count == 0:
            raise ValueError(f"PDF '{path}' contains no pages.")
        page = doc.load_page(0)
        matrix = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=matrix)

    buffer = np.frombuffer(pix.samples, dtype=np.uint8)
    image = buffer.reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image


def load_scan(path: str) -> np.ndarray:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return load_pdf_first_page(path)
    return load_color_image(path)


def preprocess_grayscale(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return blur, gray


def threshold_image(blur: np.ndarray) -> np.ndarray:
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh


def align_student_to_template(
    template_gray: np.ndarray, student_gray: np.ndarray, student_color: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    print("Aligning student scan to template ...")
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    criteria = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        80,
        1e-6,
    )
    try:
        cv2.findTransformECC(
            template_gray,
            student_gray,
            warp_matrix,
            cv2.MOTION_AFFINE,
            criteria,
            None,
            5,
        )
        height, width = template_gray.shape
        aligned_color = cv2.warpAffine(
            student_color,
            warp_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
        )
        aligned_gray = cv2.cvtColor(aligned_color, cv2.COLOR_BGR2GRAY)
        print("Alignment successful.")
    except cv2.error as exc:
        print(f"Alignment warning: {exc}. Proceeding without alignment.")
        aligned_color = student_color
        aligned_gray = student_gray
    return aligned_color, aligned_gray


def clamp_roi(roi: ROI, width: int, height: int) -> ROI:
    x1, y1, x2, y2 = roi
    x1 = max(0, min(width - 1, x1))
    x2 = max(0, min(width, x2))
    y1 = max(0, min(height - 1, y1))
    y2 = max(0, min(height, y2))
    if x2 <= x1 or y2 <= y1:
        raise ValueError("ROI is invalid after clamping; please update your coordinates.")
    return x1, y1, x2, y2


def mean_intensity(image: np.ndarray, roi: ROI) -> float:
    height, width = image.shape[:2]
    x1, y1, x2, y2 = clamp_roi(roi, width, height)
    crop = image[y1:y2, x1:x2]
    return float(np.mean(crop))


def pick_darkest_option(image: np.ndarray, options: Sequence[ROI]) -> Optional[int]:
    best_idx: Optional[int] = None
    best_value: Optional[float] = None
    second_value: Optional[float] = None

    for idx, roi in enumerate(options):
        value = mean_intensity(image, roi)
        if best_value is None or value < best_value:
            second_value = best_value
            best_value = value
            best_idx = idx
        elif second_value is None or value < second_value:
            second_value = value

    if best_value is None:
        return None

    if second_value is None:
        return best_idx

    if second_value - best_value < MIN_FILL_DELTA:
        return None

    return best_idx


def option_label(index: Optional[int]) -> str:
    if index is None:
        return "blank"
    return chr(ord("A") + index)


def evaluate_answers(image: np.ndarray, question_definitions: List[dict]) -> List[Optional[int]]:
    selections: List[Optional[int]] = []
    for question in question_definitions:
        idx = pick_darkest_option(image, question["options"])
        selections.append(idx)
    return selections


def format_question_result(qid: int, correct_idx: Optional[int], student_idx: Optional[int]) -> str:
    correct_label = option_label(correct_idx).upper()
    student_label = option_label(student_idx).upper()

    if correct_idx is not None and student_idx is not None and correct_idx == student_idx:
        return f"Q{qid}: CORRECT"
    return f"Q{qid}: INCORRECT (correct {correct_label}, student {student_label})"


def main() -> None:
    try:
        template_color = load_scan(TEMPLATE_IMAGE_PATH)
        student_color = load_scan(STUDENT_IMAGE_PATH)
    except FileNotFoundError as missing:
        print(missing)
        sys.exit(1)

    template_blur, template_gray = preprocess_grayscale(template_color)
    template_thresh = threshold_image(template_blur)

    student_blur, student_gray = preprocess_grayscale(student_color)
    _ = threshold_image(student_blur)

    aligned_color, aligned_gray = align_student_to_template(template_gray, student_gray, student_color)
    aligned_blur = cv2.GaussianBlur(aligned_gray, (5, 5), 0)

    print("Determining correct answers from template ...")
    correct_indices = evaluate_answers(template_blur, questions)
    print("Determining student selections ...")
    student_indices = evaluate_answers(aligned_blur, questions)

    results_lines: List[str] = []
    correct_count = 0
    blank_count = 0

    for question, correct_idx, student_idx in zip(questions, correct_indices, student_indices):
        qid = question["id"]
        line = format_question_result(qid, correct_idx, student_idx)
        results_lines.append(line)
        if correct_idx is not None and student_idx == correct_idx:
            correct_count += 1
        elif student_idx is None:
            blank_count += 1

    total_questions = len(questions)
    incorrect_count = total_questions - correct_count

    summary_lines = [
        "",
        "Summary:",
        f"Total questions: {total_questions}",
        f"Correct: {correct_count}",
        f"Incorrect: {incorrect_count}",
        f"Blanks: {blank_count}",
    ]

    output_text = "\n".join(results_lines + summary_lines)
    RESULT_PATH.write_text(output_text)
    print(f"Results written to {RESULT_PATH}")


if __name__ == "__main__":
    main()
