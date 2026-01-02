# Milestone 5 - Full Codex Prompt (PDF to Image + Bubble Detection + Marking Logic)

Use this Markdown file as a single prompt for VS Code Copilot or Codex at the repo root once Milestone 4 is complete.

Copy everything from "Codex Prompt for Milestone 5" into Copilot Chat.

---

# Codex Prompt for Milestone 5: Core CV Pipeline and Marking Logic

You are an AI coding agent working at the root of this repo.

Milestones completed so far:

- Milestone 0 - Backend and frontend skeleton
- Milestone 1 - Authentication and session store
- Milestone 2 - Admin config endpoints
- Milestone 3 - Login and Config page wired to backend
- Milestone 4 - Marking page UI plus backend PDF upload stub that returns a ZIP

Your job in Milestone 5 is to implement the core backend marking engine, without yet wiring it fully into the existing `/mark/single-student` endpoint.

In this milestone you will:

- Convert PDFs to images using `pdf2image` and Pillow
- Implement ROI based bubble detection to determine chosen options
- Implement marking logic for reading, QR, and AR using the JSON answer keys stored in the session
- Implement strengths and weaknesses calculation based on the concept map and the 51 percent rule
- Keep the existing `/mark/single-student` endpoint returning the stub ZIP for now

Frontend is not touched in this milestone. Endpoint wiring and annotated output happens in a later milestone.

---

## Rules for this milestone

You must:

- Work only in:
  - `backend/core/` (new and existing files)
  - `backend/routes/marking.py` (only if you add helper calls, but keep the stub response)
- Preserve:
  - Existing behavior of `/mark/single-student` returning a stub ZIP
  - Existing auth and session store
  - Existing config endpoints

You must NOT:

- Change how JSON configs are stored in the session
- Change any frontend code
- Change how `/auth/login` or `/config/*` behave

This milestone prepares a clean, testable library layer for marking that can be called later by the route.

---

## 1. Create `backend/core/pdf_tools.py`

Create a new file:

`backend/core/pdf_tools.py`

Implement:

```python
from typing import List
from io import BytesIO

from pdf2image import convert_from_bytes
from PIL import Image


def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
    """Convert a single or multi page PDF (as bytes) into a list of Pillow images."""
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    return images


def image_to_pdf_bytes(image: Image.Image) -> bytes:
    """Convert a single Pillow image into a single page PDF as bytes."""
    buf = BytesIO()
    image.save(buf, format="PDF")
    buf.seek(0)
    return buf.read()
```

For now:

- Assume single page PDFs for the ASET sheets
- Use `pdf_to_images(pdf_bytes)[0]` when you want the first page

---

## 2. Create ROI configuration files

Create:

- `backend/core/questions_reading.py`
- `backend/core/questions_qr_ar.py`

These files will hold the ROI rectangles for each bubble. Use placeholder values that can be edited manually later.

### 2.1 Reading sheet

In `questions_reading.py`:

```python
from typing import List, Tuple

Rect = Tuple[int, int, int, int]

class QuestionROI:
    def __init__(self, qid: int, options: List[Rect]):
        self.id = qid
        self.options = options  # [A, B, C, D, E]


# Placeholder structure for 35 questions.
# Replace the coordinates with real values for the final system.
QUESTIONS_READING: List[QuestionROI] = [
    QuestionROI(1, [(0, 0, 0, 0)] * 5),
    QuestionROI(2, [(0, 0, 0, 0)] * 5),
    # Fill out up to QuestionROI(35, ...) as needed
]
```

You do not need to fill all coordinates now. The important part is that the data structure is defined and used consistently.

### 2.2 QR and AR sheet

In `questions_qr_ar.py`:

```python
from typing import List, Tuple

Rect = Tuple[int, int, int, int]

class QuestionROI:
    def __init__(self, qid: int, options: List[Rect]):
        self.id = qid
        self.options = options  # [A, B, C, D, E]


QUESTIONS_QR: List[QuestionROI] = [
    QuestionROI(1, [(0, 0, 0, 0)] * 5),
    # add more questions as needed
]

QUESTIONS_AR: List[QuestionROI] = [
    QuestionROI(1, [(0, 0, 0, 0)] * 5),
    # add more questions as needed
]
```

