"""
features.py
===========
Real-time payment feature extractor.

Takes a raw AssessRequest and returns a feature vector suitable
for the V1-V4 ML pipeline. Uses Redis for cached velocity aggregates.

Payment-specific features (replacing the V1..V28 PCA features from research):
  - amount_log:              log1p(amount) — matches research transformation
  - amount_vs_merchant_avg:  amount / merchant_30d_average
  - velocity_1h_count:       transactions in last 1 hour (customer+card)
  - velocity_1h_amount:      total spend in last 1 hour
  - velocity_24h_count:      transactions in last 24 hours
  - velocity_24h_amount:     total spend in last 24 hours
  - bin_risk_score:          card BIN country risk (0=low, 1=high)
  - device_seen_before:      0/1 — device fingerprint in history
  - is_odd_hour:             0/1 — transaction between 1am-5am
  - payment_method_upi:      one-hot UPI
  - payment_method_card:     one-hot CARD
  - hour_sin / hour_cos:     cyclic hour encoding
"""
from __future__ import annotations

import logging
import math
from typing import Optional

import numpy as np

logger = logging.getLogger("riskguard.features")

# High-risk BIN country codes (ISO 3166-1 alpha-2)
HIGH_RISK_COUNTRIES = {"NG", "KP", "IR", "PK", "BD", "LY", "SD", "SY", "MM"}

# High-risk card BIN prefixes (prepaid/gift)
HIGH_RISK_BIN_PREFIXES = {"400066", "404756", "410057", "438935", "461046"}

FEATURE_NAMES = [
    "amount_log",
    "amount_vs_merchant_avg",
    "velocity_1h_count",
    "velocity_1h_amount_log",
    "velocity_24h_count",
    "velocity_24h_amount_log",
    "bin_risk_score",
    "device_seen_before",
    "is_odd_hour",
    "hour_sin",
    "hour_cos",
    "payment_method_upi",
    "payment_method_card",
    "payment_method_wallet",
]

N_FEATURES = len(FEATURE_NAMES)


class FeatureExtractor:
    """
    Converts AssessRequest -> numpy feature vector for the ML pipeline.
    Optionally reads Redis for velocity/historical data.
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client

    async def extract(self, req) -> np.ndarray:
        """
        Returns shape (1, N_FEATURES) numpy array.
        """
        features = await self._build_features(req)
        return np.array(features, dtype=np.float32).reshape(1, -1)

    async def _build_features(self, req) -> list:
        amount = float(req.amount)
        amount_log = math.log1p(amount)

        # Merchant average from Redis (Phase 2 will populate this)
        merchant_avg = await self._get_merchant_avg(req.merchant_id, amount)
        amount_vs_avg = amount / max(merchant_avg, 1.0)

        # Velocity from Redis
        vel = await self._get_velocity(req.customer_id or "unknown", req.card_bin)

        # BIN risk
        bin_risk = self._compute_bin_risk(req.card_bin)

        # Device consistency
        device_seen = await self._check_device(req.device_id, req.merchant_id)

        # Time features
        from datetime import datetime, timezone
        ts = req.timestamp or datetime.now(timezone.utc)
        hour = ts.hour
        is_odd_hour = 1.0 if (1 <= hour <= 5) else 0.0
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)

        # Payment method one-hot
        pm = (req.payment_method or "CARD").upper()
        pm_upi    = 1.0 if pm == "UPI"    else 0.0
        pm_card   = 1.0 if pm == "CARD"   else 0.0
        pm_wallet = 1.0 if pm == "WALLET" else 0.0

        return [
            amount_log,
            float(np.clip(amount_vs_avg, 0, 20)),
            float(vel["count_1h"]),
            math.log1p(vel["amount_1h"]),
            float(vel["count_24h"]),
            math.log1p(vel["amount_24h"]),
            float(bin_risk),
            float(device_seen),
            is_odd_hour,
            hour_sin,
            hour_cos,
            pm_upi,
            pm_card,
            pm_wallet,
        ]

    def _compute_bin_risk(self, card_bin: Optional[str]) -> float:
        if not card_bin:
            return 0.2  # Unknown BIN is slightly elevated
        if card_bin in HIGH_RISK_BIN_PREFIXES:
            return 1.0
        return 0.0

    async def _get_merchant_avg(self, merchant_id: str, fallback_amount: float) -> float:
        if self.redis:
            try:
                val = await self.redis.get(f"merchant:avg:{merchant_id}")
                if val:
                    return float(val)
            except Exception:
                pass
        # Fallback: category defaults loaded from seeded data
        return 2500.0  # INR default until Phase 2 Redis warming

    async def _get_velocity(self, customer_id: str, card_bin: Optional[str]) -> dict:
        defaults = {"count_1h": 0, "amount_1h": 0.0, "count_24h": 0, "amount_24h": 0.0}
        if self.redis:
            try:
                key_1h  = f"vel:{customer_id}:1h"
                key_24h = f"vel:{customer_id}:24h"
                count_1h   = await self.redis.get(f"{key_1h}:count")
                amount_1h  = await self.redis.get(f"{key_1h}:amount")
                count_24h  = await self.redis.get(f"{key_24h}:count")
                amount_24h = await self.redis.get(f"{key_24h}:amount")
                return {
                    "count_1h":  float(count_1h or 0),
                    "amount_1h": float(amount_1h or 0),
                    "count_24h": float(count_24h or 0),
                    "amount_24h": float(amount_24h or 0),
                }
            except Exception as e:
                logger.warning(f"Redis velocity lookup failed: {e}")
        return defaults

    async def _check_device(self, device_id: Optional[str], merchant_id: str) -> float:
        if not device_id or not self.redis:
            return 0.5  # neutral when unknown
        try:
            key = f"device:{device_id}:merchants"
            seen = await self.redis.sismember(key, merchant_id)
            return 1.0 if seen else 0.0
        except Exception:
            return 0.5


_extractor: Optional[FeatureExtractor] = None


def get_extractor(redis_client=None) -> FeatureExtractor:
    global _extractor
    if _extractor is None:
        _extractor = FeatureExtractor(redis_client=redis_client)
    return _extractor
