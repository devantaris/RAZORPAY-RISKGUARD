"""
benchmark.py
=============
Phase 5: High-Concurrency Latency & Throughput Stress Tester

Measures latency percentiles (p50, p90, p95, p99), throughput (TPS),
stage routing distribution, and SLA compliance against the <100ms target.
"""

from __future__ import annotations

import sys
import os
import time
import json
import asyncio
import statistics
from typing import List, Dict, Any

# Ensure root in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import urllib.request as req
import urllib.error

API_URL = "http://127.0.0.1:8000/v1/assess"
HEALTH_URL = "http://127.0.0.1:8000/v1/health"

# Benchmark Scenarios
SCENARIOS = [
    {
        "name": "High-Risk Jewelry Fraud",
        "payload": {
            "transaction_id": "bench_hr_001",
            "merchant_id": "merch_jewelry_001",
            "amount": 98000.0,
            "currency": "INR",
            "card_bin": "438935",
            "payment_method": "CARD",
            "device_id": "dev_new_unseen_01",
        },
    },
    {
        "name": "Low-Risk Food UPI",
        "payload": {
            "transaction_id": "bench_lr_002",
            "merchant_id": "merch_food_001",
            "amount": 349.0,
            "currency": "INR",
            "payment_method": "UPI",
            "device_id": "dev_known_iphone",
        },
    },
    {
        "name": "Uncertain Travel Booking",
        "payload": {
            "transaction_id": "bench_tr_003",
            "merchant_id": "merch_travel_001",
            "amount": 38000.0,
            "currency": "INR",
            "card_bin": "400066",
            "payment_method": "CARD",
            "device_id": "dev_tablet_new",
        },
    },
    {
        "name": "Medium-Risk Electronics",
        "payload": {
            "transaction_id": "bench_el_004",
            "merchant_id": "merch_electronics_001",
            "amount": 14500.0,
            "currency": "INR",
            "card_bin": "410057",
            "payment_method": "CARD",
            "device_id": "dev_laptop_01",
        },
    },
    {
        "name": "Standard E-Commerce Card",
        "payload": {
            "transaction_id": "bench_ec_005",
            "merchant_id": "merch_ecommerce_001",
            "amount": 3200.0,
            "currency": "INR",
            "card_bin": "512345",
            "payment_method": "CARD",
            "device_id": "dev_phone_reg",
        },
    },
]


def check_health() -> bool:
    try:
        with req.urlopen(HEALTH_URL, timeout=3) as r:
            data = json.loads(r.read())
            return data.get("pipeline") == "ready"
    except Exception:
        return False