Again, coordinates can be placeholder values for now.

---

## 3. Implement core bubble detection in `backend/core/cv.py`

Create a new file:

`backend/core/cv.py`

Implement a function that:

- Takes a Pillow image and a list of QuestionROI
- For each ROI rectangle:
  - crops the region
  - converts to grayscale
  - computes mean pixel intensity
- For each question:
  - chooses the darkest bubble (lowest mean value)
  - maps index 0..4 to option letters "A" to "E"

Implementation:

```python
from typing import Dict, List
from PIL import Image
import numpy as np

from .questions_reading import QuestionROI

LETTERS = ["A", "B", "C", "D", "E"]


def detect_answers(image: Image.Image, questions: List[QuestionROI]) -> Dict[str, str]:
    """Return a dict mapping question id (as string) to chosen letter A-E."""
    gray = image.convert("L")
    arr = np.array(gray)

    results: Dict[str, str] = {}

    for q in questions:
        darkest_idx = None
        darkest_val = None

        for idx, (x1, y1, x2, y2) in enumerate(q.options):
            if x1 == x2 == y1 == y2 == 0:
                continue

            crop = arr[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            mean_val = crop.mean()

            if darkest_val is None or mean_val < darkest_val:
                darkest_val = mean_val
                darkest_idx = idx

        if darkest_idx is not None:
            results[str(q.id)] = LETTERS[darkest_idx]

    return results
```

Later, you will call this with the appropriate ROI set:

- Reading: `QUESTIONS_READING`
- QR: `QUESTIONS_QR`
- AR: `QUESTIONS_AR`

---

## 4. Implement marking logic in `backend/core/marking_logic.py`

Create:

`backend/core/marking_logic.py`

This module should:

- Compare student answers vs answer keys
- Compute per question correctness
- Compute section totals
- Compute strengths and weaknesses using the concept map and 51 percent rule

Structure:

```python
from typing import Dict, List, Tuple

Letter = str  # "A" to "E"


def mark_section(student_answers: Dict[str, Letter], answer_key: Dict[str, Letter]) -> Tuple[Dict[str, bool], int, int]:
    """Return (per_question_correct, total_correct, total_questions)."""
    results: Dict[str, bool] = {}
    total_correct = 0
    total_questions = len(answer_key)

    for qid, correct_letter in answer_key.items():
        student_letter = student_answers.get(qid)
        is_correct = student_letter == correct_letter
        results[qid] = is_correct
        if is_correct:
            total_correct += 1

    return results, total_correct, total_questions
```

### 4.1 Strengths and weaknesses function

Concept map structure from Milestone 2:

`Dict[str, Dict[str, List[int]]]`

For each subject and concept:

- Count how many of its questions are correct
- Compute percentage correct
- If percentage is greater than or equal to 51 percent it is a strength ("done well")
- Otherwise it is a weakness ("needs improvement")

Implement:

```python
def compute_strengths_weaknesses(
    per_question_correct_by_subject: Dict[str, Dict[str, bool]],
    concept_map: Dict[str, Dict[str, List[int]]],
) -> Dict[str, Dict[str, List[str]]]:
    """Return { subject: { 'done_well': [concepts], 'needs_improvement': [concepts] } }"""
    result: Dict[str, Dict[str, List[str]]] = {}

    for subject, concepts in concept_map.items():
        subject_results = {
            "done_well": [],
            "needs_improvement": [],
        }

        question_correct = per_question_correct_by_subject.get(subject, {})

        for concept_name, question_numbers in concepts.items():
            if not question_numbers:
                continue

            correct_count = 0
            total = len(question_numbers)

            for qnum in question_numbers:
                qid = str(qnum)
                if question_correct.get(qid):
                    correct_count += 1

            percent_correct = 100.0 * correct_count / total

            if percent_correct >= 51.0:
                subject_results["done_well"].append(concept_name)
            else:
                subject_results["needs_improvement"].append(concept_name)

        result[subject] = subject_results

    return result
```

