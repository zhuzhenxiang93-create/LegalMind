# Full Demo

Full Mode reuses `LegalMindPipeline`, the BF16 classifier, charge-partitioned retrieval, temporal statute filtering, Evidence Packet and OpenAI-compatible generation. This release exercised mocked provider/component tests and the CPU Lite flow; it did not run the external BF16 checkpoint or paid generation service.

## Assets

Provide your licensed Qwen3-4B base, the matching `checkpoint-7500` adapter, **its** 202-label mapping and **its** Validation-calibrated thresholds. Do not reuse thresholds from the historical 10K classifier. The adapter must save the `score` head.

Provide locally built `ChargePartitionedRetriever` and `LexicalBM25Index` statute directories. Only trusted local indexes should be loaded: historical index serialization uses pickle. The statute index must contain verified official-source metadata and applicable effective/expiry dates. Merely downloading an official page does not establish verified legal validity.

```bash
python -m pip install -e '.[demo,train,retrieval,generation,sentencing]'
cp .env.example .env
# Edit .env with local asset locations and provider credentials.
set -a
. ./.env
set +a
legalmind analyze --fact "此处填入匿名化案件事实" --as-of-date 2026-01-01
```

`train` retains historical QLoRA optional dependencies. BF16 inference does not require quantization; a minimal inference environment can instead install `torch transformers peft accelerate scikit-learn joblib rank-bm25 requests` alongside `.[demo,generation]`. Pin versions to the checkpoint's training environment for scientific reproduction.

For the UI, run `uvicorn legalmind.demo.api:app --host 127.0.0.1 --port 8000`, then the frontend as documented in README. Full Mode becomes selectable after required environment variables and paths exist. This is an asset preflight, not proof that model loading has succeeded. The Full response is shown in the structured result view with actual classification, evidence, generation validation and timings.

Model loading is lazy and cached once per process. Restart after changing assets. Full mode errors never substitute preset output. Missing assets return HTTP 503; provider generation failures produce an explicit validated abstention envelope. The server does not persist user facts.

## Building local indexes

Review available arguments before building from privately held, authorized source data:

```bash
python scripts/build_partitioned_case_index.py --help
python scripts/build_statute_bm25.py --help
```

The public release includes no case corpus, weights or distributable adapter. Data provenance remains `legacy_local_file_unverified`; resolve licensing before any redistribution.

## Experimental Hybrid

`configs/pipeline/hybrid.experimental.yaml` demonstrates the existing BM25 + Dense → RRF → Reranker route. Configure its index and credentials and invoke:

```bash
legalmind analyze --config configs/pipeline/hybrid.experimental.yaml \
  --fact "匿名化案件事实" --as-of-date 2026-01-01
```

This is a research configuration route and may explicitly degrade to sparse retrieval. Inspect `initialization_warnings`; do not label a fallback as successful Hybrid. Real Hybrid E2E needs external assets and remains unverified in this release.

## Docker boundary

`docker compose up --build` runs CPU Demo Lite only. To containerize Full Mode, extend the backend with inference dependencies and mount your private assets read-only; inject `.env` at runtime. The provided Lite image deliberately includes no GPU runtime or credentials. Full container execution has not been tested.
