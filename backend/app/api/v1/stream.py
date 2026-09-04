"""
GET /v1/stream — Server-Sent Events live transaction feed.
Full SSE implementation will be wired in Phase 4 (Dashboard).
This stub lets the Next.js frontend connect without errors in Phase 1.
"""

from __future__ import annotations

import asyncio
import json
import time
import random
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

DECISIONS = ["APPROVE", "APPROVE", "APPROVE", "DECLINE", "STEP_UP", "PEND"]
MERCHANTS = [
    "merch_flipkart_01",
    "merch_amazon_in",
    "merch_swiggy_02",
    "merch_myntra_03",
]


async def _event_generator() -> AsyncGenerator[str, None]:
    """
    Phase 1: emits synthetic demo events every second.
    Phase 4: will emit real pipeline decisions pushed via Redis pub/sub.
    """
    txn_counter = 1
    while True:
        decision = random.choice(DECISIONS)
        amount = round(random.uniform(100, 50000), 2)
        event = {
            "transaction_id": f"txn_stream_{txn_counter:06d}",
            "merchant_id": random.choice(MERCHANTS),
            "amount": amount,
            "currency": "INR",
            "decision": decision,
            "confidence": round(random.uniform(0.55, 0.99), 3),
            "stage_reached": random.choice(["V1", "V2", "V3", "V4"]),
            "inference_ms": round(random.uniform(12, 95), 1),
            "ts": time.time(),
        }
        yield f"data: {json.dumps(event)}\n\n"
        txn_counter += 1
        await asyncio.sleep(1.0)


@router.get("/stream", summary="SSE live transaction decision feed")
async def stream_decisions():
    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
