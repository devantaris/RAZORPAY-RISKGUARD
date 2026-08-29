"""
POST /v1/assess   — single transaction fraud assessment
POST /v1/batch    — batch assessment (up to 1000 transactions)
"""
from __future__ import annotations

import time
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.transaction import (
    AssessRequest, AssessResponse,
    BatchAssessRequest, BatchAssessResponse,
    Decision, RiskReport, ShapFeature,
)

logger = logging.getLogger("riskguard.assess")
router = APIRouter()


def _mock_assess(req: AssessRequest) -> AssessResponse:
    """
    Phase 1 mock — returns a plausible skeleton response.
    Will be replaced by real pipeline in Phase 2.
    """
    return AssessResponse(
        transaction_id=req.transaction_id,
        decision=Decision.APPROVE,
        confidence=0.12,
        stage_reached="V1_MOCK",
        risk_report=RiskReport(
            explanation=(
                "Mock decision: pipeline not yet loaded. "
                "This skeleton will be replaced with V1-V4 staged uncertainty in Phase 2."
            ),
            shap_top_features=[
                ShapFeature(feature="amount", impact=0.05, direction="suppresses_fraud"),
            ],
            merchant_threshold=0.80,
            chargeback_risk=None,
        ),
        inference_ms=0.5,
    )


@router.post(
    "/assess",
    response_model=AssessResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess a single payment transaction for fraud risk",
)
async def assess(req: AssessRequest) -> AssessResponse:
    t0 = time.perf_counter()

    try:
        from app.pipeline.orchestrator import get_orchestrator
        orch = get_orchestrator()
        result = await orch.evaluate(req)
    except ImportError:
        logger.debug("Pipeline not loaded — using mock response (Phase 1 skeleton)")
        result = _mock_assess(req)
    except Exception as e:
        logger.error(f"Pipeline error for {req.transaction_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline evaluation failed: {str(e)}",
        )

    result.inference_ms = round((time.perf_counter() - t0) * 1000, 2)
    logger.info(
        f"txn={req.transaction_id} merchant={req.merchant_id} "
        f"amount={req.amount} decision={result.decision} "
        f"conf={result.confidence:.3f} stage={result.stage_reached} "
        f"latency={result.inference_ms}ms"
    )
    return result


@router.post(
    "/batch",
    response_model=BatchAssessResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess a batch of transactions (up to 1000)",
)
async def batch_assess(req: BatchAssessRequest) -> BatchAssessResponse:
    t0 = time.perf_counter()
    results = []
    for txn in req.transactions:
        try:
            from app.pipeline.orchestrator import get_orchestrator
            orch = get_orchestrator()
            r = await orch.evaluate(txn)
        except ImportError:
            r = _mock_assess(txn)
        results.append(r)

    total_ms = round((time.perf_counter() - t0) * 1000, 2)
    tps = round(len(results) / (total_ms / 1000), 1) if total_ms > 0 else 0.0
    return BatchAssessResponse(results=results, total_ms=total_ms, throughput_tps=tps)
