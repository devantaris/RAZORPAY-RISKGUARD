from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Enums ──────────────────────────────────────────────────────────────────


class Decision(str, Enum):
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    STEP_UP = "STEP_UP"
    PEND = "PEND"


class PaymentMethod(str, Enum):
    CARD = "CARD"
    UPI = "UPI"
    WALLET = "WALLET"
    NETBANKING = "NETBANKING"


# ── Request ─────────────────────────────────────────────────────────────────


class AssessRequest(BaseModel):
    transaction_id: str = Field(..., example="txn_abc123")
    merchant_id: str = Field(..., example="merch_xyz789")
    amount: float = Field(..., gt=0, example=2500.00)
    currency: str = Field(default="INR")
    card_bin: Optional[str] = Field(None, min_length=6, max_length=8)
    payment_method: str = Field(default="CARD")
    device_id: Optional[str] = Field(None)
    customer_id: Optional[str] = Field(None)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None)
    upi_vpa: Optional[str] = Field(None)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)


# ── SHAP Feature Impact ─────────────────────────────────────────────────────


class ShapFeature(BaseModel):
    feature: str = Field(..., example="amount_vs_merchant_avg")
    impact: float = Field(..., example=0.34)
    direction: str = Field(..., example="elevates_fraud")


# ── Risk Report ─────────────────────────────────────────────────────────────


class RiskReport(BaseModel):
    explanation: str = Field(..., example="High-risk: amount is 4.2x merchant average.")
    shap_top_features: List[ShapFeature] = Field(default_factory=list)
    merchant_threshold: float = Field(..., example=0.72)
    chargeback_risk: Optional[float] = Field(None, ge=0.0, le=1.0)
    uncertainty_type: Optional[str] = Field(None)
    pend_reason_code: Optional[str] = Field(None)


# ── Response ────────────────────────────────────────────────────────────────


class AssessResponse(BaseModel):
    transaction_id: str = Field(..., example="txn_abc123")
    decision: Decision = Field(..., example="DECLINE")
    confidence: float = Field(..., ge=0.0, le=1.0)
    stage_reached: str = Field(..., example="V3")
    risk_report: RiskReport
    inference_ms: float = Field(..., example=87.4)


class BatchAssessRequest(BaseModel):
    transactions: List[AssessRequest] = Field(..., min_length=1, max_length=1000)


class BatchAssessResponse(BaseModel):
    results: List[AssessResponse]
    total_ms: float
    throughput_tps: float
