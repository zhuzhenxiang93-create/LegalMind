"""Bailian configuration shared by demo retrieval, generation and Full Mode."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

from dotenv import load_dotenv


class BailianUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class BailianSettings:
    api_key: str = field(repr=False)
    base_url: str
    rerank_url: str
    embedding_model: str = "text-embedding-v4"
    reranker_model: str = "qwen3-rerank"
    generation_model: str = "qwen-plus"
    dimensions: int = 1024

    @classmethod
    def from_env(cls):
        load_dotenv(override=False)
        names = ["DASHSCOPE_API_KEY", "DASHSCOPE_BASE_URL", "DASHSCOPE_RERANK_URL"]
        missing = [name for name in names if not os.getenv(name, "").strip()]
        if missing:
            raise BailianUnavailable("Configure backend .env: " + ", ".join(missing))
        for name in names[1:]:
            url = os.environ[name].strip()
            if (
                urlparse(url).scheme != "https"
                or not urlparse(url).netloc
                or any(x in url for x in "{}<>")
            ):
                raise BailianUnavailable(
                    f"{name} requires the complete HTTPS endpoint from your Bailian console"
                )
        reranker = os.getenv("DASHSCOPE_RERANK_MODEL", "qwen3-rerank")
        if reranker != "qwen3-rerank":
            raise BailianUnavailable(
                "This adapter uses the qwen3-rerank flat request/response contract; other rerank models require a different adapter"
            )
        try:
            dimensions = int(os.getenv("DASHSCOPE_EMBEDDING_DIMENSIONS", "1024"))
            if dimensions <= 0:
                raise ValueError
        except ValueError:
            raise BailianUnavailable(
                "DASHSCOPE_EMBEDDING_DIMENSIONS must be a positive integer"
            ) from None
        return cls(
            api_key=os.environ[names[0]].strip(),
            base_url=os.environ[names[1]].strip().rstrip("/"),
            rerank_url=os.environ[names[2]].strip(),
            embedding_model=os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v4"),
            reranker_model=reranker,
            generation_model=os.getenv("GENERATION_MODEL", "qwen-plus"),
            dimensions=dimensions,
        )

    def generation_config(self):
        return {
            "mode": "openai_compatible_grounded",
            "model": self.generation_model,
            "base_url": self.base_url,
            "api_key_env": "DASHSCOPE_API_KEY",
            "temperature": 0,
            "max_tokens": 2048,
            "max_repairs": 1,
            "enable_thinking": False,
            "response_format": {"type": "json_object"},
            "timeout_seconds": 60,
        }
