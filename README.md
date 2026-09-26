# LegalMind-RAG

**Evidence-Grounded Criminal Case Analysis with Qwen3-4B LoRA, Hybrid Retrieval and Controlled LLM Generation**

A research prototype that turns anonymized case facts into candidate charges, traceable case evidence and a reviewable structured response. **The default retrieval is charge-aware BM25; Hybrid is experimental.**

![Training cases](https://img.shields.io/badge/training_cases-120K%2B-254c76)
![Charge labels](https://img.shields.io/badge/charge_labels-202-254c76)
![Validation](https://img.shields.io/badge/Validation_Micro--F1-91.50%25-4c75ad)
![Outputs](https://img.shields.io/badge/outputs-evidence--grounded-557b74)
[![CI](https://github.com/zhuzhenxiang93-create/RAG/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/zhuzhenxiang93-create/RAG/actions/workflows/ci.yml)

![LegalMind-RAG evidence workspace — actual Demo Lite screenshot](demo/assets/hero.png)

[Try the demo](#quick-start) · [Architecture](docs/architecture.md) · [Evaluation](docs/evaluation.md) · [Full Mode](docs/full-demo.md)

## Why LegalMind-RAG?

Charge classification alone leaves the reviewer without supporting evidence. Free-form generation makes it difficult to inspect where a claim came from. This prototype connects domain classification, charge-constrained retrieval, explicit Evidence IDs and validation, while exposing uncertainty and missing information.

**For recruiters:** try the three scenarios, inspect Pipeline Trace, then open Evaluation. This takes about three minutes. No GPU, API key or private dataset is needed for Demo Lite.

## Product Demo

- **Clear facts:** theft, restitution and a forgiveness statement; view synthetic case matches.
- **Competing charges:** theft / snatching / robbery; inspect candidate ambiguity and missing facts.
- **Insufficient facts:** see abstention and a request for more information.

The UI explicitly displays **Demo / Precomputed Mode**. Scores are manually authored illustrative fixtures, **not outputs from the trained checkpoint**. BM25 retrieval, Pydantic parsing, Evidence-ID checks and the review decision execute locally. Generation is deterministic. Edited/free-text inputs never inherit preset scores.

Demo statute summaries have a recorded official-source URL but have **not** been verified against a dated authoritative text. All Lite scenarios therefore withhold legal/sentencing conclusions and require review. This is a transparent walkthrough of the workflow, not a validated legal answer demo.

## What It Does

1. Full Mode loads the Qwen3-4B **BF16 LoRA** classifier to predict candidate charges.
2. Candidate charges constrain the case retrieval space.
3. Case and applicable statute evidence form an Evidence Packet.
4. A configurable OpenAI-compatible model generates structured analysis.
5. Pydantic, Evidence-ID membership, evidence types, statute metadata and privacy patterns are checked.
6. Failures or incomplete support produce abstention / manual review.

## Architecture

```mermaid
flowchart TD
    A[Anonymized case facts] --> B[BF16 LoRA classifier]
    B --> C[Charge-aware case retrieval]
    C --> D[Default: partitioned BM25]
    C -. Optional .-> E[Experimental: Dense + BM25 / RRF / Reranker]
    D --> F[Evidence Packet]
    E --> F
    G[Dated statute retrieval] --> F
    F --> H[OpenAI-compatible generation]
    H --> I[Pydantic + citation + statute validation]
    I --> J[Structured response / manual review]
```

Lite replaces classification with preset fixtures and generation with extractive deterministic output. Full Mode uses the existing research pipeline; it requires external assets. See [runtime boundaries](docs/architecture.md).

## Quick Start

### Demo Lite: one command with Docker

```bash
git clone https://github.com/zhuzhenxiang93-create/RAG.git LegalMind-RAG
cd LegalMind-RAG
docker compose up --build
```

Open **http://localhost:8080**. Docker configuration is supplied; container startup was not executed in the build environment because Docker was unavailable. Native backend, frontend build and browser flow were tested.

### Native development

Python 3.10+ and Node 22+:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[demo]'
uvicorn legalmind.demo.api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd app/frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open **http://localhost:5173**. The development server proxies `/api` to the backend. A terminal-only walkthrough also works:

```bash
python -m legalmind.demo --case clear-theft --as-of-date 2026-01-01
```

## Example Input / Output

Input: a manually constructed account of an adult secretly taking a shop's phone, later returning it, compensating the loss and obtaining a forgiveness statement.

Output includes candidate charge fixture scores, three synthetic BM25 matches, unverified article summaries, cited Evidence IDs, a six-stage trace and a clear manual-review decision. Inspect the [complete output](demo/expected_outputs/clear-theft.json). Historical sentences and fines in Lite are invented interface examples; the system does not recommend them for the input case.

## Charge Classification

**Qwen3-4B + BF16 LoRA**, 202-label multi-label classification with `BCEWithLogitsLoss`.

| Training configuration | Value |
|---|---:|
| Training cases | 120,468 |
| Epochs / micro batch / gradient accumulation | 2 / 8 / 4 |
| Effective batch / optimizer updates | 32 / 7,530 |
| Best checkpoint | checkpoint-7500 |
| Max tokens / truncation | 2,048 / Head-Tail |
| LoRA r / alpha / dropout | 16 / 32 / 0.05 |
| Target modules / saved head | all-linear / score |
| Trainable parameters | ≈33,547,264 (≈0.827%) |
| Peak GPU memory | ≈15.95 GiB |

Dynamic padding, token-length bucketing and gradient checkpointing are implemented. Training/results above are the project owner's supplied run record; weights and the complete BF16 evaluation artifact are not redistributed here. Historical QLoRA experiments remain in the research archive and are not the current classifier.

## Retrieval

**Default Full Mode:** charge-partitioned BM25 with existing factual reranking and up to three case matches. **Lite:** live character-bigram BM25 over six synthetic records, constrained to demo candidate charges.

**Experimental:** BM25 + Dense → RRF → Reranker. Implemented in `src/legalmind/retrieval/` and covered by component tests. No real model/index/API E2E was available in this release environment, so `configs/pipeline/hybrid.experimental.yaml` is optional and is not advertised as a validated default. Synthetic or stub retrieval tests do not establish real legal relevance.

## Grounded Generation

Full Mode builds an Evidence Packet and calls an OpenAI-compatible API (`qwen-plus` by default). Configure `GENERATION_BASE_URL`, `GENERATION_API_KEY` and `GENERATION_MODEL`. Standard request fields are used unless a research configuration explicitly enables provider-specific `top_k`.

Invalid output gets at most one repair. Provider errors or repeated validation failures return an explicit low-confidence fallback. Historical [generation SFT](docs/experiments/generation-sft.md) is outside the default pipeline. The traditional sentencing model remains a research baseline / sanity check, disabled by default.

## Safety & Reliability

- Strict Pydantic schema and evidence membership/type checks.
- Official-source domain and recorded verification-status checks; applicability uses supplied effective/expiry dates.
- Missing verified legal support blocks an `analyzed` generation result.
- Pattern-based privacy redaction; this is not comprehensive anonymization.
- Candidate probabilities are not legal certainty; thresholds require matching validation calibration.
- Citation validation checks provenance and structure, **not semantic entailment or legal correctness**.

## Evaluation

| Metric | **Validation** result |
|---|---:|
| Micro-F1 | 0.9150 |
| Macro-F1 | 0.8394 |
| Micro Precision | 0.9311 |
| Micro Recall | 0.8995 |
| Hamming Loss | 0.001027 |

**Independent BF16 test evaluation pending corrected evaluator run.** No corrected independent BF16 test artifact was found in the audited branches. Do not present these Validation numbers as Test results.

The [30-request synthetic demo regression](demo/evaluation/results.json) checks schema, citations and fail-closed behavior. It is **not a human-reviewed legal benchmark**. All requests are expected to abstain; review selectivity and useful legal answering are not measured. See [evaluation scope and results](docs/evaluation.md).

## Current vs Experimental

| Component | Status |
|---|---|
| Qwen3-4B BF16 LoRA | Implemented; external checkpoint required |
| Charge-aware BM25 | Default Full route; component-tested |
| Hybrid / RRF / Reranker | Implemented, experimental; real E2E unverified |
| Statute retrieval and temporal filters | Implemented; verified source metadata required |
| Evidence Packet / OpenAI-compatible generation | Implemented; provider tests use mocks |
| Pydantic / Evidence-ID whitelist | Implemented and regression-tested |
| Recruiting Web UI / Lite | Implemented and browser-tested |
| Generation SFT | Historical / experimental |
| Traditional sentencing model | Research baseline, disabled by default |
| Long-text sliding window | Planned |
| Human-reviewed legal benchmark | Planned |

## Repository Structure

```text
app/                    Frontend and backend container definitions
src/legalmind/demo/     Lite service, FastAPI and strict Full Mode adapter
src/legalmind/          Classification, retrieval, generation, data and baseline modules
demo/                   Synthetic cases, expected outputs, screenshots and evaluation
configs/                Research configurations; Hybrid is explicitly experimental
docs/                   Architecture, evaluation, full reproduction and historical notes
scripts/                Training, indexing and evaluation entry points
tests/                  Component, contract and demo regression tests
.github/workflows/      Python and frontend CI
```

## Full Reproduction

Use [Full Mode setup](docs/full-demo.md) for the matching base model, adapter, label mapping, calibrated thresholds, case index, statute index and API configuration.

```bash
legalmind analyze --fact "匿名化案件事实……" --as-of-date 2026-01-01
```

Full Mode fails explicitly if required assets are absent. Lite remains available independently.

## Data Governance & Limitations

**Training data is not redistributed by this repository.** The inherited CAIL-derived source is recorded as `legacy_local_file_unverified`; the source/license chain needs verification before redistribution or adapter release. Full model artifacts are not redistributed. Public demo cases are authored synthetic fixtures.

The prototype is not deployed as a public production service. It lacks a human-reviewed legal benchmark, demonstrated legal-answer reliability, broad privacy guarantees, hosted GPU inference and live Hybrid E2E validation. The demo is intentionally conservative about statute provenance. Old documents under `reports/` and research notes describe historical runs; this README and the release audit define the recruiting release.

## Roadmap

- Re-run and publish corrected independent BF16 test artifacts.
- Verify dated statute snapshots and evaluate useful answers as well as abstention.
- Validate real Hybrid E2E against default BM25 on reviewed relevance judgments.
- Add long-text sliding-window inference and calibrated review thresholds.

## Disclaimer

**Research / decision-support prototype, not legal advice.** Outputs do not constitute judicial decisions, sentencing recommendations or professional legal advice.
