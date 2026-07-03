from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.db import get_db
from backend.app.routers import audit, entities, relationships
from backend.app.schemas import EntityRead


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Mitologia API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(audit.router)
    app.include_router(entities.router)
    app.include_router(relationships.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/search", response_model=list[EntityRead])
    def search(q: str, db: Session = Depends(get_db)):
        return entities.search_entities(q, db)

    return app


app = create_app()
