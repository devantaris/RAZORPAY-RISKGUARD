"""
orchestrator.py
================
Master V1 -> V2 -> V3 -> V4 + Agentic AI Layer

Flow:
  [AssessRequest]
       |
  [FeatureExtractor]  (14 payment features, Redis velocity)
       |
  [V1: XGBoost + IsoForest]
       +-- APPROVE/DECLINE/STEP_UP  ──────────────> terminal
       +-- ABSTAIN  ──> [V2: Calibrated SVM] ──────> APPROVE or PEND
       +-- ESCALATE ──> [V3: Dempster-Shafer] ──────> DECLINE/STEP_UP or PEND
                                 |
                           [V4: SHAP Deferral]  (for PEND)
       |
  [3A: Explanation Agent]   (LLM natural language, Redis cached)
  [3B: Threshold Bandit]    (merchant-specific effective threshold)
  [3C: Chargeback Predictor](pre-settlement risk score)
       |
  [AssessResponse]
"""

from __future__ import annotations

import asyncio
import logging
import os
from functools import lru_cache
from typing import Optional

import numpy as np

logger = logging.getLogger("riskguard.orchestrator")

ARTIFACT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")
)


class PipelineOrchestrator:
    def __init__(self, artifact_dir: str = ARTIFACT_DIR):
        self.artifact_dir = artifact_dir
        self._loaded = False
        self._v1 = None
        self._v2 = None
        self._v3_svm = None
        self._v4 = None
        self._feat = None
        # Agentic layer
        self._explanation_agent = None
        self._threshold_bandit = None
        self._chargeback_predictor = None

    # ── Loading ──────────────────────────────────────────────────────────────

    def load(self) -> None:
        if self._loaded:
            return

        from app.pipeline.v1_ensemble import V1Ensemble
        from app.pipeline.v2_svm import V2SVM
        from app.pipeline.v2_svm_v3 import V3SVM
        from app.pipeline.v4_shap_deferral import V4ShapDeferral
        from app.pipeline.features import FeatureExtractor
        from app.agents.explanation_agent import ExplanationAgent
        from app.agents.threshold_bandit import ThresholdBandit
        from app.agents.chargeback_agent import ChargebackPredictor

        logger.info(f"Loading pipeline from: {self.artifact_dir}")

        self._v1 = V1Ensemble()
        self._v1.load(self.artifact_dir)
        self._v2 = V2SVM()
        self._v2.load(self.artifact_dir)
        self._v3_svm = V3SVM()
        self._v3_svm.load(self.artifact_dir)
        self._v4 = V4ShapDeferral()
        self._v4.load(self.artifact_dir)
        self._feat = FeatureExtractor(redis_client=None)

        # Agents (no Redis in skeleton — will wire in Phase 4 with actual Redis)
        self._explanation_agent = ExplanationAgent(redis_client=None)
        self._threshold_bandit = ThresholdBandit(redis_client=None)
        self._chargeback_predictor = ChargebackPredictor()
        try:
            self._chargeback_predictor.load(
                os.path.join(self.artifact_dir, "chargeback_model.pkl")
            )
        except FileNotFoundError:
            logger.warning("Chargeback model not found — chargeback_risk will be null.")

        self._loaded = True
        logger.info(
            "Pipeline + Agents fully loaded (V1+V2+V3+V4 + ExplainAgent + Bandit + Chargeback)."
        )

    def status(self) -> str:
        return "ready" if self._loaded else "skeleton_phase1"

    # ── Full Evaluation ───────────────────────────────────────────────────────

    async def evaluate(self, req) -> "AssessResponse":
        from app.models.transaction import (
            AssessResponse,
            Decision,
            RiskReport,
            ShapFeature,
        )

        if not self._loaded:
            try:
                self.load()
            except FileNotFoundError:
                return self._mock_response(req)

        # ── Feature extraction ────────────────────────────────────────────────
        X = await self._feat.extract(req)

        # ── Stage V1 ─────────────────────────────────────────────────────────
        mean_prob, std_prob, iso_score = self._v1.predict(X)

        # ── Bandit: get merchant-specific effective threshold ─────────────────
        effective_threshold = await self._threshold_bandit.get_threshold(
            req.merchant_id
        )
        # Override V1 decline threshold dynamically
        from app.pipeline import v1_ensemble as v1_mod

        orig_threshold = v1_mod.DECLINE_THRESHOLD
        v1_mod.DECLINE_THRESHOLD = effective_threshold
        v1_decision = self._v1.decide(mean_prob, std_prob, iso_score)
        v1_mod.DECLINE_THRESHOLD = orig_threshold  # restore global

        # ── Stage V2 (ABSTAIN only) ───────────────────────────────────────────
        v2_decision = v1_decision
        if v1_decision == "ABSTAIN":
            v2_decision, _ = self._v2.decide(X)

        # ── Stage V3 (ESCALATE only) ──────────────────────────────────────────
        v3_sub = v2_decision
        ds_metrics = {}
        if v1_decision == "ESCALATE":
            svm_prob = self._v3_svm.predict_proba(X)
            from app.pipeline.v3_dempster_shafer import fuse_and_route

            v3_sub, ds_metrics = fuse_and_route(
                mean_prob=mean_prob,
                std=std_prob,
                iso_score=iso_score,
                svm_prob=svm_prob,
            )

        # ── Stage V4: collapse to 4 terminal states ───────────────────────────
        decision, stage, unc_type = self._collapse(
            v1_decision, v2_decision, v3_sub, ds_metrics
        )

        # ── V4 SHAP reason codes (PEND) / feature importance (all) ──────────
        shap_features_raw, reason_code = [], None
        if decision == Decision.PEND:
            unc_val = float(ds_metrics.get("ignorance", std_prob))
            shap_raw, reason_code = self._v4.explain(X, unc_type, unc_val)
            shap_features_raw = shap_raw
        else:
            # For non-PEND: get top features from model importances (fast, no SHAP needed)
            shap_raw, _ = self._v4.explain(X, unc_type or "NONE", 0.0)
            shap_features_raw = shap_raw

        # ── 3A: LLM Risk Explanation ──────────────────────────────────────────
        explanation = await self._explanation_agent.explain(
            decision=str(decision.value),
            shap_features=shap_features_raw,
            amount=float(req.amount),
            merchant_id=req.merchant_id,
            uncertainty_type=unc_type,
        )

        # ── 3C: Chargeback prediction (non-blocking) ──────────────────────────
        chargeback_risk = None
        try:
            cb_prob, _ = self._chargeback_predictor.predict(X)
            chargeback_risk = cb_prob if cb_prob > 0.01 else None
        except Exception:
            pass

        # ── 3B: Record bandit outcome (async, fire-and-forget) ────────────────
        confidence = float(np.clip(mean_prob, 0.0, 1.0))
        asyncio.ensure_future(
            self._threshold_bandit.record_outcome(
                req.merchant_id, str(decision.value), confidence
            )
        )

        return AssessResponse(
            transaction_id=req.transaction_id,
            decision=decision,
            confidence=round(confidence, 4),
            stage_reached=stage,
            risk_report=RiskReport(
                explanation=explanation,
                shap_top_features=[
                    ShapFeature(
                        feature=f["feature"],
                        impact=f["impact"],
                        direction=f["direction"],
                    )
                    for f in shap_features_raw
                ],
                merchant_threshold=round(effective_threshold, 3),
                chargeback_risk=round(chargeback_risk, 4) if chargeback_risk else None,
                uncertainty_type=unc_type if decision == Decision.PEND else None,
                pend_reason_code=reason_code,
            ),
            inference_ms=0.0,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _collapse(v1, v2, v3_sub, ds_metrics):
        from app.models.transaction import Decision

        if v1 == "DECLINE":
            return Decision.DECLINE, "V1", None
        if v1 == "APPROVE":
            return Decision.APPROVE, "V1", None
        if v1 == "STEP_UP":
            return Decision.STEP_UP, "V1", None
        if v1 == "ABSTAIN":
            if v2 == "APPROVE":
                return Decision.APPROVE, "V2", None
            return Decision.PEND, "V2", "MODEL_DISAGREEMENT"
        # ESCALATE path
        if v3_sub == "AUTO_DECLINE":
            return Decision.DECLINE, "V3", None
        if v3_sub == "STEP_UP_AUTH":
            return Decision.STEP_UP, "V3", None
        k = ds_metrics.get("conflict_K", 0.0)
        unc = "EVIDENCE_CONFLICT" if k >= 0.25 else "INSUFFICIENT_EVIDENCE"
        return Decision.PEND, "V4", unc

    def _mock_response(self, req):
        from app.models.transaction import AssessResponse, Decision, RiskReport

        return AssessResponse(
            transaction_id=req.transaction_id,
            decision=Decision.APPROVE,
            confidence=0.05,
            stage_reached="V1_MOCK",
            risk_report=RiskReport(
                explanation="Pipeline not loaded. Run train_payment_models.py first.",
                shap_top_features=[],
                merchant_threshold=0.80,
            ),
            inference_ms=0.0,
        )


@lru_cache(maxsize=1)
def get_orchestrator() -> PipelineOrchestrator:
    orch = PipelineOrchestrator()
    try:
        orch.load()
    except FileNotFoundError:
        logger.info("Models not found — running in skeleton mode.")
    return orch
