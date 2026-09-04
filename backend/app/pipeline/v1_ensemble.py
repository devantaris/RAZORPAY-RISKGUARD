"""
v1_ensemble.py
==============
V1: Bootstrap XGBoost Ensemble + Isolation Forest Novelty Detector

Ported from Knowing-When-Not-to-Decide, adapted for payment feature space.
- 5 Calibrated XGBoost models (isotonic, bootstrap resampling)
- Isolation Forest for novelty detection (patterns never seen before)
- Returns: mean_prob, std_prob, iso_score, v1_decision

V1 Decision Rules (from research, adapted for payments):
  DECLINE   : mean_prob >= 0.80  AND std < 0.02   (high confidence fraud)
  ESCALATE  : mean_prob >= 0.60  AND std >= 0.02  (risky but uncertain -> V3)
  ESCALATE  : novelty_flag == True                (unknown pattern)
  STEP_UP   : 0.30 <= mean_prob < 0.80            (medium risk)
  ABSTAIN   : mean_prob < 0.30   AND std >= 0.02  (low risk but uncertain -> V2)
  APPROVE   : mean_prob < 0.30   AND std < 0.02   (clear legit)
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional, Tuple

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier

logger = logging.getLogger("riskguard.v1")

# Thresholds (matched to research repo decision_engine.py)
DECLINE_THRESHOLD = 0.80
ESCALATE_THRESHOLD = 0.60
AUTH_THRESHOLD = 0.30
UNCERTAINTY_THRESH = 0.02
ANOMALY_THRESHOLD = -0.08


class V1Ensemble:
    """
    Bootstrap XGBoost Ensemble (5 models, isotonic calibration)
    + Isolation Forest for novelty detection.
    """

    def __init__(self):
        self.ensemble: Optional[List] = None
        self.iso_forest: Optional[IsolationForest] = None
        self._loaded = False

    # ── Model loading / saving ──────────────────────────────────────────────

    def load(self, artifact_dir: str) -> None:
        ens_path = os.path.join(artifact_dir, "v1_xgb_ensemble.pkl")
        iso_path = os.path.join(artifact_dir, "v1_iso_forest.pkl")
        if not os.path.exists(ens_path):
            raise FileNotFoundError(f"V1 ensemble not found: {ens_path}")
        self.ensemble = joblib.load(ens_path)
        self.iso_forest = joblib.load(iso_path) if os.path.exists(iso_path) else None
        self._loaded = True
        logger.info(
            f"V1 loaded: ensemble={len(self.ensemble)} models, "
            f"iso={'yes' if self.iso_forest else 'no'}"
        )

    def save(self, artifact_dir: str) -> None:
        os.makedirs(artifact_dir, exist_ok=True)
        joblib.dump(self.ensemble, os.path.join(artifact_dir, "v1_xgb_ensemble.pkl"))
        if self.iso_forest:
            joblib.dump(
                self.iso_forest, os.path.join(artifact_dir, "v1_iso_forest.pkl")
            )
        logger.info(f"V1 saved to {artifact_dir}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train 5-model bootstrap XGBoost ensemble + Isolation Forest.
        """
        logger.info("Training V1: XGBoost Bootstrap Ensemble (5 models, isotonic)...")
        n_models = 5
        scale_pos_weight = float((len(y_train) - y_train.sum()) / max(y_train.sum(), 1))
        logger.info(
            f"  scale_pos_weight={scale_pos_weight:.1f} | "
            f"fraud={int(y_train.sum())} legit={int((y_train == 0).sum())}"
        )

        ensemble = []
        for seed in range(n_models):
            np.random.seed(seed)
            idx = np.random.choice(len(X_train), len(X_train), replace=True)
            X_b, y_b = X_train[idx], y_train[idx]
            base = XGBClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=seed,
                tree_method="hist",
                device="cpu",
                verbosity=0,
            )
            model = CalibratedClassifierCV(base, method="isotonic", cv=3)
            model.fit(X_b, y_b)
            ensemble.append(model)
            logger.info(f"  Model {seed + 1}/5 trained.")

        logger.info("Training Isolation Forest (contamination=0.02)...")
        iso = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
        iso.fit(X_train)

        self.ensemble = ensemble
        self.iso_forest = iso
        self._loaded = True
        logger.info("V1 training complete.")

    # ── Inference ────────────────────────────────────────────────────────────

    def predict(self, X: np.ndarray) -> Tuple[float, float, float]:
        """
        Returns (mean_prob, std_prob, iso_score) for a single sample.
        X shape: (1, n_features)
        """
        if not self._loaded:
            raise RuntimeError("V1 not loaded. Call train() or load() first.")

        probs = np.array([m.predict_proba(X)[:, 1][0] for m in self.ensemble])
        mean_prob = float(probs.mean())
        std_prob = float(probs.std())

        iso_score = (
            float(self.iso_forest.decision_function(X)[0]) if self.iso_forest else 0.0
        )

        return mean_prob, std_prob, iso_score

    def decide(self, mean_prob: float, std_prob: float, iso_score: float) -> str:
        """
        5-state V1 routing logic — exact match to research repo.
        Returns: APPROVE | DECLINE | ESCALATE | STEP_UP | ABSTAIN
        """
        novelty = iso_score < ANOMALY_THRESHOLD

        if mean_prob >= DECLINE_THRESHOLD and std_prob < UNCERTAINTY_THRESH:
            return "DECLINE"
        if mean_prob >= ESCALATE_THRESHOLD and std_prob >= UNCERTAINTY_THRESH:
            return "ESCALATE"
        if novelty:
            return "ESCALATE"
        if mean_prob >= AUTH_THRESHOLD:
            return "STEP_UP"
        if std_prob >= UNCERTAINTY_THRESH:
            return "ABSTAIN"
        return "APPROVE"
