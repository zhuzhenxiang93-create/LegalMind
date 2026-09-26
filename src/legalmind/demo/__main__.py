import argparse

from legalmind.demo.assets import CASES
from legalmind.demo.service import AnalyzeRequest, analyze_lite

parser = argparse.ArgumentParser(
    description="LegalMind-RAG Bailian API / Precomputed Classification"
)
parser.add_argument("--case", choices=[c["id"] for c in CASES], default="clear-theft")
parser.add_argument("--as-of-date", default="2026-01-01")
args = parser.parse_args()
case = next(c for c in CASES if c["id"] == args.case)
print(
    analyze_lite(AnalyzeRequest(fact=case["fact"], as_of_date=args.as_of_date)).model_dump_json(
        indent=2
    )
)
