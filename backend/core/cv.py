from typing import Dict, List

import numpy as np
from PIL import Image

from .questions_reading import QuestionROI

LETTERS = ["A", "B", "C", "D", "E"]


def detect_answers(image: Image.Image, questions: List[QuestionROI]) -> Dict[str, str]:
    """Return a dict mapping question id (as string) to chosen letter A-E."""
    gray = image.convert("L")
    arr = np.array(gray)

    results: Dict[str, str] = {}

    for question in questions:
        darkest_idx = None
        darkest_val = None

        for idx, (x1, y1, x2, y2) in enumerate(question.options):
            if x1 == x2 == y1 == y2 == 0:
                continue

            crop = arr[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            mean_val = float(crop.mean())

            if darkest_val is None or mean_val < darkest_val:
                darkest_val = mean_val
                darkest_idx = idx

        if darkest_idx is not None:
            results[str(question.id)] = LETTERS[darkest_idx]

    return results
