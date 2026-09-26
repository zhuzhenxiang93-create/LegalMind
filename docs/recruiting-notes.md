# Recruiting notes

## Suggested resume bullets

- Designed LegalMind-RAG, an evidence-grounded criminal-case research prototype connecting domain charge classification, charge-aware retrieval, structured generation and explicit human-review decisions.
- Trained Qwen3-4B with BF16 LoRA for 202-label classification on 120,468 cases; recorded Validation Micro-F1 0.9150 and Macro-F1 0.8394, with separate independent Test verification pending.
- Productized a GPU-free React/FastAPI demonstration with evidence cards, execution trace and schema/citation checks; added a 30-request synthetic regression and 150 passing component/contract tests, while clearly separating illustrative fixtures from real model inference.

Do not describe fixture scores as model predictions, synthetic checks as legal accuracy, BM25 scores as confidence, or experimental Hybrid as verified Full E2E. Traditional sentencing remains a disabled research baseline.

Use the default `main` URL for recruiting. After the owner renames the repository, the preferred link is `https://github.com/zhuzhenxiang93-create/LegalMind-RAG`. Until that rename is completed, the working URL is `https://github.com/zhuzhenxiang93-create/RAG`.

Recommended hero: `demo/assets/hero.png`, captured from the actual web app. It shows the product context, Validation labels, case input and synthetic evidence. The mobile capture provides a secondary responsive-layout example.
