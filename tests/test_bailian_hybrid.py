import json

import pytest
from fastapi.testclient import TestClient

from legalmind.demo.api import app
from legalmind.demo.assets import CASES, RECORDS

client = TestClient(app)


def analyze():
    return client.post("/api/analyze", json={"fact": CASES[0]["fact"], "as_of_date": "2026-01-01"})


def test_http_contract_and_charge_gated_rankings(bailian_mock):
    response = analyze()
    assert response.status_code == 200
    data = response.json()
    trace = data["retrieval_trace"]
    assert [path.rsplit("/", 1)[-1] for path, _ in bailian_mock.calls] == [
        "embeddings",
        "embeddings",
        "reranks",
        "completions",
    ]
    embed, query, rerank, chat = [body for _, body in bailian_mock.calls]
    assert embed["model"] == "text-embedding-v4"
    assert embed["dimensions"] == 1024 and embed["encoding_format"] == "float"
    assert len(embed["input"]) == len(RECORDS) and len(query["input"]) == 1
    assert rerank["model"] == "qwen3-rerank" and "instruct" in rerank and "input" not in rerank
    assert chat["model"] == "qwen-plus" and chat["enable_thinking"] is False
    assert chat["response_format"] == {"type": "json_object"}
    assert chat["messages"][0]["role"] == "system"
    assert 'disposition="insufficient_evidence"' in chat["messages"][-1]["content"]
    allowed = {r["id"] for r in RECORDS if r["charge"] in trace["charge_filter"]}
    for stage in ["bm25", "dense", "rrf", "reranker"]:
        assert trace[stage]
        assert {r["case_id"] for r in trace[stage]} <= allowed
    # The fake provider reverses fused order: validates response-index mapping end to end.
    assert trace["reranker"][0]["case_id"] == trace["rrf"][-1]["case_id"]
    first = data["retrieved_cases"][0]
    assert set(first["source_scores"]) == {"bm25", "vector", "rrf", "reranker"}
    assert data["generation"]["validation"]["valid"]
    assert "offline-contract-key" not in response.text
    analyze()
    assert len(bailian_mock.calls) == 7  # corpus vectors cached; query, rerank, generation rerun


@pytest.mark.parametrize(
    "missing", ["DASHSCOPE_API_KEY", "DASHSCOPE_BASE_URL", "DASHSCOPE_RERANK_URL"]
)
def test_missing_configuration_never_calls_provider(bailian_mock, monkeypatch, missing):
    monkeypatch.delenv(missing)
    response = analyze()
    assert response.status_code == 503 and missing in response.text
    assert not bailian_mock.calls
    assert client.get("/api/capabilities").json()["bailian_configured"] is False


@pytest.mark.parametrize("path", ["/embeddings", "/reranks"])
def test_failed_hybrid_has_no_sparse_fallback(bailian_mock, path):
    bailian_mock.fail_path = path
    response = analyze()
    assert response.status_code == 503
    assert "No BM25 fallback" in response.text
    assert "private-provider-error" not in response.text
    assert not any(p.endswith("/chat/completions") for p, _ in bailian_mock.calls)


def test_generation_failure_is_explicit_safe_fallback(bailian_mock):
    bailian_mock.fail_path = "/chat/completions"
    response = analyze()
    assert response.status_code == 200
    data = response.json()
    assert data["generation"]["status"] == "fallback"
    assert data["analysis"]["requires_manual_review"]
    assert "private-provider-error" not in json.dumps(data)


def test_invalid_citations_trigger_one_repair_then_fallback(bailian_mock):
    bailian_mock.bad_citation = True
    data = analyze().json()
    assert data["generation"]["status"] == "fallback"
    assert data["generation"]["validation"]["attempts"] == 2
    assert data["analysis"]["analogous_cases"] == []


def test_invalid_dimensions_are_configuration_error(bailian_mock, monkeypatch):
    monkeypatch.setenv("DASHSCOPE_EMBEDDING_DIMENSIONS", "invalid")
    assert analyze().status_code == 503
    assert not bailian_mock.calls


def test_rejected_draft_not_returned_in_validation(bailian_mock):
    bailian_mock.bad_citation = True
    data = analyze().json()
    assert "analysis" not in data["generation"]["validation"]
    assert data["analysis"]["refusal_reason"] == "generation_validation_failed"
