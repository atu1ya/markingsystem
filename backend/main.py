from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# Run with:
# uvicorn main:app --reload --port 8000
