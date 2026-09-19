<div align="center">

# ⟠ GEO-Scope

### Open-Source AI Answer & Generative Engine Visibility Measurement Platform

**An empirical measurement framework for AI answer visibility, entity mentions, recommendations, and citations across generative AI systems.**

*توسعه‌داده‌شده توسط [تقی مولوی (Taghi Molavi)](https://molavi.pro/) — بخشی از اکوسیستم پژوهشی AI Visibility در کنار [`mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server)*

[![Website](https://img.shields.io/badge/Website-molavi.pro-blue?logo=googlechrome&logoColor=white)](https://molavi.pro/)
[![Research Transparency](https://img.shields.io/badge/Research-Transparency%20%26%20Limitations-blueviolet?logo=readme&logoColor=white)](docs/research-transparency.md)
[![Benchmark Methodology](https://img.shields.io/badge/Benchmark-Methodology%20v1-teal?logo=arxiv&logoColor=white)](docs/benchmark-methodology.md)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%20Ready-8A2BE2?logo=anthropic&logoColor=white)](geo_scope/mcp_server.py)
[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English Overview](#-english-overview) • [راهنمای فارسی](#-راهنمای-فارسی) • [🔬 Published Benchmarks](#-published-research-benchmarks) • [🏗️ Architecture](#️-measurement-architecture) • [📊 Methodology](docs/benchmark-methodology.md) • [🗺️ Evidence Map](docs/EVIDENCE_MAP.md) • [MCP Server Setup](#-mcp-integration-claude-desktop--cursor)

</div>

---

> ### 🎯 **"Don't trust GEO claims. Observe, measure, and verify them."**
> **WHAT**: An empirical measurement framework for Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and AI Search Visibility research.  
> **WHY**: AI visibility claims are often speculative or ungrounded. GEO-Scope provides empirical, entity-aware measurement of observed brand presence, citation graphs, and recommendation positioning.  
> **HOW**: **Discover Questions** ➔ **Execute Across Model Classes** ➔ **Parse Multi-Type Observations** ➔ **Publish Cryptographically Verifiable Evidence Bundles**.

---

## 🔬 Transparency Statement

> **"Simulation fixtures are only for testing and development. Published measurements are based on preserved execution evidence and are separately identified."**

GEO-Scope separates execution into 3 verifiable workflows:
1. **`geo-scope demo`**: Fast 5-minute onboarding using deterministic simulation fixtures. Prominently labeled with disclaimers and `simulated_*` metrics.
2. **`geo-scope measure`**: Production measurement across live answer engines and LLMs with **zero silent fallback** (provider failures are saved directly to `errors.jsonl` rather than masked with synthetic responses).
3. **`geo-scope replay`**: Deterministic offline re-evaluation of previously recorded raw AI responses against entity registries with **zero network calls**.

---

## 🏗️ Measurement Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │                    AnswerPath GEO                      │
       │               Question Discovery Layer                 │
       │   (Real Query Mining · Intent Strata · Provenance)     │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                       GEO-Scope                        │
       │                   Measurement Layer                    │
       │     (Experiment Config · Zero Fallback · Routing)      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                Provider Execution Layer                │
       │  ┌───────────────────────┐  ┌───────────────────────┐  │
       │  │     Answer Engine     │  │       Base LLM        │  │
       │  │   (Search-Grounded)   │  │  (Direct Completion)  │  │
       │  └───────────────────────┘  └───────────────────────┘  │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                     Entity Parser                      │
       │   (Multi-Type Entities · Homonyms · Negative Guards)   │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                Metrics & Evidence Release              │
       │ (Observations · Citations · Checksums · Reproducibility)│
       └────────────────────────────────────────────────────────┘
```

### Architecture Layer Descriptions

1. **AnswerPath GEO (Question Discovery Layer)**: Mines real user questions and conversational search patterns. Categorizes queries into distinct intent strata (`commercial`, `comparative`, `problem_solving`, `long_tail`, `reputation`) and preserves strict provenance between observed user demand ($60\%$) and systematic research templates ($40\%$).
2. **GEO-Scope (Measurement Layer)**: Manages reproducible multi-model measurement runs, enforces experimental configurations, handles rate limiting, and guarantees zero silent synthetic fallbacks.
3. **Provider Execution Layer**: Dispatches queries to configured model adapters, strictly partitioning providers into search-grounded **Answer Engines** (e.g., Perplexity Sonar, Google Gemini with Grounding) and direct **LLMs** (e.g., OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet). Raw API payloads, execution latency, and error states are preserved verbatim.
4. **Entity Parser**: Evaluates raw model completions against multi-type entity registries (People, Companies, Countries, Universities, Technologies, Communities), enforcing exact name matching, multilingual aliases, domain validation, and negative homonym exclusion (`do_not_confuse`).
5. **Metrics & Evidence Release**: Computes descriptive statistics (mention rates, recommendation rates, top-1 positioning, citation density), generates structured datasets (`observations.jsonl`, `citations.jsonl`, `metrics.json`), and seals the package with cryptographic SHA-256 hashes.

---

## 📐 GEO-Scope Measurement Layers

GEO-Scope structures its empirical methodology across 5 formal measurement layers:

### Layer 1 — Question Discovery
* **Engine**: [AnswerPath GEO](https://github.com/tmolavi/answerpath-geo)
* **Purpose**: Discovers authentic user queries, classifies search intent, and maintains provenance metadata.
* **Integrity**: Explicitly tags questions as `observed_user_questions` (mined from real-world search corpora) versus `research_questions` (systematic comparative templates).

### Layer 2 — Entity Understanding
* **Purpose**: Disambiguates entity mentions across heterogeneous entity classes:
  * **People** (Founders, researchers, executives)
  * **Companies** (Agencies, vendors, SaaS platforms)
  * **Countries & Regions** (Geographic and migration targets)
  * **Universities** (Academic and research institutions)
  * **Technologies** (Frameworks, libraries, protocols)
  * **Communities** (Forums, open-source ecosystems)
* **Disambiguation Rules**: Enforces primary names, multilingual aliases, canonical domains, and explicit negative homonym guards (`do_not_confuse`). Founder mentions (`person_mentioned`) are strictly isolated from brand mentions (`mentioned`).

### Layer 3 — Model Execution
* **Separation of Provider Classes**:
  * `answer_engine`: Search-grounded models with active web retrieval and source citation indexing.
  * `llm`: Direct parametric completion models evaluating intrinsic knowledge representation.
* **Execution Boundary**: Search-grounded systems and general language models are measured and reported as distinct metric families.

### Layer 4 — Observation Extraction
* **Metrics Recorded Per Execution**:
  * `mentioned`: Entity appeared in response body.
  * `person_mentioned`: Associated person/founder appeared (does not increment brand score).
  * `recommended`: Entity explicitly presented as an endorsed solution or choice.
  * `top1`: Entity presented as the primary (#1) recommended option.
  * `cited`: Entity domain cited in grounding references (Answer Engines).
  * `attributed`: Entity named as the source of a fact or statement.
  * `confused_with`: Triggered negative homonym collision terms.
  * `scoring_status`: `scored` for comparative/recommendation queries; `unscored` for navigational/informational lookups.
  * `parser_confidence`: Parser certainty score ($0.0 - 1.0$).

### Layer 5 — Evidence & Reproduction
* **Release Artifacts**:
  * `manifest.json`: Execution metadata, provider routing, and prompt breakdowns.
  * `prompts.jsonl`: Complete prompt bank with categorization and provenance.
  * `entities.json`: Complete entity registry with aliases and constraints.
  * `raw_responses.jsonl`: Preserved raw API completions.
  * `observations.jsonl`: Granular per-entity observation records.
  * `citations.jsonl`: Parsed source domains and URLs.
  * `metrics.json`: Aggregated descriptive rates and confidence intervals.
  * `errors.jsonl`: Transparent log of provider timeouts and errors.
  * `checksums.sha256`: Cryptographic integrity manifest.

---

## 📊 Published Research Benchmarks

All GEO-Scope benchmark releases are immutable, cryptographically sealed, and reproducible offline with zero network calls:

```
benchmark/releases/
├── global-ai-answers-2026.2/         # Full global research benchmark (500 prompts, 50 countries)
├── global-ai-answers-2026.2-pilot/   # Controlled pilot benchmark (100 prompts, 10 countries)
├── global-ai-answers-2026.1/         # Baseline global concerns benchmark (34 prompts, 7 regions)
└── geo-seo-digital-agency-iran-2026.1/ # Domain benchmark for digital agencies
```

---

### 1. Global AI Answers Benchmark 2026.2 (Full Research Release)
* **Path**: [`benchmark/releases/global-ai-answers-2026.2/`](benchmark/releases/global-ai-answers-2026.2/)
* **Objective**: Measure observed generative AI responses to major human concerns across 50 countries, 22+ languages, and 9 essential life/work categories without subjective ranking or normative superiority claims.
* **Dataset Scope**:
  * **500 Culturally Localized Prompts**: $60\%$ `observed_user_questions` ($n=300$) + $40\%$ `research_questions` ($n=200$).
  * **50 Countries**: Distributed across North America, Europe, MENA, Sub-Saharan Africa, Asia-Pacific, and Latin America.
  * **9 Concern Categories**: Future Skills & Learning, Career & Migration, Entrepreneurship & Business, AI Adoption, Technology Impact, Health & Lifestyle, Education Choices, Financial Decisions, Creativity & Culture.
  * **4 Providers**: Google Gemini 2.5 Flash, Perplexity Sonar Pro, OpenAI GPT-4o Mini, Anthropic Claude 3.5 Sonnet.
  * **73 Multi-Type Entities**: People, Companies, Countries, Universities, Technologies, Communities.
  * **Evidence Preserved**: 626 raw completions, 45,698 parsed observations, verified domain citations.
* **Research Publications**:
  * [Academic Research Paper](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md)
  * [Executive Briefing Report](docs/research/global-ai-answers-2026.2/global-ai-answers-report.md)
  * [Data Stories & Article Angles](docs/research/global-ai-answers-2026.2/article-ideas.md)

#### Verification & Reproduction Commands
```bash
# 1. Verify SHA-256 package cryptographic checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# 2. Validate schema compliance, prompt counts, and secret sanitization
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2

# 3. Deterministically recompute all metric math from raw response evidence
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2
```

---

### 2. Global AI Answers Benchmark 2026.2 Pilot
* **Path**: [`benchmark/releases/global-ai-answers-2026.2-pilot/`](benchmark/releases/global-ai-answers-2026.2-pilot/)
* **Objective**: Controlled pilot release validating the end-to-end 5-layer measurement pipeline prior to full global deployment.
* **Dataset Scope**:
  * **100 Prompts**: 55 observed user questions + 45 systematic research templates.
  * **10 Representative Countries**: Iran, Turkey, Germany, UK, US, India, Japan, Saudi Arabia, Brazil, Nigeria.
  * **8 Languages**: Persian, Turkish, German, English, Hindi, Japanese, Arabic, Portuguese.
  * **30 Multi-Type Entities**: Tracked across 4 model adapters.
  * **Evidence Preserved**: 298 raw completions, 8,940 entity observations, zero synthetic substitutions.
* **Documentation**: [Pilot Report](docs/GLOBAL_AI_ANSWERS_2026_2_PILOT_REPORT.md) · [Methodology](benchmark/releases/global-ai-answers-2026.2-pilot/methodology.md) · [Limitations](benchmark/releases/global-ai-answers-2026.2-pilot/limitations.md)

#### Verification & Reproduction Commands
```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# Deterministically replay metrics
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```

---

### 3. Global AI Answers Benchmark 2026.1
* **Path**: [`benchmark/releases/global-ai-answers-2026.1/`](benchmark/releases/global-ai-answers-2026.1/)
* **Objective**: Initial empirical baseline measuring observed AI answer distributions on critical human inquiries.
* **Dataset Scope**: 34 culturally localized prompts across 7 regions, 9 languages, and 4 models tracking 24 multi-type entities.
* **Documentation**: [Methodology](docs/global-ai-answers-methodology.md) · [Limitations](docs/global-ai-answers-limitations.md) · [Reproduction Guide](docs/REPRODUCE_GLOBAL_AI_ANSWERS.md)

#### Verification & Reproduction Commands
```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1

# Replay metrics
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.1
```

---

### 4. GEO & SEO Digital Agency Iran Benchmark
* **Path**: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](benchmark/releases/geo-seo-digital-agency-iran-2026.1/)
* **Objective**: Measure observed visibility, recommendation rates, and citation presence for digital marketing agencies in Iran.
* **Dataset Scope**: 30 prompts (15 observed real queries + 15 exploratory templates across 5 intent strata) evaluated across 4 models ($N=120$ completions).
* **Limitations**: Domain-specific, cross-sectional cohort measurement. Does not represent a universal or permanent agency ranking.
* **Documentation**: [Methodology](benchmarks/geo-seo-digital-agency-iran-2026.1/methodology.md) · [Full Report](benchmarks/geo-seo-digital-agency-iran-2026.1/report.md) · [Case Study](docs/case-studies/geo-seo-digital-agency-iran-2026.md)

#### Verification & Reproduction Commands
```bash
# Verify checksums
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Reproduce metrics and bootstrap confidence intervals
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

---

## 🏛️ Ecosystem Integration

GEO-Scope operates as the empirical execution and visibility measurement component of the **Molavi AI Visibility Stack**:

- **Discovery**: [AnswerPath GEO](https://github.com/tmolavi/answerpath-geo) — Intent classification & question mining
- **Measurement**: [GEO-Scope](https://github.com/tmolavi/geo-scope) — Multi-model empirical measurement & replay
- **Diagnostics**: [SAGE Audit](https://github.com/tmolavi/sage-audit) — Multi-pillar technical auditing (SEO + AEO + GEO)
- **Action**: [SiteProbe](https://github.com/tmolavi/siteprobe) — Automated remediation & schema patch verification
- **Protocol**: [MCP GEO Server](https://github.com/tmolavi/mcp-geo-server) — Model Context Protocol for AI coding agents

See the complete [Cross-Repository Evidence Map](docs/EVIDENCE_MAP.md) and [Documentation Index](docs/index.md).

---

## 🌐 English Overview

**GEO-Scope** is an open-source platform created by **[Taqi Molavi](https://molavi.pro/)** for studying observed brand mentions, explicit recommendation positions, and source references across configured AI providers.

Search-enabled and direct-completion adapters are identified separately. Statistical validity depends on sampling, annotation quality, and repeated observations, not query count alone.

---

## 🇮🇷 راهنمای فارسی

**GEO-Scope** یک فریم‌ورک استاندارد و پلتفرم متن‌باز طراحی شده توسط **[تقی مولوی](https://molavi.pro/)** برای سنجش، مشاهده‌پذیری و ارزیابی تجربی نحوه نمایش برندها در موتورهای پاسخ و مدل‌های زبانی هوش مصنوعی (**AI Answer & Generative Engine Visibility**) است.

این ابزار برای سنجش میزان دیده‌شدن برند، استخراج صریح پیشنهادها و تفکیک منابع استناد طراحی شده است. اجرای واقعی، بازپخش آفلاین و شبیه‌سازی کاملاً از هم تفکیک شده‌اند و شواهد خام مدل‌ها به همراه هش‌های رمزنگاری شده برای بازتولیدپذیری نگهداری می‌شوند.

### درباره ساختار سنجش و بازتولیدپذیری

۱. **حالت آزمایشی (Demo)**: اجرای شبیه‌سازی ۵ دقیقه‌ای با برچسب مشخص داده‌های ساختگی جهت آشنایی سریع.  
۲. **حالت سنجش زنده (Measure)**: اجرای سنجش واقعی بدون هیچ‌گونه جایگزینی خودکار شبیه‌سازی (Zero Silent Fallback) با تفکیک موتورهای جستجوی متصل به وب (Answer Engine) از مدل‌های مستقیم (LLM).  
۳. **حالت بازپخش قطعی (Replay)**: بازخوانی و تحلیل آفلاین پاسخ‌های ثبت‌شده با هزینه و دسترسی شبکه صفر.  

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

### 2. Run Instant 5-Minute Simulation Demo

```bash
geo-scope demo
```

### 3. Execute Live Measurement (Zero Silent Fallback)

```bash
geo-scope measure \
  --entities entities/iran-seo-agencies.json \
  --prompts examples/research_run/prompts.jsonl \
  --mode live \
  --providers perplexity_sonar,gemini_grounding \
  --out-dir output/research_run_01
```

### 4. Deterministic Offline Replay (Zero Network Calls)

```bash
geo-scope replay \
  --bundle output/research_run_01 \
  --entities entities/iran-seo-agencies.json \
  --out-dir output/replay_01
```

### 5. Launch Interactive Web Dashboard

```bash
geo-scope serve --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** to view the live dashboard, interactive charts, prompt comparator, and benchmark explorer.

---

## 🔌 MCP Integration (Claude Desktop, Cursor, Antigravity)

GEO-Scope includes a native **Model Context Protocol (MCP)** stdio server, allowing local MCP clients such as **Claude Desktop**, **Cursor**, **Antigravity**, or custom AI agents to invoke measurement tools.

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

See [client-specific setup and configuration guide](docs/CLIENT_INTEGRATIONS.md).

---

## 🧪 Testing

```bash
# Run complete test suite
pytest tests/ -v
```

---

## 📚 Documentation & Research Guides

- 📖 [Documentation Index](docs/index.md)
- 🗺️ [Cross-Repository Evidence Map](docs/EVIDENCE_MAP.md)
- 🔬 [Scientific Methodology](docs/benchmark-methodology.md)
- 📄 [Research Whitepaper](docs/WHITEPAPER.md)
- 📐 [Mathematical Model](docs/MATHEMATICAL_MODEL.md)
- 🥊 [Challenge Our Findings & Replication Guide](CHALLENGE.md)
- 🔌 [Live API Integration Guide](docs/API_INTEGRATION.md)
- 🇮🇷 [راهنمای تفصیلی فارسی](docs/FA_GUIDE.md)

---

## Citation & Author

Developed by **[Taqi Molavi](https://molavi.pro)** (Senior SEO Strategist & GEO Systems Architect).  
Part of the **[Molavi GEO Pyramid](https://molavi.pro/research/geo-pyramid)** research framework.

### BibTeX

```bibtex
@software{molavi2026geoscope,
  author = {Molavi, Taqi},
  title = {GEO-Scope: Open-Source AI Engine & LLM Visibility Measurement Platform},
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
