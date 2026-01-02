# Milestone 4 – Full Codex Prompt (Marking Page UI + File Upload Plumbing)

---

# Codex Prompt for Milestone 4: Marking Page UI + Backend PDF Upload Endpoint

You are an AI coding agent working at the root of this repo.

Milestones completed so far:

- Milestone 0 — Backend + frontend skeleton
- Milestone 1 — Authentication + session store
- Milestone 2 — Admin config endpoints
- Milestone 3 — Login + Config page wired to backend

Your job in **Milestone 4** is to implement the full end to end file upload pipeline for *single student marking*:

- Build the real `/mark` page UI
- Allow staff to:
  - enter student name
  - enter writing score
  - upload the Reading PDF
  - upload the QR/AR PDF
- Send data to backend as multipart form data
- Backend:
  - validates files
  - accepts uploads
  - returns a ZIP file
- Frontend:
  - downloads the ZIP to the user’s computer

This is a **plumbing milestone** — no computer vision or marking logic yet.
Later milestones will replace the stub processing with real marking.

---

## Rules for this milestone

You must:

- Work only in:
  - `backend/routes/`
  - `backend/main.py`
  - `frontend/src/pages/MarkPage.jsx`
- Preserve:
  - existing auth logic
  - session store logic
  - config endpoints
  - login + config pages

You must NOT:

- modify how sessions work
- modify JSON config behavior
- touch PDFs, misc folders or deployment files

This milestone only establishes upload + download flow.

---

## 1. BACKEND — Create `routes/marking.py`

Create a new file:

```
backend/routes/marking.py
```

Contents should:

- define a router:

```python
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Dict
from core.session_store import get_session
import io
import zipfile

router = APIRouter(prefix="/mark", tags=["mark"])
```

---

## 2. Implement endpoint: POST `/mark/single-student`

This endpoint:

- requires a valid session (`get_session`)
- accepts uploaded PDFs
- validates MIME type
- returns a ZIP file containing:
  - original reading sheet
  - original QR/AR sheet
  - text meta file

Stub behavior only — marking logic will be added in a later milestone.

Implementation spec:

```python
@router.post("/single-student")
async def mark_single_student(
    student_name: str = Form(...),
    writing_score: str = Form(...),
    reading_pdf: UploadFile = File(...),
    qr_ar_pdf: UploadFile = File(...),
    session: Dict = Depends(get_session),
):
    if reading_pdf.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reading_pdf must be a PDF")

    if qr_ar_pdf.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="qr_ar_pdf must be a PDF")

    reading_bytes = await reading_pdf.read()
    qr_ar_bytes = await qr_ar_pdf.read()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{student_name}_reading_original.pdf", reading_bytes)
        zip_file.writestr(f"{student_name}_qr_ar_original.pdf", qr_ar_bytes)

        meta = f"Student: {student_name}\nWriting score: {writing_score}\n"
        zip_file.writestr("meta.txt", meta)

    zip_buffer.seek(0)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{student_name}_marked_stub.zip"'
        },
    )
```

This confirms upload + binary download flow works before introducing marking logic.

---

## 3. Register router in `backend/main.py`

Open `backend/main.py`.

Add import:

```python
from routes.marking import router as marking_router
```

(or `from backend.routes.marking import router as marking_router` depending on path style)

Include router:

```python
app.include_router(marking_router)
```

Do not change `/health`, `auth`, or `config` routing.

---

## 4. FRONTEND — Implement real `/mark` page

Open:

```
frontend/src/pages/MarkPage.jsx
```

Replace placeholder with functional form:

```jsx
import { useState } from "react";

export default function MarkPage() {
  const sessionId = localStorage.getItem("sessionId");

  const [studentName, setStudentName] = useState("");
  const [writingScore, setWritingScore] = useState("");
  const [readingFile, setReadingFile] = useState(null);
  const [qrArFile, setQrArFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("");

    if (!sessionId) {
      setStatus("You must log in first.");
      return;
    }

    if (!studentName || !writingScore || !readingFile || !qrArFile) {
      setStatus("Please fill in all fields and upload both PDFs.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("student_name", studentName);
      formData.append("writing_score", writingScore);
      formData.append("reading_pdf", readingFile);
      formData.append("qr_ar_pdf", qrArFile);

      const res = await fetch("http://localhost:8000/mark/single-student", {
        method: "POST",
        headers: {
          "X-Session-ID": sessionId,
        },
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `${studentName}_marked_stub.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);

      setStatus("Download started.");
    } catch (err) {
      console.error(err);
      setStatus("Upload or download failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Mark ASET Sheet</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Student Name: </label>
          <input value={studentName} onChange={e => setStudentName(e.target.value)} />
        </div>

        <div>
          <label>Writing Score: </label>
          <input value={writingScore} onChange={e => setWritingScore(e.target.value)} />
        </div>

        <div>
          <label>Reading MCQ PDF: </label>
          <input type="file" accept="application/pdf" onChange={e => setReadingFile(e.target.files[0] || null)} />
        </div>

        <div>
          <label>QR/AR MCQ PDF: </label>
          <input type="file" accept="application/pdf" onChange={e => setQrArFile(e.target.files[0] || null)} />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Generate ZIP (stub)"}
        </button>
      </form>

      {status && <p>{status}</p>}
    </div>
  );
}
```

This verifies:

- FormData upload works
- Auth headers work
- Backend receives PDFs
- ZIP blob downloads successfully

---

## 5. What should work after Milestone 4

When backend + frontend are running:

1) Staff logs in
2) Loads config JSONs
3) Goes to `/mark`
4) Enters:

- student name
- writing score

5) Uploads:

- Reading PDF
- QR/AR PDF

6) Clicks submit

Result:

- Backend receives files
- ZIP stream is returned
- Browser downloads:

```
<student_name>_marked_stub.zip
```

ZIP contains:

- original reading sheet
- original qr/ar sheet
- meta.txt with student info

---

## 6. Future milestones will replace stub logic with:

- pdf2image conversion
- ROI mapping and bubble detection
- answer marking
- strength + weakness logic
- annotated sheets
- generated PDF report
- batch processing

The upload/download API contract should remain stable.

---

## Final instructions

Modify ONLY:

- backend/routes/marking.py (new file)
- backend/main.py (include router)
- frontend/src/pages/MarkPage.jsx

Do **not** change:

- auth
- session store
- config endpoints
- login page
- config page
- any PDFs or external assets

Backend must still run with:

```
uvicorn main:app --reload --port 8000
```

Frontend must still run with:

```
npm run dev
```

