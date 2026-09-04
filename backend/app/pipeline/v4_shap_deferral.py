"""
v4_shap_deferral.py
====================
V4: SHAP Tree Explainer — generates PEND reason codes and risk report features.

For every transaction that reaches V4 (via PEND from ABSTAIN or HUMAN_ESCALATE),
this module:
  1. Runs SHAP TreeExplainer on the raw XGBoost model (no calibration wrapper)
  2. Extracts top-K feature attributions
  3. Builds a structured PEND reason code: PEND_feat1_feat2_feat3
  4. Returns ShapFeature list for the risk report

The SHAP model is a raw XGBClassifier (NOT calibrated) because
shap.TreeExplainer requires direct access to the tree structure.
It is trained in parallel with the V1 ensemble but saved separately.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional, Tuple

import joblib
import numpy as np
from xgboost import XGBClassifier

logger = logging.getLogger("riskguard.v4")

TOP_K = 3  # number of top SHAP features to report

# Payment feature names (must match features.py FEATURE_NAMES order)
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


class V4ShapDeferral:
    """
    SHAP-based reason code generator for PEND transactions.
    Requires a raw (uncalibrated) XGBClassifier trained on the same data.
    """

    def __init__(self):
        self.shap_model: Optional[XGBClassifier] = None
        self._explainer = None
        self._loaded = False

    def load(self, artifact_dir: str) -> None:
        model_path = os.path.join(artifact_dir, "v4_shap_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"V4 SHAP model not found: {model_path}")
        self.shap_model = joblib.load(model_path)
        self._init_explainer()
        self._loaded = True
        logger.info("V4 SHAP model loaded.")

    def save(self, artifact_dir: str) -> None:
        os.makedirs(artifact_dir, exist_ok=True)
        joblib.dump(self.shap_model, os.path.join(artifact_dir, "v4_shap_model.pkl"))
        logger.info(f"V4 SHAP model saved to {artifact_dir}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        logger.info("Training V4: Raw XGBClassifier for SHAP TreeExplainer...")
        scale_pos_weight = float((len(y_train) - y_train.sum()) / max(y_train.sum(), 1))
        self.shap_model = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=42,
            tree_method="hist",
            device="cpu",
            verbosity=0,
        )
        self.shap_model.fit(X_train, y_train)
        self._init_explainer()
        self._loaded = True
        logger.info("V4 SHAP model training complete.")

    def _init_explainer(self) -> None:
        try:
            import shap

            self._explainer = shap.TreeExplainer(self.shap_model)
            logger.info("SHAP TreeExplainer initialised.")
        except Exception as e:
            logger.warning(f"SHAP init failed: {e}. Reason codes will be unavailable.")
            self._explainer = None

    def explain(
        self,
        X: np.ndarray,
        uncertainty_type: str = "UNKNOWN",
        uncertainty_val: float = 0.0,
    ) -> Tuple[List[dict], str]:
        """
        Returns (shap_features_list, reason_code_string).

        shap_features_list: [{"feature": ..., "impact": ..., "direction": ...}, ...]
        reason_code: "PEND_feature1_feature2_feature3"
        """
        if not self._loaded or self._explainer is None:
            return self._fallback_explain(X, uncertainty_type)

        try:
            import shap

            sv = self._explainer.shap_values(X)[0]  # shape: (n_features,)
            top_idx = np.argsort(np.abs(sv))[::-1][:TOP_K]

            shap_features = []
            for rank, fi in enumerate(top_idx):
                fname = (
                    FEATURE_NAMES[fi] if fi < len(FEATURE_NAMES) else f"feature_{fi}"
                )
                sval = float(sv[fi])
                shap_features.append(
                    {
                        "feature": fname,
                        "impact": round(abs(sval), 4),
                        "direction": "elevates_fraud"
                        if sval > 0
                        else "suppresses_fraud",
                    }
                )

            reason_code = "PEND_" + "_".join(f["feature"] for f in shap_features)
            return shap_features, reason_code

        except Exception as e:
            logger.warning(f"SHAP explain failed: {e}")
            return self._fallback_explain(X, uncertainty_type)

    def _fallback_explain(
        self, X: np.ndarray, uncertainty_type: str
    ) -> Tuple[List[dict], str]:
        """Returns basic feature importance when SHAP is unavailable."""
        if self.shap_model is not None:
            try:
                scores = self.shap_model.feature_importances_
                top_idx = np.argsort(scores)[::-1][:TOP_K]
                shap_features = [
                    {
                        "feature": FEATURE_NAMES[fi]
                        if fi < len(FEATURE_NAMES)
                        else f"f{fi}",
                        "impact": round(float(scores[fi]), 4),
                        "direction": "elevates_fraud",
                    }
                    for fi in top_idx
                ]
                return shap_features, "PEND_" + "_".join(
                    f["feature"] for f in shap_features
                )
            except Exception:
                pass
        return (
            [{"feature": "unknown", "impact": 0.0, "direction": "unknown"}],
            f"PEND_{uncertainty_type}",
        )
