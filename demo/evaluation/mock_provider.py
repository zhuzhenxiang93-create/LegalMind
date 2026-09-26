"""Offline HTTP contract fixture. Never imported by the production API."""

from __future__ import annotations

import hashlib
import json
from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import httpx
import openai

from legalmind.data.privacy import redact_privacy
from legalmind.demo import hybrid
from legalmind.generation.contracts_v2 import LegalAnalysisV1


class MockBailian:
    def __init__(self):
        self.calls = []
        self.fail_path = None
        self.bad_citation = False

    def handle(self, request):
        payload = json.loads(request.content)
        self.calls.append((request.url.path, payload))
        if self.fail_path and request.url.path.endswith(self.fail_path):
            return httpx.Response(
                401, json={"error": {"message": "private-provider-error", "type": "auth"}}
            )
        if request.url.path.endswith("/embeddings"):
            rows = []
            for i, text in enumerate(payload["input"]):
                digest = hashlib.sha256(text.encode()).digest()
                # Deliberately synthetic vectors, exclusively for transport/algorithm tests.
                vector = [(digest[j % 32] + 1) / 256 for j in range(payload["dimensions"])]
                rows.append({"object": "embedding", "index": i, "embedding": vector})
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": list(reversed(rows)),
                    "model": payload["model"],
                    "usage": {"prompt_tokens": 1, "total_tokens": 1},
                },
            )
        if request.url.path.endswith("/reranks"):
            n = len(payload["documents"])
            return httpx.Response(
                200,
                json={
                    "results": [
                        {"index": i, "relevance_score": (i + 1) / (n + 1)}
                        for i in reversed(range(n))
                    ][: payload["top_n"]]
                },
            )
        if request.url.path.endswith("/chat/completions"):
            prompt = payload["messages"][0]["content"]
            packet = json.loads(
                prompt.split("INPUT_EVIDENCE_PACKET=", 1)[1].split("\nOUTPUT_SCHEMA=", 1)[0]
            )
            output = LegalAnalysisV1(
                disposition="insufficient_evidence",
                candidate_accusations=packet["predicted_accusations"],
                key_facts=[packet["fact"]],
                analogous_cases=[
                    {
                        "claim": redact_privacy(e["summary"]).text,
                        "evidence_ids": ["INVENTED" if self.bad_citation else e["evidence_id"]],
                    }
                    for e in packet["evidence"]
                ],
                missing_information=[
                    "核验法条官方正文与指定日期的有效版本",
                    "补充行为方式、金额与关键证据",
                ],
                confidence="low",
                requires_manual_review=True,
                refusal_reason="合成接口测试输出：缺少已核验法条，保留法律结论。",
            )
            return httpx.Response(
                200,
                json={
                    "id": "mock-contract",
                    "object": "chat.completion",
                    "created": 0,
                    "model": payload["model"],
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": output.model_dump_json()},
                        }
                    ],
                },
            )
        raise AssertionError(f"Unexpected mock route: {request.url.path}")


@contextmanager
def mock_bailian():
    fake = MockBailian()
    real_openai = openai.OpenAI
    clients = []

    def sdk(**kwargs):
        client = real_openai(
            **kwargs, http_client=httpx.Client(transport=httpx.MockTransport(fake.handle))
        )
        clients.append(client)
        return client

    def rerank(settings):
        client = httpx.Client(
            transport=httpx.MockTransport(fake.handle),
            headers={"Authorization": f"Bearer {settings.api_key}"},
        )
        clients.append(client)
        return client

    env = {
        "DASHSCOPE_API_KEY": "offline-contract-key",
        "DASHSCOPE_BASE_URL": "https://bailian.example.test/compatible-mode/v1",
        "DASHSCOPE_RERANK_URL": "https://bailian.example.test/compatible-api/v1/reranks",
        "DASHSCOPE_EMBEDDING_MODEL": "text-embedding-v4",
        "DASHSCOPE_EMBEDDING_DIMENSIONS": "1024",
        "DASHSCOPE_RERANK_MODEL": "qwen3-rerank",
        "GENERATION_MODEL": "qwen-plus",
    }
    hybrid._load.cache_clear()
    with ExitStack() as stack:
        stack.enter_context(patch.dict("os.environ", env))
        stack.enter_context(patch("legalmind.demo.bailian.load_dotenv"))
        stack.enter_context(patch("openai.OpenAI", sdk))
        stack.enter_context(patch("legalmind.demo.hybrid._rerank_client", rerank))
        try:
            yield fake
        finally:
            hybrid._load.cache_clear()
            for client in clients:
                client.close()
