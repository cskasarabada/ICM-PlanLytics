"""Standalone FastAPI app for comp_plan module.

Run with: uvicorn comp_plan.api.app:app --port 8000
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from comp_plan.api.routes import router as plan_router
from comp_plan.api.landing import router as landing_router
from comp_plan.api.admin_routes import router as admin_router
from comp_plan.api.auth_routes import router as auth_router

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

# Mount route groups
app.include_router(landing_router, tags=["Landing"])
app.include_router(plan_router, prefix="/plan", tags=["Plan Analysis"])
app.include_router(admin_router, prefix="/admin", tags=["Admin Dashboard"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Mount static files for exports
data_dir = Path("data")
outputs_dir = data_dir / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(outputs_dir)), name="files")
