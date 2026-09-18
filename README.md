<div align="center">

# ⟠ GEO-Scope

### Open-Source AI Engine & LLM Visibility Measurement Platform

**An open-source measurement lab for observing how brands appear in answer engines and language models through reproducible experiments, verifiable raw evidence, and entity-aware parsing.**

*توسعه‌داده‌شده توسط [تقی مولوی (Taghi Molavi)](https://molavi.pro/) — بخشی از اکوسیستم پژوهشی AI Visibility در کنار [`mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server)*

[![Website](https://img.shields.io/badge/Website-molavi.pro-blue?logo=googlechrome&logoColor=white)](https://molavi.pro/)
[![Research Transparency](https://img.shields.io/badge/Research-Transparency%20%26%20Limitations-blueviolet?logo=readme&logoColor=white)](docs/research-transparency.md)
[![Benchmark Methodology](https://img.shields.io/badge/Benchmark-Methodology%20v1-teal?logo=arxiv&logoColor=white)](docs/benchmark-methodology.md)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%20Ready-8A2BE2?logo=anthropic&logoColor=white)](geo_scope/mcp_server.py)
[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English Overview](#-english-overview) • [راهنمای فارسی](#-راهنمای-فارسی) • [🔬 Research Transparency](docs/research-transparency.md) • [📊 Benchmark Methodology](docs/benchmark-methodology.md) • [📄 Research Report](reports/geo-scope-live-2026.1-report.md) • [راهنمای نصب و استفاده](docs/CLIENT_INTEGRATIONS.md) • [MCP Server Setup](#-mcp-integration-claude-desktop--cursor) • [Live API Setup](docs/API_INTEGRATION.md)

</div>

---

> ### 🎯 **"Don't trust GEO claims. Observe and measure them."**
> **WHAT**: An Open Measurement Framework for Generative Engine Optimization (GEO) & AI Search Visibility Research.  
> **WHY**: AI visibility claims are often speculative. GEO-Scope provides empirical, entity-aware measurement of observed brand presence, citation graphs, and recommendation positioning.  
> **HOW**: **Define Entities & Prompts** ➔ **Execute Inferences (Live or Replay)** ➔ **Parse Observations & Disambiguate Homonyms** ➔ **Generate Verifiable Evidence Bundles**.

### Core Product Architecture: 3 Operational Modes

GEO-Scope separates execution into 3 distinct, verifiable workflows:

1. **`geo-scope demo`**: Fast 5-minute onboarding experience using deterministic simulation fixtures. Prominently labeled with disclaimers and `simulated_*` metrics.
2. **`geo-scope measure`**: Production measurement across live answer engines and LLMs. Strictly enforces **zero silent fallback** (provider failures are saved directly to `errors.jsonl` rather than masked with synthetic responses). Separates metrics into **AI Search Visibility** (answer engines with grounding citations) vs **LLM Brand Observation** (pure text completions).
3. **`geo-scope replay`**: Deterministic offline re-evaluation of previously recorded raw AI responses against entity registries with **zero network calls**.

```bash
# 1. Quickstart Simulation Demo
geo-scope demo

# 2. Live Measurement (Zero Fallback)
geo-scope measure --entities entities/iran-seo-agencies.json --prompts examples/prompts/observed-sample.jsonl --mode live --providers perplexity_sonar,gemini_grounding

# 3. Deterministic Offline Replay
geo-scope replay --input output/measure_latest --entities entities/iran-seo-agencies.json --out output/replay_latest
```

### Standard Output Contract & Evidence Bundles

Every measurement and replay run writes a self-contained, reproducible bundle with SHA-256 cryptographic verification:

- `manifest.json`: Run metadata, provider classes, prompt source breakdown, and execution timestamps.
- `prompts.jsonl`: Normalized input prompts categorized by source type (`observed` real queries vs `hypothesis` templates) and query intent.
- `raw_responses.jsonl`: Raw, unparsed model payloads and metadata for full auditability.
- `observations.jsonl`: Independent entity observations (`mentioned`, `person_mentioned`, `recommended`, `top1`, `rank`, `cited`, `attributed`, `confused_with`, `scoring_status`, `parser_confidence`).
- `metrics.json`: Aggregated metrics strictly partitioned into `ai_search_visibility` and `llm_brand_observation`.
- `errors.jsonl`: Explicit failure logs for any provider timeouts or API errors.
- `checksums.sha256`: SHA-256 hashes of all bundle files.

---

## 📊 Evidence & Published Benchmarks

GEO-Scope publishes fully reproducible, peer-review-ready empirical benchmark releases under [`benchmarks/`](benchmarks/) and [`benchmark/releases/`](benchmark/releases/) with SHA-256 cryptographic verification, full model routing provenance, and 95% bootstrap confidence intervals:

- **Ecosystem Evidence Map**: [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md)
- **Public Evidence Artifact Audit**: [`docs/PUBLIC_EVIDENCE_AUDIT.md`](docs/PUBLIC_EVIDENCE_AUDIT.md)
- **Public Proof & Verification Report**: [`docs/PUBLIC_PROOF_REPORT.md`](docs/PUBLIC_PROOF_REPORT.md)
- **Standalone Offline Demo Fixture**: [`examples/public_demo/`](examples/public_demo/)

### 🌍 [Global AI Answers Benchmark 2026](docs/global-ai-answers-methodology.md)
* **Subtitle**: *Measuring How Generative AI Systems Respond to Human Concerns Across Regions*
* **Dataset Package**: [`benchmark/releases/global-ai-answers-2026.1/`](benchmark/releases/global-ai-answers-2026.1/)
* **Purpose**: Provide empirical, multi-model visibility observations for critical human inquiries (skills, migration, entrepreneurship, technology adoption, finance, health, and education) across diverse cultural cohorts without subjective or normative claims.
* **Core Principle**: *"Demo outputs are simulation fixtures. Benchmark results come from recorded measurement runs."*
* **Documentation**: [Scientific Methodology](docs/global-ai-answers-methodology.md) · [Research Limitations](docs/global-ai-answers-limitations.md) · [Reproduction Guide](docs/REPRODUCE_GLOBAL_AI_ANSWERS.md) · [Reviewer Checklist](docs/EXTERNAL_RESEARCH_REVIEW.md) · [Versioning](docs/BENCHMARK_VERSIONING.md) · [2026.2 Roadmap](docs/ROADMAP_GLOBAL_AI_ANSWERS_2026_2.md)
* **Scope**: 34 culturally localized prompts across 7 essential concern categories, 7 regions, 9 languages, and 4 leading AI providers.
* **Execution & Provenance**: Live API execution via Hamzad AI Gateway (`https://api.molavi.pro`) across `gemini-2.5-flash`, `sonar-pro`, `gpt-4o-mini`, and `claude-3.5-sonnet`.
* **Entities Tracked (24 Multi-Type)**: Companies (Google, Microsoft, OpenAI, Anthropic, Apple, Amazon, LinkedIn, Meta, NVIDIA), Destinations (Germany, Canada, UAE, US, Singapore, Australia), Tech & Platforms (Python, Docker, PyTorch, ChatGPT, GitHub, Coursera, edX, Kaggle, WHO, MIT).

```bash
# 1. Verify bit-for-bit SHA-256 package checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1

# 2. Run dataset quality, schema & secret hygiene validation
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.1

# 3. Deterministically replay and recompute metrics from raw evidence
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.1
```

### 🏆 [GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark](benchmarks/geo-seo-digital-agency-iran-2026.1/)
* **Subtitle**: *Measuring AI Visibility, Recommendations, and Citation Presence Across Generative AI Platforms*
* **Dataset Package**: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](benchmark/releases/geo-seo-digital-agency-iran-2026.1/)
* **Methodology**: [Methodology v1](benchmarks/geo-seo-digital-agency-iran-2026.1/methodology.md) · [Full Report](benchmarks/geo-seo-digital-agency-iran-2026.1/report.md) · [Dataset Reference](benchmarks/geo-seo-digital-agency-iran-2026.1/dataset-reference.md) · [Case Study](docs/case-studies/geo-seo-digital-agency-iran-2026.md)
* **Ecosystem Stack**: [Molavi AI Visibility Stack & Evidence Map](docs/BENCHMARK_ECOSYSTEM.md)
* **Question Layer**: [AnswerPath GEO](https://github.com/tmolavi/answerpath-geo) (15 observed real queries + 15 exploratory hypothesis templates across 5 search intent strata)

#### Observed Metrics Summary ($N=120$ completions across Gemini 2.5 Flash, GPT-4o, Claude 3.5 Sonnet, Sonar Pro)

| Entity Name | Observed Mentions | Mention Rate [95% CI] | Recommendations | Rec Rate [95% CI] | Top-1 Recs |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Web24** (وب۲۴) | 26 | 21.7% [14.2%, 29.2%] | 25 | 20.8% [13.3%, 28.3%] | 14 |
| **Novin** (نوین) | 23 | 19.2% [12.5%, 26.7%] | 23 | 19.2% [12.5%, 26.7%] | 8 |
| **Dimarketing** | 8 | 6.7% [2.5%, 11.7%] | 8 | 6.7% [2.5%, 11.7%] | 4 |
| **Triboon** (تریبون) | 6 | 5.0% [1.7%, 9.2%] | 6 | 5.0% [1.7%, 9.2%] | 0 |
| **DMN Agency** | 5 | 4.2% [0.8%, 7.5%] | 5 | 4.2% [0.8%, 7.5%] | 0 |
| **Rayan** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 |
| **Hamrah Marketing** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 |
| **Inten** | 0 | 0.0% [0.0%, 0.0%] | 0 | 0.0% [0.0%, 0.0%] | 0 |

#### Reproduction & Verification Commands

```bash
# Verify bit-for-bit SHA-256 package checksums
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Reproduce all metric math and 95% bootstrap CIs from raw evidence
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

## 🏛️ Ecosystem

GEO-Scope operates as the empirical execution and multi-model benchmark component of the **Molavi AI Visibility Stack**:

- **Discovery**: [AnswerPath GEO](https://github.com/tmolavi/answerpath-geo)
- **Measurement**: [GEO-Scope](https://github.com/tmolavi/geo-scope)
- **Diagnostics**: [SAGE Audit](https://github.com/tmolavi/sage-audit)
- **Action**: [SiteProbe](https://github.com/tmolavi/siteprobe)
- **Protocol**: [MCP GEO Server](https://github.com/tmolavi/mcp-geo-server)

---

## 🖥️ Illustrative Terminal & MCP Workflow Demo

The following is a presentation example, not evidence of a live measurement.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  Claude Desktop / Cursor IDE ──▶ MCP Tool: audit_ai_visibility("HubSpot", "crm_sales") │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⟠ GEO-Scope 1,000-Prompt Inference Result                                              │
│                                                                                        │
│ [✓] Overall Share of Model (SoM) : 77.6% (ChatGPT: 68.4% | Perplexity: 82.1%)          │
│ [✓] Top-1 Recommendation Rate    : 44.9% (Primary recommended pick across models)      │
│ [✓] Dominant Grounding Signal    : Reddit UGC threads (38%) + G2 Leaderboard (26%)     │
│ [!] Critical Vulnerability Found : Missing comparison tables for "Enterprise API" queries│
│ [→] Action Playbook Generated    : Implement BLUF schema on 3 key landing pages         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌐 English Overview

**GEO-Scope** is an open-source platform created by **[Taqi Molavi](https://molavi.pro/)** for studying observed brand mentions, explicit recommendation positions, and source references across configured AI providers. Search-enabled and direct-completion adapters are identified separately.

Evaluate up to **1,000 categorized queries** across 5 intent groups, or bring your own prompts. Statistical validity depends on sampling, annotation quality and repeated observations, not query count alone.

---

## 🇮🇷 راهنمای فارسی

**GEO-Scope** یک فریم‌ورک استاندارد و پلتفرم متن‌باز طراحی شده توسط **[تقی مولوی](https://molavi.pro/)** برای سنجش، مشاهده‌پذیری و ارزیابی تجربی نحوه نمایش برندها در موتورهای پاسخ و مدل‌های زبانی هوش مصنوعی (**AI Search Visibility & Brand Observation**) است.

این ابزار برای سنجش میزان دیده‌شدن برند، استخراج صریح پیشنهادها و تفکیک منابع استناد طراحی شده است. اجرای واقعی، بازپخش آفلاین و شبیه‌سازی کاملاً از هم تفکیک شده‌اند و شواهد خام مدل‌ها به همراه هش‌های رمزنگاری شده برای بازتولیدپذیری نگهداری می‌شوند.

### درباره ساختار سنجش و بازتولیدپذیری

۱. **حالت آزمایشی (Demo)**: اجرای شبیه‌سازی ۵ دقیقه‌ای با برچسب مشخص داده‌های ساختگی جهت آشنایی سریع.
۲. **حالت سنجش زنده (Measure)**: اجرای سنجش واقعی بدون هیچ‌گونه جایگزینی خودکار شبیه‌سازی (Zero Silent Fallback) با تفکیک موتورهای جستجوی متصل به وب (Answer Engine) از مدل‌های مستقیم (LLM).
۳. **حالت بازپخش قطعی (Replay)**: بازخوانی و تحلیل آفلاین پاسخ‌های ثبت‌شده با هزینه و دسترسی شبکه صفر.

هدف پروژه این است که پژوهشگران و کسب‌وکارها بتوانند به صورت مستقل و بدون اتکا به ادعاهای اثبات‌نشده، نحوه دیده شدن برندها را به صورت تجربی و آزمون‌پذیر رصد نمایند.

---

## 🔌 MCP Integration (Codex, Antigravity, Claude, Cursor and other clients)

GEO-Scope includes a native **Model Context Protocol (MCP)** stdio server, allowing local MCP clients such as **Codex**, **Antigravity**, **Claude Desktop**, **Cursor**, **Windsurf**, or custom AI agents to run the same tools. Cloud clients require a separately deployed authenticated MCP HTTP transport; the repository does not pretend that the local dashboard is one.

### Common configuration (`claude_desktop_config.json`, Cursor, Windsurf or Antigravity MCP settings)

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

### Available MCP Tools:
1. `audit_ai_visibility(brand, niche, competitors, prompt_count)`: Calculates Share of Model (SoM) and Top-1 rank across AI engines.
2. `reverse_engineer_ranking_factors(target_brand, niche)`: Returns labeled platform-specific research priors (Reddit vs G2 vs PR vs Freshness); does not fit weights.
3. `generate_geo_playbook(brand, niche)`: Generates actionable on-page and off-page GEO strategies.

See [client-specific setup, smoke test and Cloud boundary](docs/CLIENT_INTEGRATIONS.md).

---

## 📐 Computational Methodology & Visibility Score

The composite **GEO Visibility Score ($\mathcal{V}_{\text{GEO}}$)** measures a brand's authority, recommendation priority, and retrieval readiness:

$$\mathcal{V}_{\text{GEO}} = w_1 \cdot \text{SoM} + w_2 \cdot \mathbb{P}(\text{Rank}_1) + w_3 \cdot \mathcal{S}_{\text{Sentiment}} + w_4 \cdot \mathcal{C}_{\text{Authority}}$$

```
┌───────────────────────────────────────────────┬─────────┬───────────────────────────────────────────┐
│ Ranking Signal Dimension                      │ Weight  │ Grounding Mechanism in LLM Synthesis      │
├───────────────────────────────────────────────┼─────────┼───────────────────────────────────────────┤
│ 1. Community & Forum Footprint (Reddit/UGC)   │ 32%     │ Perplexity/ChatGPT index upvoted threads  │
│ 2. 3rd-Party Review Leadership (G2/Capterra)  │ 24%     │ LLMs synthesize top-rated grid leaders    │
│ 3. Tier-1 Digital PR & Authority Media        │ 20%     │ Bing & Google Web grounding index         │
│ 4. Entity Grounding (Wikidata / JSON-LD)      │ 12%     │ Google Knowledge Graph disambiguation     │
│ 5. Structured Tables & BLUF Formatting        │ 8%      │ Token extraction density in context window│
│ 6. Information Freshness (Recency Decay)      │ 4%      │ Temporal filtering (year/quarter penalty) │
└───────────────────────────────────────────────┴─────────┴───────────────────────────────────────────┘
```

---

## 🧪 Experimental Philosophy & Reproducibility

**GEO-Scope** is **"An Open Experimental Framework for GEO & AI Visibility Research."**

It is designed to function as an experimental laboratory and observatory for studying how generative engines discover, retrieve, cite, compare, and recommend brands across diverse search contexts.

### Important Clarification on Baseline Metrics

The numerical factor profiles in the repository are **hypothesis priors**, not weights estimated from the current benchmark. Simulation examples illustrate the workflow. Live visibility results must be interpreted using their saved prompts, actual model, execution date and provider evidence.

They are **NOT** claimed to be:
- Universal ranking factors
- Permanent weights
- Official weights of any AI engine
- Immutable GEO rules

AI retrieval pipelines and search grounding indexes are dynamic, probabilistic, and constantly evolving. Results may change depending on:
- **Prompt Set & Phrasing** (intent framing, question depth, specificity)
- **Industry & Vertical** (B2B SaaS vs consumer ecommerce vs local services)
- **Brand & Competitors** (established market leaders vs emerging entrants)
- **Language & Market** (English, Persian, bilingual, regional queries)
- **Country & Geographic Grounding**
- **AI Model & Grounding System** (ChatGPT Search vs Perplexity vs Gemini vs Claude)
- **Execution Date & Information Recency**
- **Experimental Configuration & Temperature**

---

### Core Experimental Principles

> **Don't trust GEO claims. Test them.**

#### 1. Bring Your Own Prompts
Anyone can use prompts and queries representing their own real market, user personas, and commercial queries.

#### 2. Run Your Own Experiments
Users can define their own brands, competitors, models, languages, markets, prompts, and scenarios.

#### 3. Build Your Own Evidence
The purpose of GEO-Scope is to enable empirical testing rather than asking users to blindly accept GEO claims.

Use this standardized experimental workflow:
$$\text{Baseline} \longrightarrow \text{Change} \longrightarrow \text{Re-test} \longrightarrow \text{Compare}$$

GEO-Scope preserves complete reproducibility metadata across runs:
- **Experiment ID**
- **Timestamp**
- **Models**
- **Prompt Set**
- **Market / Language**
- **Brands & Competitors**
- **Configuration**
- **Raw Results**
- **Metrics**
- **Observed Changes**

#### 4. Challenge the Results
We actively encourage users to reproduce, challenge, confirm, reject, or extend the initial findings. If another researcher gets different results, that is **valuable evidence** — not a failure of GEO-Scope.

```text
Bring your own prompts.
Run your own experiments.
Build your own evidence.
```

---

## 🎯 Real-World Use Cases (سناریوهای کاربردی)

### سناریوی ۱: چرا Perplexity برند ما را نشان نمی‌دهد ولی ChatGPT نشان می‌دهد؟
- **مسئله**: یک کسب‌وکار در پاسخ‌های ChatGPT Search رتبه ۲ است اما در Perplexity اصلا نامی از آن برده نمی‌شود.
- **حل با GEO-Scope**: اجرای ۱,۰۰۰ سوال نشان می‌دهد Perplexity ۳۸٪ وزن را به تاپیک‌های ساب‌ردیت‌های تخصصی اختصاص داده است؛ جایی که رقبای شما حضور فعال دارند اما برند شما هیچ ردپای UGC در آن ندارد.

### سناریوی ۲: مهندسی معکوس منابع طلایی رقبا (Citation Hijacking)
- **مسئله**: رقیب اصلی شما در سوالات مقایسه‌ای همواره رتبه ۱ را می‌گیرد.
- **حل با GEO-Scope**: گراف منابع (`citations_graph.csv`) نشان می‌دهد که ۷۲٪ از استنادهای هوش مصنوعی برای این سوالات، فقط از **۳ صفحه مقایسه در سایت G2 و یک مقاله در TechCrunch** برداشت شده‌اند. هدف‌گذاری مستقیم روی این ۴ منبع، بازی را تغییر می‌دهد.

### سناریوی ۳: ارزیابی آمادگی GEO قبل از لانچ محصول (Pre-Launch Audit)
- **مسئله**: انتشار یک ویژگی جدید یا بازطراحی صفحات لندینگ.
- **حل با GEO-Scope**: قبل از انتشار رسمی، ۱۰۰۰ پرسش شبیه‌سازی‌شده اجرا می‌شود تا اطمینان حاصل شود ساختار جداول مقایسه‌ای و متد **BLUF (پاسخ مستقیم در ۳۰ کلمه اول)** توسط RAG قابل استخراج است.

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

### 3. Execute Live AI Visibility Measurement (Zero Silent Fallback)

```bash
# Measure live across configured search-grounded and completion providers
geo-scope measure \
  --entities entities/iran-seo-agencies.json \
  --prompts examples/research_run/prompts.jsonl \
  --mode live \
  --providers perplexity_sonar,gemini_grounding \
  --out-dir output/research_run_01
```

### 4. Deterministic Offline Replay (Zero Network Calls)

```bash
# Re-evaluate previous responses against new or updated entity definitions offline
geo-scope replay \
  --bundle output/research_run_01 \
  --entities entities/iran-seo-agencies.json \
  --out-dir output/replay_01
```

### 5. Launch Interactive Web Dashboard

```bash
geo-scope serve --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** to view the live dashboard, interactive charts, prompt comparator, and custom benchmark runner.

### 6. Run with Docker Compose

```bash
docker-compose up -d
```

---

## 📊 The 1,000-Prompt Intent Matrix

| Intent Category | Distribution | Sample Prompt (EN) | نمونه پرسش فارسی |
| :--- | :---: | :--- | :--- |
| **Commercial Direct** | 30% ($n=300$) | *"What is the best CRM software for startups in 2026?"* | بهترین نرم‌افزار CRM برای استارتاپ‌ها در سال ۲۰۲۶ چیست؟ |
| **Comparative** | 25% ($n=250$) | *"Comprehensive comparison between HubSpot vs Salesforce"* | مقایسه کامل هاب‌اسپات و سلزفورس، کدام ارزش خرید دارد؟ |
| **Problem Solving** | 20% ($n=200$) | *"How to fix sales pipeline leaks with modern CRM?"* | چگونه مشکل ریزش سرنخ‌ها را با اتوماسیون حل کنیم؟ |
| **Long-Tail Niche** | 15% ($n=150$) | *"Affordable cloud CRM under $50 with open webhook API"* | نرم‌افزار CRM ابری ارزان با وب‌هوک باز برای تیم ۳ نفره |
| **Reputation / UGC** | 10% ($n=100$) | *"Real user reviews on Reddit about complaints for HubSpot"* | نظرات کاربران در ردیت درباره معایب و هزینه‌های ابزار |

---

## 🧪 Testing

```bash
# Run test suite
pytest tests/ -v
```

---

## 📚 Documentation & Research Guides

- 📖 [Scientific Methodology](docs/METHODOLOGY.md)
- 📄 [Research Whitepaper](docs/WHITEPAPER.md)
- 📐 [Mathematical Formulations](docs/MATHEMATICAL_MODEL.md)
- 🥊 [Challenge Our Findings & Replication Guide](CHALLENGE.md)
- 🧪 [Community Experiments Directory](experiments/)
- 📂 [Bring Your Own Prompts (BYOP) Guide](docs/CUSTOM_PROMPTS_GUIDE.md)
- 🤖 [How to Add an AI / Search Provider](docs/ADD_A_PROVIDER.md)
- 🔌 [Live API Integration (OpenAI, Perplexity, Gemini, Claude)](docs/API_INTEGRATION.md)
- 📊 [Industry Datasets & Schema](docs/DATASETS.md)
- 🇮🇷 [راهنمای تفصیلی فارسی](docs/FA_GUIDE.md)

---

## 🔗 Related Projects in the GEO Ecosystem

- 🌐 [**molavi.pro**](https://molavi.pro/): Personal homepage & AI research by Taqi Molavi (تقی مولوی).
- ⚡ [**mcp-geo-server**](https://github.com/tmolavi/mcp-geo-server): Model Context Protocol (MCP) Server for Generative Engine Optimization & RAG Readiness Audits by Taqi Molavi.
- 🤖 [**mcp-agent-skills-hub**](https://github.com/tmolavi/mcp-agent-skills-hub): Curated AI Agent Skills & MCP Hub by Taghi Molavi.

## 💬 Community & External Collaboration

We welcome researchers, developers, and practitioners to participate in the empirical AI visibility ecosystem:

- **Participate in Discussions**: [GitHub Discussions](https://github.com/tmolavi/geo-scope/discussions) across **General**, **Research**, **Ideas**, **Help**, and **Show and Tell**.
- **Research Collaboration**: Read our [Research Collaboration Framework](docs/RESEARCH_COLLABORATION.md) for contributing new prompt banks, benchmark runs, or evaluation metrics.
- **First-Time Contributors**: Follow our [First Contribution Guide](docs/FIRST_CONTRIBUTION.md) to set up your local environment and submit pull requests.
- **Report Issues**: Use our structured [Issue Templates](https://github.com/tmolavi/geo-scope/issues/new/choose) to report bugs, submit replication findings, or propose new AI providers.
- **Contribution Standards**: See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

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

---

## 🏷️ Multilingual Keywords & Topics (فارسی / Türkçe / English)

`GEO` • `Generative Engine Optimization` • `AI SEO` • `LLM Search Optimization` • `Perplexity AI` • `ChatGPT Search` • `Google Gemini Grounding` • `Claude 3.7` • `Share of Model` • `Citation Graph` • `RAG Benchmarking` • `MCP Server` • `سئو در هوش مصنوعی` • `سنجش تجربی دیده‌شدن هوش مصنوعی` • `بهینه‌سازی موتورهای مولد` • `سئو چت‌جی‌پی‌تی` • `هوش مصنوعی و سئو` • `تقی مولوی` • `Yapay Zeka SEO` • `Üretken Motor Optimizasyonu` • `Yapay Zeka Arama Motoru` • `LLM Görünürlük Kıyaslaması` • `Taqi Molavi`
