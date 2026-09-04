"""Train the chargeback model and append it to artifacts."""

import sys, os, math, warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score

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


print("[Chargeback] Loading data...")
df = pd.read_csv(DATA_PATH)
X = build_features(df)
y = df["is_fraud"].values.astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

from app.agents.chargeback_agent import ChargebackPredictor

cb = ChargebackPredictor()
cb.train(X_train, y_train)
cb.save(os.path.join(ARTIFACT_DIR, "chargeback_model.pkl"))

# Quick eval on test set (chargeback proxy labels)
rng = np.random.default_rng(42)
y_cb = np.zeros_like(y_test)
fi = np.where(y_test == 1)[0]
if len(fi) > 0:
    y_cb[rng.choice(fi, size=int(len(fi) * 0.70), replace=False)] = 1
li = np.where(y_test == 0)[0]
y_cb[rng.choice(li, size=max(1, int(len(li) * 0.002)), replace=False)] = 1

scores = [cb.predict(X_test[i : i + 1])[0] for i in range(len(X_test))]
scores = np.array(scores)

auc = roc_auc_score(y_cb, scores)
ap = average_precision_score(y_cb, scores)
print(f"[Chargeback] ROC-AUC: {auc:.4f}  |  Avg Precision: {ap:.4f}")
print(f"[Chargeback] Chargeback labels in test: {y_cb.sum()} / {len(y_cb)}")
print("[Chargeback] Model saved to artifacts/chargeback_model.pkl")
