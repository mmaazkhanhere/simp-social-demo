from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import conversations, dashboard, dealerships, internal
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    db = SessionLocal()
    try:
        init_db(engine, db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(dealerships.router)
app.include_router(conversations.router)
app.include_router(dashboard.router)
app.include_router(internal.router)

