"""Explicit full-mode asset configuration; never silently substitutes demo outputs."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from legalmind.demo.bailian import BailianSettings
from legalmind.demo.service import AnalyzeRequest


def full_config() -> dict:
    settings = BailianSettings.from_env()
    required = [
        "LEGALMIND_BASE_MODEL",
        "LEGALMIND_ADAPTER",
        "LEGALMIND_LABEL_MAPPING",
        "LEGALMIND_THRESHOLDS",
        "LEGALMIND_HYBRID_INDEX",
        "LEGALMIND_STATUTE_INDEX",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError("Full Mode requires: " + ", ".join(missing))
    for name in required[1:6]:
        if not Path(os.environ[name]).exists():
            raise ValueError(f"Full Mode asset unavailable: {name}")
    manifest_path = Path(os.environ["LEGALMIND_HYBRID_INDEX"]) / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError):
        raise ValueError("Full Mode requires a valid Hybrid index manifest") from None
    if (
        manifest.get("embedding_provider") != "api"
        or manifest.get("embedding_model") != settings.embedding_model
        or manifest.get("vector_dimension") != settings.dimensions
    ):
        raise ValueError(
            "Rebuild Full Mode Hybrid index with the configured Bailian embedding model and dimensions"
        )
    return {
        "classifier": {
            "enabled": True,
            "base_model": os.environ[required[0]],
            "adapter": os.environ[required[1]],
            "label_mapping": os.environ[required[2]],
            "thresholds": os.environ[required[3]],
            "max_length": 2048,
            "truncation_strategy": "head_tail",
        },
        "retrieval": {
            "mode": "hybrid_rrf_rerank",
            "hybrid_index": os.environ[required[4]],
            "strict_hybrid": True,
            "reranker_provider": "api",
            "reranker_model": settings.reranker_model,
            "reranker_url_env": "DASHSCOPE_RERANK_URL",
            "reranker_api_key_env": "DASHSCOPE_API_KEY",
            "statute_bm25_index": os.environ[required[5]],
        },
        "generation": settings.generation_config(),
        "sentencing": {"enabled": False},
    }


@lru_cache(maxsize=1)
def full_pipeline():
    from legalmind.pipeline.analyze_case import build_pipeline

    pipeline = build_pipeline(full_config())
    if any(
        x is None
        for x in [
            pipeline.classifier,
            pipeline.retriever,
            pipeline.statute_retriever,
            pipeline.grounded_analysis_service,
        ]
    ):
        raise ValueError("Full Mode initialization incomplete; check local assets and dependencies")
    return pipeline


def analyze_full(request: AnalyzeRequest) -> dict:
    from legalmind.data.privacy import redact_privacy

    return (
        full_pipeline()
        .analyze(redact_privacy(request.fact).text, as_of_date=request.as_of_date.isoformat())
        .model_dump(mode="json")
    )
