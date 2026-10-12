# GEO-Scope Regional Commercial AI Visibility Benchmark (2026.1)
### Iran (`fa-IR`) & Türkiye (`tr-TR`) Commercial Search Markets

**Identifier:** `regional-commercial-intent-2026.1`  
**Execution Status:** `COMPLETE` (144/144 Planned Empirical Observations, 0 Errors, 2,291 Citations)  
**Execution Mode:** `empirical` (100% Live Search-Grounded Engines, Zero Synthetic Fallbacks)  
**Methodological Baseline:** Inspired by [Peak Ace AI Visibility LLM Benchmark 2026](https://peakace.agency/en/latest/ai-visibility-llm-benchmark-2026/)  

---

<div align="center">

### 🌐 Read Benchmark Documentation in 5 Languages
[**English**](README.md) • [**فارسی**](README.fa.md) • [**Türkçe**](README.tr.md) • [**Azərbaycan**](README.az.md) • [**العربية**](README.ar.md)

### 📊 Full Benchmark Results & Reports
[**Results (EN)**](results.md) • [**نتایج کامل (FA)**](results.fa.md) • [**Tam Sonuçlar (TR)**](results.tr.md) • [**Tam Nəticələr (AZ)**](results.az.md) • [**النتائج الكاملة (AR)**](results.ar.md)

[⬅ Back to GEO-Scope Repository Root](../../README.md)

</div>

---

> [!IMPORTANT]
> ### 🏆 Published for the First Time at this Scale in Regional Search
> This study marks the **first comprehensive empirical benchmark** evaluating commercial AI search visibility, entity recommendations, and web citation patterns across **Iran** and **Türkiye**. 
> Conducted with **zero synthetic fabrication**, **100% real-time search-grounded completions**, and **rigorous cryptographic auditability**, it sets a new gold standard for Generative Engine Optimization (GEO) research in Middle Eastern and Eurasian digital markets.

---

## 1. Executive Summary

| Parameter | Measured Value | Validation Note |
| :--- | :--- | :--- |
| **Total Live Completions** | **144 / 144** (100.0%) | 24 unique prompts $\times$ 3 search engines $\times$ 2 repetitions |
| **Entity-Level Observations** | **1,584 observations** | 11 target agencies evaluated across all responses |
| **Total Real Citations Harvested** | **2,291 verified URLs** | Zero fabricated or dead URLs; 100% live grounding |
| **Provider Error Rate** | **0.0% (0 errors)** | Full completion with zero fallback across all engines |
| **Manual QA Audit Accuracy** | **100.0%** | Stratified audit on 20 random samples (10 IR, 10 TR) |
| **Execution Cost** | **$2.16 USD** | Well below the designated \$10.00 pilot ceiling |
| **Cryptographic Integrity** | **SHA-256 Verified** | All artifacts tracked in [`checksums.sha256`](checksums.sha256) |

---

## 2. Market-Specific Findings & Share of Voice

### 2.1 Iran (`fa-IR`) Commercial Search Market
Evaluation of 5 leading digital agencies across 72 prompt completions ($12 \text{ queries} \times 3 \text{ engines} \times 2 \text{ runs}$):

| Rank | Agency / Brand | Mentions | Mention Rate (%) | 95% Wilson CI | Explicit Recs | Citations | Top-1 Pos | Share of Voice (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Novin** (`novin`) | 12 | 16.67% | [9.80%, 26.91%] | 2 | 0 | 1 | **36.36%** |
| 🥈 | **Web24** (`web24`) | 11 | 15.28% | [8.75%, 25.32%] | 1 | 0 | 1 | **33.33%** |
| 🥉 | **Triboon** (`triboon`) | 7 | 9.72% | [4.79%, 18.74%] | 0 | 7 | 0 | **21.21%** |
| 4 | **Inten** (`inten`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 1 | 0 | **9.09%** |
| 5 | **Dimarketing** (`dimarketing`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

*Note: Total captured brand mentions in Iran $N=34$. Mentions are distributed across competitive agencies, indicating an active multi-vendor consideration set.*

---

### 2.2 Türkiye (`tr-TR`) Commercial Search Market
Evaluation of 6 prominent digital agencies across 72 prompt completions ($12 \text{ queries} \times 3 \text{ engines} \times 2 \text{ runs}$):

| Rank | Agency / Brand | Mentions | Mention Rate (%) | 95% Wilson CI | Explicit Recs | Citations | Top-1 Pos | Share of Voice (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Zeo Agency** (`zeo`) | 18 | 25.00% | [16.44%, 36.09%] | 1 | 0 | 0 | **47.37%** |
| 🥈 | **Webtures** (`webtures`) | 17 | 23.61% | [15.30%, 34.60%] | 1 | 6 | 1 | **44.74%** |
| 🥉 | **Roas Digital** (`roas`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 0 | 0 | **7.89%** |
| 4 | **SEM Danışmanlık** (`semtr`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 5 | **Stradiji** (`stradiji`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 6 | **B2Press** (`b2press`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

*Scientific Integrity Note on Entity Disambiguation: Stradiji recorded 0 genuine commercial brand mentions. 60 false-positive token matches for the generic Turkish noun 'strateji' (strategy) were successfully intercepted and filtered by GEO-Scope's boundary-aware entity disambiguation pipeline.*

---

## 3. Provider Grounding & Citation Performance

| Provider Engine | Underlying Model | Completions | Total Citations | Citations / Query | Avg Latency | Error Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Perplexity Sonar** | `sonar-pro` | 48 | **1,003** | **20.90** | 7.94s | 0.0% |
| **Google Gemini Grounding** | `gemini-2.5-flash` | 48 | **944** | **19.67** | 17.85s | 0.0% |
| **ChatGPT Search** | `gpt-4o` (Web Search) | 48 | **344** | **7.17** | 10.42s | 0.0% |

- **Citation Density**: Perplexity and Gemini surface approximately $3\times$ more citation references per query than ChatGPT Search.
- **Latency**: Perplexity Sonar achieved the fastest response time (7.94s), while Gemini Grounding performed in-depth multi-turn grounding searches (17.85s).

---

## 4. Top Cited Ecosystem Domains

AI answer engines do not prioritize commercial service landing pages. Instead, they overwhelmingly cite independent third-party aggregators, technical blogs, and comparison platforms:

| Rank | Iran (`fa-IR`) Top Sources | Citations | Category | Türkiye (`tr-TR`) Top Sources | Citations | Category |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| 1 | `iranweblife.com` | 21 | Agency / Industry Blog | `agencies.semrush.com` | 22 | Agency Directory |
| 2 | `miladjalayi.com` | 14 | Technical SEO Specialist | `edvido.com` | 16 | Agency Matchmaker |
| 3 | `frac.tl` | 14 | Digital PR Authority | `pr.net.tr` | 16 | Digital PR Platform |
| 4 | `demandsage.com` | 12 | Tech & Benchmarks | `prix-studio.com` | 14 | Marketing Review |
| 5 | `triboon.net` | 12 | Digital PR & Media | `ranktracker.com` | 13 | Global SEO Tool Portal |
| 6 | `virgool.io` | 11 | Tech Publishing (UGC) | `onuruzunonline.com` | 12 | Independent SEO Blog |
| 7 | `setare.com` | 11 | Reviews & Media | `habergazetesi.com.tr` | 12 | News Media Portal |

---

## 5. Intent Stratification Dynamics

The 24 benchmark prompts were equally stratified across 4 fundamental buyer intent groups (6 prompts each across 2 markets):

| Intent Group | Total Citations | Citations / Query | Brand Mentions | Explicit Recs | Strategic Takeaway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Best / Recommendation** | 622 | **17.28** | **31** | **5** | Primary driver of agency brand mentions and direct endorsements. |
| **Comparison** | 584 | **16.22** | **22** | **0** | Drives heavy multi-entity comparative listings without single winners. |
| **Pricing / Vendor Selection** | 542 | **15.06** | **14** | **0** | Models default to pricing criteria guides and directory platforms. |
| **Criteria / Guidance** | 543 | **15.08** | **6** | **0** | Educational intent surfaces frameworks rather than individual vendors. |

---

## 6. Directory Structure & Verified Evidence Files

```
benchmarks/regional-commercial-intent-2026.1/
├── README.md               # English Benchmark Documentation (this file)
├── README.fa.md            # Persian Documentation (راهنمای فارسی)
├── README.tr.md            # Turkish Documentation (Türkçe Dokümantasyon)
├── README.az.md            # Azerbaijani Documentation (Azərbaycan Dili)
├── README.ar.md            # Arabic Documentation (الوثائق بالعربية)
├── results.md              # Complete Empirical Results (English)
├── results.fa.md           # گزارش کامل نتایج بنچمارک (فارسی)
├── results.tr.md           # Kapsamlı Ampirik Sonuç Raporu (Türkçe)
├── results.az.md           # Tam Empirik Nəticələr Hesabatı (Azərbaycan)
├── results.ar.md           # التقرير التجريبي الكامل للنتائج (العربية)
├── manifest.json           # Conforms to schema v0.3 (status: COMPLETE)
├── run-config.json         # Execution parameters & cost audit ($2.16 USD)
├── prompts.jsonl           # 24 unique unbranded neutral buyer prompts
├── entities.json           # Target agency profiles (5 IR, 6 TR)
├── metrics.json            # Computed metrics package with 95% Wilson CIs
├── raw_responses.jsonl     # 144 unmodified live response payloads
├── observations.jsonl      # 1,584 scored entity observation records
├── errors.jsonl            # 0 errors recorded
├── methodology.md          # Scientific methodology & Peak Ace comparison
├── limitations.md          # Epistemic boundaries and sample design notes
└── checksums.sha256        # Cryptographic SHA-256 verification manifest
```

---

## 7. Peak Ace Benchmark Comparison

- **Methodological Status**: `REPRODUCED_DIRECTIONALLY`
- **Core Convergence**: Corroborates Peak Ace's foundational thesis that search-grounded AI engines shift discovery towards third-party comparison portals, aggregator directories, and independent expert reviews rather than corporate homepages.
- **Distinctions**:
  - Markets: Iran (`fa-IR`) and Türkiye (`tr-TR`) vs Western European markets.
  - Scale: 144 focused regional observations vs broad global enterprise sets.
  - Engines: ChatGPT Search, Gemini Grounding, and Perplexity Sonar.

---

## 8. Reproducibility & Offline Verification

To cryptographically audit and recompute all metrics offline without API costs:

```bash
# Verify all artifact hashes
sha256sum -c benchmarks/regional-commercial-intent-2026.1/checksums.sha256

# Recompute metrics from raw evidence (zero network access required)
geo-scope replay \
  --archive benchmarks/regional-commercial-intent-2026.1/raw_responses.jsonl \
  --entities benchmarks/regional-commercial-intent-2026.1/entities.json \
  --out-dir /tmp/replay-verification
```

---

## 9. Citation

```bibtex
@misc{geoscope_regional_benchmark_2026,
  author = {Molavi, Taqi and GEO-Scope Contributors},
  title = {GEO-Scope Regional Commercial AI Visibility Benchmark 2026.1: An Empirical Evaluation of AI Answer Engines in Iran and Türkiye},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/tmolavi/geo-scope/tree/main/benchmarks/regional-commercial-intent-2026.1}}
}
```
