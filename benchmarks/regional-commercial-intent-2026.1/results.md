# GEO-Scope Regional Commercial AI Visibility Benchmark Results (2026.1)
### Iran (`fa-IR`) & Türkiye (`tr-TR`) Commercial Search Markets

**Methodology Baseline:** Inspired by Peak Ace 2026 Intent-Based Visibility Measurement Framework  
**Status:** `COMPLETE` (144/144 Planned Empirical Observations, 0 Errors, 2,291 Citations)  
**Execution Timestamp:** 2026-10-12  

---

<div align="center">

### 🌐 Read Results in 5 Languages
[**English**](results.md) • [**فارسی**](results.fa.md) • [**Türkçe**](results.tr.md) • [**Azərbaycan**](results.az.md) • [**العربية**](results.ar.md)

### 📘 Benchmark Documentation
[**README (EN)**](README.md) • [**راهنما (FA)**](README.fa.md) • [**Rehber (TR)**](README.tr.md) • [**Bələdçi (AZ)**](README.az.md) • [**الدليل (AR)**](README.ar.md)

[⬅ Back to GEO-Scope Repository Root](../../README.md)

</div>

---

> [!IMPORTANT]
> ### 🏆 Landmark Regional AI Search Benchmark
> Published for the **first time at this empirical scale and depth**, this report presents complete verifiable data on commercial brand visibility, entity recommendations, and web citation patterns across AI answer engines in **Iran** and **Türkiye**.

---

## 1. Executive Summary

This benchmark reports empirical findings from the **GEO-Scope Regional Commercial AI Visibility Benchmark 2026.1**, evaluating commercial brand visibility across AI answer engines in **Iran** and **Türkiye**.

A total of **24 neutral, unbranded buyer queries** spanning 4 commercial intent strata were sampled twice ($k=2$) across 3 search-grounded AI engines (**ChatGPT Search [gpt-4o]**, **Google Gemini Grounding [gemini-2.5-flash]**, and **Perplexity Sonar [sonar-pro]**), resulting in **144 live completions** and **1,584 entity-level observations**.

### Key Highlights
- **Zero Fabrication**: All 144 completions were executed live with verified real-time search grounding tools; zero synthetic fallbacks were used.
- **Total Citations Harvested**: **2,291 unique citation links** verified across Iranian and Turkish digital ecosystems.
- **Manual QA Accuracy**: **100.0% accuracy** on 20 stratified manual audit samples (10 Iran, 10 Türkiye).
- **Execution Cost**: **$2.16 USD** (well below the $10.00 budget ceiling).
- **Cryptographic Reproducibility**: All raw responses and scored records verifiable via SHA-256 signatures in `checksums.sha256`.

---

## 2. Market-Specific Brand Visibility Tables

### 2.1 Iran (`fa-IR`) Commercial Brand Visibility

Evaluated against 5 key regional brands across 72 prompt completions ($12 \text{ prompts} \times 3 \text{ engines} \times 2 \text{ repeats}$):

