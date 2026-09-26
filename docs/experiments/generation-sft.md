# Historical generation SFT

The project includes Qwen3-4B generation-SFT smoke experiments for JSON adherence and abstention. They used small automatic/unreviewed targets and did not establish legal reliability. Historical configurations and reports remain available for research reproducibility.

Generation SFT is not loaded by the recruiting Demo or the default Full pipeline. Current Full generation uses a configurable strong OpenAI-compatible model, strict Pydantic output contracts and grounding checks. The API Demo also uses Qwen-Plus; provider failures use an explicitly labelled safe fallback.
