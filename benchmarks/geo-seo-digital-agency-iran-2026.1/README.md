# GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark (v2026.1)

**Subtitle**: Measuring AI Visibility, Recommendations, and Citation Presence Across Generative AI Platforms  
**Dataset Version**: `geo-seo-digital-agency-iran-2026.1`  
**Research Classification**: Exploratory Prototype & Format Verification Dataset (Not a Commercial Market Ranking)  
**Status**: Peer Review & Reproduction Ready  
**Release Date**: September 2026  
**License**: MIT (Open Research Dataset)

> [!NOTE]
> **Dataset Nature & Limitations**:
> This dataset demonstrates the benchmark schema, entity matching, bootstrap confidence interval calculations, and reproducible verification pipeline ($N=120$ completions across 30 prompts).
> - **Prompt Basis**: 30 researcher-generated hypothesis templates (0 observed real-time user query logs).
> - **Provider Routing**: Endpoints utilized gateway routing with fallback behavior.
> - **Scope**: **This dataset does NOT represent a definitive market ranking, agency ranking, or live production search index.** Real-world market claims require live measurements on observed real-time query logs.

---

## 1. Benchmark Overview

This benchmark measures the empirical presence, recommendation frequencies, and citation groundings of **8 digital marketing and SEO agencies** across **4 leading generative AI routes** (Google Gemini 2.5 Flash, OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, and Perplexity Sonar Pro) over **30 standardized search queries** ($N=120$ total provider completions).

### Evaluated Entities (8 Agencies):
1. **Web24** (`وب۲۴`)
2. **Novin** (`نوین`)
3. **Dimarketing** (`دی‌مارکتینگ`)
4. **Triboon** (`تریبون`)
5. **DMN Agency** (`دی‌ام‌ان`)
6. **Rayan** (`رایان`)
7. **Hamrah Marketing** (`همراه مارکتینگ`)
8. **Inten** (`اینتن`)

---

## 2. Key Empirical Findings Summary

*Total Observations: 120 (30 Prompts × 4 Providers)*

| Entity Name | Observed Mentions | Mention Rate [95% CI] | Top Recommendations | Rec Rate [95% CI] | Top-1 Recs | Top-1 Share |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Web24** (وب۲۴) | 26 | 21.7% [14.2%, 29.2%] | 25 | 20.8% [13.3%, 28.3%] | 14 | 11.7% |
| **Novin** (نوین) | 23 | 19.2% [12.5%, 26.7%] | 23 | 19.2% [12.5%, 26.7%] | 8 | 6.7% |
| **Dimarketing** | 8 | 6.7% [2.5%, 11.7%] | 8 | 6.7% [2.5%, 11.7%] | 4 | 3.3% |
| **Triboon** (تریبون) | 6 | 5.0% [1.7%, 9.2%] | 6 | 5.0% [1.7%, 9.2%] | 0 | 0.0% |
| **DMN Agency** | 5 | 4.2% [0.8%, 7.5%] | 5 | 4.2% [0.8%, 7.5%] | 0 | 0.0% |
| **Rayan** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 | 0.0% |
| **Hamrah Marketing** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 | 0.0% |
| **Inten** | 0 | 0.0% [0.0%, 0.0%] | 0 | 0.0% [0.0%, 0.0%] | 0 | 0.0% |

*Note: All confidence intervals are calculated via non-parametric empirical bootstrapping (1,000 resamples, $\alpha=0.05$).*

---

## 3. Reproduction & Verification

To verify checksums and reproduce all metrics bit-for-bit from raw evidence:

```bash
# 1. Cryptographic SHA-256 Checksum Verification
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# 2. Complete Metric Math & Bootstrap CI Reproduction
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

---

## 4. Documentation & Artifacts

- [`methodology.md`](methodology.md): Full experimental design, prompt strata, and mathematical formulas.
- [`report.md`](report.md): In-depth research report with provider breakdowns and intent analysis.
- [`metrics.json`](metrics.json): Machine-readable summary metrics and CI bounds.
- [`dataset-reference.md`](dataset-reference.md): Complete data dictionary and file schemas.
- Release Data: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](../../benchmark/releases/geo-seo-digital-agency-iran-2026.1/)
