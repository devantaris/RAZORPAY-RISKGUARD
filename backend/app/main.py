"""
Razorpay RiskGuard — FastAPI Application Entry Point
======================================================
Staged Uncertainty Fraud Defense + Agentic AI Layer
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("riskguard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")


# ── Lifespan: startup / shutdown ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("═" * 60)
    logger.info("  Razorpay RiskGuard starting up ...")
    logger.info("═" * 60)

    # Lazy-import pipeline on startup so models are loaded once
    try:
        from app.pipeline.orchestrator import get_orchestrator
        orch = get_orchestrator()
        logger.info(f"  Pipeline ready: {orch.status()}")
    except Exception as e:
        logger.warning(f"  Pipeline not loaded yet (will load on first request): {e}")

    yield  # ── application runs ────────────────────────────────────────────

    logger.info("RiskGuard shutting down.")


# ── Application ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Agentic Payment Fraud Defense: Staged Uncertainty Pipeline "
        "(V1 XGBoost + Isolation Forest → V2 Calibrated SVM → "
        "V3 Dempster-Shafer Fusion → V4 SHAP Deferral) + "
        "LLM Risk Explanation Agent + ε-Greedy Auto-Threshold Bandit."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ────────────────────────────────────────────────

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response


# ── Routers ──────────────────────────────────────────────────────────────────

from app.api.v1 import assess, health, stream, merchants

app.include_router(assess.router,    prefix=settings.API_V1_STR, tags=["Assessment"])
app.include_router(health.router,    prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(stream.router,    prefix=settings.API_V1_STR, tags=["Stream"])
app.include_router(merchants.router, prefix=settings.API_V1_STR, tags=["Merchants"])


# ── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs":    "/docs",
        "health":  f"{settings.API_V1_STR}/health",
    }
