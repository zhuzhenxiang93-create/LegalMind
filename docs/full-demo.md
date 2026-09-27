# Full Demo

Full Mode reuses `LegalMindPipeline`, the BF16 classifier, strict Hybrid retrieval, temporal statute filtering, Evidence Packet and OpenAI-compatible generation. This release exercised mocked provider/component tests through mocked HTTP transport; the API Demo subsequently passed a three-preset live Bailian check. Full BF16/private-corpus execution remains unverified.

## Assets

Provide your licensed Qwen3-4B base, the matching `checkpoint-7500` adapter, **its** 202-label mapping and **its** Validation-calibrated thresholds. Do not reuse thresholds from the historical 10K classifier. The adapter must save the `score` head.

Provide locally built `HybridIndex` and `LexicalBM25Index` statute directories. Only trusted local indexes should be loaded: historical index serialization uses pickle. The statute index must contain verified official-source metadata and applicable effective/expiry dates. Merely downloading an official page does not establish verified legal validity.

```bash
python -m pip install -e '.[demo-hybrid,train,retrieval,generation,sentencing]'
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

## Default Hybrid

`LEGALMIND_HYBRID_INDEX` must point to a saved HybridIndex built with `embedding_provider: api`, the configured `text-embedding-v4` model and 1,024 dimensions. Rebuild old local/Qwen embedding indexes: vectors from different models cannot be mixed. Configure Bailian as described in [Hybrid setup](hybrid-demo.md). Full Mode uses `qwen3-rerank` and `qwen-plus` through the same backend credentials.
The default `full_config()` and `configs/pipeline/default.yaml` require Hybrid and a reranker. Missing components raise an explicit error, with no sparse fallback. The legacy filename `hybrid.experimental.yaml` is retained for compatibility; it now also uses strict Hybrid. Research configurations can still explicitly opt into older fallback behavior, but the recruiting default cannot.

A full Qwen/private-corpus run still requires separately provided weights, index and credentials. Offline tests verify the HTTP contracts and retrieval algorithms using synthetic provider responses. The API Demo live check is documented separately; private-corpus quality remains unverified.

## Docker boundary

`docker compose up --build` runs the Bailian API Demo with `.env` injected at runtime. The image needs no local retrieval weights or GPU. To containerize Full Mode, add inference dependencies and mount private assets read-only. Container execution has not been verified locally.
