from fastapi import APIRouter
from app.config import settings
from app.db.schemas import HealthResponse
from app.services.llm.factory import get_llm_provider

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health():
    """Return backend health and runtime configuration."""
    provider = get_llm_provider()
    db_engine = "SQLite (Local)" if settings.DATABASE_URL.startswith("sqlite") else "PostgreSQL"

    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_engine,
        "llm_provider": provider.provider_name,
        "llm_model": settings.LLM_MODEL,
        "analysis_mode": provider.provider_name
    }
