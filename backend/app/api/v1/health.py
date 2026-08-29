from __future__ import annotations

import platform
import sys
import time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

_start_time = time.time()


class HealthResponse(BaseModel):
    status:       str
    service:      str
    version:      str
    uptime_s:     float
    python:       str
    pipeline:     str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    from app.core.config import settings

    pipeline_status = "unknown"
    try:
        from app.pipeline.orchestrator import get_orchestrator
        pipeline_status = get_orchestrator().status()
    except Exception:
        pipeline_status = "not_loaded"

    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        uptime_s=round(time.time() - _start_time, 1),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        pipeline=pipeline_status,
    )
