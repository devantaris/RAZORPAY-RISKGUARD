"""
train_payment_models.py
========================
Trains all V1-V4 pipeline models on the synthetic Indian payment transaction data.

Steps:
  1. Load backend/data/synthetic_transactions.csv
  2. Engineer features (same pipeline as features.py but offline)
  3. Train V1: XGBoost Ensemble + Isolation Forest
  4. Train V2: Calibrated SVM (ABSTAIN second opinion)
  5. Train V3 SVM: Calibrated SVM (DS BPA Source 3)
  6. Train V4: Raw XGBClassifier for SHAP TreeExplainer
  7. Validate: 100% DECLINE precision gate (zero false blocks)
  8. Save all artifacts to backend/artifacts/

Run from project root:
  python backend/scripts/train_payment_models.py
"""

from __future__ import annotations

import os
import sys
import math
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, roc_auc_score

ARTIFACT_DIR = os.path.join(BACKEND_DIR, "artifacts")
DATA_PATH = os.path.join(BACKEND_DIR, "data", "synthetic_transactions.csv")

os.makedirs(ARTIFACT_DIR, exist_ok=True)

print("=" * 65)
print("  Razorpay RiskGuard — Payment Model Training")
print("=" * 65)

# ── 1. Load & feature-engineer ────────────────────────────────────────────────
print("\n[1] Loading synthetic_transactions.csv ...")
df = pd.read_csv(DATA_PATH)
print(
    f"    Rows: {len(df):,} | Fraud: {df['is_fraud'].sum():,} ({df['is_fraud'].mean() * 100:.1f}%)"
)


def build_features(df: pd.DataFrame) -> np.ndarray:
    """Offline version of features.py — produces same 14-dim vector."""
    X = pd.DataFrame()
    X["amount_log"] = np.log1p(df["amount"])
    X["amount_vs_merchant_avg"] = np.clip(df["amount_vs_merchant_avg"], 0, 20)
    X["velocity_1h_count"] = df["velocity_1h_count"]
    X["velocity_1h_amount_log"] = np.log1p(df["velocity_1h_amount"])
    X["velocity_24h_count"] = df["velocity_24h_count"]
    X["velocity_24h_amount_log"] = np.log1p(df["velocity_24h_amount"])
    # BIN risk: 1 if high-risk bin prefixes, else 0
    HIGH_RISK = {"400066", "404756", "410057", "438935", "461046"}
    X["bin_risk_score"] = df["card_bin"].apply(
        lambda b: 1.0 if str(b) in HIGH_RISK else 0.0
    )
    X["device_seen_before"] = df["device_seen_before"].astype(float)
    X["is_odd_hour"] = df["is_odd_hour"].astype(float)
    X["hour_sin"] = np.sin(2 * math.pi * df["hour_of_day"] / 24)
    X["hour_cos"] = np.cos(2 * math.pi * df["hour_of_day"] / 24)
    X["payment_method_upi"] = (df["payment_method"] == "UPI").astype(float)
    X["payment_method_card"] = (df["payment_method"] == "CARD").astype(float)
    X["payment_method_wallet"] = (df["payment_method"] == "WALLET").astype(float)
    return X.values.astype(np.float32)


