"""Health check and monitoring endpoints."""

from fastapi import APIRouter
from ..schemas import HealthResponse
from ..database import get_predictions_stats
from .credit import MODEL_LOADED

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model loading status."""
    return HealthResponse(
        status="healthy" if MODEL_LOADED else "degraded",
        model_loaded=MODEL_LOADED
    )


@router.get("/stats")
async def get_stats():
    """Get prediction statistics for monitoring."""
    stats = get_predictions_stats()
    stats["model_loaded"] = MODEL_LOADED
    return stats
