<div align="center">

# ⟠ GEO-Scope

### Generative Engine Optimization (GEO) & AI Search Visibility Reverse-Engineering

**An open-source scientific benchmark and reverse-engineering platform to discover how brands, products, and content are ranked and cited across AI engines.**

*توسعه‌داده‌شده توسط [تقی مولوی (Taqi Molavi)](https://molavi.pro/) — بخشی از اکوسیستم پژوهشی GEO در کنار [`mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server)*

[![Website](https://img.shields.io/badge/Website-molavi.pro-blue?logo=googlechrome&logoColor=white)](https://molavi.pro/)
[![Whitepaper](https://img.shields.io/badge/Research-Whitepaper%202026-teal?logo=arxiv&logoColor=white)](docs/WHITEPAPER.md)
[![MCP Ready](https://img.shields.io/badge/MCP-Protocol%20Ready-8A2BE2?logo=anthropic&logoColor=white)](geo_scope/mcp_server.py)
[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org/project/geo-scope/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Support](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English Overview](#-english-overview) • [راهنمای فارسی](#-راهنمای-فارسی) • [📄 Research Whitepaper](docs/WHITEPAPER.md) • [MCP Server Setup](#-mcp-integration-claude-desktop--cursor) • [Visibility Score Algorithm](#-computational-methodology--visibility-score) • [Real-World Use Cases](#-real-world-use-cases-سناریوهای-کاربردی) • [Live API Setup](docs/API_INTEGRATION.md)

</div>

---

## 🖥️ Live Terminal & MCP Workflow Demo

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

**GEO-Scope** is an open-source platform created by **[Taqi Molavi](https://molavi.pro/)** that reverse-engineers the ranking and citation mechanics of modern search-augmented AI models (**ChatGPT Search, Perplexity Sonar, Google Gemini Grounding, and Anthropic Claude 3.7**).

By evaluating a statistically significant matrix of **1,000 categorized queries** across 5 search intent strata, GEO-Scope gives brands, growth engineers, and researchers complete visibility into how AI synthesizers discover, rank, and cite content.

---

## 🇮🇷 راهنمای فارسی

**GEO-Scope** یک فریم‌ورک استاندارد و پژوهشی متن‌باز طراحی شده توسط **[تقی مولوی](https://molavi.pro/)** برای مهندسی معکوس الگوریتم‌های دیده‌شدن در هوش مصنوعی (**GEO / AI SEO**) است.

دیگر دوران تمرکز صرف روی ۱۰ لینک آبی گوگل به پایان رسیده است. هوش مصنوعی‌ها (مانند Perplexity و ChatGPT Search) مستقیماً به کاربر پاسخ نهایی می‌دهند. این ابزار با ارسال **۱,۰۰۰ سوال واقعی**، کشف می‌کند که الگوریتم هر هوش مصنوعی چه وزنی به فاکتورهایی مثل **ردیت (UGC)، سایت‌های نقد و بررسی (G2)، روابط عمومی (PR) و اسکیما** می‌دهد.

### درباره نتایج آزمایش‌ها

اعداد و وزن‌های نمایش‌داده‌شده در این پروژه، نتایج آزمایش‌های اولیه GEO-Scope در شرایط مشخص هستند و «فاکتور رتبه‌بندی قطعی» یا قوانین ثابت موتورهای هوش مصنوعی محسوب نمی‌شوند.

هدف پروژه این است که هر پژوهشگر، متخصص یا کسب‌وکار بتواند پرامپت‌ها، برندها، رقبا، مدل‌ها، زبان و بازار خودش را وارد کند، آزمایش‌های خودش را اجرا کند و نتایج اولیه را تأیید، رد، مقایسه یا تکمیل کند.

GEO-Scope قرار نیست از کاربران بخواهد نتایج اولیه این پروژه را به‌عنوان حقیقت قطعی بپذیرند؛ هدف، فراهم‌کردن بستری برای آزمایش‌پذیر کردن فرضیه‌های GEO است.

---

## 🔌 MCP Integration (Claude Desktop & Cursor)

GEO-Scope includes a native **Model Context Protocol (MCP)** server, allowing you to run AI visibility audits directly inside **Claude Desktop**, **Cursor**, **Windsurf**, or custom AI agents.

### Configuration for Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "geo-scope": {
      "command": "python3",
      "args": ["-m", "geo_scope.mcp_server"]
    }
  }
}
```

### Configuration for Cursor IDE (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "geo-scope": {
      "command": "geo-scope",
      "args": ["mcp"]
    }
  }
}
```

### Available MCP Tools in Claude / Cursor:
1. `audit_ai_visibility(brand, niche, competitors, prompt_count)`: Calculates Share of Model (SoM) and Top-1 rank across AI engines.
2. `reverse_engineer_ranking_factors(target_brand, niche)`: Deduces platform-specific weights (Reddit vs G2 vs PR vs Freshness).
3. `generate_geo_playbook(brand, niche)`: Generates actionable on-page and off-page GEO strategies.

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

The numerical results and weights presented in this project — such as **Reddit/UGC 32%**, **Reviews 24%**, **PR 20%**, **Entity Grounding 12%**, **Structured Tables/BLUF 8%**, **Freshness 4%**, and observed engine behaviors (e.g. 38% Reddit citation density in Perplexity) — are empirical observations derived from the project's **INITIAL baseline experiments**.

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

## ⚡ Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Install package in editable mode
pip install -e .
```

### 2. Launch Interactive Web Dashboard

```bash
geo-scope serve --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** to view the live dashboard, interactive charts, prompt comparator, and custom benchmark runner.

### 3. Run Benchmark from CLI

```bash
# Run a 1,000 prompt benchmark for CRM SaaS
geo-scope run --niche crm_sales --brand HubSpot --count 1000 --out results/
```

### 4. Run with Docker Compose

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

## 🔗 Related Projects in the GEO Ecosystem

- 🌐 [**molavi.pro**](https://molavi.pro/): Personal homepage & AI research by Taqi Molavi (تقی مولوی).
- ⚡ [**mcp-geo-server**](https://github.com/tmolavi/mcp-geo-server): Model Context Protocol (MCP) Server for Generative Engine Optimization & RAG Readiness Audits by Taqi Molavi.
- 🤖 [**mcp-agent-skills-hub**](https://github.com/tmolavi/mcp-agent-skills-hub): Curated AI Agent Skills & MCP Hub by Taghi Molavi.

---

## 📜 Citation

```bibtex
@software{molavi2026geoscope,
  author = {Molavi, Taqi},
  title = {GEO-Scope: Generative Engine Optimization & AI Search Reverse-Engineering Framework},
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