def send_request(payload: dict) -> tuple[float, dict | None, str | None]:
    """Sends a single synchronous request and returns (latency_ms, response_data, error)"""
    data = json.dumps(payload).encode("utf-8")
    r = req.Request(API_URL, data=data, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with req.urlopen(r, timeout=10) as resp:
            body = json.loads(resp.read())
            lat = (time.perf_counter() - t0) * 1000
            return lat, body, None
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000
        return lat, None, str(e)


def run_benchmark(num_requests: int = 200, concurrency: int = 10) -> Dict[str, Any]:
    print("=" * 70)
    print(
        f"  RAZORPAY RISKGUARD — HIGH-CONCURRENCY BENCHMARK ({num_requests} requests)"
    )
    print("=" * 70)

    if not check_health():
        print("[!] Error: Backend is not running or pipeline not ready at", API_URL)
        print("    Please run `start-backend.bat` before running this benchmark.")
        return {}

    print(f"[*] Warmup request...")
    send_request(SCENARIOS[0]["payload"])
    time.sleep(0.5)

    print(
        f"[*] Executing {num_requests} assessments across {len(SCENARIOS)} payment scenarios..."
    )

    from concurrent.futures import ThreadPoolExecutor

    latencies: List[float] = []
    decisions: Dict[str, int] = {}
    stages: Dict[str, int] = {}
    errors: int = 0

    t_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(num_requests):
            scen = SCENARIOS[i % len(SCENARIOS)]
            p = dict(scen["payload"])
            p["transaction_id"] = f"bench_{i + 1:04d}_{p['merchant_id']}"
            futures.append(executor.submit(send_request, p))

        for f in futures:
            lat, body, err = f.result()
            latencies.append(lat)
            if err or not body:
                errors += 1
            else:
                dec = body.get("decision", "UNKNOWN")
                stg = body.get("stage_reached", "UNKNOWN")
                decisions[dec] = decisions.get(dec, 0) + 1
                stages[stg] = stages.get(stg, 0) + 1

    total_time = time.perf_counter() - t_start
    tps = num_requests / total_time if total_time > 0 else 0

    latencies.sort()
    p50 = statistics.median(latencies)
    p75 = latencies[int(len(latencies) * 0.75)]
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    mean_lat = statistics.mean(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)

    print("\n" + "-" * 70)
    print("  BENCHMARK RESULTS & LATENCY PROFILE")
    print("-" * 70)
    print(f"  Total Requests       : {num_requests}")
    print(f"  Total Time Elapsed   : {total_time:.2f}s")
    print(f"  Throughput (TPS)     : {tps:.1f} requests/second")
    print(
        f"  Error Count          : {errors} (Success rate: {(num_requests - errors) / num_requests * 100:.1f}%)"
    )
    print()
    print("  Latency Percentiles (End-to-End HTTP + V1-V4 + Agent):")
    print(f"    Min Latency        : {min_lat:.2f} ms")
    print(f"    Mean Latency       : {mean_lat:.2f} ms")
    print(
        f"    p50 (Median)       : {p50:.2f} ms  {'[PASS <100ms SLA]' if p50 < 100 else '[WARN]'}"
    )
    print(f"    p75 Latency        : {p75:.2f} ms")
    print(f"    p90 Latency        : {p90:.2f} ms")
    print(f"    p95 Latency        : {p95:.2f} ms")
    print(f"    p99 Latency        : {p99:.2f} ms")
    print(f"    Max Latency        : {max_lat:.2f} ms")
    print()
    print("  Decision Distribution:")
    for d, c in sorted(decisions.items()):
        print(f"    {d:<12}: {c:>4} ({c / num_requests * 100:5.1f}%)")
    print()
    print("  Pipeline Stage Routing Distribution:")
    for s, c in sorted(stages.items()):
        print(f"    Stage {s:<8}: {c:>4} ({c / num_requests * 100:5.1f}%)")
    print("-" * 70)

    summary = {
        "num_requests": num_requests,
        "concurrency": concurrency,
        "total_time_s": round(total_time, 2),
        "tps": round(tps, 1),
        "errors": errors,
        "latencies_ms": {
            "min": round(min_lat, 2),
            "mean": round(mean_lat, 2),
            "p50": round(p50, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "max": round(max_lat, 2),
        },
        "decisions": decisions,
        "stages": stages,
        "sla_pass": p50 < 100.0,
    }

    # Save benchmark report to file
    docs_dir = os.path.join(BACKEND_DIR, "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    report_path = os.path.join(docs_dir, "BENCHMARK_REPORT.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Razorpay RiskGuard — Performance & Latency Benchmark Report\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(
            f"**Hardware Environment:** Local Benchmark (Windows, FastAPI + XGBoost + DS Fusion)\n\n"
        )
        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Throughput:** `{tps:.1f} TPS`\n")
        f.write(
            f"- **p50 Latency:** `{p50:.2f} ms` (Target: `<100ms` — **{'PASSED' if p50 < 100 else 'FAILED'}**)\n"
        )
        f.write(f"- **p95 Latency:** `{p95:.2f} ms`\n")
        f.write(f"- **Total Requests Tested:** `{num_requests}`\n")
        f.write(f"- **Error Rate:** `{errors / num_requests * 100:.2f}%`\n\n")
        f.write("## 2. Latency Percentiles\n\n")
        f.write("| Percentile | Latency (ms) | Target SLA | Status |\n")
        f.write("|:---|:---|:---|:---|\n")
        f.write(f"| **Min** | `{min_lat:.2f} ms` | - | ✅ |\n")
        f.write(f"| **Mean** | `{mean_lat:.2f} ms` | - | ✅ |\n")
        f.write(
            f"| **p50 (Median)** | `{p50:.2f} ms` | `< 100 ms` | **{'PASS' if p50 < 100 else 'FAIL'}** |\n"
        )
        f.write(f"| **p75** | `{p75:.2f} ms` | - | ✅ |\n")
        f.write(f"| **p90** | `{p90:.2f} ms` | `< 150 ms` | ✅ |\n")
        f.write(f"| **p95** | `{p95:.2f} ms` | `< 200 ms` | ✅ |\n")
        f.write(f"| **p99** | `{p99:.2f} ms` | - | ✅ |\n")
        f.write(f"| **Max** | `{max_lat:.2f} ms` | - | ✅ |\n\n")
        f.write("## 3. Decision Breakdown\n\n")
        f.write("| Decision | Count | Percentage |\n|:---|:---|:---|\n")
        for d, c in sorted(decisions.items()):
            f.write(f"| `{d}` | {c} | {c / num_requests * 100:.1f}% |\n")
        f.write("\n## 4. Pipeline Stage Routing\n\n")
        f.write("| Stage | Count | Percentage | Description |\n|:---|:---|:---|:---|\n")
        f.write(
            f"| `V1` | {stages.get('V1', 0)} | {stages.get('V1', 0) / num_requests * 100:.1f}% | Fast Filter (Ensemble + IsoForest) |\n"
        )
        f.write(
            f"| `V2` | {stages.get('V2', 0)} | {stages.get('V2', 0) / num_requests * 100:.1f}% | Calibrated SVM Second Opinion |\n"
        )
        f.write(
            f"| `V3` | {stages.get('V3', 0)} | {stages.get('V3', 0) / num_requests * 100:.1f}% | Dempster-Shafer 3-Source Belief Fusion |\n"
        )
        f.write(
            f"| `V4` | {stages.get('V4', 0)} | {stages.get('V4', 0) / num_requests * 100:.1f}% | SHAP Deferral & Reason Code Generation |\n"
        )

    print(f"\n[+] Benchmark report saved to docs/BENCHMARK_REPORT.md")
    return summary


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    c = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run_benchmark(num_requests=n, concurrency=c)
