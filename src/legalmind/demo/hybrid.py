"""Bailian API Hybrid retrieval; missing providers never downgrade to sparse-only."""

from __future__ import annotations

import threading
import time
from functools import lru_cache

from legalmind.demo.assets import RECORDS
from legalmind.demo.bailian import BailianSettings, BailianUnavailable
from legalmind.retrieval.embedding import OpenAIEmbeddingBackend
from legalmind.retrieval.index import HybridIndex
from legalmind.retrieval.reranker import APIReranker
from legalmind.retrieval.retriever import HybridRetriever
from legalmind.schemas import CaseChunk

_LOAD_LOCK = threading.Lock()
HybridUnavailable = BailianUnavailable


def _rerank_client(settings):
    import httpx

    return httpx.Client(timeout=60, headers={"Authorization": f"Bearer {settings.api_key}"})


@lru_cache(maxsize=1)
def _load(settings: BailianSettings):
    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url, timeout=60, max_retries=1)
    encoder = OpenAIEmbeddingBackend(
        settings.embedding_model,
        "DASHSCOPE_BASE_URL",
        "DASHSCOPE_API_KEY",
        dimensions=settings.dimensions,
        client=client,
    )
    index = HybridIndex(
        settings.embedding_model,
        embedding_provider="api",
        embedding_dimension=settings.dimensions,
        backend=encoder,
    )
    index.build(
        [
            CaseChunk(
                chunk_id=r["id"],
                case_id=r["id"],
                text=r["text"],
                chunk_index=0,
                start_char=0,
                end_char=len(r["text"]),
                accusations=[r["charge"]],
                penalty={"imprisonment_months": r["months"], "fine": r["fine"]},
            )
            for r in RECORDS
        ]
    )
    reranker = APIReranker(
        settings.reranker_model,
        "DASHSCOPE_RERANK_URL",
        "DASHSCOPE_API_KEY",
        instruction="Rank criminal case facts by similar conduct and charge elements.",
        client=_rerank_client(settings),
    )
    return HybridRetriever(index, reranker=reranker, candidate_k=6, fusion_top_k=6, rerank_top_k=6)


def retrieve_hybrid(fact: str, charges: list[str], limit: int = 3):
    settings = BailianSettings.from_env()
    if not charges:
        return [], {
            "status": "skipped",
            "reason": "No supported candidate charges",
            "bm25": [],
            "dense": [],
            "rrf": [],
            "reranker": [],
        }
    try:
        started = time.perf_counter()
        with _LOAD_LOCK:
            retriever = _load(settings)
        initialization_ms = (time.perf_counter() - started) * 1000
        hits, trace = retriever.search_with_trace(fact, set(charges), final_k=limit)
    except Exception as error:
        raise BailianUnavailable(
            "Bailian Hybrid request failed. Check backend API key, regional endpoints, model access and quota. No BM25 fallback was used."
        ) from error
    records = {r["id"]: r for r in RECORDS}
    result = [
        {
            **records[h.case_id],
            "evidence_id": h.chunk_id,
            "score": h.score,
            "source_scores": h.source_scores,
            "origin": "synthetic",
        }
        for h in hits
    ]
    trace.update(
        status="live_api",
        embedding_model=settings.embedding_model,
        reranker_model=settings.reranker_model,
        index_initialization_ms=round(initialization_ms, 2),
        provider="Alibaba Cloud Bailian",
    )
    return result, trace
