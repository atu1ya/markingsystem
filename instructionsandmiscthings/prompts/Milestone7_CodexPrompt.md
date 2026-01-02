# Milestone 7 — Full Codex Prompt (Backend Batch Marking Endpoint)

Use this Markdown file as a **single prompt** for VS Code Copilot / Codex at the repo root once Milestone 6 is complete.

Copy everything from **"Codex Prompt for Milestone 7"** into Copilot Chat.

---

# Codex Prompt for Milestone 7: Batch Marking Engine + ZIP Output (No UI Yet)

You are an AI coding agent working at the root of this repo.

Milestones completed so far:

- Milestone 0 — Project skeleton
- Milestone 1 — Auth + session store
- Milestone 2 — Config JSON upload + validation
- Milestone 3 — Frontend login + config integration
- Milestone 4 — Mark page UI + single student upload plumbing
- Milestone 5 — Core marking engine (pdf2image + CV + marking + strengths/weaknesses)
- Milestone 6 — `/mark/single-student` now runs engine + annotated output ZIP

Your job in **Milestone 7** is to add **batch marking support on the backend**:

- Accept multiple students in one upload request
- Reuse the existing marking engine
- Produce a single combined ZIP output
- NO frontend changes yet (backend only milestone)

---

## Goals of this milestone

Create a new endpoint:

```
POST /mark/batch
```

Which:

1) Accepts:
- a ZIP file of all student MCQ PDFs
- a JSON manifest describing which file belongs to which student

2) For each student:
- runs the same engine used for `/mark/single-student`
- generates the annotated reading + QR/AR PDFs
- generates JSON marking data

3) Returns:
- one combined ZIP containing **per-student folders** with outputs

This prepares the backend for a future batch UI milestone.

---

## Request contract

Endpoint:

```
POST /mark/batch
```

Request type:

`multipart/form-data`

Fields:

| Field | Type | Description |
|------|------|-------------|
| `files_zip` | UploadFile | ZIP containing all uploaded PDFs |
| `manifest` | string (JSON) | JSON array that maps files to students |

Example manifest:

```json
[
  {
    "student_name": "Alice Smith",
    "writing_score": "23",
    "reading_pdf": "alice_reading.pdf",
    "qr_ar_pdf": "alice_qr_ar.pdf"
  },
  {
    "student_name": "Bob Chan",
    "writing_score": "18",
    "reading_pdf": "bob_reading.pdf",
    "qr_ar_pdf": "bob_qr_ar.pdf"
  }
]
```

The uploaded ZIP must contain the referenced filenames.

---

## 1. Create `backend/core/batch.py`

Create a new orchestrator module that:

- loads PDFs from uploaded ZIP
- loops through manifest entries
- calls `mark_single_student_papers`
- annotates sheets
- exports annotated PDFs + JSON
- writes them into a student folder in an output ZIP

Implementation spec:

```python
from typing import Any, Dict, List
from io import BytesIO
import json
import zipfile

from .engine import mark_single_student_papers
from .pdf_tools import pdf_to_images
from .questions_reading import QUESTIONS_READING
from .questions_qr_ar import QUESTIONS_QR, QUESTIONS_AR
from .annotate import annotate_incorrect_bubbles, write_section_score
from .export import image_to_pdf_bytes  # or import via pdf_tools / export as implemented


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
            student_name = entry["student_name"]
            writing_score = entry["writing_score"]
            reading_name = entry["reading_pdf"]
            qr_ar_name = entry["qr_ar_pdf"]

            reading_bytes = input_zip.read(reading_name)
            qr_ar_bytes = input_zip.read(qr_ar_name)

            # Run existing marking engine
            result = mark_single_student_papers(
                reading_bytes,
                qr_ar_bytes,
                answer_keys,
                concept_map,
            )

            # Convert PDFs back to images for annotation
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
            out_zip.writestr(
                base + f"{student_name}_marking_data.json",
                json.dumps(result, indent=2),
            )

    out_buf.seek(0)
    return out_buf
```

This function mirrors the single student flow but across many students.

---

## 2. Add new endpoint in `backend/routes/marking.py`

Import dependencies:

```python
from fastapi import UploadFile, File, Form, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
import json

from core.session_store import get_session
from core.batch import process_batch_zip
```

Add endpoint:

```python
@router.post("/batch")
async def mark_batch(
    files_zip: UploadFile = File(...),
    manifest: str = Form(...),
    session: dict = Depends(get_session),
):
    if files_zip.content_type not in ("application/zip", "application/x-zip-compressed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="files_zip must be a ZIP")

    try:
        manifest_data = json.loads(manifest)
        if not isinstance(manifest_data, list):
            raise ValueError("manifest must be a JSON list")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid manifest JSON")

    zip_bytes = await files_zip.read()

    answer_keys = session.get("answer_keys", {})
    concept_map = session.get("concept_map", {})

    out_buf = process_batch_zip(
        zip_bytes,
        manifest_data,
        answer_keys,
        concept_map,
    )

    return StreamingResponse(
        out_buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="batch_marked_output.zip"'
        },
    )
```

This endpoint:

- authenticates using session
- uses the same answer keys and concept map already loaded by the admin
- does not change UI behavior yet

---

## 3. Output structure of returned ZIP

After batch processing, the returned ZIP should look like:

```
Alice Smith/
  Alice Smith_reading_annotated.pdf
  Alice Smith_qr_ar_annotated.pdf
  Alice Smith_marking_data.json

Bob Chan/
  Bob Chan_reading_annotated.pdf
  Bob Chan_qr_ar_annotated.pdf
  Bob Chan_marking_data.json
```

Each folder contains:

- annotated reading sheet
- annotated QR/AR sheet
- JSON breakdown for later student report generation

---

## 4. What should be true after Milestone 7

After this milestone:

- Backend now supports **multi-student marking**
- `/mark/batch` accepts:
  - ZIP of PDFs
  - JSON manifest
- Reuses:
  - marking engine
  - annotation logic
  - export pipeline
- Returns:
  - one combined output ZIP

Frontend still only supports single student workflow. Batch UI comes in a later milestone.

---

## Final instructions

Modify ONLY:

- `backend/core/batch.py`
- `backend/routes/marking.py` (to add `/batch`)

Do NOT modify:

- `/mark/single-student`
- frontend code
- auth + session logic
- engine function signatures

Backend must still run with:

```
uvicorn main:app --reload --port 8000
```

Frontend must still run with:

```
npm run dev
```

