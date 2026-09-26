# Demo walkthrough

Configure the three Bailian values in `.env`, then follow the root README. The API Demo needs no GPU or classifier weights; live requests consume provider quota.

1. Select **01 · 盗窃与退赔** and run Analyze Case.
2. Inspect illustrative classifier scores and BM25 / Dense / RRF / Reranker rankings.
3. Inspect Qwen-Plus output, allowed Evidence IDs, generation status and validation.
4. Try **02 · 取财方式存疑** for competing charge candidates.
5. Try **03 · 信息不足** for skipped retrieval and a request for additional evidence.
6. Edited facts do not reuse preset classifier scores; Full Mode is required for arbitrary-input classification.

All statute summaries await source/date verification. They are excluded from generation evidence. Every API Demo output must withhold legal conclusions and require review.

`cases/` contains synthetic fixtures. `expected_outputs/` and checked-in `evaluation/results.json` / `outputs.jsonl` contain **mock API contract outputs**, not live Bailian predictions. Result screenshots are visibly labelled mock previews. These artifacts verify implementation flow, not legal or model quality.
