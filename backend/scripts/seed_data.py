"""
seed_data.py
=============
Generates 10,000 realistic synthetic Indian payment transactions
with ~2% skewed fraud labels. Outputs to:
  - backend/data/synthetic_transactions.csv
  - Optionally inserts into Postgres (if DB_URL env is set)

Indian payment flavour:
  - UPI VPAs (bank handles)
  - Realistic card BINs (Visa/MC/Amex/Rupay)
  - Merchant categories (e-commerce, food, travel, petrol, etc.)
  - INR amount distributions per category
  - Device fingerprinting
  - Velocity-injected fraud patterns
"""
from __future__ import annotations

import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from faker import Faker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────

N_TRANSACTIONS = 10_000
FRAUD_RATE      = 0.02          # 2% fraud

MERCHANT_CATEGORIES = {
    "ecommerce":   {"min": 299,   "max": 49999,  "avg": 2500,  "fraud_mult": 1.0},
    "food":        {"min": 80,    "max": 3500,   "avg": 350,   "fraud_mult": 0.4},
    "travel":      {"min": 800,   "max": 120000, "avg": 8500,  "fraud_mult": 1.8},
    "petrol":      {"min": 200,   "max": 5000,   "avg": 1200,  "fraud_mult": 0.6},
    "electronics": {"min": 1999,  "max": 200000, "avg": 18000, "fraud_mult": 2.5},
    "pharmacy":    {"min": 50,    "max": 2500,   "avg": 450,   "fraud_mult": 0.3},
    "gaming":      {"min": 99,    "max": 12000,  "avg": 800,   "fraud_mult": 2.0},
    "jewelry":     {"min": 5000,  "max": 500000, "avg": 35000, "fraud_mult": 3.0},
}

CARD_BINS = {
    "visa_in":     ["411111", "427622", "453978", "461046", "476173"],
    "mastercard":  ["510810", "521234", "532101", "543210", "554321"],
    "rupay":       ["607080", "608000", "608001", "609000", "609001"],
    "amex":        ["340000", "370000", "371449", "378282"],
    # High-risk BINs (prepaid/gift card)
    "high_risk":   ["400066", "404756", "410057", "438935", "461046"],
}

HIGH_RISK_COUNTRIES = ["NG", "KP", "IR", "PK", "BD"]
NORMAL_COUNTRIES    = ["IN", "IN", "IN", "IN", "IN", "IN", "IN", "IN", "IN", "US", "GB", "AE"]

UPI_SUFFIXES = ["@oksbi", "@okaxis", "@okhdfcbank", "@okicici", "@ybl", "@upi",
                "@paytm", "@gpay", "@ibl", "@paytmbank"]

PAYMENT_METHODS = ["CARD", "CARD", "CARD", "UPI", "UPI", "WALLET", "NETBANKING"]

MERCHANT_IDS = [f"merch_{cat}_{i:03d}" for cat, _ in MERCHANT_CATEGORIES.items() for i in range(10)]
DEVICE_POOL  = [f"dev_{fake.lexify('??????????').lower()}" for _ in range(3000)]
IP_POOL      = [fake.ipv4() for _ in range(500)]


# ── Helper functions ─────────────────────────────────────────────────────────

def pick_card_bin(is_fraud: bool) -> tuple[str, str]:
    if is_fraud and random.random() < 0.55:
        network = "high_risk"
    else:
        network = random.choice(["visa_in", "mastercard", "rupay", "visa_in", "mastercard"])
    bins = CARD_BINS[network]
    return random.choice(bins), network


def pick_bin_country(is_fraud: bool, network: str) -> str:
    if is_fraud and random.random() < 0.45:
        return random.choice(HIGH_RISK_COUNTRIES)
    return random.choice(NORMAL_COUNTRIES)


def generate_amount(category: str, is_fraud: bool) -> float:
    cfg = MERCHANT_CATEGORIES[category]
    if is_fraud:
        # Fraud amounts are often outliers — inject 4-6x normal
        multiplier = random.uniform(3.5, 6.5)
        amount = cfg["avg"] * multiplier
    else:
        # Log-normal centered around avg
        sigma = 0.8
        mu    = np.log(cfg["avg"])
        amount = np.exp(np.random.normal(mu, sigma))
    return round(float(np.clip(amount, cfg["min"], cfg["max"])), 2)


