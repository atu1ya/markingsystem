from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

# Fallback to default font if system font missing
try:
    FONT = ImageFont.truetype("arial.ttf", 22)
except Exception:  # pragma: no cover - font availability varies by system
    FONT = ImageFont.load_default()


def annotate_incorrect_bubbles(
    image: Image.Image,
    answers: Dict[str, str],
    results: Dict[str, bool],
    rois: List,
) -> Image.Image:
    """Draw a red rectangle around bubbles that were answered incorrectly."""

    annotated = image.convert("RGB")
    draw = ImageDraw.Draw(annotated)

    for roi in rois:
        qid = str(getattr(roi, "id", None))
        if not qid or qid not in answers:
            continue

        if results.get(qid, True):
            # correct — no highlight
            continue

        idx = ord(answers[qid]) - ord("A")
        try:
            x1, y1, x2, y2 = roi.options[idx]
        except Exception:
            continue

        draw.rectangle((x1, y1, x2, y2), outline="red", width=4)

    return annotated


def write_section_score(
    image: Image.Image,
    label: str,
    correct: int,
    total: int,
    position: Tuple[int, int] = (50, 50),
) -> Image.Image:
    """Write score summary onto page."""

    annotated = image.convert("RGB")
    draw = ImageDraw.Draw(annotated)

    text = f"{label}: {correct}/{total}"
    draw.text(position, text, fill="black", font=FONT)

    return annotated
