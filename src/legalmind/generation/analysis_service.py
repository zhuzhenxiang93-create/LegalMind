from __future__ import annotations

import json
from typing import Protocol

from legalmind.generation.contracts_v2 import EvidencePacketV1, LegalAnalysisV1
from legalmind.generation.grounding_validator import validate_generated_text

SYSTEM_PROMPT_V2 = (
    "你是结构化法律分析模型。只输出符合 legal-analysis-v1 的单个 JSON 对象，不输出思维链。"
    "所有法律依据、类案和量刑判断必须逐项引用输入 evidence_id；禁止引用目录外材料。"
    "没有经过核验且在 as_of_date 有效的法条时，必须输出 insufficient_evidence。"
    "case 类型证据只能支持类案事实比较，禁止把 case ID 放入 legal_basis。"
    "合成案例只能作为演示材料，禁止描述为真实裁判或推断其未提供的定罪量刑结论。"
    "不得输出姓名、证件号、电话、住址等直接身份信息。本系统不构成法律意见。"
)


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str: ...


def build_analysis_prompt(packet: EvidencePacketV1, repair_error: str | None = None) -> str:
    suffix = ""
    if not any(item.evidence_type == "statute" for item in packet.evidence):
        suffix += (
            "\n本次证据目录没有任何法条。以下字段必须逐字采用指定值："
            'disposition="insufficient_evidence", legal_basis=[], sentencing_assessment=[], '
            'confidence="low", requires_manual_review=true。'
            "refusal_reason 说明缺少已核验法条。可以描述并引用类案事实相似点，"
            "但不得补充模型记忆中的法律标准、认定罪名成立或提出量刑结论。"
        )
    if repair_error:
        suffix += f"\n上次输出未通过验证：{repair_error}。请重新输出完整 JSON。"
    return f"{SYSTEM_PROMPT_V2}\n{build_analysis_user_payload(packet)}{suffix}"


def build_analysis_user_payload(packet: EvidencePacketV1) -> str:
    return (
        f"INPUT_EVIDENCE_PACKET={packet.model_dump_json()}\n"
        "OUTPUT_SCHEMA="
        f"{json.dumps(LegalAnalysisV1.model_json_schema(), ensure_ascii=False)}"
    )


def deterministic_fallback(packet: EvidencePacketV1, reason: str) -> LegalAnalysisV1:
    return LegalAnalysisV1(
        disposition="insufficient_evidence",
        candidate_accusations=packet.predicted_accusations,
        key_facts=[packet.fact[:240]],
        missing_information=["生成结果未通过结构、引用、时效或隐私验证"],
        confidence="low",
        requires_manual_review=True,
        refusal_reason=reason,
    )


class GroundedAnalysisService:
    def __init__(self, generator: TextGenerator, max_repairs: int = 1):
        self.generator = generator
        self.max_repairs = max_repairs

    def analyze(self, packet: EvidencePacketV1) -> tuple[LegalAnalysisV1, dict]:
        last_report: dict = {"valid": False, "error": "not_run"}
        for attempt in range(self.max_repairs + 1):
            try:
                output = self.generator.generate(
                    build_analysis_prompt(packet, None if attempt == 0 else str(last_report))
                )
            except Exception:  # noqa: BLE001 - public boundary must not leak provider errors
                fallback = deterministic_fallback(packet, "generation_provider_unavailable")
                return fallback, {
                    "valid": False,
                    "attempts": attempt + 1,
                    "fallback_used": True,
                    "error": "generation_provider_unavailable",
                }
            last_report = validate_generated_text(output, packet)
            analysis = last_report.pop("analysis", None)
            if last_report.get("valid"):
                return analysis, {**last_report, "attempts": attempt + 1, "fallback_used": False}
        fallback = deterministic_fallback(packet, "generation_validation_failed")
        return fallback, {**last_report, "attempts": self.max_repairs + 1, "fallback_used": True}
