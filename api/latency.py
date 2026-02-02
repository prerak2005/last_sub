from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# Load telemetry once
BASE_DIR = Path(__file__).resolve().parent.parent
json_path = BASE_DIR / "data" / "q-vercel-latency.json"

with open(json_path) as f:
    data = json.load(f)


class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float                         

@app.post("/")
def latency_metrics(body: RequestBody):
    response = {}

    for region in body.regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        response[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(l > body.threshold_ms for l in latencies),
        }

    return response