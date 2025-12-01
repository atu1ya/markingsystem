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