This will be used later when you have actual per question correctness for Reading, QR, and AR.

---

## 5. High level marking engine in `backend/core/engine.py`

Create:

`backend/core/engine.py`

This file will orchestrate marking a single student. For this milestone it does not change API responses but exposes a function the route can call later.

Skeleton:

```python
from typing import Dict, Any

from .pdf_tools import pdf_to_images
from .cv import detect_answers
from .questions_reading import QUESTIONS_READING
from .questions_qr_ar import QUESTIONS_QR, QUESTIONS_AR
from .marking_logic import mark_section, compute_strengths_weaknesses


def mark_single_student_papers(
    reading_pdf_bytes: bytes,
    qr_ar_pdf_bytes: bytes,
    answer_keys: Dict[str, Any],
    concept_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Core engine for marking a single student's papers.

    Steps:
    - convert PDFs to images
    - run bubble detection
    - compare to answer keys
    - compute section scores
    - compute strengths and weaknesses
    Returns a dict with enough info to later drive annotation and reporting.
    """

    reading_images = pdf_to_images(reading_pdf_bytes)
    qr_ar_images = pdf_to_images(qr_ar_pdf_bytes)

    reading_image = reading_images[0]
    qr_ar_image = qr_ar_images[0]

    reading_answers = detect_answers(reading_image, QUESTIONS_READING)
    qr_answers = detect_answers(qr_ar_image, QUESTIONS_QR)
    ar_answers = detect_answers(qr_ar_image, QUESTIONS_AR)

    reading_key = answer_keys.get("reading", {})
    qr_ar_key = answer_keys.get("qr_ar", {})

    qr_key = qr_ar_key.get("qr", qr_ar_key.get("qr"))
    ar_key = qr_ar_key.get("ar", qr_ar_key.get("ar"))

    reading_results, reading_correct, reading_total = mark_section(reading_answers, reading_key)
    qr_results, qr_correct, qr_total = mark_section(qr_answers, qr_key or {})
    ar_results, ar_correct, ar_total = mark_section(ar_answers, ar_key or {})

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
```

You may need to tweak how `answer_keys["qr_ar"]` is structured depending on your Milestone 2 implementation. The key idea is:

- `answer_keys["reading"]` is a dict of question string to letter
- `answer_keys["qr_ar"]["qr"]` and `["ar"]` are dicts of question string to letter

---

## 6. Do not change the response of `/mark/single-student` yet

In `backend/routes/marking.py` you may import `mark_single_student_papers` for testing, but the official HTTP response should remain the same stub ZIP that you implemented in Milestone 4.

You can, for example, add commented out code or temporary debug logs, but do not ship a different HTTP contract in this milestone.

---

## 7. What should be true after Milestone 5

After this milestone:

- `backend/core/pdf_tools.py` can convert PDF bytes to Pillow images
- `backend/core/questions_reading.py` and `backend/core/questions_qr_ar.py` define the ROI structures
- `backend/core/cv.py` can detect answers A to E based on ROI darkness
- `backend/core/marking_logic.py` can mark a section and compute strengths and weaknesses
- `backend/core/engine.py` can take PDF bytes, answer keys and concept map and return a full marking result for Reading, QR, and AR

The `/mark/single-student` HTTP endpoint still behaves as in Milestone 4 and returns a ZIP of the original PDFs plus meta.txt.

Frontend behavior is unchanged and continues to work.

---

## Final instructions

Modify ONLY:

- `backend/core/pdf_tools.py`
- `backend/core/questions_reading.py`
- `backend/core/questions_qr_ar.py`
- `backend/core/cv.py`
- `backend/core/marking_logic.py`
- `backend/core/engine.py`
- Optionally imports in `backend/routes/marking.py` (but not its response behavior)

Do NOT touch:

- Frontend
- Auth and session store
- Config endpoints
- External ZIP response of `/mark/single-student`

Backend must still run with:

```bash
uvicorn main:app --reload --port 8000
```

Frontend must still run with:

```bash
npm run dev
```

