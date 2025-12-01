# Development Roadmap for Automated ASET Marking System (Up To Step 8)

This roadmap is for you (developer) and for code generation tools like Copilot or Codex.  
It is organized into milestones that you can tackle one by one.

---

## Milestone 0: Repository and Base Setup

**Goal:** Have a single repo with backend and frontend folders and a basic runnable skeleton.

### Tasks
1. Create a new git repository.
2. Create folders:
   - `backend/`
   - `frontend/`
3. In `backend/`:
   - Initialize a Python virtual environment.
   - Add `requirements.txt`.
4. In `frontend/`:
   - Create a new React project with Vite or Create React App.
5. Add a top level `README.md` that briefly explains:
   - Project purpose.
   - Folder structure.
   - How to run backend and frontend.

### Example prompt for Codex
> Create a basic FastAPI backend skeleton in a folder called `backend`, with a `main.py` that exposes a `/health` endpoint returning `{"status": "ok"}` and a `requirements.txt` with FastAPI and Uvicorn.

> Create a React app in a folder called `frontend` with routes for `/login`, `/config`, and `/mark` using React Router.

---

## Milestone 1: Backend Authentication and Session Store

**Goal:** Staff only access with a simple password and an in memory session store.

### Tasks
1. In `backend/app/` create structure:
   - `main.py`
   - `routes/auth.py`
   - `core/session_store.py`
2. Install extra dependencies:
   - `python-multipart`
   - `python-dotenv` (optional for environment variables).
3. Implement a global `SESSION_STORE` dictionary in `session_store.py`.
4. In `routes/auth.py`:
   - Implement `POST /auth/login`:
     - Accept JSON with a `password` field.
     - Compare to an environment variable `ASET_APP_PASSWORD`.
     - On success:
       - Generate a `session_id` (UUID).
       - Store an entry in `SESSION_STORE`:
         ```python
         SESSION_STORE[session_id] = {
             "answer_keys": {},
             "concept_map": None
         }
         ```
       - Return the `session_id` in JSON or set it as a cookie.
5. Add a dependency function `get_session()` in `session_store.py`:
   - Reads `session_id` from header or cookie.
   - Looks it up in `SESSION_STORE`.
   - Raises HTTP 401 if not found.
6. Wire `routes/auth.py` into `main.py`.

### Example prompt for Codex
> In `backend/app`, implement FastAPI routes for `/auth/login` that check a password from the environment variable `ASET_APP_PASSWORD`, generate a UUID `session_id`, store session data in a global dictionary, and return `session_id`. Also provide a helper dependency `get_session()` that validates the session on protected routes.

---

## Milestone 2: Admin Config Endpoints (Answer Keys and Concept Map)

**Goal:** Backend endpoints to accept and store the three JSON configs per session.

### Tasks
1. Create `routes/config.py`.
2. Add three POST endpoints:
   - `POST /config/reading-key`
   - `POST /config/qr-ar-key`
   - `POST /config/concepts`
3. Use `get_session()` to access the current session.
4. For each endpoint:
   - Accept raw JSON in the request body.
   - Validate basic structure:
     - Reading key: keys are question numbers as strings, values are `"A"`, `"B"`, `"C"`, `"D"`.
     - QR or AR key: object with `"qr"` and `"ar"` sub objects.
     - Concept map: object keyed by subject, then concept, then list of question numbers.
   - Store them in the session:
     ```python
     session["answer_keys"]["reading"] = reading_json
     session["answer_keys"]["qr_ar"] = qr_ar_json
     session["concept_map"] = concepts_json
     ```
5. Return simple status JSON for success or error.

### Example prompt for Codex
> In `backend/app/routes/config.py`, create three FastAPI POST endpoints `/config/reading-key`, `/config/qr-ar-key`, and `/config/concepts`. Each should use a `get_session()` dependency, validate the incoming JSON has the expected shape, store it in the session dictionary, and return a success message or a 400 error if validation fails.

---

## Milestone 3: React Frontend for Login and Config Pages

**Goal:** Staff can log in and load JSON configs once per session.

### Tasks
1. In `frontend`:
   - Set up React Router routes for:
     - `/login`
     - `/config`
