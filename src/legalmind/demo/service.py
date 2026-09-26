from __future__ import annotations

import math
import re
import time
from collections import Counter
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from legalmind.data.privacy import redact_privacy
from legalmind.demo.assets import CASES, RECORDS, SOURCE_URL, STATUTES
from legalmind.generation.contracts_v2 import LegalAnalysisV1


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fact: str = Field(min_length=5, max_length=8000)
    as_of_date: date
    mode: Literal["lite", "full"] = "lite"


class DemoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: str
    case_id: str | None
    classification_origin: str
    candidate_charges: list[dict]
    retrieved_cases: list[dict]
    legal_basis: list[dict]
    analysis: LegalAnalysisV1
    checks: list[dict]
    trace: list[dict]
    evidence_ids: list[str]
    elapsed_ms: float
    requires_manual_review: bool
    disclaimer: str


def tokens(text: str) -> list[str]:
    clean = re.sub(r"\s+", "", text)
    return [clean[i : i + 2] for i in range(max(0, len(clean) - 1))]


def retrieve(fact: str, charges: list[str], limit: int = 3) -> list[dict]:
    """BM25 over the charge-constrained synthetic corpus, computed on every request."""
    docs = [r for r in RECORDS if r["charge"] in charges]
    if not docs:
        return []
    bags = [Counter(tokens(r["text"])) for r in docs]
    lengths = [sum(b.values()) for b in bags]
    avg = sum(lengths) / len(docs)
    scores = []
    for row, bag, length in zip(docs, bags, lengths):
        score = 0.0
        for token in set(tokens(fact)):
            df = sum(token in b for b in bags)
            idf = math.log(1 + (len(docs) - df + 0.5) / (df + 0.5))
            tf = bag[token]
            score += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * length / avg))
        if score > 0:
            scores.append(
                {**row, "evidence_id": row["id"], "score": round(score, 4), "origin": "synthetic"}
            )
    return sorted(scores, key=lambda r: (-r["score"], r["id"]))[:limit]


def citation_check(analysis: LegalAnalysisV1, allowed: set[str]) -> bool:
    claims = analysis.legal_basis + analysis.analogous_cases + analysis.sentencing_assessment
    return all(e in allowed for c in claims for e in c.evidence_ids)


def analyze_lite(request: AnalyzeRequest) -> DemoResponse:
    start = time.perf_counter()
    fixture = next((c for c in CASES if c["fact"] == request.fact.strip()), None)
    privacy = redact_privacy(request.fact)
    scores = fixture["scores"] if fixture else []
    candidates = [
        {
            "charge": name + "罪",
            "confidence": score,
            "threshold": 0.5,
            "above_threshold": score >= 0.5,
        }
        for name, score in scores
    ]
    enough = fixture is not None and fixture["id"] != "insufficient-facts"
    charges = [name for name, _ in scores] if enough else []
    hits = retrieve(privacy.text, charges)
    statutes = [
        {
            **s,
            "evidence_id": f"DEMO-ART-{s['article']}",
            "source_url": SOURCE_URL,
            "source_status": "unverified_demo_summary",
            "temporal_status": "not_verified",
            "as_of_date": request.as_of_date.isoformat(),
        }
        for s in STATUTES
        if s["charge"] in charges
    ]
    allowed = {h["evidence_id"] for h in hits}
    # Never certify an unverified statute snapshot or fabricate arbitrary-input inference.
    missing = (
        fixture["missing"]
        if fixture
        else ["Demo Lite 仅支持预置案情的演示分数；自定义案情请配置 Full Mode。"]
    )
    analysis = LegalAnalysisV1(
        disposition="insufficient_evidence",
        candidate_accusations=[c["charge"] for c in candidates],
        key_facts=[privacy.text],
        analogous_cases=[{"claim": h["text"], "evidence_ids": [h["id"]]} for h in hits],
        missing_information=[*missing, "核验法条官方正文与指定日期的有效版本"],
        confidence="low",
        requires_manual_review=True,
        refusal_reason="演示法条摘要尚未完成来源与时效核验，暂不生成法律或量刑结论。"
        if fixture
        else "自定义输入没有预计算分类结果。",
    )
    valid = citation_check(analysis, allowed)
    checks = [
        {"name": "Schema Valid", "status": "pass", "detail": "LegalAnalysisV1 · Pydantic"},
        {
            "name": "Citation Valid",
            "status": "pass" if valid else "fail",
            "detail": "Evidence-ID whitelist" if hits else "No claims to validate",
        },
        {
            "name": "Evidence Grounded",
            "status": "pass" if hits else "pending",
            "detail": "Synthetic excerpts copied with IDs; semantic correctness not assessed",
        },
        {
            "name": "Statute Source Verified",
            "status": "pending",
            "detail": "Source link recorded; summary unverified",
        },
        {
            "name": "Temporal Valid",
            "status": "pending",
            "detail": "No certified effective-date snapshot",
        },
        {
            "name": "Privacy Check",
            "status": "pass",
            "detail": "Pattern redaction only; not comprehensive anonymization",
        },
        {
            "name": "Manual Review Required",
            "status": "review",
            "detail": "Legal conclusions withheld",
        },
    ]
    trace = [
        {
            "name": "Charge classification",
            "status": "precomputed" if fixture else "unavailable",
            "detail": "Illustrative fixture scores · no LoRA inference",
        },
        {
            "name": "Charge-aware routing",
            "status": "live",
            "detail": f"{len(charges)} candidate charge partitions",
        },
        {
            "name": "Case retrieval",
            "status": "live",
            "detail": f"BM25 · Chinese character bigrams · {len(hits)} synthetic matches",
        },
        {
            "name": "Statute lookup",
            "status": "limited",
            "detail": "Curated article mapping · unverified summaries",
        },
        {
            "name": "Grounded output",
            "status": "deterministic",
            "detail": "Extractive case summaries · legal abstention",
        },
        {
            "name": "Output validation",
            "status": "live",
            "detail": "Pydantic + Evidence-ID whitelist + review decision",
        },
    ]
    return DemoResponse(
        mode="Demo / Precomputed Mode",
        case_id=fixture["id"] if fixture else None,
        classification_origin="Illustrative manually authored scores; not checkpoint predictions",
        candidate_charges=candidates,
        retrieved_cases=hits,
        legal_basis=statutes,
        analysis=analysis,
        checks=checks,
        trace=trace,
        evidence_ids=sorted(allowed),
        elapsed_ms=round((time.perf_counter() - start) * 1000, 2),
        requires_manual_review=True,
        disclaimer="Research / decision-support prototype, not legal advice.",
    )
