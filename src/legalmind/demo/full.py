"""Explicit full-mode asset configuration; never silently substitutes demo outputs."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from legalmind.demo.service import AnalyzeRequest


def full_config() -> dict:
    required = [
        "LEGALMIND_BASE_MODEL",
        "LEGALMIND_ADAPTER",
        "LEGALMIND_LABEL_MAPPING",
        "LEGALMIND_THRESHOLDS",
        "LEGALMIND_CASE_INDEX",
        "LEGALMIND_STATUTE_INDEX",
        "GENERATION_BASE_URL",
        "GENERATION_API_KEY",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError("Full Mode requires: " + ", ".join(missing))
    for name in required[1:6]:
        if not Path(os.environ[name]).exists():
            raise ValueError(f"Full Mode asset unavailable: {name}")
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
            "mode": "partitioned_bm25",
            "partitioned_index": os.environ[required[4]],
            "statute_bm25_index": os.environ[required[5]],
        },
        "generation": {
            "mode": "openai_compatible_grounded",
            "model": os.getenv("GENERATION_MODEL", "qwen-plus"),
            "base_url_env": "GENERATION_BASE_URL",
            "api_key_env": "GENERATION_API_KEY",
            "temperature": 0,
            "max_tokens": 2048,
            "max_repairs": 1,
        },
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
