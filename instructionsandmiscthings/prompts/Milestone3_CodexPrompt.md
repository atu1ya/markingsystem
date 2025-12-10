# Milestone 3 – Full Codex Prompt (Frontend Login + Config Integration)

Use this Markdown file as a **single prompt** for VS Code Copilot/Codex at the **repo root** once Milestone 2 is complete.

Copy everything from **"Codex Prompt for Milestone 3"** into Copilot Chat.

---

# Codex Prompt for Milestone 3: Frontend Login + Config Page Connectivity

You are an AI coding agent working at the root of this repo.

Milestones completed so far:

- Milestone 0: Backend & frontend skeleton  
- Milestone 1: Authentication (`/auth/login`) + session store  
- Milestone 2: Admin config endpoints (`/config/reading-key`, `/config/qr-ar-key`, `/config/concepts`)

Your job in **Milestone 3** is to make the frontend functional:

- User login page must call `/auth/login`  
- Store the returned `session_id` locally  
- Config page must:
  - Accept JSON text
  - Send it to backend config endpoints
  - Show success/error messages  
- Add a shared API request helper
- Backend may need CORS if missing

Do NOT modify:
- Any backend logic outside CORS
- Any PDFs or misc folders

Work only in `frontend/` except for optional CORS setup.

---

## 1. (Optional but recommended) Enable CORS in backend

If not already added, open `backend/main.py` and insert:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If CORS is already configured, skip this step.

---

## 2. Create global API helper

Inside `frontend/src/` create a file:

```
api.js
```

Insert:

```javascript
const BASE_URL = "http://localhost:8000";

export async function apiRequest(path, method = "GET", body = null, sessionId = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (sessionId) {
    headers["X-Session-ID"] = sessionId;
  }

  const options = { method, headers };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(BASE_URL + path, options);

  if (!response.ok) {
    const result = await response.text();
    throw new Error(result);
  }

  return await response.json();
}
```

---

## 3. Implement Login Page (`/login`)

Modify `frontend/src/pages/LoginPage.jsx` to:

```jsx
import { useState } from "react";
import { apiRequest } from "../api";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    try {
      const res = await apiRequest("/auth/login", "POST", { password });
      localStorage.setItem("sessionId", res.session_id);
      window.location.href = "/config";
    } catch (err) {
      setError("Incorrect password");
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Login</h1>
      <input
        type="password"
        placeholder="Enter admin password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
```

---

## 4. Implement Config Page (`/config`)

Modify `frontend/src/pages/ConfigPage.jsx`:

```jsx
import { useState } from "react";
import { apiRequest } from "../api";

export default function ConfigPage() {
  const sessionId = localStorage.getItem("sessionId");

  const [readingJson, setReadingJson] = useState("");
  const [qrArJson, setQrArJson] = useState("");
  const [conceptsJson, setConceptsJson] = useState("");
  const [message, setMessage] = useState("");

  async function uploadReading() {
    try {
      const parsed = JSON.parse(readingJson);
      await apiRequest("/config/reading-key", "POST", parsed, sessionId);
      setMessage("Reading key uploaded");
    } catch {
      setMessage("Invalid reading JSON");
    }
  }

  async function uploadQrAr() {
    try {
      const parsed = JSON.parse(qrArJson);
      await apiRequest("/config/qr-ar-key", "POST", parsed, sessionId);
      setMessage("QR/AR key uploaded");
    } catch {
      setMessage("Invalid QR/AR JSON");
    }
  }

  async function uploadConcepts() {
    try {
      const parsed = JSON.parse(conceptsJson);
      await apiRequest("/config/concepts", "POST", parsed, sessionId);
      setMessage("Concept map uploaded");
    } catch {
      setMessage("Invalid concept map JSON");
    }
  }

  function goNext() {
    window.location.href = "/mark";
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Admin Configuration</h1>

      <h2>Reading Answer Key JSON</h2>
      <textarea rows="6" cols="60" value={readingJson} onChange={(e) => setReadingJson(e.target.value)} />
      <button onClick={uploadReading}>Upload Reading Key</button>

      <h2>QR/AR Answer Key JSON</h2>
      <textarea rows="6" cols="60" value={qrArJson} onChange={(e) => setQrArJson(e.target.value)} />
      <button onClick={uploadQrAr}>Upload QR/AR Key</button>

      <h2>Concept Map JSON</h2>
      <textarea rows="6" cols="60" value={conceptsJson} onChange={(e) => setConceptsJson(e.target.value)} />
      <button onClick={uploadConcepts}>Upload Concept Map</button>

      {message && <p>{message}</p>}

      <hr />
      <button onClick={goNext}>Go to Marking Page</button>
    </div>
  );
}
```

---

## 5. Expected behaviors after Milestone 3

### Login:
- User enters password
- Calls `/auth/login`
- Saves `session_id` to localStorage
- Redirects to `/config`

### Config Page:
- User pastes JSON into textareas
- Presses upload
- Frontend validates JSON
- Backend validates through Pydantic and stores it
- Message updates ("Reading key uploaded", etc)

### Ready for next milestone:
- All config data is correctly stored in per-session memory
- You may now proceed to Milestone 4 (Marking Page + file uploads)

---

## Final instructions

Modify ONLY:

- `frontend/src/api.js`
- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/ConfigPage.jsx`

Backend modifications allowed ONLY for CORS.

Do not touch:

- PDFs  
- Instructions folder  
- Auth/session logic  

Frontend must successfully communicate with backend using `X-Session-ID`.

---

