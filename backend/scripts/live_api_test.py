"""
live_api_test.py
=================
End-to-end live API test against the running FastAPI server.
Tests 4 transaction scenarios that exercise all 4 pipeline outcomes.
"""
import sys, json, time
try:
    import urllib.request as req
    import urllib.error
except ImportError:
    sys.exit("urllib missing")

BASE = "http://127.0.0.1:8000"

def post(path, body):
    data = json.dumps(body).encode()
    request = req.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"})
    try:
        with req.urlopen(request, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}

scenarios = [
    {
        "name": "HIGH-RISK: Jewelry store, 5x avg amount, high-risk BIN, 1am, velocity spike",
        "payload": {
            "transaction_id": "txn_HIGH_001",
            "merchant_id": "merch_jewelry_001",
            "amount": 98000.0,
            "currency": "INR",
            "card_bin": "438935",       # high-risk BIN
            "payment_method": "CARD",
            "device_id": "dev_new_unknown",
            "customer_id": "cust_00099",
            "ip_address": "197.22.14.5",
        }
    },
    {
        "name": "LOW-RISK: Food delivery, small amount, UPI, normal hour",
        "payload": {
            "transaction_id": "txn_LOW_002",
            "merchant_id": "merch_food_001",
            "amount": 349.0,
            "currency": "INR",
            "payment_method": "UPI",
            "upi_vpa": "customer@oksbi",
            "device_id": "dev_known_phone",
            "customer_id": "cust_01234",
        }
    },
    {
        "name": "MEDIUM-RISK: E-commerce, 2.5x avg, Mastercard, normal hour",
        "payload": {
            "transaction_id": "txn_MED_003",
            "merchant_id": "merch_ecommerce_002",
            "amount": 6200.0,
            "currency": "INR",
            "card_bin": "532101",
            "payment_method": "CARD",
            "device_id": "dev_tablet_01",
            "customer_id": "cust_05678",
        }
    },
    {
        "name": "BATCH: 3 transactions in one call",
        "batch": True,
        "payload": {
            "transactions": [
                {"transaction_id": "txn_B_001", "merchant_id": "merch_travel_001", "amount": 45000.0, "currency": "INR", "card_bin": "410057", "payment_method": "CARD"},
                {"transaction_id": "txn_B_002", "merchant_id": "merch_food_002",   "amount": 280.0,   "currency": "INR", "payment_method": "UPI"},
                {"transaction_id": "txn_B_003", "merchant_id": "merch_petrol_001", "amount": 2100.0,  "currency": "INR", "payment_method": "CARD"},
            ]
        }
    },
]

# Wait for server
for _ in range(10):
    try:
        req.urlopen(f"{BASE}/v1/health", timeout=2)
        break
    except:
        time.sleep(0.5)

print()
print("=" * 65)
print("  RAZORPAY RISKGUARD  |  Live API End-to-End Test")
print("=" * 65)

for s in scenarios:
    print(f"\n  [{s['name']}]")
    is_batch = s.get("batch", False)
    path = "/v1/batch" if is_batch else "/v1/assess"

    t0 = time.perf_counter()
    resp = post(path, s["payload"])
    ms = (time.perf_counter() - t0) * 1000

    if "error" in resp:
        print(f"  ERROR: {resp['error']}")
        continue

    if is_batch:
        print(f"  Batch results ({resp.get('total_ms', 0):.1f}ms | {resp.get('throughput_tps', 0):.0f} TPS):")
        for r in resp.get("results", []):
            print(f"    txn={r['transaction_id']}  decision={r['decision']:<8}  conf={r['confidence']:.3f}  stage={r['stage_reached']}")
    else:
        rr = resp.get("risk_report", {})
        print(f"  Decision     : {resp['decision']}")
        print(f"  Confidence   : {resp['confidence']:.4f}")
        print(f"  Stage        : {resp['stage_reached']}")
        print(f"  Latency      : {resp.get('inference_ms', ms):.1f}ms  (wall: {ms:.1f}ms)")
        print(f"  Explanation  : {rr.get('explanation', '')[:90]}...")
        if rr.get("shap_top_features"):
            print("  SHAP Features:")
            for f in rr["shap_top_features"]:
                print(f"    {f['feature']:<30} impact={f['impact']:.4f}  [{f['direction']}]")
        if rr.get("pend_reason_code"):
            print(f"  Reason Code  : {rr['pend_reason_code']}")

print()
print("  Health check:")
h = post("/v1/health", None) if False else json.loads(req.urlopen(f"{BASE}/v1/health", timeout=5).read())
print(f"    status={h['status']}  pipeline={h['pipeline']}  uptime={h['uptime_s']}s")
print()
print("  Live API test complete.")
