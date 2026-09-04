"""
threshold_bandit.py
====================
3B: Auto-Threshold Agent — epsilon-greedy bandit per merchant

Each merchant gets an independent threshold offset that drifts
based on their dispute and approval rates, using:

  - e-greedy exploration  (epsilon = 0.10)
  - Exponential moving average reward (alpha = 0.30)
  - Minimum 50 samples before any adjustment
  - Hard floor (0.40) and ceiling (0.95) safety guards

State is persisted in Redis with key:  bandit:{merchant_id}
Fallback: in-memory dict when Redis is unavailable.

Reward signal:
  +1.0  when APPROVE is followed by no chargeback (good threshold)
  -0.5  when a DECLINE is later confirmed fraudulent (missed at higher threshold)
  -1.0  when an APPROVE is later charged back (false negative)

For the demo, we simulate rewards with a simple heuristic based on
the pipeline decision and confidence score.
"""

from __future__ import annotations

import json
import logging
import random
from typing import Optional

logger = logging.getLogger("riskguard.threshold_bandit")


# Hyperparameters (from docx)
EPSILON = 0.10  # exploration rate
ALPHA = 0.30  # EMA smoothing factor
MIN_SAMPLES = 50  # minimum samples before threshold adjusts
FLOOR_THRESHOLD = 0.40
CEILING_THRESHOLD = 0.95
BASE_THRESHOLD = 0.80  # default Razorpay decline threshold
MAX_OFFSET = 0.15  # max signed offset from base

# Discrete offset arms to explore
OFFSET_ARMS = [-0.10, -0.05, 0.0, +0.05, +0.10]


def _default_state() -> dict:
    return {
        "n_samples": 0,
        "arm_rewards": {str(a): 0.0 for a in OFFSET_ARMS},
        "arm_counts": {str(a): 0 for a in OFFSET_ARMS},
        "current_arm": "0.0",
        "ema_reward": 0.0,
    }


class ThresholdBandit:
    """
    Per-merchant epsilon-greedy threshold bandit.
    Stores state in Redis; falls back to in-memory.
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._cache: dict[str, dict] = {}  # in-memory fallback
        self.epsilon = EPSILON
        self.alpha = ALPHA

    # ── State persistence ─────────────────────────────────────────────────────

    async def _load_state(self, merchant_id: str) -> dict:
        key = f"bandit:{merchant_id}"
        if self.redis:
            try:
                raw = await self.redis.get(key)
                if raw:
                    return json.loads(raw)
            except Exception:
                pass
        return self._cache.get(merchant_id, _default_state())

    async def _save_state(self, merchant_id: str, state: dict) -> None:
        key = f"bandit:{merchant_id}"
        if self.redis:
            try:
                await self.redis.setex(key, 86400 * 7, json.dumps(state))
                return
            except Exception:
                pass
        self._cache[merchant_id] = state

    # ── Threshold selection ───────────────────────────────────────────────────

    async def get_threshold(self, merchant_id: str) -> float:
        """
        Returns the effective decline threshold for this merchant.
        Before MIN_SAMPLES: returns BASE_THRESHOLD.
        After MIN_SAMPLES: e-greedy arm selection.
        """
        state = await self._load_state(merchant_id)

        if state["n_samples"] < MIN_SAMPLES:
            return BASE_THRESHOLD

        # e-greedy: explore vs exploit
        if random.random() < self.epsilon:
            arm = str(random.choice(OFFSET_ARMS))
        else:
            arm = max(
                state["arm_rewards"],
                key=lambda a: (
                    state["arm_rewards"][a] / max(state["arm_counts"].get(a, 1), 1)
                ),
            )

        state["current_arm"] = arm
        await self._save_state(merchant_id, state)

        offset = float(arm)
        effective = float(BASE_THRESHOLD + offset)
        effective = max(FLOOR_THRESHOLD, min(CEILING_THRESHOLD, effective))
        logger.debug(
            f"Merchant {merchant_id}: arm={arm} effective_threshold={effective:.3f}"
        )
        return effective

    # ── Reward update ─────────────────────────────────────────────────────────

    async def record_outcome(
        self,
        merchant_id: str,
        decision: str,
        confidence: float,
        was_fraud: Optional[bool] = None,
    ) -> None:
        """
        Updates bandit state with the outcome of a transaction.
        Called asynchronously after ground truth is known (chargeback signal).

        For demo purposes: simulate reward from confidence + decision.
        """
        state = await self._load_state(merchant_id)
        state["n_samples"] += 1

        # Compute reward
        if was_fraud is None:
            # Heuristic simulation: confident DECLINE on high prob = good
            if decision == "DECLINE" and confidence > 0.85:
                reward = +1.0
            elif decision == "APPROVE" and confidence < 0.10:
                reward = +1.0
            elif decision == "APPROVE" and confidence > 0.60:
                reward = -1.0  # missed potential fraud
            else:
                reward = 0.0
        else:
            # Ground truth available
            if decision == "DECLINE" and was_fraud:
                reward = +1.0  # correct block
            elif decision == "APPROVE" and not was_fraud:
                reward = +1.0  # correct approve
            elif decision == "APPROVE" and was_fraud:
                reward = -1.0  # chargeback
            elif decision == "DECLINE" and not was_fraud:
                reward = -0.5  # false positive
            else:
                reward = 0.0

        # Update EMA
        state["ema_reward"] = (
            self.alpha * reward + (1 - self.alpha) * state["ema_reward"]
        )

        # Update arm stats
        arm = state.get("current_arm", "0.0")
        state["arm_rewards"][arm] = state["arm_rewards"].get(arm, 0.0) + reward
        state["arm_counts"][arm] = state["arm_counts"].get(arm, 0) + 1

        await self._save_state(merchant_id, state)
        logger.debug(
            f"Bandit update: merchant={merchant_id} arm={arm} reward={reward:.1f} ema={state['ema_reward']:.3f}"
        )

    async def get_diagnostics(self, merchant_id: str) -> dict:
        """Returns bandit state for dashboard display."""
        state = await self._load_state(merchant_id)
        threshold = await self.get_threshold(merchant_id)
        return {
            "merchant_id": merchant_id,
            "effective_threshold": threshold,
            "n_samples": state["n_samples"],
            "current_arm": state["current_arm"],
            "ema_reward": round(state["ema_reward"], 4),
            "arm_summary": {
                arm: {
                    "count": state["arm_counts"].get(arm, 0),
                    "avg_reward": round(
                        state["arm_rewards"].get(arm, 0.0)
                        / max(state["arm_counts"].get(arm, 1), 1),
                        3,
                    ),
                }
                for arm in [str(a) for a in OFFSET_ARMS]
            },
            "is_adjusted": state["n_samples"] >= MIN_SAMPLES,
        }


_bandit: Optional[ThresholdBandit] = None


def get_bandit(redis_client=None) -> ThresholdBandit:
    global _bandit
    if _bandit is None:
        _bandit = ThresholdBandit(redis_client=redis_client)
    return _bandit
