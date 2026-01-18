"""FastAPI application for credit scoring."""

from fastapi import FastAPI
from .routes import credit, health

app = FastAPI(
    title="Cashi Credit Scoring API",
    description="Credit scoring API using WoE-based logistic regression scorecard",
    version="1.0.0"
)

# Include routers
app.include_router(health.router)
app.include_router(credit.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Cashi Credit Scoring API",
        "docs": "/docs",
        "health": "/health"
    }
