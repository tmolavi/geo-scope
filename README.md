<div align="center">

# ⟠ GEO-Scope

### Empirical AI Answer Visibility Measurement Framework

**An open-source framework for empirical measurement of AI answer visibility, entity mentions, recommendations, and citations across generative AI systems.**

[![Language](https://img.shields.io/badge/Language-English-blue)](#)
[![فارسی](https://img.shields.io/badge/فارسی-README.fa.md-green)](README.fa.md)
[![Türkçe](https://img.shields.io/badge/T%C3%BCrk%C3%A7e-README.tr.md-red)](README.tr.md)
[![Azərbaycan](https://img.shields.io/badge/Az%C9%99rbaycan-README.az.md-orange)](README.az.md)
[![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README.ar.md-teal)](README.ar.md)

[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Scientific Foundation](https://img.shields.io/badge/Scientific%20Foundation-v1.0%20Published-darkgreen)](docs/SCIENTIFIC_FOUNDATION_V1.md)
[![Measurement Contract](https://img.shields.io/badge/Measurement%20Contract-v1.0-informational)](docs/measurement-contract-v1.md)
[![Research Paper Outline](https://img.shields.io/badge/Research-Paper%20Outline-purple)](docs/RESEARCH_PAPER_OUTLINE.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)
[![Security Audit](https://img.shields.io/badge/Security-Audit%20Passed-success)](docs/SECURITY_AUDIT.md)

[PyPI package](https://pypi.org/project/geo-scope/) · [Hugging Face demo](https://huggingface.co/spaces/taqimolavi/geo-scope)

[Introduction](#1-introduction) • [What It Measures](#2-what-geo-scope-measures) • [Scientific Foundation](#6-measurement-contract-v1--scientific-foundation) • [Benchmarks](#7-published-benchmark-releases) • [Reproducibility](#8-reproducibility--auditability) • [Research](#9-research--documentation) • [Quickstart](#10-installation--usage) • [MCP](#11-model-context-protocol-mcp)

</div>

---

## شروع خیلی ساده (برای تیم)

GEO-Scope پاسخ‌های یک یا چند موتور هوش مصنوعی را بررسی می‌کند و پنج چیز را جداگانه گزارش می‌دهد: آیا نام شما آمده، آیا پیشنهاد شده، آیا لینک یا citation داده شده، آیا مطلبی به شما نسبت داده شده و آیا در فهرست رتبه گرفته‌اید.

### نکته‌ی مهم درباره‌ی نیازمندی‌ها

خود موتور به‌تنهایی کلید API ندارد و چیزی را جعل نمی‌کند. برای یک تست بدون هزینه و بدون اینترنت از حالت `simulation` یا `replay` استفاده کنید. برای `live` باید خودتان دسترسی و کلید ارائه‌دهنده‌ی موردنظر را تنظیم کنید؛ Hugging Face، ZeroGPU و «LLM رایگان نامحدود» جزو نیازمندی‌های این بسته نیستند.

### نصب و اولین تست بدون کلید

```bash
pip install geo-scope
geo-scope demo
```

این دستور یک **SIMULATION FIXTURE** می‌سازد؛ یعنی برای یادگیری و بررسی فرمت خروجی است و به مدل زنده وصل نمی‌شود. بنابراین عددهای آن را گزارش واقعی بازار یا رتبه‌ی برند ندانید.

### چهار واژه‌ای که باید بدانید

- `simulation`: اجرای آزمایشی قطعی و بدون تماس با مدل.
- `live`: اجرای واقعی با provider و هزینه/کلید همان provider.
- `replay`: تحلیل دوباره‌ی پاسخ‌های ذخیره‌شده، کاملاً آفلاین.
- `citation`: لینکی که موتور پاسخ به‌عنوان منبع نشان داده؛ با «ذکر نام» یکی نیست.

### اجرای واقعی با مدل Hugging Face (اختیاری)

دموی عمومی Space عمداً بدون کلید و بدون GPU کار می‌کند و خروجی آن fixture
قطعی است. برای یک اندازه‌گیری زنده با مدل متن‌باز، کلید حساب خودتان را فقط
در محیط محلی بگذارید:

```bash
pip install geo-scope
export HF_TOKEN="hf_..."
# در صورت نیاز مدل قابل‌دسترسی حساب/ارائه‌دهنده را انتخاب کنید
export HF_MODEL="Qwen/Qwen2.5-7B-Instruct"
geo-scope measure \
  --entities examples/public_demo/brands.json \
  --prompts examples/public_demo/prompts/observed.jsonl \
  --providers huggingface_inference \
  --mode live \
  --out-dir output/hf-live
```

`hf`، `huggingface` و `huggingface_inference` نام‌های قابل‌استفاده‌اند. این
provider پاسخ مدل را می‌سنجد، اما web search یا citation واقعی به آن اضافه
نمی‌کند؛ بنابراین citationهای خروجی را فقط وقتی گزارش کنید که خود مدل واقعاً
لینک داده باشد. کلید را در README، فایل Space، issue، commit یا لاگ قرار
ندهید. اعتبار رایگان Hugging Face محدود و وابسته به سیاست فعلی حساب است؛
«رایگان نامحدود» وعده‌ی فنی قابل‌اتکایی نیست. برای استفاده‌ی بدون هزینه‌ی
ابری، از `simulation`/`replay` یا یک مدل محلی با Ollama استفاده کنید.

- [ساخت توکن Hugging Face](https://huggingface.co/settings/tokens)
- [قیمت و اعتبار Inference Providers](https://huggingface.co/docs/inference-providers/pricing)
- [دموی عمومی GEO-Scope](https://huggingface.co/spaces/taqimolavi/geo-scope)
- [Molavi.pro](https://molavi.pro)

اگر هدف فقط یادگیری است، از `demo` شروع کنید. اگر هدف اندازه‌گیری واقعی visibility است، ابتدا یک فایل entity و یک فایل prompt آماده کنید، provider را تنظیم کنید و بعد `live` را اجرا کنید. بدون پاسخ واقعی provider، GEO-Scope ادعای visibility نمی‌کند. [راهنمای فارسی](README.fa.md) برای مثال‌های تیمی آماده است.

## 1. Introduction

Generative AI systems and search-grounded answer engines are rapidly becoming the primary discovery layer for users seeking products, vendors, services, and factual insights. 

**GEO-Scope** is an evidence-first, open-source measurement framework designed to empirically quantify and preserve auditable evidence of how generative AI systems surface entities. It records, normalizes, and analyzes observable AI completions under documented, neutral prompt sets without relying on speculative ranking algorithms or ungrounded claims.

### Core Observable Outputs Measured:
- **Entity Mentions**: Observable presence of brands, products, technologies, and public figures in generated text.
- **Recommendations**: Explicit linguistic endorsements and ordered top-position recommendations.
- **Citations**: Grounding source URLs and referenced web domains returned by search-augmented models.
- **Attribution**: Textual credit linking specific facts, statistics, or claims to source entities.
- **Provider Differences**: Distributional shifts between live search-grounded answer engines and parametric foundation LLMs.
- **Multilingual Behavior**: Cross-lingual response variations across 26+ evaluated languages.

---

## 2. What GEO-Scope Measures

GEO-Scope enforces a strict taxonomic separation between four independent visibility dimensions:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI RESPONSE VISIBILITY MATRIX                    │
├───────────────────┬─────────────────────────────────────────────────────┤
│ Mention           │ Did the entity appear anywhere in the completion?   │
│ Recommendation    │ Was the entity explicitly endorsed or recommended?  │
│ Citation          │ Was a source URL or grounding domain link provided? │
│ Attribution       │ Was specific data/claim textually credited to it?  │
│ Rank              │ Extracted ONLY when a valid ordered list exists.   │
└───────────────────┴─────────────────────────────────────────────────────┘
```

1. **Mention (`mentioned: true/false`)**:
   - Captures whether the target entity (or associated canonical aliases/founders) appeared in the generated completion.
   - Evaluated via Unicode NFKC normalization, Arabic/Persian letter unification, Zero-Width Non-Joiner (ZWNJ) handling, and negative homonym collision filtering.
2. **Recommendation (`recommended: true/false`)**:
   - Strict rule: `mentioned != recommended`.
   - Evaluated based on explicit linguistic recommendation markers (e.g., *"We recommend..."*, *"Top pick"*, *"گزینه پیشنهادی"*) or inclusion in an ordered list answering a recommendation query.
3. **Citation (`cited: true/false`)**:
   - Identifies presence of target entity web domains in grounding references, markdown hyperlinks, or structured provider citation chunks.
4. **Attribution (`attributed: true/false`)**:
   - Distinct from citation: detects explicit textual sourcing phrasing (e.g., *"According to [Entity]..."*, *"طبق گزارش [موجودیت]"*) even if an active URL link was omitted by the model.
5. **Rank (`rank: 1..N | null`)**:
   - Extracted strictly from numbered lists or ordinal items. If an informational question yields an unranked mention, rank is set to `null` to prevent artificial ranking bias.

---

## 3. What GEO-Scope Does NOT Measure

To maintain scientific integrity, GEO-Scope clearly outlines its epistemic boundaries:

- ❌ **It does NOT reverse-engineer internal ranking algorithms**: GEO-Scope observes external API completions; it cannot inspect internal model weights, attention matrices, or proprietary ranking formulas.
- ❌ **It does NOT inspect hidden training data**: Observed entity knowledge reflects generated outputs, not full visibility into private training corpora.
- ❌ **It does NOT claim causal ranking factors**: All reported metrics represent descriptive statistical associations under documented prompts, not causal guarantees.
- ❌ **It does NOT guarantee SEO or AI visibility improvements**: Measurements provide historical observation, not predictive visibility promises.
- ❌ **It does NOT treat simulation as live empirical data**: Simulation fixtures are strictly quarantined for testing and CI.

---

## 4. Architecture

GEO-Scope operates as a modular, six-stage evidence pipeline:

```text
  ┌─────────────────────────────────────────────────────────────┐
  │                       Provider Layer                        │
  │   ┌──────────────────────────┐  ┌────────────────────────┐  │
  │   │  Search Answer Engines   │  │ Parametric Base LLMs   │  │
  │   │  (Perplexity, Gemini...) │  │ (OpenAI, Claude...)    │  │
  │   └──────────────────────────┘  └────────────────────────┘  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                     Measurement Engine                      │
  │     (Prompt Provenance · Zero Silent Fallback · Runs)       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                    Raw Response Storage                     │
  │    (Unparsed API Payloads · Latency · Token Usage)          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                     Observation Parser                      │
  │    (Multi-Lingual Normalizer · Homonyms · Citations)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                     Metrics Calculation                     │
  │    (OMR · Rec Share · Citation Rate · Honest Denominators)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 Reports + Replayable Bundle                 │
  │    (JSONL Bundles · SHA-256 Checksums · Markdown Summaries) │
  └─────────────────────────────────────────────────────────────┘
```

---

## 5. Execution Modes

GEO-Scope provides three mutually exclusive execution modes:

### `demo` (Simulation Fixture)
- **Purpose**: Rapid offline testing, development fixtures, and CI validation.
- **Behavior**: Uses local mock completions with prefixed IDs (`simulated_*`) and a clear simulation banner.
- **Guarantee**: Simulation data is strictly rejected by the release quality gate and can **never** enter published empirical benchmarks.

### `measure` (Live Empirical Execution)
- **Purpose**: Real-world observation runs against live generative AI endpoints.
- **Behavior**: Dispatches neutral prompt bundles to configured API providers with **zero silent fallback**.
- **Preservation**: Saves full unmodified payloads to `raw_responses.jsonl` with exact model governance metadata (`requested_provider`, `actual_provider`, `search_grounded`).

### `replay` (Deterministic Offline Replay)
- **Purpose**: Independent auditability and benchmark verification without API calls or cost.
- **Behavior**: Reruns the observation parser and metric calculations directly against preserved `raw_responses.jsonl`.
- **Integrity**: Verifies that recomputed metrics match published results bit-for-bit.

---

## 6. Measurement Contract v1 & Scientific Foundation

GEO-Scope does not claim universal AI visibility truth. It measures empirical observations under declared, reproducible measurement configurations.

> [!IMPORTANT]
> **Fundamental Measurement Axiom**  
> *"AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."*

- 🏛️ **Scientific Foundation Release v1.0**: [`docs/SCIENTIFIC_FOUNDATION_V1.md`](docs/SCIENTIFIC_FOUNDATION_V1.md)
- 📄 **Full Measurement Contract Specification**: [`docs/measurement-contract-v1.md`](docs/measurement-contract-v1.md)
- ❓ **Why Measurement Contract Exists**: [`docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md`](docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md)
- 📐 **Machine-Readable Schema**: [`schemas/measurement-contract-v1.json`](schemas/measurement-contract-v1.json)
- 🧪 **Validation Example Fixture**: [`examples/measurement-contract-v1-example.json`](examples/measurement-contract-v1-example.json)
- 📊 **Releases & Milestones Timeline**: [`docs/RELEASES.md`](docs/RELEASES.md)

### Core Measurement Principles
1. **Mention Definition**: A response-level binary observation indicating whether the target entity appears at least once in the completion. Multiple mentions in a single answer do **not** artificially inflate response-level mention counts.
2. **Citation Separation**: Strict 4-way separation between `entity_mentioned` in text, `target_domain_cited` (root domain), `target_url_cited` (deep link), and `third_party_source_cited` (external authority/review links). Mention and citation are never treated as equivalent.
3. **Recommendation Semantics**: Evaluated as true only when the model semantically recommends, selects, or endorses the entity. Ambiguous detections are gated and marked `experimental`.
4. **Comparability Rules**: Machine-readable comparability verification. Two studies are marked `comparable: true` only when prompt universe, market/language, provider/model family, measurement definitions, and observation windows match.
5. **Raw Evidence Traceability**: Every public observation is linked to prompt ID, raw response or cryptographic SHA-256 hash (`response_hash_sha256`), extracted entities, citations, and execution configuration hash.

---

## 7. Published Benchmark Releases

GEO-Scope maintains immutable, peer-review-ready benchmark releases under `benchmark/releases/` (see complete [Releases & Milestones Timeline](docs/RELEASES.md)):

| Benchmark Release | Prompt Count | Observations | Providers | Cryptographic Status | Documentation |
|:---|:---|:---|:---|:---|:---|
| [`global-ai-answers-2026.2`](benchmark/releases/global-ai-answers-2026.2/) | 500 prompts (50 countries) | 45,698 obs | 4 models | SHA-256 Verified | [Paper Draft](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md) |
| [`global-ai-answers-2026.2-pilot`](benchmark/releases/global-ai-answers-2026.2-pilot/) | 100 prompts (10 countries) | 8,940 obs | 4 models | SHA-256 Verified | [Pilot Report](docs/GLOBAL_AI_ANSWERS_2026_2_PILOT_REPORT.md) |
| [`global-ai-answers-2026.1`](benchmark/releases/global-ai-answers-2026.1/) | 34 prompts (7 regions) | Baseline obs | 4 models | SHA-256 Verified | [Methodology](docs/global-ai-answers-methodology.md) |
| [`geo-seo-digital-agency-iran-2026.1`](benchmarks/geo-seo-digital-agency-iran-2026.1/) | 30 prompts (5 intent strata) | 120 completions | 4 models | SHA-256 Verified | [Agency Report](benchmarks/geo-seo-digital-agency-iran-2026.1/report.md) |
| [`query-fanout-brand-introduction`](benchmarks/query-fanout-brand-introduction/) | 50 prompts (5 sectors) | 300 brand obs | Grounded AI Search | SHA-256 Verified | [Findings & Methodology](benchmarks/query-fanout-brand-introduction/README.md) |

### Mechanism & Replication Studies
- **[Query Fan-Out Brand Introduction](benchmarks/query-fanout-brand-introduction/)**: Empirical replication test examining whether brands introduced by the engine's internal search/fan-out queries are more likely to appear in the final answer than retrieved-only brands. Across 50 commercial discovery conversations (300 brand observations), engine-introduced brands achieved a **65.7%** mention rate vs **13.1%** for retrieved-only brands (**5.01×** ratio; `REPRODUCED_DIRECTIONALLY`). Intermediate query fan-out tracking is preserved as an experimental diagnostic layer and explicitly excluded from composite visibility scores to avoid causal overreach.

Every release bundle contains:
- `manifest.json`: Dataset metadata, provider matrix, and schema version (`measurement_contract_version: "1.0"`).
- `prompts.jsonl`: Neutral, categorized prompts.
- `raw_responses.jsonl`: Verbatim API completion payloads.
- `observations.jsonl`: Granular extracted observation records.
- `metrics.json`: Aggregated metrics with explicit failure denominators.
- `checksums.sha256`: SHA-256 hashes of all artifacts.

---

## 8. Reproducibility & Auditability

### 1. Cryptographic SHA-256 Verification
Verify that dataset files have not been modified or corrupted:
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
```

### 2. Zero-Network Replay Workflow
Replay metrics directly from preserved raw responses without executing live API calls:
```bash
geo-scope replay \
  --bundle benchmark/releases/global-ai-answers-2026.2 \
  --out-dir output/replay_2026_2
```

### 3. Golden Parser Evaluation
Evaluate the deterministic multi-lingual parser against human-labeled ground truth:
```bash
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

**Golden Set Benchmark Results (`v1`, 220 examples across 5 languages)**:
- **Mention F1**: `99.75%` (Precision: 99.51%, Recall: 100.00%)
- **Recommendation F1**: `100.00%` (Precision: 100.00%, Recall: 100.00%)
- **Citation F1**: `100.00%` (Precision: 100.00%, Recall: 100.00%)
- **Attribution F1**: `91.56%` (Precision: 100.00%, Recall: 84.44%)
- **Wrong Entity (Homonym) F1**: `96.97%`
- **Rank Accuracy**: `100.00%`

---

## 9. Research & Documentation

- 🏛️ **Scientific Foundation Release v1.0**: [`docs/SCIENTIFIC_FOUNDATION_V1.md`](docs/SCIENTIFIC_FOUNDATION_V1.md)
- 📊 **Releases & Milestones Timeline**: [`docs/RELEASES.md`](docs/RELEASES.md)
- 📄 **Measurement Contract v1 Specification**: [`docs/measurement-contract-v1.md`](docs/measurement-contract-v1.md)
- ❓ **Why Measurement Contract Exists**: [`docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md`](docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md)
- 🔬 **Research Methods & Protocol**: [`docs/RESEARCH_METHODS.md`](docs/RESEARCH_METHODS.md)
- 📄 **Research Paper Outline**: [`docs/RESEARCH_PAPER_OUTLINE.md`](docs/RESEARCH_PAPER_OUTLINE.md)
- 🔒 **Open Source Security Audit**: [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md)
- 📊 **Methodology Crosswalk (Public Practice Comparison)**: [`docs/METHODOLOGY_CROSSWALK.md`](docs/METHODOLOGY_CROSSWALK.md)
- 🔬 **Scientific Benchmark Methodology**: [`docs/benchmark-methodology.md`](docs/benchmark-methodology.md)
- 🗺️ **Cross-Repository Evidence Map**: [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md)
- 📐 **Mathematical Formulation & MAVI**: [`docs/MATHEMATICAL_MODEL.md`](docs/MATHEMATICAL_MODEL.md)
- 🔌 **API Integration Guide**: [`docs/API_INTEGRATION.md`](docs/API_INTEGRATION.md)
- 🛡️ **Release Gate Integrity Protocol**: [`docs/SCIENTIFIC_MEASUREMENT_GATE.md`](docs/SCIENTIFIC_MEASUREMENT_GATE.md)

---

## 10. Installation & Usage

### Installation
```bash
# Clone the repository
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Install package in editable mode
pip install -e .
```

### PyPI publishing

The stable package is available at [PyPI](https://pypi.org/project/geo-scope/).
Future releases are published from GitHub Actions through Trusted Publishing;
no PyPI token is stored in the repository.

To publish a new version:

1. Update the version in `pyproject.toml`.
2. Commit and push the release changes to `main`.
3. Create a **published GitHub Release** for the matching version.

The workflow is [`.github/workflows/publish.yml`](.github/workflows/publish.yml)
and uses the `pypi` GitHub environment for `tmolavi/geo-scope`. The PyPI-side
publisher must remain mapped to Owner `tmolavi`, Repository `geo-scope`,
Workflow `publish.yml`, Environment `pypi`.

Do not put a PyPI API token in GitHub secrets or commit it to this repository.

### Quick Commands
```bash
# 1. Run local simulation fixture demo
geo-scope demo

# 2. Execute live empirical measurement (requires API credentials)
geo-scope measure \
  --entities entities/iran-seo-agencies.json \
  --prompts examples/research_run/prompts.jsonl \
  --mode live \
  --providers perplexity_sonar,gemini_grounding \
  --out-dir output/live_run_01

# 3. Deterministic offline replay
geo-scope replay \
  --bundle output/live_run_01 \
  --out-dir output/replay_run_01

# 4. Launch interactive local research dashboard
geo-scope serve --host 127.0.0.1 --port 8000
```

---

## 11. Model Context Protocol (MCP)

GEO-Scope includes a native **MCP Server** (`stdio`), enabling AI coding assistants and agents (Claude Desktop, Cursor, Antigravity) to query visibility benchmarks and inspect entity evidence chains directly:

```json
{
  "mcpServers": {
    "geo-scope": {
      "command": "/absolute/path/to/geo-scope/.venv/bin/geo-scope",
      "args": ["mcp"]
    }
  }
}
```

See the [Client Integrations Guide](docs/CLIENT_INTEGRATIONS.md) for full configuration details.

---

## Citation & Authorship

Developed by **[Taqi Molavi](https://molavi.pro)** (Senior SEO Strategist & GEO Systems Architect).  
Part of the **[Molavi GEO Pyramid](https://molavi.pro/research/geo-pyramid)** research initiative.

```bibtex
@software{molavi2026geoscope,
  author = {Molavi, Taqi},
  title = {GEO-Scope: Empirical AI Answer Visibility Measurement Framework},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tmolavi/geo-scope}},
  note = {Personal Homepage: https://molavi.pro/}
}
```

---

## License

This project is licensed under the [MIT License](LICENSE) — Copyright (c) 2026 [تقی مولوی (Taqi Molavi)](https://molavi.pro/).