def generate_velocity(is_fraud: bool) -> dict:
    if is_fraud and random.random() < 0.60:
        # Fraud: velocity spike
        return {
            "velocity_1h_count":    random.randint(4, 15),
            "velocity_1h_amount":   round(random.uniform(5000, 80000), 2),
            "velocity_24h_count":   random.randint(8, 40),
            "velocity_24h_amount":  round(random.uniform(15000, 200000), 2),
        }
    return {
        "velocity_1h_count":    random.randint(0, 3),
        "velocity_1h_amount":   round(random.uniform(0, 3000), 2),
        "velocity_24h_count":   random.randint(0, 8),
        "velocity_24h_amount":  round(random.uniform(0, 12000), 2),
    }


def generate_time_of_day(is_fraud: bool) -> tuple[datetime, bool]:
    now = datetime.now(timezone.utc)
    if is_fraud and random.random() < 0.50:
        # Fraud often happens 1am-5am
        hour   = random.randint(1, 5)
        is_odd_hour = True
    else:
        # Normal distribution centered on business hours
        hour = int(np.clip(np.random.normal(14, 4), 0, 23))
        is_odd_hour = hour < 6 or hour > 22
    days_back = random.randint(0, 30)
    ts = now - timedelta(days=days_back, hours=(now.hour - hour) % 24,
                         minutes=random.randint(0, 59))
    return ts, is_odd_hour


def generate_merchant_avg_ratio(amount: float, category: str, is_fraud: bool) -> float:
    cfg = MERCHANT_CATEGORIES[category]
    ratio = amount / cfg["avg"]
    return round(ratio, 4)


# ── Main generator ───────────────────────────────────────────────────────────

def generate_transactions(n: int = N_TRANSACTIONS) -> pd.DataFrame:
    n_fraud = int(n * FRAUD_RATE)
    labels  = [1] * n_fraud + [0] * (n - n_fraud)
    random.shuffle(labels)

    records = []
    for i, label in enumerate(labels):
        is_fraud = label == 1
        category = random.choice(list(MERCHANT_CATEGORIES.keys()))
        merchant_id = random.choice([m for m in MERCHANT_IDS if category in m] or MERCHANT_IDS)

        amount          = generate_amount(category, is_fraud)
        card_bin, network = pick_card_bin(is_fraud)
        bin_country     = pick_bin_country(is_fraud, network)
        payment_method  = random.choice(PAYMENT_METHODS)
        device_id       = random.choice(DEVICE_POOL[:200] if is_fraud else DEVICE_POOL)
        ip_address      = random.choice(IP_POOL[:50] if is_fraud else IP_POOL)
        velocity        = generate_velocity(is_fraud)
        timestamp, odd  = generate_time_of_day(is_fraud)
        mer_avg_ratio   = generate_merchant_avg_ratio(amount, category, is_fraud)
        upi_vpa         = f"{fake.user_name()}{random.choice(UPI_SUFFIXES)}" if payment_method == "UPI" else None
        customer_id     = f"cust_{random.randint(1, 5000):05d}"

        # Device consistency (fraud: low consistency)
        device_seen_before = (random.random() > 0.70) if is_fraud else (random.random() > 0.20)

        rec = {
            "transaction_id":       f"txn_seed_{i:07d}",
            "merchant_id":          merchant_id,
            "customer_id":          customer_id,
            "amount":               amount,
            "currency":             "INR",
            "card_bin":             card_bin,
            "card_network":         network,
            "bin_country":          bin_country,
            "payment_method":       payment_method,
            "upi_vpa":              upi_vpa,
            "device_id":            device_id,
            "device_seen_before":   int(device_seen_before),
            "ip_address":           ip_address,
            "timestamp":            timestamp.isoformat(),
            "hour_of_day":          timestamp.hour,
            "is_odd_hour":          int(odd),
            "merchant_category":    category,
            "amount_vs_merchant_avg": mer_avg_ratio,
            **velocity,
            "is_fraud":             label,
        }
        records.append(rec)

    df = pd.DataFrame(records)
    print(f"\n[seed_data] Generated {len(df):,} transactions")
    print(f"  Fraud: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.2f}%)")
    print(f"  Legit: {(1-df['is_fraud']).sum():,}")
    print(f"\n  Amount stats:")
    print(df.groupby("is_fraud")["amount"].describe().round(2))
    print(f"\n  Category breakdown:")
    print(df.groupby("merchant_category")["is_fraud"].agg(["sum","count","mean"]).round(4))
    return df


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "synthetic_transactions.csv")

    df = generate_transactions()
    df.to_csv(out_path, index=False)
    print(f"\n[seed_data] Saved to: {out_path}")