2. Implement `/login` page:
   - Password input.
   - Login button.
   - Call `POST /auth/login`.
   - On success, store `session_id` (for example in `localStorage` or via cookies).
   - Redirect to `/config`.
3. Implement a small API helper:
   - Handles adding `session_id` to headers if needed.
   - Handles base URL for the backend.
4. Implement `/config` page:
   - Three large textareas:
     - Reading answer key JSON.
     - QR and AR answer key JSON.
     - Concept mapping JSON.
   - Save buttons for each section that call the corresponding backend endpoints.
   - Visual status labels like "Reading key loaded" etc.
   - A button "Go to Marking" that routes to `/mark` once all three configs were successfully saved.

### Example prompt for Codex
> In the React frontend, create two pages `LoginPage` and `ConfigPage`. `LoginPage` should post the entered password to `/auth/login`, store `session_id` on success, and navigate to `/config`. `ConfigPage` should have three textareas for JSON and three save buttons that call `/config/reading-key`, `/config/qr-ar-key`, and `/config/concepts` with the provided JSON. Use React Router for navigation.

---

## Milestone 4: ROI Configuration for Reading and QR or AR Sheets

**Goal:** Define the ROI coordinates for each bubble on the sheets in static Python files.

### Tasks
1. Create files in `backend/app/core/`:
   - `questions_reading.py`
   - `questions_qr_ar.py`
2. In `questions_reading.py`, define a data structure like:
   ```python
   QUESTIONS_READING = [
       {
           "id": 1,
           "options": [
               (x1, y1, x2, y2),  # A
               (x1, y1, x2, y2),  # B
               (x1, y1, x2, y2),  # C
               (x1, y1, x2, y2)   # D
           ]
       },
       ...
   ]
   ```
3. In `questions_qr_ar.py`, define data structures for both QR and AR:
   ```python
   QUESTIONS_QR = [ ... ]
   QUESTIONS_AR = [ ... ]
   ```
4. Fill in the real ROI coordinates after measuring them from the template sheet.
5. Optionally add small helper functions to retrieve ROIs.

### Example prompt for Codex
> In `backend/app/core/questions_reading.py`, define a constant `QUESTIONS_READING` that contains a list of question dictionaries. Each dictionary should contain an `"id"` and an `"options"` list of four `(x1, y1, x2, y2)` tuples for the A, B, C, and D bubbles. Use placeholder integer coordinates that I can manually replace later.

---

## Milestone 5: Core Computer Vision and Marking Logic

**Goal:** Implement PDF to image conversion, bubble detection based on ROI, and comparison with answer keys.

### Tasks
1. In `pdf_tools.py`, implement:
   - `pdf_to_image(pdf_bytes: bytes) -> Image.Image` using `pdf2image.convert_from_bytes`.
   - Assume a single page PDF for now.
2. In `cv.py`, implement:
   - `detect_answers(image, questions)`:
     - `questions` comes from `QUESTIONS_READING` or `QUESTIONS_QR` or `QUESTIONS_AR`.
     - For each question:
       - For each option `(x1, y1, x2, y2)`:
         - Crop the region from the image.
         - Convert to grayscale.
         - Compute mean pixel intensity.
       - Select the option with the lowest mean intensity.
       - Return a dict: `{question_id: "A" or "B" or "C" or "D"}`.
3. Create `marking_logic.py` in `core`:
   - Functions:
     - `mark_reading(student_answers, answer_key)`
     - `mark_qr(student_answers, answer_key)`
     - `mark_ar(student_answers, answer_key)`
   - Each returns:
     - Per question result (correct or incorrect).
     - Total correct and total questions.

### Example prompt for Codex
> In `backend/app/core/cv.py`, implement a `detect_answers(image, questions)` function that takes a Pillow image and a questions list with ROI coordinates, crops each ROI, converts it to grayscale, calculates mean pixel intensity, and returns the selected answer (A to D) per question based on the darkest ROI.

---

## Milestone 6: Annotation of Sheets (Mark Wrong Answers and Write Scores)

**Goal:** Draw visual markings on the sheets: correct answers in red for wrong questions and scores in predefined spots.

### Tasks
1. Create `annotate_sheet.py` in `core`.
2. Decide on fixed coordinates for:
   - Reading score text on the reading sheet.
   - QR score text on the QR or AR sheet.
   - AR score text on the QR or AR sheet.
