"""
merchants.py
=============
Merchant threshold control endpoints (for dashboard Phase 4).
  GET  /v1/merchants/{merchant_id}/threshold  - current bandit state
  POST /v1/merchants/{merchant_id}/threshold  - manual override
"""

from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ThresholdOverride(BaseModel):
    offset: float = Field(
        ..., ge=-0.15, le=0.15, description="Signed offset from base 0.80 threshold"
    )


@router.get(
    "/merchants/{merchant_id}/threshold",
    summary="Get bandit state and effective threshold for a merchant",
)
async def get_threshold(merchant_id: str):
    from app.agents.threshold_bandit import get_bandit

    bandit = get_bandit()
    return await bandit.get_diagnostics(merchant_id)


@router.post(
    "/merchants/{merchant_id}/threshold",
    summary="Manually override merchant threshold offset",
)
async def set_threshold(merchant_id: str, body: ThresholdOverride):
    from app.agents.threshold_bandit import (
        get_bandit,
        BASE_THRESHOLD,
        FLOOR_THRESHOLD,
        CEILING_THRESHOLD,
    )

    bandit = get_bandit()
    state = await bandit._load_state(merchant_id)
    state["current_arm"] = str(body.offset)
    await bandit._save_state(merchant_id, state)
    effective = max(
        FLOOR_THRESHOLD, min(CEILING_THRESHOLD, BASE_THRESHOLD + body.offset)
    )
    return {
        "merchant_id": merchant_id,
        "offset": body.offset,
        "effective_threshold": round(effective, 3),
        "message": f"Threshold manually set to {effective:.3f} for {merchant_id}",
    }
