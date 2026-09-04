"""
v3_dempster_shafer.py
======================
Exact Dempster-Shafer belief fusion ported from Knowing-When-Not-to-Decide.

Three Basic Probability Assignment (BPA) sources:
  Source 1 (Ensemble): XGBoost mean_prob + std  -> m1(F), m1(L), m1(Theta)
  Source 2 (Novelty):  Isolation Forest score   -> m2(F), m2(L), m2(Theta)
  Source 3 (SVM):      Calibrated SVM prob_fraud -> m3(F), m3(L), m3(Theta)

Combined via Dempster's combination rule with conflict metric K.
Decision logic:
  K >= 0.25              -> PEND (Evidence Conflict — sources fundamentally disagree)
  Bel(F) >= 0.91,
    Ignorance <= 0.05    -> AUTO_DECLINE (high confidence, low ignorance)
  Ignorance >= 0.10      -> PEND (Insufficient Evidence)
  Bel(F) >= 0.35         -> STEP_UP_AUTH (medium confidence, request extra auth)
  else                   -> PEND (catch-all)
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

logger = logging.getLogger("riskguard.v3")

# Hyperparameters (tuned in Knowing-When-Not-to-Decide experiments)
STD_SCALE = 0.05  # normalise ensemble std to [0,1]
MAX_IGN_ENSEMBLE = 0.50
BASE_IGN_IF = 0.40
BASE_IGN_SVM = 0.15
MAX_IGN_SVM = 0.45

# Decision thresholds
K_CONFLICT_THRESHOLD = 0.25
BEL_DECLINE_THRESHOLD = 0.91
IGN_DECLINE_MAX = 0.05
IGN_INSUFFICIENT = 0.10
BEL_STEP_UP_THRESHOLD = 0.35

BPAType = Dict[str, float]  # {'F': ..., 'L': ..., 'FL': ...}


# ── BPA Generation ───────────────────────────────────────────────────────────


def bpa_from_ensemble(mean_prob: float, std: float) -> BPAType:
    """Source 1: Bootstrap XGBoost ensemble."""
    std_norm = float(np.clip(std / STD_SCALE, 0.0, 1.0))
    uncertainty_weight = std_norm * MAX_IGN_ENSEMBLE
    m_F = mean_prob * (1.0 - uncertainty_weight)
    m_L = (1.0 - mean_prob) * (1.0 - uncertainty_weight)
    m_FL = uncertainty_weight
    total = m_F + m_L + m_FL
    return {"F": m_F / total, "L": m_L / total, "FL": m_FL / total}


def bpa_from_isolation_forest(raw_score: float, sigmoid_scale: float = 20.0) -> BPAType:
    """Source 2: Isolation Forest anomaly score."""
    anomaly_degree = float(
        np.clip(1.0 / (1.0 + np.exp(raw_score * sigmoid_scale)), 0.0, 1.0)
    )
    m_F = anomaly_degree * (1.0 - BASE_IGN_IF)
    m_L = (1.0 - anomaly_degree) * (1.0 - BASE_IGN_IF)
    m_FL = BASE_IGN_IF
    total = m_F + m_L + m_FL
    return {"F": m_F / total, "L": m_L / total, "FL": m_FL / total}


def bpa_from_svm(svm_prob_fraud: float) -> BPAType:
    """Source 3: Calibrated SVM probability."""
    confidence = float(np.clip(abs(svm_prob_fraud - 0.5) * 2.0, 0.0, 1.0))
    ign = MAX_IGN_SVM - (MAX_IGN_SVM - BASE_IGN_SVM) * confidence
    m_F = svm_prob_fraud * (1.0 - ign)
    m_L = (1.0 - svm_prob_fraud) * (1.0 - ign)
    m_FL = ign
    total = m_F + m_L + m_FL
    return {"F": m_F / total, "L": m_L / total, "FL": m_FL / total}


# ── Dempster Combination Rule ────────────────────────────────────────────────


def dempster_combine(m1: BPAType, m2: BPAType) -> Tuple[BPAType, float]:
    """
    Combines two BPA functions using Dempster's rule.
    Returns (combined_bpa, conflict_K).
    Raises ValueError if K >= 1.0 (complete contradiction).
    """
    K = m1["F"] * m2["L"] + m1["L"] * m2["F"]
    if K >= 1.0 - 1e-9:
        raise ValueError(f"Complete contradiction in DS combination: K={K:.6f}")
    norm = 1.0 - K
    combined = {
        "F": (m1["F"] * m2["F"] + m1["F"] * m2["FL"] + m1["FL"] * m2["F"]) / norm,
        "L": (m1["L"] * m2["L"] + m1["L"] * m2["FL"] + m1["FL"] * m2["L"]) / norm,
        "FL": (m1["FL"] * m2["FL"]) / norm,
    }
    total = sum(combined.values())
    return {k: v / total for k, v in combined.items()}, float(K)


def extract_belief_metrics(m: BPAType) -> dict:
    return {
        "bel_F": m["F"],
        "pl_F": m["F"] + m["FL"],
        "bel_L": m["L"],
        "pl_L": m["L"] + m["FL"],
        "ignorance": m["FL"],
    }


# ── Three-Source Fusion & Routing ────────────────────────────────────────────


def fuse_and_route(
    mean_prob: float,
    std: float,
    iso_score: float,
    svm_prob: float,
) -> Tuple[str, dict]:
    """
    Fuses three BPA sources and returns (sub_decision, belief_metrics).

    sub_decision in:
      AUTO_DECLINE    -> collapses to DECLINE in V4
      STEP_UP_AUTH    -> collapses to STEP_UP in V4
      HUMAN_ESCALATE  -> collapses to PEND in V4
    """
    b1 = bpa_from_ensemble(mean_prob, std)
    b2 = bpa_from_isolation_forest(iso_score)
    b3 = bpa_from_svm(svm_prob)

    m12, K12 = dempster_combine(b1, b2)
    m123, K = dempster_combine(m12, b3)
    metrics = extract_belief_metrics(m123)

    bel = metrics["bel_F"]
    ign = metrics["ignorance"]

    if K >= K_CONFLICT_THRESHOLD:
        sub = "HUMAN_ESCALATE"
    elif bel >= BEL_DECLINE_THRESHOLD and ign <= IGN_DECLINE_MAX:
        sub = "AUTO_DECLINE"
    elif ign >= IGN_INSUFFICIENT:
        sub = "HUMAN_ESCALATE"
    elif bel >= BEL_STEP_UP_THRESHOLD:
        sub = "STEP_UP_AUTH"
    else:
        sub = "HUMAN_ESCALATE"

    metrics["conflict_K"] = K
    logger.debug(f"DS fusion: bel_F={bel:.3f} ign={ign:.3f} K={K:.3f} -> {sub}")
    return sub, metrics
