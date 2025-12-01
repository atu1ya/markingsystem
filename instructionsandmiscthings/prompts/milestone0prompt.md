# Codex Prompt for Milestone 0: Repository and Base Setup

You are an AI coding agent working at the root of this repo.  
Create everything needed for **Milestone 0** of my ASET marking system **automatically**.

Overall goals:
- Create a `backend/` folder containing a runnable FastAPI app and requirements file.
- Create a `frontend/` folder containing a Vite React app with routes for `/login`, `/config`, and `/mark`.
- Create a top level `README.md` describing purpose, structure, and how to run each part.
- Keep all existing files such as PDFs or `instructionsandmiscthings/`. Do not modify or delete them.

Follow these steps exactly:

## 1. Create backend folder and FastAPI skeleton
1. Create a folder `backend` at the repo root (if it does not exist).
2. Inside `backend`, create a Python virtual environment folder called `.venv` but **do not add it to git**.  
   If you can execute shell commands, run:
   ```
   python -m venv .venv
   ```
   If not, simply create the folder structure.
3. Inside `backend`, create a file `requirements.txt` containing exactly:

   ```
   fastapi
   "uvicorn[standard]"
   python-multipart
   pdf2image
   pillow
   opencv-python
   ```

4. Create `backend/main.py` with this exact content:

   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/health")
   def health():
       return {"status": "ok"}

   # Run with:
   # uvicorn main:app --reload --port 8000
   ```

5. Do **not** overwrite or modify any existing files outside of `backend/`.

---

## 2. Create frontend folder and React app with routing
1. At the repo root, create a folder `frontend` (if it does not exist).
2. Inside `frontend`, create a Vite React project.  
   If you can run shell commands:

   ```
   npm create vite@latest . -- --template react
   npm install
   npm install react-router-dom
   ```

   If you cannot run shell commands, generate the equivalent file structure manually:
   - `package.json`
   - `index.html`
   - `vite.config.js`
   - `src/main.jsx`
   - `src/App.jsx`
   - `src/index.css`
   - `src/pages/LoginPage.jsx`
   - `src/pages/ConfigPage.jsx`
   - `src/pages/MarkPage.jsx`

3. Implement React Router in `src/main.jsx` so routes `/login`, `/config`, and `/mark` load simple placeholder pages:

   ```jsx
   import React from "react";
   import ReactDOM from "react-dom/client";
   import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
   import LoginPage from "./pages/LoginPage.jsx";
   import ConfigPage from "./pages/ConfigPage.jsx";
   import MarkPage from "./pages/MarkPage.jsx";
   import "./index.css";

   function AppRouter() {
     return (
       <BrowserRouter>
         <nav style={{ padding: "1rem", borderBottom: "1px solid #ccc" }}>
           <Link to="/login" style={{ marginRight: "1rem" }}>Login</Link>
           <Link to="/config" style={{ marginRight: "1rem" }}>Config</Link>
           <Link to="/mark">Mark</Link>
         </nav>
         <Routes>
           <Route path="/login" element={<LoginPage />} />
           <Route path="/config" element={<ConfigPage />} />
           <Route path="/mark" element={<MarkPage />} />
           <Route path="*" element={<LoginPage />} />
         </Routes>
       </BrowserRouter>
     );
   }

   ReactDOM.createRoot(document.getElementById("root")).render(
     <React.StrictMode>
       <AppRouter />
     </React.StrictMode>
   );
   ```

4. Create placeholder pages:

   **`src/pages/LoginPage.jsx`**
   ```jsx
   export default function LoginPage() {
     return (
       <div style={{ padding: "2rem" }}>
         <h1>ASET Marking System – Login</h1>
         <p>Milestone 0 placeholder.</p>
       </div>
     );
   }
   ```

   **`src/pages/ConfigPage.jsx`**
   ```jsx
   export default function ConfigPage() {
     return (
       <div style={{ padding: "2rem" }}>
         <h1>Config Page</h1>
         <p>Milestone 0 placeholder.</p>
       </div>
     );
   }
   ```

   **`src/pages/MarkPage.jsx`**
   ```jsx
   export default function MarkPage() {
     return (
       <div style={{ padding: "2rem" }}>
         <h1>Mark Page</h1>
         <p>Milestone 0 placeholder.</p>
       </div>
     );
   }
   ```

5. Ensure `src/index.css` contains very simple default styling:

   ```css
   body {
     margin: 0;
     font-family: system-ui, sans-serif;
   }
   a {
     text-decoration: none;
   }
   ```

---

## 3. Create top-level README.md
Place a new file in the repo root named `README.md` with:

```
# ASET Automated Marking System

Internal tool used by staff to mark ASET multiple choice papers, annotate answer sheets, and generate downloadable PDFs.

## Folder Structure

- backend/
  FastAPI server. Start with:
  python -m venv .venv
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000

- frontend/
  React app (Vite). Start with:
  npm install
  npm run dev

- instructionsandmiscthings/
  Misc notes, prompts, roadmap files.

## Running the Project

### Backend
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### Frontend
cd frontend
npm install
npm run dev
```

---

## Final rule
**Do not modify or delete:**
- PDFs
- `instructionsandmiscthings/`
- Any other existing files not explicitly mentioned.

Produce all new files and folders exactly as instructed and confirm completion.