3. Implement:
   - `annotate_reading_sheet(image, results, layout_config)`
   - `annotate_qr_ar_sheet(image, qr_results, ar_results, layout_config)`
4. For each wrong question:
   - Get the correct answer letter.
   - Use the ROI of that option to:
     - Draw a red rectangle or circle around the bubble.
5. Use `ImageDraw.Draw` and `ImageFont` from Pillow to:
   - Write `"Reading: X/Y"` on the reading sheet.
   - Write `"QR: X/Y"` and `"AR: X/Y"` on the QR or AR sheet.

### Example prompt for Codex
> In `backend/app/core/annotate_sheet.py`, implement functions that take a Pillow image, marking results, and layout coordinates, then draw red rectangles around the correct answer bubbles for questions the student got wrong and draw the section scores (for example "Reading: 32/40") at fixed positions on the page.

---

## Milestone 7: Image to PDF Conversion and Marking Endpoint

**Goal:** Accept uploaded PDFs, run the full pipeline, and return annotated PDFs.

### Tasks
1. In `pdf_tools.py`, implement:
   - `image_to_pdf_bytes(image: Image.Image) -> bytes` using Pillow.
2. Create `routes/marking.py` with `POST /mark/single-student`:
   - Protected by `get_session()`.
   - Accept multipart form data:
     - `student_name`
     - `writing_score`
     - `reading_pdf` file
     - `qr_ar_pdf` file
   - For `reading_pdf`:
     - Convert PDF to image.
     - Run `detect_answers` with `QUESTIONS_READING`.
     - Load reading answer key from session.
     - Run `mark_reading`.
     - Annotate the image.
     - Convert annotated image to PDF bytes.
   - For `qr_ar_pdf`:
     - Convert PDF to image.
     - Run `detect_answers` separately with `QUESTIONS_QR` and `QUESTIONS_AR`.
     - Load QR and AR keys from session.
     - Run `mark_qr` and `mark_ar`.
     - Annotate the image.
     - Convert annotated image to PDF bytes.
   - Package both resulting PDFs into a ZIP in memory.
   - Return the ZIP as the response with an appropriate content type and filename.

### Example prompt for Codex
> In `backend/app/routes/marking.py`, implement a FastAPI endpoint `/mark/single-student` that takes student name, writing score, and two PDF files (reading and QR or AR), runs the PDF to image conversion, bubble detection, marking logic, and sheet annotation, then converts the annotated images back into PDFs and returns a ZIP file containing `reading_marked.pdf` and `qr_ar_marked.pdf`.

---

## Milestone 8: React Marking Page and Download Handling

**Goal:** Connect the frontend marking page to the backend endpoint and support file download.

### Tasks
1. Implement `/mark` page in React:
   - Inputs for:
     - Student name.
     - Writing score.
   - Two drag and drop or browse file inputs:
     - Reading PDF.
     - QR or AR PDF.
   - A "Generate Marked Sheets" button.
2. When the form is submitted:
   - Build a `FormData` object with:
     - `student_name`
     - `writing_score`
     - `reading_pdf`
     - `qr_ar_pdf`
   - Send POST request to `/mark/single-student` with `responseType: 'blob'`.
3. On response:
   - Create a Blob from the response data.
   - Create an object URL from the Blob.
   - Trigger a download of something like `ASET_<studentName>_marked_sheets.zip`.
4. Add basic error handling and loading state.

### Example prompt for Codex
> In the React frontend, implement the `/mark` page with a form that collects `student_name`, `writing_score`, and two PDF files. On submit, send them as multipart form data to `/mark/single-student`, receive a ZIP file as a blob, and trigger a file download named `ASET_<studentName>_marked_sheets.zip`.

---

## Status After This Roadmap

After completing all milestones above you will have:

- A staff only web app.
- In memory answer keys and concept mapping per session.
- A marking page where staff:
  - Enter student name and writing score.
  - Upload reading and QR or AR MCQ PDFs.
- A backend that:
  - Converts PDFs to images.
  - Detects filled bubbles using defined ROIs.
  - Compares answers to keys and computes scores.
  - Annotates sheets with correct answers and scores.
  - Returns annotated PDFs as a ZIP file for download.

Step 9 (full PDF report generation) can be added on top of this pipeline later.
