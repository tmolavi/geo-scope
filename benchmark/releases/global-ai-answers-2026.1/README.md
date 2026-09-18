# Global AI Answers Benchmark 2026 (`global-ai-answers-2026.1`)
**Measuring How Generative AI Systems Respond to Human Concerns Across Regions**

## Overview
This benchmark release contains live, empirical observations of major generative AI answer engines and foundation models answering real human questions across 7 essential concern categories and 7 global regions in 9 languages.

- **Status**: Live Benchmark (Peer-Review Ready)
- **Dataset ID**: `global-ai-answers-2026.1`
- **Execution Mode**: `live` (Via Hamzad AI Gateway)
- **Date**: 2026-09-18
- **Cryptographic Verification**: SHA-256 integrity manifest

---

## Lineage & Infrastructure
- **Question Discovery**: AnswerPath GEO (Cultural & intent-mined query clusters)
- **Measurement Engine**: GEO-Scope 0.2.0 (Deterministic entity parsing & observation schema)
- **Model Execution Layer**: Hamzad AI Gateway (`https://api.molavi.pro`)

---

## Scope & Dataset Dimensions
- **Prompts**: 34 culturally localized prompts
- **Categories (7)**:
  1. `learning_skills`
  2. `career_migration`
  3. `business_entrepreneurship`
  4. `technology_adoption`
  5. `personal_finance`
  6. `health_lifestyle`
  7. `education`
- **Regions (7)**: Middle East, North America, Europe, Asia, Africa, Latin America, Global
- **Languages (9)**: Arabic (`ar`), German (`de`), English (`en`), Spanish (`es`), Persian (`fa`), French (`fr`), Japanese (`ja`), Portuguese (`pt`), Chinese (`zh`)
- **Providers & Models (4)**:
  - `hamzad_gemini` (`gemini-2.5-flash` | Answer Engine / Search Grounded)
  - `hamzad_perplexity` (`sonar-pro` | Answer Engine / Search Grounded)
  - `hamzad_openai` (`gpt-4o-mini` | LLM / Parametric)
  - `hamzad_claude` (`anthropic/claude-3.5-sonnet` | LLM / Parametric)
- **Entities Tracked (24 Multi-Type Entities)**:
  - Companies: Google, Microsoft, OpenAI, Anthropic, Apple, Amazon, LinkedIn, NVIDIA, Meta
  - Countries/Destinations: Germany, Canada, United Arab Emirates, United States, Singapore, Australia
  - Products & Technologies: Python, Docker, PyTorch, ChatGPT
  - Platforms & Organizations: GitHub, Coursera, edX, Kaggle, World Health Organization, MIT

---

## Dataset Files
- `manifest.json`: Benchmark metadata, schema parameters, provider matrix, and file inventory.
- `prompts.jsonl`: Complete 34 prompt specifications with intent categorization, language, and cultural localization notes.
- `prompts/global.jsonl`: Cross-regional baseline human inquiry prompts.
- `prompts/regional.jsonl`: Culturally and regionally adapted inquiries across North America, Europe, Middle East, Asia, Latin America, and Africa.
- `entities.json`: Multi-type entity catalog with aliases and `do_not_confuse` homonym disambiguation rules.
- `raw_responses.jsonl`: Raw, unedited model outputs with execution latency, timestamps, and model hashes.
- `observations.jsonl`: Deterministically extracted entity mentions, positions, sentiment context, and confidence scores.
- `citations.jsonl`: Extracted and grounded URL citations from answer engine providers.
- `metrics.json`: Aggregated mention rates, category visibility distributions, regional cross-tabulations, and provider breakdowns.
- `errors.jsonl`: Transparent log of provider timeouts, status codes, and transient errors.
- `checksums.sha256`: SHA-256 hashes of all files in the release bundle.
- `methodology.md`: Complete scientific methodology and operational protocol.

---

## Reproducibility & Verification
To verify the cryptographic integrity of this benchmark bundle:

```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1
```

To recompute all metrics deterministically from raw observations:

```bash
geo-scope benchmark reproduce --dataset benchmark/releases/global-ai-answers-2026.1
```

---

## Scientific & Epistemic Boundaries
- **No Global Winner**: This study does not rank "best country", "smartest human", or "best company".
- **No Algorithm Claims**: This benchmark measures observed output distributions; it does not claim to reverse-engineer proprietary black-box ranking algorithms.
- **Empirical Observation**: Results reflect the specific model checkpoints and execution window (September 2026).
