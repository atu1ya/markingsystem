# Milestone 1 – Full Codex Prompt (Backend Auth + Session Store)

Use this file as a **single prompt** for VS Code Copilot/Codex at the **repo root** once Milestone 0 is done.

Copy everything from the heading **"Codex Prompt for Milestone 1"** down into Copilot Chat.

---

# Codex Prompt for Milestone 1: Backend Authentication and Session Store

You are an AI coding agent working at the root of this repo.  
Milestone 0 is already completed: there is a `backend/main.py` FastAPI app and a `frontend` Vite React app.

Your task now is to implement **Milestone 1 – Backend Authentication and Session Store**.

Overall goals:

- Add a simple staff login endpoint that checks a single password from an environment variable `ASET_APP_PASSWORD`.
- Create an in memory session store keyed by `session_id` (UUID).
- Each session stores:
  - `answer_keys`: an object for future JSON configs.
  - `concept_map`: initially `None`.
- Provide a FastAPI dependency `get_session()` that future endpoints can use.
- Do **not** break the existing `/health` endpoint.
- Do **not** touch anything in `frontend/`, PDFs, or `instructionsandmiscthings/`.

Follow these steps exactly.

---

## 1. Backend folder structure

Work only inside the `backend/` folder.

1. Create two sub-packages inside `backend`:

   - `backend/core/`
   - `backend/routes/`

   Each should contain an empty `__init__.py` so they are Python packages.

2. Leave `backend/main.py` at the top level and keep the existing `/health` endpoint.

---

## 2. Session store implementation

Create a file `backend/core/session_store.py` with the following responsibilities:

- Maintain a global `SESSION_STORE` dictionary.
- Provide a helper `create_session()` that:
  - Generates a new UUID string `session_id`.
  - Inserts a new entry in `SESSION_STORE` with:

    ```python
    {
        "answer_keys": {},
        "concept_map": None
    }
    ```

  - Returns the `session_id`.

- Provide a FastAPI dependency `get_session()` that:
  - Reads the session id from the `X-Session-ID` HTTP header.
  - Validates that it exists and is present in `SESSION_STORE`.
  - Raises HTTP 401 if missing or invalid.
  - Returns the session dict.

Implement `session_store.py` like this (you can add minor typing / docstring improvements but keep the behavior the same):

```python
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request, status
from uuid import uuid4

SESSION_STORE: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    """Create a new session and return its id."""
    session_id = str(uuid4())
    SESSION_STORE[session_id] = {
        "answer_keys": {},
        "concept_map": None,
    }
    return session_id


def get_session_id_from_header(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Session-ID header",
        )
    if session_id not in SESSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return session_id


def get_session(session_id: str = Depends(get_session_id_from_header)) -> Dict[str, Any]:
    """FastAPI dependency to retrieve the current session dict."""
    return SESSION_STORE[session_id]
```

---

## 3. Authentication route

Create a file `backend/routes/auth.py` that defines an `APIRouter` with a `POST /auth/login` endpoint.

Requirements:

- Read the expected password from environment variable `ASET_APP_PASSWORD`.
- Request body:

  ```json
  {
    "password": "string"
  }
  ```

- If the password does not match, return HTTP 401.
- If `ASET_APP_PASSWORD` is not set, return HTTP 500 with a clear message.
- On success:
  - Call `create_session()` from `core.session_store`.
  - Return JSON `{ "session_id": "<uuid>" }`.

Implementation template:

```python
import os

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.session_store import create_session

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    session_id: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    expected_password = os.getenv("ASET_APP_PASSWORD")
    if expected_password is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: ASET_APP_PASSWORD not set",
        )

    if payload.password != expected_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    session_id = create_session()
    return LoginResponse(session_id=session_id)
```

Make sure the import path for `create_session` is correct based on how Python resolves packages from `backend/`.  
If necessary you can change the import to `from backend.core.session_store import create_session`, but keep the semantics identical.

---

## 4. Update main.py to include the auth router

Open `backend/main.py` and update it to:

- Import the auth router from `routes/auth.py`.
- Include this router in the FastAPI app.
- Keep the existing `/health` endpoint unchanged.

The final `backend/main.py` should look like this (adjust the import path if required):

```python
from fastapi import FastAPI

from routes.auth import router as auth_router  # or: from backend.routes.auth import router as auth_router

app = FastAPI()

# Include routers
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

Ensure `uvicorn main:app --reload --port 8000` still works from inside the `backend` folder.

---

## 5. Requirements update (optional)

If `pydantic` is not already available through FastAPI, nothing else is required.  
If you want to support `.env` files later you may append this line to `backend/requirements.txt`:

```
python-dotenv
```

Do **not** remove any existing dependencies.

---

## 6. What should work after this milestone

After you complete these steps:

1. Start the backend:

   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. `GET /health` still returns:

   ```json
   {"status": "ok"}
   ```

3. `POST /auth/login` with an incorrect password returns HTTP 401.

4. `POST /auth/login` with the correct password (matching `ASET_APP_PASSWORD`) returns:

   ```json
   { "session_id": "<uuid>" }
   ```

5. The new `session_id` exists as a key in `SESSION_STORE` in `core/session_store.py` with:

   ```python
   {
       "answer_keys": {},
       "concept_map": None
   }
   ```

Do not modify any frontend code or non-backend files while completing this milestone.
