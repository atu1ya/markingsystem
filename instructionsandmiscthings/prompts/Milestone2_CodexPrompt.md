
# Milestone 2 – Full Codex Prompt (Admin Config Endpoints)

Use this Markdown file as a **single prompt** for VS Code Copilot/Codex at the **repo root** once Milestone 1 is complete.

Copy everything from **"Codex Prompt for Milestone 2"** into Copilot Chat.

---

# Codex Prompt for Milestone 2: Admin Config Endpoints (Answer Keys + Concept Map)

You are an AI coding agent working at the root of this repo.
Milestones 0 and 1 are already done:
- FastAPI backend is running with `/health` and `/auth/login`
- Session store using `X-Session-ID` header is implemented
- Frontend skeleton exists but should not be touched for this milestone

Your job is to implement **Milestone 2**, which adds backend endpoints for loading JSON configs (answer keys + concept map) into the per-session state.

Do **not** modify:
- any frontend files
- PDFs
- `instructionsandmiscthings/`
- or existing auth/session logic

Work only inside the `backend/` folder.

---

## 1. Create `backend/routes/config.py`

Create a new FastAPI router for configuration endpoints.

### 1.1 Ensure folder structure
Inside `backend/`, ensure this exists:

```
backend/
  routes/
    __init__.py
```

Create it if missing.

### 1.2 Create the `config.py` file

Inside `backend/routes/config.py`, implement:

- `router = APIRouter(prefix="/config", tags=["config"])`

- Import:
  - `APIRouter`, `Depends`, `HTTPException`, `status`
  - `BaseModel`, `validator`
  - `Dict`, `List`, `Literal`
  - `get_session` from `core.session_store`

---

## 2. Define validation models

The answer sheets use options A to E, so define:

```python
Letter = Literal["A", "B", "C", "D", "E"]
```

### 2.1 Reading Answer Key JSON

Structure:
`{ "1": "C", "2": "A", ..., "35": "B" }`

Pydantic model:

```python
class ReadingAnswerKey(BaseModel):
    __root__: Dict[str, Letter]

    @validator("__root__")
    def validate_keys(cls, v):
        for k in v:
            if not k.isdigit():
                raise ValueError("All question keys must be numeric strings")
        return v
```

### 2.2 QR/AR Combined Answer Key JSON

Structure:

```json
{
  "qr": { "1": "A", ... },
  "ar": { "1": "D", ... }
}
```

Models:

```python
class SubjectAnswerKey(BaseModel):
    __root__: Dict[str, Letter]

    @validator("__root__")
    def validate_keys(cls, v):
        for k in v:
            if not k.isdigit():
                raise ValueError("All question keys must be numeric strings")
        return v

class QrArAnswerKey(BaseModel):
    qr: SubjectAnswerKey
    ar: SubjectAnswerKey
```

### 2.3 Concept Map JSON

Structure:

```json
{
  "Reading": { "Inference": [1,2,3] },
  "QR": { "Numbers": [1,2] },
  "AR": { "Patterns": [1,2] }
}
```

Model:

```python
class ConceptMap(BaseModel):
    __root__: Dict[str, Dict[str, List[int]]]
```

---

## 3. Implement the 3 POST endpoints

All three endpoints:

- use `Depends(get_session)` to access the session
- validate JSON using Pydantic
- store values in:

```python
session["answer_keys"]["reading"]
session["answer_keys"]["qr_ar"]
session["concept_map"]
```

### 3.1 POST /config/reading-key

```python
@router.post("/reading-key")
def set_reading_key(payload: ReadingAnswerKey, session: dict = Depends(get_session)):
    session["answer_keys"]["reading"] = payload.__root__
    return {"status": "ok", "message": "Reading answer key loaded"}
```

### 3.2 POST /config/qr-ar-key

```python
@router.post("/qr-ar-key")
def set_qr_ar_key(payload: QrArAnswerKey, session: dict = Depends(get_session)):
    session["answer_keys"]["qr_ar"] = payload.dict()
    return {"status": "ok", "message": "QR/AR answer key loaded"}
```

### 3.3 POST /config/concepts

```python
@router.post("/concepts")
def set_concepts(payload: ConceptMap, session: dict = Depends(get_session)):
    session["concept_map"] = payload.__root__
    return {"status": "ok", "message": "Concept map loaded"}
```

---

## 4. Register router in backend/main.py

Open `backend/main.py` and:

### Add import:

```python
from routes.config import router as config_router
```

(or use `from backend.routes.config import router as config_router` depending on import paths)

### Include router:

```python
app.include_router(config_router)
```

Keep `/health` exactly the same.

---

## 5. What should work after Milestone 2

### 5.1 Login

POST `/auth/login`
returns `{ "session_id": "<uuid>" }`

### 5.2 POST reading key

Headers:

```
X-Session-ID: <uuid>
Content-Type: application/json
```

Body example:

```json
{
  "1": "C",
  "2": "A",
  "3": "E"
}
```

### 5.3 POST QR/AR key

```json
{
  "qr": { "1": "B", "2": "A" },
  "ar": { "1": "E", "2": "D" }
}
```

### 5.4 POST Concept Map

```json
{
  "Reading": { "Inference":[1,2] },
  "QR": { "Numbers":[1,2] }
}
```

### 5.5 Session now contains

```python
session["answer_keys"]["reading"]
session["answer_keys"]["qr_ar"]
session["concept_map"]
```

---

## Final instructions

Perform all edits ONLY in:

- `backend/routes/config.py` (new)
- `backend/main.py` (add router inclusion)
- `backend/routes/__init__.py` (ensure exists)

Do **not** touch:
- Authentication logic
- Session store logic
- Frontend
- PDFs or misc folders

Backend must still run normally with:

```
uvicorn main:app --reload --port 8000
```

