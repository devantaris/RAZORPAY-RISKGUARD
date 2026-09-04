"""
v2_svm_v3.py
=============
V3's dedicated Calibrated SVM — third evidence source for Dempster-Shafer fusion.

This is a separate model from V2 (different cv=3 vs cv=5, to prevent data leakage
across the belief sources). Trained on the same payment data, used only within V3
as BPA Source 3.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

logger = logging.getLogger("riskguard.v3_svm")


class V3SVM:
    def __init__(self):
        self.svm: Optional[CalibratedClassifierCV] = None
        self.scaler: Optional[StandardScaler] = None
        self._loaded = False

    def load(self, artifact_dir: str) -> None:
        svm_path = os.path.join(artifact_dir, "v3_svm.pkl")
        scaler_path = os.path.join(artifact_dir, "v3_scaler.pkl")
        if not os.path.exists(svm_path):
            raise FileNotFoundError(f"V3 SVM not found: {svm_path}")
        self.svm = joblib.load(svm_path)
        self.scaler = joblib.load(scaler_path)
        self._loaded = True
        logger.info("V3 SVM loaded.")

    def save(self, artifact_dir: str) -> None:
        os.makedirs(artifact_dir, exist_ok=True)
        joblib.dump(self.svm, os.path.join(artifact_dir, "v3_svm.pkl"))
        joblib.dump(self.scaler, os.path.join(artifact_dir, "v3_scaler.pkl"))
        logger.info(f"V3 SVM saved to {artifact_dir}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        logger.info("Training V3 SVM: Calibrated LinearSVC (sigmoid, cv=3)...")
        self.scaler = StandardScaler()
        X_sc = self.scaler.fit_transform(X_train)
        base = LinearSVC(
            C=1.0, class_weight="balanced", max_iter=5000, random_state=42, dual="auto"
        )
        self.svm = CalibratedClassifierCV(base, method="sigmoid", cv=3)
        self.svm.fit(X_sc, y_train)
        self._loaded = True
        logger.info("V3 SVM training complete.")

    def predict_proba(self, X: np.ndarray) -> float:
        if not self._loaded:
            raise RuntimeError("V3 SVM not loaded.")
        X_sc = self.scaler.transform(X)
        return float(self.svm.predict_proba(X_sc)[:, 1][0])
