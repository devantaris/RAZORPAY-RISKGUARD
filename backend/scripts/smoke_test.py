import sys

sys.path.insert(0, ".")

print("=== Smoke Test: Phase 1 ===\n")

# Config
from app.core.config import settings

print("[1] Config OK")
print(f"    Project: {settings.PROJECT_NAME}")
print(f"    Decline threshold: {settings.DEFAULT_DECLINE_THRESHOLD}")

# Pydantic schema
from app.models.transaction import AssessRequest, Decision

req = AssessRequest(
    transaction_id="txn_test_001",
    merchant_id="merch_flipkart_01",
    amount=42999.0,
    currency="INR",
    card_bin="438935",
    payment_method="CARD",
    device_id="dev_samsung_s23",
    customer_id="cust_00042",
)
print(f"\n[2] Pydantic Schema OK")
print(f"    txn={req.transaction_id}  amount=INR{req.amount}")

# DS Math
from app.pipeline.v3_dempster_shafer import fuse_and_route

sub, m = fuse_and_route(mean_prob=0.88, std=0.015, iso_score=-0.12, svm_prob=0.91)
print(f"\n[3] DS Fusion: High-Risk -> {sub}")
print(f"    Bel_F={m['bel_F']:.4f}  Ign={m['ignorance']:.4f}  K={m['conflict_K']:.4f}")

sub2, _ = fuse_and_route(mean_prob=0.05, std=0.008, iso_score=0.15, svm_prob=0.03)
print(f"    Low-Risk  -> {sub2}")

sub3, m3 = fuse_and_route(mean_prob=0.65, std=0.08, iso_score=-0.05, svm_prob=0.55)
print(f"    Uncertain -> {sub3}")
print(
    f"    Bel_F={m3['bel_F']:.4f}  Ign={m3['ignorance']:.4f}  K={m3['conflict_K']:.4f}"
)

# FastAPI app import
from app.main import app

print(f"\n[4] FastAPI App OK: {app.title} v{app.version}")
print(f"    Routes: {[r.path for r in app.routes]}")

print("\n=== All checks passed ===")
