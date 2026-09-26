# Demo walkthrough

Start from the Quick Start in the root README. No GPU, checkpoint, training corpus or API key is needed.

1. Select **01 · 盗窃与退赔**, click **Analyze Case**, inspect candidate fixture scores and three synthetic BM25 matches.
2. Open Evidence IDs and Pipeline Trace. Classification is illustrative/precomputed; retrieval and validators run live.
3. Select **02 · 取财方式存疑** to see competing candidates and requested missing facts.
4. Select **03 · 信息不足** to see no retrieval and legal abstention.
5. Edit the fact: preset predictions disappear because the fixture no longer matches.
6. Open Structured JSON to inspect the full response.

All statute summaries are pending source/date verification, so every Lite example requires review and withholds legal conclusions. Full Mode requires independently supplied assets; see `docs/full-demo.md`.

`cases/` contains authored fixtures, `expected_outputs/` example responses, `evaluation/` the synthetic regression and `assets/` actual browser screenshots. Sentence and fine values are invented case-card examples. The recorded official-source URL does not itself mean a statute is verified.
