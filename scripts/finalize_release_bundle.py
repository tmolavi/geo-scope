import json
import os
from pathlib import Path
from geo_scope.benchmark.hasher import write_checksums_file, verify_dataset_checksums

release_dir = Path("benchmark/releases/global-ai-answers-2026.1")
prompts_dir = release_dir / "prompts"
prompts_dir.mkdir(exist_ok=True)

# 1. Split prompts into global.jsonl and regional.jsonl
global_prompts = []
regional_prompts = []

with open(release_dir / "prompts.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            p = json.loads(line)
            if p.get("region") == "global":
                global_prompts.append(p)
            else:
                regional_prompts.append(p)

with open(prompts_dir / "global.jsonl", "w", encoding="utf-8") as f:
    for p in global_prompts:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open(prompts_dir / "regional.jsonl", "w", encoding="utf-8") as f:
    for p in regional_prompts:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# 2. Write benchmark/releases/global-ai-answers-2026.1/README.md
readme_content = """# Global AI Answers Benchmark 2026 (`global-ai-answers-2026.1`)
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
"""

with open(release_dir / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

# 3. Write benchmark/releases/global-ai-answers-2026.1/methodology.md
methodology_content = """# Global AI Answers Benchmark 2026: Methodology

## 1. Research Question
When people worldwide query leading generative AI systems regarding critical life decisions—such as acquiring skills, international career migration, founding a digital business, managing personal finances, adopting emerging technology, and educational pathways—**what entities, organizations, platforms, and recommendations are surfaced?**

---

## 2. Epistemic Principles & Anti-Hype Constraints
1. **Empirical Measurement, Not Algorithm Deconstruction**: We observe and record model responses as emitted; we make no unsubstantiated claims regarding inner weights or proprietary ranking mechanics.
2. **Value-Neutral Multi-Type Extraction**: Entities are classified across organizations, technologies, destinations, platforms, and products without normative scoring or judgment.
3. **Cultural Adaptation Over Literal Translation**: Inquiries were localized to reflect authentic socioeconomic contexts rather than robotic word-for-word translation.
4. **Homonym Disambiguation**: The entity parser enforces `do_not_confuse` filters to prevent false positive entity attribution.
5. **Separation of Search Grounding from Parametric Memory**: Providers are categorized into `answer_engine` (search-grounded real-time engines) and `llm` (parametric completion models) to isolate web retrieval effects from internal parametric knowledge.

---

## 3. Sampling & Matrix Design
- **Categories (7)**:
  - `learning_skills`: Foundational programming, data science, and AI tool adoption.
  - `career_migration`: Global mobility, work visas, and talent attraction hubs.
  - `business_entrepreneurship`: Low-capital online ventures, scalable SaaS, and digital services.
  - `technology_adoption`: Generative AI tools and enterprise software workflows.
  - `personal_finance`: Diversified index investing, inflation hedging, and wealth preservation.
  - `health_lifestyle`: Burnout prevention, ergonomics, and evidence-based knowledge worker routines.
  - `education`: University degree vs. self-directed portfolio learning paths.
- **Geographic Dimensions (7)**: Middle East, North America, Europe, Asia, Africa, Latin America, and Global.
- **Languages (9)**: Arabic, German, English, Spanish, Persian, French, Japanese, Portuguese, Chinese.
- **Models Evaluated**:
  - `gemini-2.5-flash` (via Hamzad Gateway `hamzad_gemini`)
  - `sonar-pro` (via Hamzad Gateway `hamzad_perplexity`)
  - `gpt-4o-mini` (via Hamzad Gateway `hamzad_openai`)
  - `anthropic/claude-3.5-sonnet` (via Hamzad Gateway `hamzad_claude`)

---

## 4. Execution & Parser Pipeline
1. **Execution**: Prompts are dispatched sequentially to the Hamzad AI Gateway. Raw completions, status codes, latency, and HTTP metadata are logged directly to `raw_responses.jsonl`.
2. **Normalization & Extraction**: The `ObservationParser` scans response tokens with Unicode-aware boundary matching, Persian character normalization, alias resolution, and homonym exclusion.
3. **Metric Formulation**:
   $$\\text{Mention Rate} = \\frac{\\sum_{i=1}^N \\mathbb{I}(\\text{Entity} \\in \\text{Response}_i)}{N}$$
   $$\\text{Share of Observed Visibility (SOV)} = \\frac{\\text{Total Mentions of Entity}}{\\sum_{e \\in E} \\text{Total Mentions of } e}$$

---

## 5. Limitations & Future Work
- Snapshot observations reflect model versions active in September 2026.
- Temperature and sampling parameters introduce slight response variance across runs.
- Subsequent iterations will expand the query set to longitudinal tracking across seasonal hiring and educational cycles.
"""

with open(release_dir / "methodology.md", "w", encoding="utf-8") as f:
    f.write(methodology_content)

# 4. Write Checksums
write_checksums_file(str(release_dir))
result = verify_dataset_checksums(str(release_dir))
print("Final Release Verification:", result)