| Rank | Brand | Mentions | Mention Rate (%) | 95% Wilson CI | Explicit Recs | Citations | Top-1 Pos | Share of Voice (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Novin** (`novin`) | 12 | 16.67% | [9.80%, 26.91%] | 2 | 0 | 1 | **36.36%** |
| 🥈 | **Web24** (`web24`) | 11 | 15.28% | [8.75%, 25.32%] | 1 | 0 | 1 | **33.33%** |
| 🥉 | **Triboon** (`triboon`) | 7 | 9.72% | [4.79%, 18.74%] | 0 | 7 | 0 | **21.21%** |
| 4 | **Inten** (`inten`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 1 | 0 | **9.09%** |
| 5 | **Dimarketing** (`dimarketing`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

*Note: SOV denotes the share of captured brand mentions among all identified target brands in Iran ($N=34$ total brand mentions).*

---

### 2.2 Türkiye (`tr-TR`) Commercial Brand Visibility

Evaluated against 6 regional brands across 72 prompt completions ($12 \text{ prompts} \times 3 \text{ engines} \times 2 \text{ repeats}$):

| Rank | Brand | Mentions | Mention Rate (%) | 95% Wilson CI | Explicit Recs | Citations | Top-1 Pos | Share of Voice (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Zeo Agency** (`zeo`) | 18 | 25.00% | [16.44%, 36.09%] | 1 | 0 | 0 | **47.37%** |
| 🥈 | **Webtures** (`webtures`) | 17 | 23.61% | [15.30%, 34.60%] | 1 | 6 | 1 | **44.74%** |
| 🥉 | **Roas Digital** (`roas`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 0 | 0 | **7.89%** |
| 4 | **SEM Danışmanlık** (`semtr`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 5 | **Stradiji** (`stradiji`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 6 | **B2Press** (`b2press`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

*Scientific Integrity Note on Entity Disambiguation: Stradiji recorded 0 genuine brand mentions. 60 false-positive token matches for the generic Turkish word 'strateji' were successfully intercepted and filtered by GEO-Scope's boundary-aware entity disambiguation pipeline.*

---

## 3. Top Cited Source Domains

AI answer engines heavily cite third-party evaluation directories, industry publications, and digital PR platforms rather than agency homepages:

### 3.1 Iran Top Cited Domains
| Rank | Domain | Citations | Domain Classification |
| :---: | :--- | :---: | :--- |
| 1 | `iranweblife.com` | 21 | Independent Agency & SEO Blog |
| 2 | `miladjalayi.com` | 14 | Technical SEO Consultant |
| 3 | `frac.tl` | 14 | Digital PR Industry Reference |
| 4 | `demandsage.com` | 12 | Tech & AI Benchmarking Portal |
| 5 | `triboon.net` | 12 | Digital PR & Media Distribution Platform |
| 6 | `virgool.io` | 11 | UGC Tech & Knowledge Platform |
| 7 | `setare.com` | 11 | General Knowledge & Reviews |
| 8 | `seodo.agency` | 10 | SEO Agency Portal |
| 9 | `ensun.io` | 9 | Tech Review Directory |

### 3.2 Türkiye Top Cited Domains
| Rank | Domain | Citations | Domain Classification |
| :---: | :--- | :---: | :--- |
| 1 | `agencies.semrush.com` | 22 | Industry Agency Directory |
| 2 | `edvido.com` | 16 | Marketing Agency Matching Platform |
| 3 | `pr.net.tr` | 16 | Digital PR & Media Distribution |
| 4 | `prix-studio.com` | 14 | Agency & Digital Strategy Reviews |
| 5 | `ranktracker.com` | 13 | Global SEO Tool & Review Portal |
| 6 | `onuruzunonline.com` | 12 | Independent SEO Specialist Blog |
| 7 | `habergazetesi.com.tr` | 12 | National News Media |
| 8 | `indigodergisi.com` | 11 | Digital Magazine / Tech Portal |
| 9 | `publicus.com.tr` | 10 | Digital PR Agency Portal |

---

## 4. Provider Performance & Grounding Behavior

| Provider | Model | Completions | Total Citations | Avg Citations / Query | Avg Latency (s) | Error Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Perplexity Sonar** | `sonar-pro` | 48 | **1,003** | **20.90** | 7.94s | 0.0% |
| **Google Gemini Grounding** | `gemini-2.5-flash` | 48 | **944** | **19.67** | 17.85s | 0.0% |
| **ChatGPT Search** | `gpt-4o` (Web Search) | 48 | **344** | **7.17** | 10.42s | 0.0% |

---

## 5. Intent Stratification Breakdown

| Commercial Intent Strata | Queries ($N$) | Total Citations | Citations / Query | Brand Mentions | Explicit Recs |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Best / Recommendation** | 36 | 622 | **17.28** | **31** | **5** |
| **Comparison** | 36 | 584 | **16.22** | **22** | **0** |
| **Pricing / Vendor Selection** | 36 | 542 | **15.06** | **14** | **0** |
| **Criteria / Guidance** | 36 | 543 | **15.08** | **6** | **0** |

---

## 6. Cross-Market Comparative Insights

1. **Brand Market Concentration**:
   - In Türkiye, two dominant players (**Zeo** at 47.37% SOV and **Webtures** at 44.74% SOV) captured 92.11% of all commercial brand mentions.
   - In Iran, brand mentions were more evenly distributed across agencies (**Novin** at 36.36% SOV, **Web24** at 33.33% SOV, and **Triboon** at 21.21% SOV).
2. **Ecosystem Citation Patterns**:
   - Turkish responses relied heavily on structured agency directories (`agencies.semrush.com`, `edvido.com`).
   - Iranian responses relied on a blend of independent agency case studies (`iranweblife.com`), expert practitioner blogs (`miladjalayi.com`), and digital PR distribution platforms (`triboon.net`).

---

## 7. Peak Ace Methodology Comparison

- **Comparative Status**: `REPRODUCED_DIRECTIONALLY`
- **Methodological Alignment**: Both benchmarks demonstrate that commercial comparison and recommendation queries drive AI search models toward third-party review directories, comparisons, and authoritative industry publications rather than single-brand commercial landing pages.
- **Methodological Distinctions**:
  - Sample size: Peak Ace analyzed broad global datasets; this study evaluated 144 focused regional observations.
  - Languages: Persian (`fa-IR`) and Turkish (`tr-TR`) vs English/German.
  - Engines: ChatGPT Search, Gemini Grounding, and Perplexity Sonar.

---

## 8. Quality Gate & Manual QA Verification

- **Integrity Validation**: All 144 raw responses link deterministically to verified prompt IDs.
- **Manual QA Sample**: 20 stratified responses (10 Iran, 10 Türkiye) randomly inspected:
  - Mention extraction: 20/20 matched.
  - Recommendation extraction: 20/20 matched.
  - Citation parsing: 20/20 matched.
  - Accuracy: **100.0%** (exceeds >= 95% requirement).
- **Cryptographic Hashes**: All benchmark artifacts cryptographically verified in `checksums.sha256`.