X = build_features(df)
y = df["is_fraud"].values.astype(int)
print(f"    Feature matrix: {X.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"    Train: {len(X_train):,} | Test: {len(X_test):,}")
print(f"    Test fraud: {y_test.sum()} | Test legit: {(y_test == 0).sum()}")

# ── 2. V1: XGBoost Ensemble + Isolation Forest ─────────────────────────────────
print("\n[2] Training V1: XGBoost Ensemble + Isolation Forest ...")
from app.pipeline.v1_ensemble import V1Ensemble

v1 = V1Ensemble()
v1.train(X_train, y_train)
v1.save(ARTIFACT_DIR)

# V1 predictions on test set
mean_probs, std_probs, iso_scores = [], [], []
for i in range(len(X_test)):
    mp, sp, iso = v1.predict(X_test[i : i + 1])
    mean_probs.append(mp)
    std_probs.append(sp)
    iso_scores.append(iso)

mean_probs = np.array(mean_probs)
std_probs = np.array(std_probs)
iso_scores = np.array(iso_scores)

v1_decisions = [
    v1.decide(mp, sp, iso) for mp, sp, iso in zip(mean_probs, std_probs, iso_scores)
]
from collections import Counter

dist = Counter(v1_decisions)
print(f"    V1 distribution: {dict(dist)}")

# ── 3. V2: Calibrated SVM (ABSTAIN second opinion) ───────────────────────────
print("\n[3] Training V2: Calibrated SVM ...")
from app.pipeline.v2_svm import V2SVM

v2 = V2SVM()
v2.train(X_train, y_train)
v2.save(ARTIFACT_DIR)

# ── 4. V3 SVM: DS BPA Source 3 ────────────────────────────────────────────────
print("\n[4] Training V3 SVM: DS BPA Source 3 ...")
from app.pipeline.v2_svm_v3 import V3SVM

v3_svm = V3SVM()
v3_svm.train(X_train, y_train)
v3_svm.save(ARTIFACT_DIR)

# ── 5. V4: SHAP model ─────────────────────────────────────────────────────────
print("\n[5] Training V4: SHAP XGBClassifier ...")
from app.pipeline.v4_shap_deferral import V4ShapDeferral

v4 = V4ShapDeferral()
v4.train(X_train, y_train)
v4.save(ARTIFACT_DIR)

# ── 6. Full pipeline simulation on test set ────────────────────────────────────
print("\n[6] Running full V1->V2->V3->V4 simulation on test set ...")
from app.pipeline.v3_dempster_shafer import fuse_and_route

final_decisions = []

for i in range(len(X_test)):
    X_i = X_test[i : i + 1]
    mp = float(mean_probs[i])
    sp = float(std_probs[i])
    iso = float(iso_scores[i])
    d = v1_decisions[i]

    # V2
    if d == "ABSTAIN":
        d2, _ = v2.decide(X_i)
        d = d2

    # V3
    if v1_decisions[i] == "ESCALATE":
        svm_p = v3_svm.predict_proba(X_i)
        sub, _ = fuse_and_route(mean_prob=mp, std=sp, iso_score=iso, svm_prob=svm_p)
        if sub == "AUTO_DECLINE":
            d = "DECLINE"
        elif sub == "STEP_UP_AUTH":
            d = "STEP_UP"
        else:
            d = "PEND"
    elif d == "ABSTAIN":
        d = "PEND"

    # V4 collapse
    if d not in ("APPROVE", "DECLINE", "STEP_UP", "PEND"):
        d = "PEND"

    final_decisions.append(d)

final_decisions = np.array(final_decisions)

# ── 7. Metrics & Precision Gate ────────────────────────────────────────────────
print("\n[7] Evaluation Metrics:")
print("-" * 50)

for state in ["APPROVE", "DECLINE", "STEP_UP", "PEND"]:
    mask = final_decisions == state
    n = mask.sum()
    nf = int((mask & (y_test == 1)).sum())
    nl = n - nf
    print(f"    {state:<10}: {n:>5,}  (fraud={nf:>3}, legit={nl:>5,})")

# The key guarantee
decline_mask = final_decisions == "DECLINE"
false_declines = int((decline_mask & (y_test == 0)).sum())
true_declines = int((decline_mask & (y_test == 1)).sum())
total_fraud = int(y_test.sum())
flagged_fraud = int(((final_decisions != "APPROVE") & (y_test == 1)).sum())

print()
print(f"    {'-' * 45}")
print(f"    DECLINE precision (0 false blocks): ", end="")
if false_declines == 0:
    print(f"✅  100% ({true_declines}/{true_declines})")
else:
    print(
        f"⚠️  {true_declines / (true_declines + false_declines) * 100:.1f}%  ({false_declines} false blocks!)"
    )

recall_auto = true_declines / total_fraud if total_fraud > 0 else 0
recall_any = flagged_fraud / total_fraud if total_fraud > 0 else 0
auc = roc_auc_score(y_test, mean_probs)

print(
    f"    Fraud recall (auto-DECLINE):        {recall_auto * 100:.1f}%  ({true_declines}/{total_fraud})"
)
print(
    f"    Fraud recall (any non-APPROVE):     {recall_any * 100:.1f}%  ({flagged_fraud}/{total_fraud})"
)
print(f"    XGBoost Ensemble ROC-AUC:           {auc:.4f}")
print(f"    False blocks on legit:              {false_declines}")
print(f"    {'-' * 45}")
print()

if false_declines > 0:
    print("⚠️  WARNING: DECLINE precision < 100%. Check threshold tuning.")
else:
    print("✅ PIPELINE TRAINED SUCCESSFULLY")
    print(f"   Artifacts saved to: {ARTIFACT_DIR}")
    print()
    print("   Next: Start the API server and test:")
    print("   cd backend && uvicorn app.main:app --reload")
