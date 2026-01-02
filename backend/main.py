from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.config import router as config_router
from routes.marking import router as marking_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(config_router)
app.include_router(marking_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Run with:
# uvicorn main:app --reload --port 8000
