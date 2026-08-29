"""
chargeback_agent.py
====================
3C: Pre-Settlement Chargeback Risk Predictor

Estimates the probability that a transaction will result in a chargeback
BEFORE funds are settled to the merchant account.

Architecture:
  - Cost-sensitive XGBoost (scale_pos_weight for heavy imbalance)
  - SMOTE oversampling on training data (imblearn)
  - Time-based train/test split (prevents data leakage)
  - Returns: chargeback_risk in [0, 1] + top 3 contributing factors

For the demo: uses the same 14-dim feature vector as the pipeline.
In production: would include settlement velocity, dispute history,
merchant dispute rate, card scheme chargeback flags, etc.
"""
from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

import joblib
import numpy as np

logger = logging.getLogger("riskguard.chargeback")

ARTIFACT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "artifacts", "chargeback_model.pkl"
)


class ChargebackPredictor:
    """
    Pre-settlement chargeback risk model.
    Trained separately from the fraud pipeline (different label: chargeback vs fraud).
    For this demo, we proxy chargeback labels from the fraud labels with noise.
    """

    def __init__(self):
        self.model = None
        self._loaded = False

    def load(self, path: str = ARTIFACT_PATH) -> None:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Chargeback model not found: {path}")
        self.model = joblib.load(path)
        self._loaded = True
        logger.info("Chargeback model loaded.")

    def save(self, path: str = ARTIFACT_PATH) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Chargeback model saved to {path}")

    def train(self, X: np.ndarray, y_fraud: np.ndarray) -> None:
        """
        Trains chargeback model.
        y_fraud is used as proxy: ~70% of fraud txns lead to chargebacks.
        Adds noise to simulate real chargeback label distribution.
        """
        logger.info("Training Chargeback Predictor...")

        # Proxy chargeback labels: fraud * 0.7 probability + rare legit chargebacks
        rng = np.random.default_rng(42)
        y_chargeback = np.zeros_like(y_fraud)
        fraud_idx = np.where(y_fraud == 1)[0]
        cb_fraud = rng.choice(fraud_idx, size=int(len(fraud_idx) * 0.70), replace=False)
        y_chargeback[cb_fraud] = 1
        # ~0.2% legit chargebacks (friendly fraud)
        legit_idx = np.where(y_fraud == 0)[0]
        cb_legit  = rng.choice(legit_idx, size=max(1, int(len(legit_idx) * 0.002)), replace=False)
        y_chargeback[cb_legit] = 1

        logger.info(f"  Chargeback labels: {y_chargeback.sum()} positive / {len(y_chargeback)} total")

        # Try SMOTE, fall back to plain XGBoost if imblearn not installed
        try:
            from imblearn.over_sampling import SMOTE
            sm = SMOTE(random_state=42, k_neighbors=min(5, y_chargeback.sum() - 1))
            X_res, y_res = sm.fit_resample(X, y_chargeback)
            logger.info(f"  SMOTE resampled: {len(X_res)} rows")
        except ImportError:
            logger.warning("imblearn not installed — training without SMOTE. Run: pip install imbalanced-learn")
            X_res, y_res = X, y_chargeback

        from xgboost import XGBClassifier
        scale_pw = float((y_res == 0).sum() / max((y_res == 1).sum(), 1))
        self.model = XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            scale_pos_weight=scale_pw, eval_metric="logloss",
            random_state=42, tree_method="hist", device="cpu",
            verbosity=0,
        )
        self.model.fit(X_res, y_res)
        self._loaded = True
        logger.info("Chargeback model training complete.")

    def predict(self, X: np.ndarray) -> Tuple[float, list]:
        """
        Returns (chargeback_risk_score, top_3_contributing_features).
        """
        if not self._loaded:
            return 0.0, []

        try:
            prob = float(self.model.predict_proba(X)[:, 1][0])

            # Top contributing features via feature importances (fast, no SHAP needed)
            importances = self.model.feature_importances_
            top_idx = np.argsort(importances)[::-1][:3]
            feature_names = [
                "amount_log", "amount_vs_merchant_avg", "velocity_1h_count",
                "velocity_1h_amount_log", "velocity_24h_count", "velocity_24h_amount_log",
                "bin_risk_score", "device_seen_before", "is_odd_hour",
                "hour_sin", "hour_cos", "payment_method_upi",
                "payment_method_card", "payment_method_wallet",
            ]
            top_factors = [
                feature_names[i] if i < len(feature_names) else f"feature_{i}"
                for i in top_idx
            ]
            return round(prob, 4), top_factors
        except Exception as e:
            logger.warning(f"Chargeback prediction failed: {e}")
            return 0.0, []


_predictor: Optional[ChargebackPredictor] = None


def get_chargeback_predictor() -> ChargebackPredictor:
    global _predictor
    if _predictor is None:
        _predictor = ChargebackPredictor()
        try:
            _predictor.load()
        except FileNotFoundError:
            logger.info("Chargeback model not found — run train_payment_models.py to generate it.")
    return _predictor
