"""Phase 3 end-to-end test: exercises Explanation Agent, Bandit, Chargeback."""

import sys, json, time, urllib.request as req, urllib.error

BASE = "http://127.0.0.1:8000"


def post(path, body):
    data = json.dumps(body).encode()
    request = req.Request(
        f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with req.urlopen(request, timeout=12) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}


def get(path):
    with req.urlopen(f"{BASE}{path}", timeout=8) as r:
        return json.loads(r.read())


# Wait for server ready
for _ in range(12):
    try:
        h = get("/v1/health")
        if h.get("pipeline") == "ready":
            break
    except:
        pass
    time.sleep(1)

print()
print("=" * 65)
print("  PHASE 3 TEST  |  Agents: Explain + Bandit + Chargeback")
print("=" * 65)

# --- Test 1: High-risk jewelry with chargeback risk ---
print("\n[1] High-risk DECLINE scenario (₹98,000 jewelry, high-risk BIN)")
t0 = time.perf_counter()
r1 = post(
    "/v1/assess",
    {
        "transaction_id": "txn_P3_001",
        "merchant_id": "merch_jewelry_001",
        "amount": 98000.0,
        "currency": "INR",
        "card_bin": "438935",
        "payment_method": "CARD",
        "device_id": "dev_unknown_new",
        "customer_id": "cust_fraud_sim",
    },
)
ms = (time.perf_counter() - t0) * 1000
rr = r1.get("risk_report", {})
print(f"  Decision        : {r1['decision']}")
print(f"  Stage           : {r1['stage_reached']}")
print(f"  Confidence      : {r1['confidence']}")
print(f"  Chargeback Risk : {rr.get('chargeback_risk', 'N/A')}")
print(f"  Merchant Thresh : {rr.get('merchant_threshold')}")
print(f"  Latency         : {ms:.1f}ms  (server: {r1.get('inference_ms', 0):.1f}ms)")
print(f"  Explanation:")
print(f"    {rr.get('explanation', '')}")
if rr.get("shap_top_features"):
    print("  SHAP Features:")
    for f in rr["shap_top_features"]:
        print(f"    {f['feature']:<30} impact={f['impact']:.4f}  [{f['direction']}]")
if rr.get("pend_reason_code"):
    print(f"  Reason Code: {rr['pend_reason_code']}")

# --- Test 2: PEND scenario ---
print("\n[2] Uncertain PEND scenario (conflicting evidence)")
r2 = post(
    "/v1/assess",
    {
        "transaction_id": "txn_P3_002",
        "merchant_id": "merch_travel_001",
        "amount": 38000.0,
        "currency": "INR",
        "card_bin": "400066",
        "payment_method": "CARD",
        "device_id": "dev_tablet_new",
        "customer_id": "cust_travel_99",
    },
)
rr2 = r2.get("risk_report", {})
print(f"  Decision        : {r2['decision']}")
print(f"  Stage           : {r2['stage_reached']}")
print(f"  Uncertainty     : {rr2.get('uncertainty_type', 'N/A')}")
print(f"  Chargeback Risk : {rr2.get('chargeback_risk', 'N/A')}")
print(f"  Latency         : {r2.get('inference_ms', 0):.1f}ms")
print(f"  Explanation:")
print(f"    {rr2.get('explanation', '')}")

# --- Test 3: Bandit diagnostics ---
print("\n[3] Bandit diagnostics for merch_jewelry_001")
diag = get("/v1/merchants/merch_jewelry_001/threshold")
print(f"  Effective threshold : {diag['effective_threshold']}")
print(f"  Samples seen        : {diag['n_samples']}")
print(f"  EMA reward          : {diag['ema_reward']}")
print(f"  Is adjusted         : {diag['is_adjusted']}")

# --- Test 4: Manual threshold override ---
print(
    "\n[4] Manual override: lower threshold for merch_food_001 (high-volume, trusted)"
)
ovr = post("/v1/merchants/merch_food_001/threshold", {"offset": -0.05})
print(f"  New effective threshold: {ovr['effective_threshold']}")
print(f"  Message: {ovr['message']}")

print()
print("  Phase 3 test complete. All agents operational.")
