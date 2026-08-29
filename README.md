# Razorpay RiskGuard

> **AI Risk Manager** - Razorpay AI Builder Internship 2026, Track 2

Real-time payment fraud assessment using staged uncertainty + Dempster-Shafer belief fusion + agentic AI. Built on peer-reviewed research from *Knowing When Not to Decide* (IEEE TDSC).

## The Unfair Advantage

> **100% DECLINE precision. Zero false blocks on legitimate transactions.**

```
Fraud recall (any flag):  97.5%   (39/40 on held-out test)
Auto-DECLINE precision:   100%    (0 false blocks on legit txns)
Ensemble ROC-AUC:         0.9840
End-to-end latency:       ~96ms   (full agentic pipeline)
Chargeback ROC-AUC:       0.93
```

## Architecture

```
POST /v1/assess
      |
[Feature Extractor]  14-dim payment features (Redis velocity, BIN risk, amount ratios)
      |
[V1: XGBoost x5]     Bootstrap ensemble + isotonic calibration + Isolation Forest
      |
  APPROVE/DECLINE    ABSTAIN              ESCALATE
      |                 |                    |
     Done         [V2: Calib SVM]    [V3: Dempster-Shafer]
                  p<0.01 -> APPROVE   3 BPA sources fused
                  else   -> PEND      Bel>=0.91 -> DECLINE
                                      K>=0.25   -> PEND
                                      else      -> STEP_UP
                                          |
                                  [V4: SHAP Deferral]
                                  Reason codes
      |
[Explanation Agent]  LLM / rule-based natural language
[Threshold Bandit]   e-greedy per-merchant (epsilon=0.10, alpha=0.30)
[Chargeback Agent]   Pre-settlement risk score (SMOTE + XGBoost)
      |
  AssessResponse
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python scripts/seed_data.py
python scripts/train_payment_models.py
python scripts/train_chargeback_model.py
uvicorn app.main:app --reload
# -> http://localhost:8000/docs

# Frontend
cd frontend
cp .env.local.example .env.local
npm install && npm run dev
# -> http://localhost:3000
```

## API

```bash
curl -X POST http://localhost:8000/v1/assess \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"txn_001","merchant_id":"merch_001","amount":42999,"currency":"INR","card_bin":"438935","payment_method":"CARD"}'
```

Response: `decision` in `{APPROVE, DECLINE, STEP_UP, PEND}` + SHAP features + explanation + chargeback risk.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/assess | Single transaction assessment |
| POST | /v1/batch | Batch assessment |
| GET | /v1/health | Pipeline status |
| GET | /v1/stream | SSE live transaction feed |
| GET | /v1/merchants/{id}/threshold | Bandit diagnostics |
| POST | /v1/merchants/{id}/threshold | Manual threshold override |

## Research Lineage

```
mari_repo (prototype)
    -> Knowing-When-Not-to-Decide (IEEE TDSC research)
           -> RAZORPAY RISKGUARD (payment domain)
```

## Environment

Copy `backend/.env.example` to `backend/.env`. Key vars:
```env
LLM_PROVIDER=mock              # mock | openai | gemini
DEFAULT_DECLINE_THRESHOLD=0.80
BANDIT_EPSILON=0.10
```

## Tags

- `v0.1.0` Phase 1: FastAPI skeleton + Pydantic schemas + Docker
- `v0.2.0` Phase 2: Full V1->V4 staged pipeline, 100% DECLINE precision
- `v0.3.0` Phase 3: Agentic AI (Explanation + Bandit + Chargeback)
- `v0.4.0` Phase 4: Next.js Risk Ops Dashboard

---
*Razorpay AI Builder Internship 2026 - Track 2: AI Risk Manager*
