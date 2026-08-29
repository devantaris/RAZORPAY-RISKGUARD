import sys, json, time
sys.stdout.reconfigure(encoding="utf-8")
import urllib.request as ureq, urllib.error

BASE = "http://127.0.0.1:8000"

def post(path, body):
    data = json.dumps(body).encode()
    r = ureq.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with ureq.urlopen(r, timeout=12) as resp:
        return json.loads(resp.read())

def get(path):
    with ureq.urlopen(BASE + path, timeout=8) as r:
        return json.loads(r.read())

print("Phase 3 Agent Tests")
print("-" * 55)

# Test 1
r1 = post("/v1/assess", {
    "transaction_id": "txn_P3_001",
    "merchant_id": "merch_jewelry_001",
    "amount": 98000.0,
    "currency": "INR",
    "card_bin": "438935",
    "payment_method": "CARD",
    "device_id": "dev_unknown_new",
    "customer_id": "cust_fraud_sim",
})
rr = r1["risk_report"]
print("[1] High-Risk Jewelry - INR 98,000, high-risk BIN")
print("  decision:", r1["decision"])
print("  stage:", r1["stage_reached"])
print("  confidence:", r1["confidence"])
print("  chargeback_risk:", rr.get("chargeback_risk"))
print("  merchant_threshold:", rr.get("merchant_threshold"))
print("  inference_ms:", r1.get("inference_ms"))
print("  explanation:", rr["explanation"][:110])
for f in rr.get("shap_top_features", []):
    print("   SHAP:", f["feature"], "impact="+str(f["impact"]), f["direction"])
if rr.get("pend_reason_code"):
    print("  reason_code:", rr["pend_reason_code"])

print()

# Test 2
r2 = post("/v1/assess", {
    "transaction_id": "txn_P3_002",
    "merchant_id": "merch_travel_001",
    "amount": 38000.0,
    "currency": "INR",
    "card_bin": "400066",
    "payment_method": "CARD",
})
rr2 = r2["risk_report"]
print("[2] Uncertain PEND - Travel INR 38,000, conflicting signals")
print("  decision:", r2["decision"])
print("  stage:", r2["stage_reached"])
print("  uncertainty_type:", rr2.get("uncertainty_type"))
print("  chargeback_risk:", rr2.get("chargeback_risk"))
print("  inference_ms:", r2.get("inference_ms"))
print("  explanation:", rr2["explanation"][:110])
if rr2.get("pend_reason_code"):
    print("  reason_code:", rr2["pend_reason_code"])

print()

# Test 3 - Bandit
diag = get("/v1/merchants/merch_jewelry_001/threshold")
print("[3] Bandit Diagnostics - merch_jewelry_001")
print("  effective_threshold:", diag["effective_threshold"])
print("  n_samples:", diag["n_samples"])
print("  ema_reward:", diag["ema_reward"])
print("  current_arm:", diag["current_arm"])
print("  is_adjusted:", diag["is_adjusted"])

print()

# Test 4 - Manual override
ovr = post("/v1/merchants/merch_food_001/threshold", {"offset": -0.05})
print("[4] Manual Threshold Override - merch_food_001")
print("  effective_threshold:", ovr["effective_threshold"])
print("  message:", ovr["message"])

print()
print("All Phase 3 agents operational.")
