from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.config import router as config_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(config_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Run with:
# uvicorn main:app --reload --port 8000
