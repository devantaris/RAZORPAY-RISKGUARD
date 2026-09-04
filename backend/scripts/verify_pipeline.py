"""
verify_pipeline.py
===================
Loads all trained models and runs the full V1->V4 pipeline validation.
Prints metrics and confirms 100% DECLINE precision gate.
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings

warnings.filterwarnings("ignore")
import math
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from collections import Counter

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = os.path.join(BACKEND_DIR, "artifacts")
DATA_PATH = os.path.join(BACKEND_DIR, "data", "synthetic_transactions.csv")

HIGH_RISK_BINS = {"400066", "404756", "410057", "438935", "461046"}


def build_features(df):
    X = pd.DataFrame()
    X["amount_log"] = np.log1p(df["amount"])
    X["amount_vs_merchant_avg"] = np.clip(df["amount_vs_merchant_avg"], 0, 20)
    X["velocity_1h_count"] = df["velocity_1h_count"]
    X["velocity_1h_amount_log"] = np.log1p(df["velocity_1h_amount"])
    X["velocity_24h_count"] = df["velocity_24h_count"]
    X["velocity_24h_amount_log"] = np.log1p(df["velocity_24h_amount"])
    X["bin_risk_score"] = df["card_bin"].apply(
        lambda b: 1.0 if str(b) in HIGH_RISK_BINS else 0.0
    )
    X["device_seen_before"] = df["device_seen_before"].astype(float)
    X["is_odd_hour"] = df["is_odd_hour"].astype(float)
    X["hour_sin"] = np.sin(2 * math.pi * df["hour_of_day"] / 24)
    X["hour_cos"] = np.cos(2 * math.pi * df["hour_of_day"] / 24)
    X["payment_method_upi"] = (df["payment_method"] == "UPI").astype(float)
    X["payment_method_card"] = (df["payment_method"] == "CARD").astype(float)
    X["payment_method_wallet"] = (df["payment_method"] == "WALLET").astype(float)
    return X.values.astype(np.float32)


print("Loading data...")
df = pd.read_csv(DATA_PATH)
X = build_features(df)
y = df["is_fraud"].values.astype(int)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print("Loading models from artifacts/...")
from app.pipeline.v1_ensemble import V1Ensemble
from app.pipeline.v2_svm import V2SVM
from app.pipeline.v2_svm_v3 import V3SVM
from app.pipeline.v4_shap_deferral import V4ShapDeferral
from app.pipeline.v3_dempster_shafer import fuse_and_route

v1 = V1Ensemble()
v1.load(ARTIFACT_DIR)
v2 = V2SVM()
v2.load(ARTIFACT_DIR)
v3_svm = V3SVM()
v3_svm.load(ARTIFACT_DIR)
v4 = V4ShapDeferral()
v4.load(ARTIFACT_DIR)

print("Running V1->V2->V3->V4 on test set...")
mean_probs, std_probs, iso_scores, v1_decs = [], [], [], []
for i in range(len(X_test)):
    mp, sp, iso = v1.predict(X_test[i : i + 1])
    mean_probs.append(mp)
    std_probs.append(sp)
    iso_scores.append(iso)
    v1_decs.append(v1.decide(mp, sp, iso))

final = []
for i in range(len(X_test)):
    Xi = X_test[i : i + 1]
    d = v1_decs[i]
    mp, sp, iso = mean_probs[i], std_probs[i], iso_scores[i]

    if d == "ABSTAIN":
        d2, _ = v2.decide(Xi)
        d = d2

    if v1_decs[i] == "ESCALATE":
        sp3 = v3_svm.predict_proba(Xi)
        sub, _ = fuse_and_route(mean_prob=mp, std=sp, iso_score=iso, svm_prob=sp3)
        d = {"AUTO_DECLINE": "DECLINE", "STEP_UP_AUTH": "STEP_UP"}.get(sub, "PEND")
    elif d == "ABSTAIN":
        d = "PEND"
    if d not in ("APPROVE", "DECLINE", "STEP_UP", "PEND"):
        d = "PEND"
    final.append(d)

final = np.array(final)

# Metrics
print()
print("=" * 55)
print("  RAZORPAY RISKGUARD  |  V1->V4 Pipeline Results")
print("=" * 55)
for state in ["APPROVE", "DECLINE", "STEP_UP", "PEND"]:
    mask = final == state
    n, nf, nl = (
        mask.sum(),
        int((mask & (y_test == 1)).sum()),
        int((mask & (y_test == 0)).sum()),
    )
    print(f"  {state:<10}: {n:>5,}  (fraud={nf:>3}, legit={nl:>5,})")

decline_mask = final == "DECLINE"
false_blocks = int((decline_mask & (y_test == 0)).sum())
true_declines = int((decline_mask & (y_test == 1)).sum())
total_fraud = int(y_test.sum())
flagged = int(((final != "APPROVE") & (y_test == 1)).sum())
auc = roc_auc_score(y_test, mean_probs)

print()
print("  CORE METRICS")
print(
    f"  DECLINE Precision : {('100% [PASS]' if false_blocks == 0 else str(round(true_declines / (true_declines + false_blocks + 1e-9) * 100, 1)) + '% [FAIL]')}"
)
print(f"  False Blocks      : {false_blocks}  (must be 0)")
print(
    f"  Recall (DECLINE)  : {true_declines}/{total_fraud} = {true_declines / max(total_fraud, 1) * 100:.1f}%"
)
print(
    f"  Recall (any flag) : {flagged}/{total_fraud} = {flagged / max(total_fraud, 1) * 100:.1f}%"
)
print(f"  Ensemble ROC-AUC  : {auc:.4f}")
print("=" * 55)

# SHAP demo on first PEND
pend_idx = np.where(final == "PEND")[0]
if len(pend_idx) > 0:
    i = pend_idx[0]
    feats, code = v4.explain(X_test[i : i + 1], "MODEL_DISAGREEMENT")
    print("\n  SHAP Demo (first PEND transaction):")
    for f in feats:
        print(f"    {f['feature']:<30} impact={f['impact']:.4f}  [{f['direction']}]")
    print(f"  Reason code: {code}")

print()
print("  Pipeline verification complete.")
