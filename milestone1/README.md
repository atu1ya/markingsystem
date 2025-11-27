# Milestone 1 – Computer Vision Marker

This milestone builds the backend-only computer vision workflow that compares a filled student bubble sheet against a template answer key and produces a text-based marking report.

## Files

- `marking_cv.py` – main script that aligns scans, measures bubble darkness, and writes results to `result.txt`.
- `questions_example.py` – placeholder ROI coordinates that describe where each answer bubble resides.
- `result.txt` – generated after each run; contains question-by-question status and a summary.

## Requirements

- Python 3.9+
- Packages: `opencv-python`, `numpy`, `pymupdf`

Install the dependencies (if needed):

```cmd
pip install opencv-python numpy pymupdf
```

## Usage

1. Place your template answer key scan at `milestone1/template.pdf` (first page is used).
2. Place the student scan you want to grade at `milestone1/student.pdf`.
3. Update the ROI coordinates inside `questions_example.py` so each `(x1, y1, x2, y2)` tuple tightly bounds a bubble option on your form.
4. Run the script from the repository root:

```cmd
python milestone1\marking_cv.py
```

Progress messages will stream to the terminal. When the script finishes, review `milestone1\result.txt` for per-question verdicts (e.g., `Q2: INCORRECT (correct B, student D)`) and a final summary block.

## Notes

- All ROIs assume an aligned student image; keep the scans consistent in orientation for best ECC alignment results.
- The fill detection uses relative darkness. If your scans are faint, adjust `MIN_FILL_DELTA` in `marking_cv.py` or re-scan with higher contrast.
- For new answer keys, regenerate `template.pdf` and re-run; no other code changes needed once ROIs are correct.
- If you only have image scans, you can still point the script to `.png`/`.jpg` files; PDF is just the default for convenience.
