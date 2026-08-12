<div align="center">

# ⟠ GEO-Scope

### Generative Engine Optimization (GEO) & AI Search Visibility Reverse-Engineering

**An open-source scientific benchmark and reverse-engineering platform to discover how brands, products, and content are ranked and cited across AI engines.**

*Developed by [Taqi Molavi](https://github.com/tmolavi) — Part of the GEO Ecosystem including [`mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server)*

[![CI](https://github.com/tmolavi/geo-scope/actions/workflows/ci.yml/badge.svg)](https://github.com/tmolavi/geo-scope/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org/project/geo-scope/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Support](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](#-english-overview) • [راهنمای فارسی](#-راهنمای-فارسی) • [Scientific Methodology](docs/METHODOLOGY.md) • [Mathematical Model](docs/MATHEMATICAL_MODEL.md) • [Live API Setup](docs/API_INTEGRATION.md) • [Related: mcp-geo-server](https://github.com/tmolavi/mcp-geo-server)

</div>

---

## 🌐 English Overview

**GEO-Scope** is a full-stack open-source platform that reverse-engineers the ranking and citation mechanics of modern search-augmented AI models (**ChatGPT Search, Perplexity Sonar, Google Gemini Grounding, and Anthropic Claude 3.7**).

By running a statistically significant matrix of **1,000 categorized queries** across multiple search intents, GEO-Scope computes:
- **Share of Model (SoM %)**: Percentage of AI responses recommending your brand vs competitors.
- **Top-1 Recommendation Rate (#1 Pick %)**: Likelihood of being selected as the primary recommended solution.
- **Citation Graph & Source Attribution**: Domain-level mapping of sources LLMs crawl and synthesize (Reddit, G2, Tier-1 PR, Wikipedia).
- **Algorithmic Weight Vectors**: Quantified importance of UGC, reviews, schema markup, and content structure per AI engine.

```
                  ┌──────────────────────────────────────────────┐
                  │          GEO-Scope Pipeline Engine           │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │ 1,000 Stratified Prompts Generator (5 Intents)│
                 └───────────────────────┬───────────────────────┘
                                         │
        ┌────────────────┬───────────────┴───────────────┬────────────────┐
        ▼                ▼                               ▼                ▼
┌───────────────┐┌───────────────┐               ┌───────────────┐┌───────────────┐
│Perplexity AI  ││ChatGPT Search │               │ Google Gemini ││  Claude 3.7   │
│  (Sonar Pro)  ││   (GPT-4o)    │               │  (Grounding)  ││ (Reasoning)   │
└───────┬───────┘└───────┬───────┘               └───────┬───────┘└───────┬───────┘
        │                │                               │                │
        └────────────────┼───────────────────────────────┼────────────────┘
                         ▼                               ▼
                 ┌───────────────────────────────────────────────┐
                 │ NLP Feature Extractor & Citation Graph Parser │
                 └───────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │ Statistical Attribution & GEO Action Playbook │
                 └───────────────────────────────────────────────┘
```

---

## 🇮🇷 راهنمای فارسی

**GEO-Scope** یک فریم‌ورک استاندارد و متن‌باز برای مهندسی معکوس الگوریتم‌های دیده‌شدن در هوش مصنوعی (**GEO / AI SEO**) است. با آزمایش **۱,۰۰۰ سوال** در ۵ دسته قصد جستجو، سیستم مشخص می‌کند هوش مصنوعی‌ها بر چه اساسی یک برند را به عنوان رتبه اول معرفی می‌کنند:

### خلاصه وزن‌های کشف‌شده در الگوریتم‌ها:
- ⚡ **Perplexity Sonar**: ۳۸٪ وزن بر مبنای تاپیک‌های بحث و نظرات در **Reddit** و انجمن‌های کاربری (UGC).
- 🟢 **ChatGPT Search**: ۲۸٪ رسانه‌های معتبر با دامین آتوریتی بالا (PR) + ۲۶٪ امتیازات در دایرکتوری‌های نقد (**G2 / Capterra**).
- 🔵 **Google Gemini**: ۲۲٪ اتکا به گراف دانش رسمی گوگل و **Wikidata** + ۱۲٪ تازگی محتوا و اسکیما.
- 🟣 **Anthropic Claude 3.7**: استدلال عمیق بر پایه اسناد فنی دقیق، جدول‌های مقایسه شفاف و آمار عددی بدون اغراق.

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
Open **`http://localhost:8000`** in your browser to view the live dashboard, charts, prompt comparator, and GEO playbook.

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

To guarantee statistical confidence ($p < 0.01$), prompts are sampled across 5 standardized strata:

| Intent Category | Distribution | Sample Prompt (EN) | نمونه پرسش فارسی |
| :--- | :---: | :--- | :--- |
| **Commercial Direct** | 30% ($n=300$) | *"What is the best CRM software for startups in 2026?"* | بهترین نرم‌افزار CRM برای استارتاپ‌ها در سال ۲۰۲۶ چیست؟ |
| **Comparative** | 25% ($n=250$) | *"Comprehensive comparison between HubSpot vs Salesforce"* | مقایسه کامل هاب‌اسپات و سلزفورس، کدام ارزش خرید دارد؟ |
| **Problem Solving** | 20% ($n=200$) | *"How to fix sales pipeline leaks with modern CRM?"* | چگونه مشکل ریزش سرنخ‌ها را با اتوماسیون حل کنیم؟ |
| **Long-Tail Niche** | 15% ($n=150$) | *"Affordable cloud CRM under $50 with open webhook API"* | نرم‌افزار CRM ابری ارزان با وب‌هوک باز برای تیم ۳ نفره |
| **Reputation / UGC** | 10% ($n=100$) | *"Real user reviews on Reddit about complaints for HubSpot"* | نظرات کاربران در ردیت درباره معایب و هزینه‌های ابزار |

---

## 🐍 Python SDK Example

```python
import asyncio
from geo_scope import (
    generate_prompt_dataset,
    ModelRunner,
    parse_model_response,
    AlgoAnalyzer,
    generate_geo_playbook
)

async def main():
    # 1. Generate 100 prompts
    prompts = generate_prompt_dataset(
        niche_key="crm_sales",
        target_brand="HubSpot",
        competitors=["Salesforce", "Zoho CRM", "Pipedrive"],
        total_count=100
    )

    # 2. Run multi-model inferences
    runner = ModelRunner()
    responses = await runner.execute_batch(prompts)

    # 3. Parse features
    parsed = [parse_model_response(r["query_item"], r["model"], r["response_text"]) for r in responses]

    # 4. Statistical reverse engineering
    analyzer = AlgoAnalyzer(parsed, "HubSpot", ["Salesforce", "Zoho CRM", "Pipedrive"])
    results = analyzer.compute_full_analysis()

    print(f"Share of Model (SoM): {results['summary']['overall_sov']}%")
    print(f"Top-1 Recommendation Rate: {results['summary']['overall_top1_rate']}%")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 Testing

```bash
# Run test suite with coverage
pytest tests/ -v --cov=geo_scope
```

---

## 📚 Documentation

- 📖 [Scientific Methodology](docs/METHODOLOGY.md)
- 📐 [Mathematical Formulations](docs/MATHEMATICAL_MODEL.md)
- 🔌 [Live API Integration (OpenAI, Perplexity, Gemini, Claude)](docs/API_INTEGRATION.md)
- 📊 [Industry Datasets & Schema](docs/DATASETS.md)
- 🇮🇷 [راهنمای تفصیلی فارسی](docs/FA_GUIDE.md)

---

## 🔗 Related Projects in the GEO Ecosystem

- [**mcp-geo-server**](https://github.com/tmolavi/mcp-geo-server): Model Context Protocol (MCP) Server for Generative Engine Optimization & RAG Readiness Audits by Taqi Molavi.
- [**mcp-agent-skills-hub**](https://github.com/tmolavi/mcp-agent-skills-hub): Curated AI Agent Skills & MCP Hub by Taghi Molavi.

---

## 📜 Citation

If you use GEO-Scope in academic research or industrial benchmarks, please cite:

```bibtex
@software{geoscope2026,
  author = {Molavi, Taqi},
  title = {GEO-Scope: Generative Engine Optimization & AI Search Reverse-Engineering Framework},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tmolavi/geo-scope}},
  version = {1.0.0}
}
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — Copyright (c) 2026 [Taqi Molavi](https://github.com/tmolavi).
