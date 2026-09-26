"""Explicit live or mocked API contract evaluation; not a legal benchmark."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from contextlib import nullcontext
from pathlib import Path

from legalmind.demo.assets import CASES
from legalmind.demo.service import AnalyzeRequest, DemoResponse, analyze_lite, citation_check

ROOT = Path(__file__).resolve().parents[1]


def evaluate(mocked: bool):
    rows = [
        json.loads(s)
        for s in (ROOT / "demo/evaluation/e2e_cases.jsonl").read_text().splitlines()
        if s
    ]
    success = schemas = citations = abstentions = reviews = expected_no_prediction = 0
    unknown_ids = total_citations = 0
    latencies = []
    outputs = []
    fallbacks = 0
    for row in rows:
        output = analyze_lite(AnalyzeRequest(fact=row["fact"], as_of_date=row["as_of_date"]))
        success += 1
        fallbacks += output.generation["status"] == "fallback"
        DemoResponse.model_validate_json(output.model_dump_json())
        schemas += 1
        citations += citation_check(output.analysis, set(output.evidence_ids))
        cited = [
            e
            for claim in output.analysis.analogous_cases
            + output.analysis.legal_basis
            + output.analysis.sentencing_assessment
            for e in claim.evidence_ids
        ]
        total_citations += len(cited)
        unknown_ids += sum(e not in output.evidence_ids for e in cited)
        abstentions += output.analysis.disposition == row["expected_disposition"]
        reviews += output.requires_manual_review
        if row["expect_no_prediction"]:
            expected_no_prediction += not output.candidate_charges
        latencies.append(output.elapsed_ms)
        outputs.append({"id": row["id"], **label_output(output, mocked)})
    n = len(rows)
    report = {
        "execution_mode": "mock_api_contract" if mocked else "live_api",
        "live_api_verified": not mocked and fallbacks == 0,
        "generation_fallback_count": fallbacks,
        "scope": "Synthetic/demo contract and fail-closed regression; not a human-reviewed legal benchmark",
        "samples": n,
        "unique_facts": len({r["fact"] for r in rows}),
        "schema_valid_rate": schemas / n,
        "citation_valid_response_rate": citations / n,
        "total_citations": total_citations,
        "unknown_evidence_id_count": unknown_ids,
        "unknown_evidence_id_rate": unknown_ids / total_citations if total_citations else None,
        "expected_abstention_rate": abstentions / n,
        "manual_review_trigger_rate": reviews / n,
        "pipeline_success_rate": success / n,
        "custom_input_no_prediction_rate": expected_no_prediction
        / sum(r["expect_no_prediction"] for r in rows),
        "latency_ms_median": statistics.median(latencies),
        "latency_ms_p95": sorted(latencies)[int(0.95 * (n - 1))],
        "limitations": [
            "All samples expect abstention because statutes are unverified or inputs unsupported.",
            "100% review is deliberate; this does not measure useful legal answering or review selectivity.",
            "Citation membership does not establish semantic support.",
            "Mock timing is not provider latency; live timing excludes UI and BF16 classification.",
            "Preset scores are manually authored illustrations, not trained-model outputs.",
        ],
    }
    target = ROOT / "demo/evaluation" / ("results.json" if mocked else "live-results.json")
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (target.parent / ("outputs.jsonl" if mocked else "live-outputs.jsonl")).write_text(
        "\n".join(json.dumps(o, ensure_ascii=False) for o in outputs) + "\n"
    )
    for case in CASES if mocked else []:
        result = analyze_lite(AnalyzeRequest(fact=case["fact"], as_of_date="2026-01-01"))
        (ROOT / f"demo/expected_outputs/{case['id']}.json").write_text(
            json.dumps(label_output(result, mocked), ensure_ascii=False, indent=2) + "\n"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def label_output(output, mocked):
    data = output.model_dump(mode="json")
    data["execution_mode"] = "mock_api_contract" if mocked else "live_api"
    if mocked:
        data["mode"] = "MOCK API CONTRACT PREVIEW / Precomputed Classification"
        for stage in [data["retrieval_trace"], data["generation"], *data["trace"]]:
            if stage.get("status") == "live_api":
                stage["status"] = "mock_api_contract"
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mock-provider", action="store_true", help="Offline HTTP fixtures, no paid API calls"
    )
    args = parser.parse_args()
    if args.mock_provider:
        sys.path.insert(0, str(ROOT))
        from demo.evaluation.mock_provider import mock_bailian

        context = mock_bailian()
    else:
        context = nullcontext()
    with context:
        evaluate(args.mock_provider)
