from __future__ import annotations

from fastapi import FastAPI, HTTPException

from legalmind.demo.assets import CASES
from legalmind.demo.full import analyze_full, full_config
from legalmind.demo.service import AnalyzeRequest, analyze_lite

app = FastAPI(title="LegalMind-RAG", version="1.0.0")


@app.get("/api/health")
def health():
    return {"status": "ok", "default_mode": "lite"}


@app.get("/api/cases")
def cases():
    return [{k: c[k] for k in ["id", "title", "subtitle", "fact"]} for c in CASES]


@app.get("/api/capabilities")
def capabilities():
    try:
        full_config()
        configured = True
    except ValueError:
        configured = False
    return {"lite": True, "full_configured": configured, "full_runtime_verified": False}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    if request.mode == "lite":
        return analyze_lite(request).model_dump(mode="json")
    try:
        return {"mode": "Full Mode", "result": analyze_full(request)}
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from None
    except Exception:  # noqa: BLE001 - public boundary must not leak provider errors
        # Keep provider payloads, API credentials and filesystem paths out of HTTP responses.
        raise HTTPException(
            status_code=503,
            detail="Full pipeline unavailable. Check server assets and provider configuration.",
        ) from None
