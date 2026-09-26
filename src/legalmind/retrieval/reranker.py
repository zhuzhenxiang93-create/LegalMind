from __future__ import annotations

import math
import os
from typing import Any, Protocol

import numpy as np

from legalmind.schemas import SearchHit


class Reranker(Protocol):
    def rerank(self, query: str, hits: list[SearchHit], top_k: int) -> list[SearchHit]: ...


class CrossEncoderReranker:
    """Instruction-aware cross-encoder reranking for fused retrieval candidates."""

    def __init__(
        self,
        model_name: str,
        max_length: int = 2048,
        batch_size: int = 8,
        device: str | None = None,
    ):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(
            model_name,
            max_length=max_length,
            trust_remote_code=False,
            device=device,
        )
        self.batch_size = batch_size

    def rerank(self, query: str, hits: list[SearchHit], top_k: int) -> list[SearchHit]:
        if not hits:
            return []
        pairs = [(query, hit.text) for hit in hits]
        values = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        scores = np.asarray(values, dtype=np.float32).reshape(-1)
        if scores.shape[0] != len(hits):
            raise ValueError("Reranker returned a score count that does not match candidates")
        for hit, score in zip(hits, scores):
            hit.source_scores["rrf"] = hit.score
            hit.source_scores["reranker"] = float(score)
            hit.score = float(score)
        return sorted(hits, key=lambda item: item.score, reverse=True)[:top_k]


class APIReranker:
    """Alibaba Model Studio qwen3-rerank client."""

    def __init__(
        self,
        model_name: str,
        url_env: str,
        api_key_env: str,
        instruction: str = "",
        timeout: float = 60.0,
        client: Any | None = None,
    ):
        self.url = os.getenv(url_env)
        api_key = os.getenv(api_key_env)
        if client is None:
            if not self.url:
                raise ValueError(f"Reranker URL is missing from environment variable {url_env}")
            if not api_key:
                raise ValueError(
                    f"Reranker API key is missing from environment variable {api_key_env}"
                )
            import httpx

            client = httpx.Client(
                timeout=timeout,
                headers={"Authorization": f"Bearer {api_key}"},
            )
        self.client = client
        self.model_name = model_name
        self.instruction = instruction.strip()

    def rerank(self, query: str, hits: list[SearchHit], top_k: int) -> list[SearchHit]:
        if not hits:
            return []
        payload: dict[str, Any] = {
            "model": self.model_name,
            "query": query,
            "documents": [hit.text for hit in hits],
            "top_n": min(top_k, len(hits)),
        }
        if self.instruction:
            payload["instruct"] = self.instruction
        response = self.client.post(self.url, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not isinstance(results, list) or len(results) != payload["top_n"]:
            raise ValueError("Reranker result count does not match top_n")
        seen = set()
        checked = []
        for item in results:
            index = item["index"]
            score = float(item["relevance_score"])
            if (
                type(index) is not int
                or not 0 <= index < len(hits)
                or index in seen
                or not math.isfinite(score)
            ):
                raise ValueError("Reranker returned invalid indexes or scores")
            seen.add(index)
            checked.append((index, score))
        reranked: list[SearchHit] = []
        for index, score in checked:
            hit = hits[index]
            hit.source_scores["rrf"] = hit.score
            hit.source_scores["reranker"] = score
            hit.score = score
            reranked.append(hit)
        if not reranked:
            raise ValueError("Reranker service returned no results")
        return sorted(reranked, key=lambda item: item.score, reverse=True)[:top_k]
