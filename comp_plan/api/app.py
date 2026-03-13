"""Standalone FastAPI app for comp_plan module.

Run with: uvicorn comp_plan.api.app:app --port 8000
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from comp_plan.api.routes import router

app = FastAPI(
    title="ICM PlanLytics - Compensation Plan Analysis",
    description="AI-powered compensation plan analysis with inherent PII scrubbing and Oracle ICM mapping.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount plan routes
app.include_router(router, prefix="/plan", tags=["Plan Analysis"])

# Mount static files for exports
data_dir = Path("data")
outputs_dir = data_dir / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(outputs_dir)), name="files")


@app.get("/")
def root():
    return {
        "name": "ICM PlanLytics",
        "version": "1.0.0",
        "description": "Compensation Plan Analysis with inherent PII protection",
        "endpoints": {
            "ui": "/plan/ui",
            "analyze": "POST /plan/analyze",
            "oracle_export": "POST /plan/oracle-export",
            "health": "/plan/healthz",
            "docs": "/docs",
        },
    }
