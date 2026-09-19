<div align="center">

# ⟠ GEO-Scope

### Empirical AI Answer Visibility Measurement Framework

**GEO-Scope measures and preserves evidence of how generative AI systems mention, recommend, cite, and attribute entities.**

*توسعه‌داده‌شده توسط [تقی مولوی (Taghi Molavi)](https://molavi.pro/) — بخشی از اکوسیستم پژوهشی AI Visibility در کنار [`mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server)*

[![Website](https://img.shields.io/badge/Website-molavi.pro-blue?logo=googlechrome&logoColor=white)](https://molavi.pro/)
[![Research Transparency](https://img.shields.io/badge/Research-Transparency%20%26%20Limitations-blueviolet?logo=readme&logoColor=white)](docs/research-transparency.md)
[![Benchmark Methodology](https://img.shields.io/badge/Benchmark-Methodology%20v1-teal?logo=arxiv&logoColor=white)](docs/benchmark-methodology.md)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%20Ready-8A2BE2?logo=anthropic&logoColor=white)](geo_scope/mcp_server.py)
[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Product Overview](#-product-overview) • [Evidence Pipeline](#-evidence-pipeline) • [Key Capabilities](#-key-capabilities) • [Published Benchmarks](#-published-benchmarks) • [Language Support](#-language-support) • [Transparency](#-what-geo-scope-does-not-claim) • [راهنمای فارسی](#-راهنمای-فارسی)

</div>

---

## 🎯 Product Overview

**GEO-Scope** is an evidence-oriented empirical measurement framework designed for researchers, analysts, and practitioners to measure and evaluate how generative AI systems answer questions.

It helps analyze:
- **Entity mentions**: When and how brands, people, technologies, and organizations appear in generated responses.
- **Recommendations**: Explicit entity recommendations and top-position endorsements.
- **Citations**: Grounding URLs and referenced domains in search-augmented AI systems.
- **Attribution**: Attribution of facts, data, and claims to source entities.
- **Answer patterns**: Distributional shifts across regions, query intents, and provider classes.

GEO-Scope avoids ungrounded claims and instead preserves the full raw evidence chain for all published metrics.

---

## 🏗️ Evidence Pipeline

GEO-Scope operates through a sequential, auditable evidence pipeline:

```text
       ┌────────────────────────────────────────────────────────┐
       │                   Question Discovery                   │
       │     (Mined Search Queries · Conversational Logs)       │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                    Prompt Provenance                   │
       │   (Observed vs Research · Intent · Region · Lang)      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                  AI Provider Execution                 │
       │  ┌───────────────────────┐  ┌───────────────────────┐  │
       │  │     Answer Engine     │  │       Base LLM        │  │
       │  │   (Search-Grounded)   │  │  (Direct Completion)  │  │
       │  └───────────────────────┘  └───────────────────────┘  │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                  Raw Response Storage                  │
       │   (Unmodified API Payloads · Execution Metadata)       │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │              Entity Observation Extraction             │
       │   (Multi-Type Entities · Homonym Rules · Context)      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             Metrics + Reproducible Evidence            │
       │  (Aggregated Rates · SHA-256 Checksums · Replay)       │
       └────────────────────────────────────────────────────────┘
```

### Pipeline Stages

1. **Question Discovery**: Identifies real-world search queries and user questions across specific verticals and regions.
2. **Prompt Provenance**: Categorizes prompts by source type (`observed_user_questions` vs `research_questions`), search intent (`commercial`, `comparative`, `problem_solving`, `long_tail`, `reputation`), language, and country code.
3. **AI Provider Execution**: Dispatches queries to live AI models with zero silent fallback. Failures and timeouts are logged explicitly rather than masked.
4. **Raw Response Storage**: Preserves full, unparsed model completion payloads (`raw_responses.jsonl`) for complete auditability.
5. **Entity Observation Extraction**: Evaluates responses against structured entity registries, extracting mention status, recommendation position, citations, and negative homonym collision checks.
6. **Metrics + Reproducible Evidence**: Computes descriptive statistics and packages all data with cryptographic SHA-256 checksums (`checksums.sha256`), enabling deterministic offline re-evaluation.

---

## ⚡ Key Capabilities

### 1. Provenance-Aware Questions
Prompts preserve structured provenance metadata:
* **Source category**: Explicit separation between real user demand (`observed_user_questions`) and systematic exploratory templates (`research_questions`).
* **Intent strata**: Classification into commercial direct, comparative, problem-solving, long-tail niche, and reputation categories.
* **Geographic & Linguistic tagging**: Explicit country ISO codes, regional tags, and language codes.

### 2. Entity-Aware Measurement
Entities are modeled as structured registries supporting multiple entity types:
* **People**: Founders, researchers, spokespersons.
* **Companies**: Brands, vendors, SaaS platforms, agencies.
* **Countries & Regions**: Geographic and migration destinations.
* **Universities**: Academic and research institutions.
* **Technologies**: Software libraries, programming languages, protocols.
* **Communities**: Forums, open-source ecosystems.

Each entity definition includes multilingual aliases, canonical domains, and explicit negative collision rules (`do_not_confuse`). Founder mentions (`person_mentioned`) are recorded separately from organizational mentions (`mentioned`).

### 3. Complete Evidence Preservation
GEO-Scope does not merely output aggregate scores; every release package contains:
* `prompts.jsonl`: Complete categorized prompt records.
* `entities.json`: Entity definitions, aliases, and constraints.
* `raw_responses.jsonl`: Verbatim API completion payloads.
* `observations.jsonl`: Granular per-entity observation records.
* `citations.jsonl`: Extracted source URLs and domains.
* `metrics.json`: Aggregated descriptive rates.
* `errors.jsonl`: Transparent log of provider timeouts and errors.
* `checksums.sha256`: Cryptographic verification hashes.

### 4. Provider Separation
GEO-Scope separates model adapters into two distinct measurement classes:
* `answer_engine`: Search-grounded models with dynamic web retrieval and citation grounding (e.g., Perplexity Sonar, Google Gemini with Grounding).
* `llm`: Parametric language models evaluating intrinsic model representations (e.g., OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet).

Metrics from different provider classes are maintained and reported separately.

---

## 🌐 Language Support

Currently verified benchmark languages across repository datasets:

| Language Code | Language | Benchmark Releases |
|:---|:---|:---|
| `en` | English | Global AI Answers 2026.1, 2026.2-pilot, 2026.2 |
| `fa` | Persian (فارسی) | Global AI Answers 2026.1, 2026.2-pilot, 2026.2, Agency Benchmark |
| `tr` | Turkish (Türkçe) | Global AI Answers 2026.1, 2026.2-pilot, 2026.2 |
| `de` | German (Deutsch) | Global AI Answers 2026.1, 2026.2-pilot, 2026.2 |
| `fr` | French (Français) | Global AI Answers 2026.1, 2026.2 |
| `es` | Spanish (Español) | Global AI Answers 2026.1, 2026.2 |
| `ar` | Arabic (العربية) | Global AI Answers 2026.1, 2026.2-pilot, 2026.2 |
| `hi` | Hindi (हिन्दी) | Global AI Answers 2026.2-pilot, 2026.2 |
| `ja` | Japanese (日本語) | Global AI Answers 2026.1, 2026.2-pilot, 2026.2 |
| `pt` | Portuguese (Português) | Global AI Answers 2026.2-pilot, 2026.2 |
| `zh` | Chinese (中文) | Global AI Answers 2026.1, 2026.2 |

*Additional localized regional languages in the 2026.2 dataset: Amharic (`am`), Danish (`da`), Finnish (`fi`), Indonesian (`id`), Italian (`it`), Korean (`ko`), Malay (`ms`), Dutch (`nl`), Norwegian (`no`), Polish (`pl`), Swedish (`sv`), Swahili (`sw`), Tagalog (`tl`), Urdu (`ur`), Vietnamese (`vi`).*

Further linguistic expansions are detailed in the [Research Roadmap](docs/ROADMAP_GLOBAL_AI_ANSWERS_2026_2.md).

---

## 📊 Published Benchmarks

GEO-Scope maintains published empirical benchmark datasets under `benchmark/releases/`. All published datasets are immutable and verifiable offline:

```
benchmark/releases/
├── global-ai-answers-2026.2/           # Full global research release (500 prompts, 50 countries)
├── global-ai-answers-2026.2-pilot/     # Controlled pilot release (100 prompts, 10 countries)
├── global-ai-answers-2026.1/           # Initial baseline release (34 prompts, 7 regions)
└── geo-seo-digital-agency-iran-2026.1/ # Domain release for digital marketing agencies
```

---

### 1. Global AI Answers Benchmark 2026.2 (Full Research Release)
* **Path**: [`benchmark/releases/global-ai-answers-2026.2/`](benchmark/releases/global-ai-answers-2026.2/)
* **Purpose**: Measure observed generative AI responses to major human concerns across 50 countries, 22+ languages, and 9 categories.
* **Dataset Scope**: 500 culturally localized prompts (300 observed user questions [60%], 200 research templates [40%]), 73 multi-type entities, 626 raw completions, 45,698 parsed observations across 4 model adapters.
* **Methodology**: Multi-model live API execution via Hamzad Gateway, zero synthetic fallback, multi-type entity parsing, and cryptographic SHA-256 verification.
* **Publications**: [Academic Paper Draft](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md) · [Executive Report](docs/research/global-ai-answers-2026.2/global-ai-answers-report.md)

```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# Deterministically replay metrics from raw responses
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2
```

---

### 2. Global AI Answers Benchmark 2026.2 Pilot
* **Path**: [`benchmark/releases/global-ai-answers-2026.2-pilot/`](benchmark/releases/global-ai-answers-2026.2-pilot/)
* **Purpose**: Controlled pilot release validating the end-to-end evidence pipeline prior to full deployment.
* **Dataset Scope**: 100 prompts (55 observed user questions, 45 research templates) across 10 representative countries and 8 languages, 30 entities, 298 raw completions, 8,940 entity observations.
* **Methodology**: Live model execution across separated provider classes with zero synthetic substitution.
* **Documentation**: [Pilot Report](docs/GLOBAL_AI_ANSWERS_2026_2_PILOT_REPORT.md) · [Methodology](benchmark/releases/global-ai-answers-2026.2-pilot/methodology.md)

```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# Replay metrics
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```

---

### 3. Global AI Answers Benchmark 2026.1
* **Path**: [`benchmark/releases/global-ai-answers-2026.1/`](benchmark/releases/global-ai-answers-2026.1/)
* **Purpose**: Initial empirical baseline measuring observed AI answer distributions on critical human inquiries.
* **Dataset Scope**: 34 prompts across 7 regions and 9 languages, 24 entities, 4 models.
* **Methodology**: Zero synthetic fallback, honest error logging, and deterministic replay.
* **Documentation**: [Methodology](docs/global-ai-answers-methodology.md) · [Limitations](docs/global-ai-answers-limitations.md)

```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1

# Replay metrics
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.1
```

---

### 4. GEO & SEO Digital Agency Iran Benchmark
* **Path**: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](benchmark/releases/geo-seo-digital-agency-iran-2026.1/)
* **Purpose**: Measure observed visibility, recommendation rates, and citation presence for digital marketing agencies in Iran.
* **Dataset Scope**: 30 prompts across 5 intent strata, 8 agencies, 120 model completions.
* **Methodology**: Cross-sectional domain observation with bootstrap confidence intervals.
* **Documentation**: [Methodology](benchmarks/geo-seo-digital-agency-iran-2026.1/methodology.md) · [Report](benchmarks/geo-seo-digital-agency-iran-2026.1/report.md)

```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Reproduce metrics
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

---

## 🛡️ What GEO-Scope Does Not Claim

GEO-Scope adheres to strict epistemic boundaries:

1. **It does not reveal proprietary model algorithms**: GEO-Scope measures empirical outputs from external APIs; it does not claim to inspect or reverse-engineer internal weights, training data, or proprietary retrieval ranking functions.
2. **It does not predict future rankings**: Generative engine responses are probabilistic and subject to continuous model and index updates.
3. **It does not measure "true influence" or entity capability**: Mention rates and recommendation positions reflect query-specific observations, not real-world entity superiority.
4. **It does not replace search analytics**: It measures generative AI answer visibility, not web search volume, click-through rates, or conversion tracking.
5. **It does not claim that simulation equals live measurement**: Simulation fixtures are strictly for development and testing; published measurements require preserved execution records.

---

## 🇮🇷 راهنمای فارسی

**GEO-Scope** یک فریم‌ورک متن‌باز برای سنجش تجربی و ثبت شواهد نحوه نمایش، پیشنهاد، استناد و ارجاع موجودیت‌ها (برندها، افراد، فناوری‌ها و سازمان‌ها) در سیستم‌های هوش مصنوعی مولد است.

### ویژگی‌های اصلی
۱. **تفکیک کامل شبیه‌سازی از سنجش واقعی**: حالت دمو صرفاً برای توسعه و تست با برچسب مشخص داده‌های شبیه‌سازی شده است. در حالت سنجش زنده هیچ‌گونه جایگزینی خودکار شبیه‌سازی وجود ندارد (Zero Silent Fallback).
۲. **تفکیک رده مدل‌ها**: موتورهای جستجوی متصل به وب (`answer_engine`) و مدل‌های زبانی مستقیم (`llm`) به عنوان دو رده اندازه‌گیری مستقل سنجیده می‌شوند.
۳. **زنجیره شواهد کامل**: هر انتشار شامل پرامپت‌ها، پاسخ‌های خام، مشاهدات، استنادها، لاگ خطاها و هش‌های SHA-256 برای بازتولیدپذیری آفلاین است.

---

## ⚡ Quickstart & CLI Commands

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Install package in editable mode
pip install -e .
```

### 2. Run Instant Simulation Demo

```bash
geo-scope demo
```

### 3. Execute Live Measurement (Zero Silent Fallback)

```bash
geo-scope measure   --entities entities/iran-seo-agencies.json   --prompts examples/research_run/prompts.jsonl   --mode live   --providers perplexity_sonar,gemini_grounding   --out-dir output/research_run_01
```

### 4. Deterministic Offline Replay (Zero Network Calls)

```bash
geo-scope replay   --bundle output/research_run_01   --entities entities/iran-seo-agencies.json   --out-dir output/replay_01
```

### 5. Launch Interactive Dashboard

```bash
geo-scope serve --host 0.0.0.0 --port 8000
```

---

## 🔌 MCP Integration (Claude Desktop, Cursor, Antigravity)

GEO-Scope includes a native **Model Context Protocol (MCP)** stdio server:

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

See [Client Integrations Guide](docs/CLIENT_INTEGRATIONS.md).

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 📚 Documentation & Research Guides

- 📖 [Documentation Index](docs/index.md)
- 🗺️ [Cross-Repository Evidence Map](docs/EVIDENCE_MAP.md)
- 🔬 [Scientific Methodology](docs/benchmark-methodology.md)
- 📄 [Research Whitepaper](docs/WHITEPAPER.md)
- 📐 [Mathematical Model](docs/MATHEMATICAL_MODEL.md)
- 🔌 [Live API Integration Guide](docs/API_INTEGRATION.md)
- 🇮🇷 [راهنمای تفصیلی فارسی](docs/FA_GUIDE.md)

---

## Citation & Author

Developed by **[Taqi Molavi](https://molavi.pro)** (Senior SEO Strategist & GEO Systems Architect).  
Part of the **[Molavi GEO Pyramid](https://molavi.pro/research/geo-pyramid)** research framework.

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

## 📄 License

This project is licensed under the [MIT License](LICENSE) — Copyright (c) 2026 [تقی مولوی (Taqi Molavi)](https://molavi.pro/).
