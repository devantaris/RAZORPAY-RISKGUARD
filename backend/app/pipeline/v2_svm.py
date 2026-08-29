"""
v2_svm.py
==========
V2: Calibrated SVM — Second Opinion on ABSTAIN cases

Only runs on transactions that V1 marked ABSTAIN
(low mean_prob but high ensemble disagreement).

If V2 P(fraud) < 0.01  -> clear to APPROVE  (cost-optimal threshold from research)
Otherwise              -> remain ABSTAIN    (collapses to PEND in V4)

Architecture: LinearSVC + CalibratedClassifierCV(method='sigmoid', cv=5)
This matches the v2_playground SVM in Knowing-When-Not-to-Decide exactly.
"""
from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

logger = logging.getLogger("riskguard.v2")

# Cost-optimal threshold from research (maximises net utility)
CLEAR_THRESHOLD = 0.01   # P(fraud) < 1% -> safe to approve


class V2SVM:
    """
    Calibrated Linear SVM second-opinion classifier.
    Scaler is stored alongside the model (trained on same data).
    """

    def __init__(self):
        self.svm:    Optional[CalibratedClassifierCV] = None
        self.scaler: Optional[StandardScaler] = None
        self._loaded = False

    def load(self, artifact_dir: str) -> None:
        svm_path    = os.path.join(artifact_dir, "v2_svm.pkl")
        scaler_path = os.path.join(artifact_dir, "v2_scaler.pkl")
        if not os.path.exists(svm_path):
            raise FileNotFoundError(f"V2 SVM not found: {svm_path}")
        self.svm    = joblib.load(svm_path)
        self.scaler = joblib.load(scaler_path)
        self._loaded = True
        logger.info("V2 SVM loaded.")

    def save(self, artifact_dir: str) -> None:
        os.makedirs(artifact_dir, exist_ok=True)
        joblib.dump(self.svm,    os.path.join(artifact_dir, "v2_svm.pkl"))
        joblib.dump(self.scaler, os.path.join(artifact_dir, "v2_scaler.pkl"))
        logger.info(f"V2 saved to {artifact_dir}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        logger.info("Training V2: Calibrated LinearSVC (sigmoid, cv=5)...")
        self.scaler = StandardScaler()
        X_sc = self.scaler.fit_transform(X_train)
        base_svm = LinearSVC(
            C=1.0, class_weight="balanced",
            max_iter=10000, random_state=42, dual="auto",
        )
        self.svm = CalibratedClassifierCV(base_svm, method="sigmoid", cv=5)
        self.svm.fit(X_sc, y_train)
        self._loaded = True
        logger.info("V2 training complete.")

    def predict_proba(self, X: np.ndarray) -> float:
        """Returns P(fraud) for a single sample."""
        if not self._loaded:
            raise RuntimeError("V2 not loaded.")
        X_sc = self.scaler.transform(X)
        return float(self.svm.predict_proba(X_sc)[:, 1][0])

    def decide(self, X: np.ndarray) -> Tuple[str, float]:
        """
        Returns (decision, p_fraud).
        decision: APPROVE if p_fraud < CLEAR_THRESHOLD, else ABSTAIN (stays pending).
        """
        p_fraud = self.predict_proba(X)
        decision = "APPROVE" if p_fraud < CLEAR_THRESHOLD else "ABSTAIN"
        logger.debug(f"V2: p_fraud={p_fraud:.4f} -> {decision}")
        return decision, p_fraud
