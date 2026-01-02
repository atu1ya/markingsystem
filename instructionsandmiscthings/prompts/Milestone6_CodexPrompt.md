# Milestone 6 — Full Codex Prompt (Wire Engine Into Endpoint + Produce Annotated PDFs)

Use this Markdown file as a **single prompt** for VS Code Copilot / Codex at the repo root once Milestone 5 is complete.

Copy everything from **"Codex Prompt for Milestone 6"** into Copilot Chat.

---

# Codex Prompt for Milestone 6: Integrate Marking Engine + Annotated Output PDFs

You are an AI coding agent working at the root of this repo.

Milestones completed so far:

- Milestone 0 — Project skeleton
- Milestone 1 — Auth + session store
- Milestone 2 — Config JSON upload + validation
- Milestone 3 — Frontend login + config integration
- Milestone 4 — Mark page UI + upload → ZIP plumbing (stub)
- Milestone 5 — Core marking engine (pdf2image + CV + marking + strengths/weaknesses)

Your job in **Milestone 6** is to:

- integrate the marking engine into `/mark/single-student`
- replace the stub ZIP with a **real generated output package**
- annotate sheets with correct / incorrect markings
- embed section score summaries onto each page
- return a ZIP containing:
  - annotated Reading sheet PDF
  - annotated QR/AR sheet PDF
  - JSON file with marking breakdown (for later report generation)

Batch mode is **not yet implemented** — single student flow only.

---

## Rules For This Milestone

You must:

- keep endpoint path and input contract exactly the same
- add engine processing
- replace stub ZIP payload with real files

You may modify:

- `backend/routes/marking.py`

You must build new helpers in:

- `backend/core/annotate.py`
- `backend/core/export.py`

You must NOT:

- change frontend behavior
- change request format
- change auth/session behavior
- introduce a database

---

## 1. Create `backend/core/annotate.py`

This module is responsible for **drawing feedback** on student sheets.

Create file:

```
backend/core/annotate.py
```

Implement functions:

- overlay correct answers summary
- mark wrong bubbles in **red**
- write section score text in a fixed area

Implementation spec:

```python
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple

# Fallback to default font if system font missing
try:
    FONT = ImageFont.truetype("arial.ttf", 22)
except:
    FONT = ImageFont.load_default()


def annotate_incorrect_bubbles(
    image: Image.Image,
    answers: Dict[str, str],
    results: Dict[str, bool],
    rois: List
) -> Image.Image:
    """Draw a red rectangle around bubbles that were answered incorrectly."""

    annotated = image.convert("RGB")
    draw = ImageDraw.Draw(annotated)

    for q in rois:
        qid = str(q.id)
        if qid not in answers:
            continue

        if results.get(qid, True):
            # correct — no highlight
            continue

        # incorrect → mark chosen bubble region
        idx = ord(answers[qid]) - ord("A")
        try:
            (x1, y1, x2, y2) = q.options[idx]
        except Exception:
            continue

        draw.rectangle((x1, y1, x2, y2), outline="red", width=4)

    return annotated


def write_section_score(
    image: Image.Image,
    label: str,
    correct: int,
    total: int,
    position: Tuple[int,int] = (50, 50)
) -> Image.Image:
    """Write score summary onto page."""

    annotated = image.convert("RGB")
    draw = ImageDraw.Draw(annotated)

    text = f"{label}: {correct}/{total}"
    draw.text(position, text, fill="black", font=FONT)

    return annotated
```

This prepares clean reusable primitives.

---

## 2. Create `backend/core/export.py`

This module converts annotated Pillow images → **single‑page PDFs** and builds a ZIP.

Create:

```
backend/core/export.py
```

Implement:

```python
from io import BytesIO
from typing import Dict
import zipfile
from PIL import Image

from .pdf_tools import image_to_pdf_bytes


def build_output_zip(
    student_name: str,
    reading_img: Image.Image,
    qr_ar_img: Image.Image,
    result_payload: Dict
) -> BytesIO:
    """Package annotated PDFs + JSON summary into a ZIP."""

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Annotated PDFs
        zf.writestr(
            f"{student_name}_reading_annotated.pdf",
            image_to_pdf_bytes(reading_img)
        )
        zf.writestr(
            f"{student_name}_qr_ar_annotated.pdf",
            image_to_pdf_bytes(qr_ar_img)
        )

        # Raw result payload for later student report generation
        import json
        zf.writestr(
            f"{student_name}_marking_data.json",
            json.dumps(result_payload, indent=2)
        )

    zip_buffer.seek(0)
    return zip_buffer
```

---

## 3. Wire Engine Into `/mark/single-student`

Modify:

```
backend/routes/marking.py
```

Replace stub ZIP logic with:

1) fetch files  
2) fetch session configs  
3) call engine  
4) annotate  
5) package ZIP  
6) stream response

Implementation spec outline:

```python
from fastapi.responses import StreamingResponse

from core.engine import mark_single_student_papers
from core.questions_reading import QUESTIONS_READING
from core.questions_qr_ar import QUESTIONS_QR, QUESTIONS_AR
from core.annotate import annotate_incorrect_bubbles, write_section_score
from core.export import build_output_zip
```

Inside endpoint:

```python
result = mark_single_student_papers(
    reading_bytes,
    qr_ar_bytes,
    session["answer_keys"],
    session.get("concept_map", {}),
)

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
    result["reading"]["total"]
)

qr_ar_img_annot = annotate_incorrect_bubbles(
    qr_ar_image,
    result["qr"]["answers"],
    result["qr"]["results"],
    QUESTIONS_QR + QUESTIONS_AR,
)
qr_ar_img_annot = write_section_score(
    qr_ar_img_annot,
    "QR/AR",
    result["qr"]["correct"] + result["ar"]["correct"],
    result["qr"]["total"] + result["ar"]["total"]
)
```

Then:

```python
zip_buf = build_output_zip(
    student_name,
    reading_img_annot,
    qr_ar_img_annot,
    result
)

return StreamingResponse(
    zip_buf,
    media_type="application/zip",
    headers={
        "Content-Disposition": f'attachment; filename="{student_name}_annotated_output.zip"'
    }
)
```

---

## 4. Acceptance Criteria

After Milestone 6:

Frontend workflow does **not change**.

But result download now contains:

1) Annotated Reading sheet PDF  
2) Annotated QR/AR sheet PDF  
3) JSON marking payload with:

- answers detected
- correctness per question
- section totals
- strengths/weaknesses

This proves:

- engine works end‑to‑end
- annotation works correctly
- backend generates usable marking artefacts
- UI + plumbing remain stable

---

## 5. Out of Scope (Later Milestones)

Do NOT implement yet:

- redrawing correct bubble choice if unanswered
- scan quality warnings
- batch processing
- student report PDF
- performance optimisation
- ROI mapping refinement UX
- export templates

Those will come in Milestones 7+.

---

## Final Instructions

Modify ONLY:

- `backend/routes/marking.py`
- `backend/core/annotate.py`
- `backend/core/export.py`

Use existing engine + ROI configs created in Milestone 5.

Do NOT modify:

- frontend code
- auth/session logic
- config endpoints
- engine function signature
- upload API shape

Backend must still run with:

```
uvicorn main:app --reload --port 8000
```

Frontend must still run with:

```
npm run dev
```

Return to user only the ZIP described above.

