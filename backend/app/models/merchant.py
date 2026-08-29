from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MerchantProfile(BaseModel):
    merchant_id:           str            = Field(..., example="merch_xyz789")
    merchant_name:         str            = Field(..., example="QuickMart Delhi")
    category:              str            = Field(default="general_retail")
    avg_transaction_amount: float         = Field(default=1500.0)
    monthly_volume:        float          = Field(default=500000.0)
    threshold_offset:      float          = Field(default=0.0,  ge=-0.3, le=0.3)
    bandit_n_samples:      int            = Field(default=0)
    bandit_reward_ema:     float          = Field(default=0.0)
    created_at:            Optional[datetime] = Field(default_factory=datetime.utcnow)


class ThresholdOverrideRequest(BaseModel):
    merchant_id: str   = Field(..., example="merch_xyz789")
    new_offset:  float = Field(..., ge=-0.3, le=0.3, description="Signed offset applied to base threshold")


class MerchantMetrics(BaseModel):
    merchant_id:   str   = Field(...)
    precision:     float = Field(...)
    recall:        float = Field(...)
    total_assessed: int  = Field(...)
    fraud_caught:  int   = Field(...)
    false_declines: int  = Field(...)
