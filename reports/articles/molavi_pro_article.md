# GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark: Empirical AI Visibility Study

**Author**: [Taqi Molavi](https://molavi.pro)  
**Published**: 2026  
**Category**: Generative Engine Optimization (GEO), Artificial Intelligence, Search Architecture  
**Dataset**: `geo-seo-digital-agency-iran-2026.1` (Open Source & Cryptographically Verified)

---

## Executive Summary

As enterprise search behavior migrates from traditional Search Engine Results Pages (SERPs) to conversational AI interfaces (such as Google Gemini, OpenAI ChatGPT, Anthropic Claude, and Perplexity Sonar), how are brand entities discovered, prioritized, and cited?

In this empirical study, we present the **GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark**, conducted across leading generative AI platforms. Using the open-source **Molavi AI Visibility Stack**—comprising **AnswerPath GEO** for intent discovery, **GEO-Scope** for benchmark orchestration, and **Hamzad AI Gateway** for zero-secret execution—we systematically observe how AI models mention, rank, and cite major Iranian digital marketing and SEO agencies (including Web24, Novin, Dimarketing, Triboon, and DMN Agency).

### Epistemic Position: Empirical Observation vs Algorithm Reverse-Engineering
We deliberately reject speculative claims of "reverse-engineering proprietary ranking algorithms" or "guaranteed AI rankings". Instead, our methodology enforces **empirical observation**: recording exact multi-model completions, categorizing prompt demand strata, tracking model execution provenance, and reporting observed associations with 95% bootstrap confidence intervals.

---

## 🔬 The 3-Tier Experimental Architecture

```text
┌────────────────────────────────────────────────────────┐
│ 1. Question Discovery & Stratification (AnswerPath GEO) │
│    - 15 Observed User Inquiries (Real Demand)          │
│    - 15 Generated Research Prompts (Exploration)       │
│    - Intent strata: commercial, compare, trust, solve  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Benchmark Orchestration & Analysis (GEO-Scope)      │
│    - Execution mode: LIVE (No synthetic injection)     │
│    - Strict vs Discovery Mode Provenance Tracking      │
│    - Brand Mention & Top-1 Recommendation Parsing      │
│    - Grounded Citation & Source Verification           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. Zero-Secret Model Gateway (Hamzad AI Gateway)       │
│    - Native Routes: Gemini 2.5 Flash, GPT-4o           │
│    - Fallback Routes: Qwen 3.8 27B                     │
│    - Transparent Provenance (requested vs actual model)│
└────────────────────────────────────────────────────────┘
```

---

## 📊 Key Findings & Empirical Observations

1. **Brand Mention Distribution**:
   - Entities with strong technical SEO footprint, structured organization entities, and deep industry co-occurrence (e.g. Web24 and Novin) demonstrated consistent mention frequencies across both direct completions and search-grounded queries.
2. **Intent Stratification Matters**:
   - High-intent commercial queries (`"بهترین آژانس سئو در تهران"`) elicited structured recommendation lists with explicit feature matrices.
   - Solutive and trust-oriented queries (`"معیارهای انتخاب آژانس دیجیتال مارکتینگ معتبر"`) focused heavily on organizational transparency and case study citations.
3. **Execution Transparency (Native vs Fallback Routing)**:
   - By preserving strict model provenance metadata (`requested_provider` vs `actual_model`), the study revealed that when gateways route through fallback backends (e.g., Qwen surrogate models during upstream provider rate limits), brand recommendation structures remain coherent while citation grounding density varies.

---

## 🛠️ The Molavi AI Visibility Index (MAVI)

This benchmark establishes Layer 5 (**Measured AI Visibility**) of the MAVI framework, completing the full diagnostic-to-empirical pipeline:
- **L1 Technical Accessibility**: Assessed via SAGE SEO (robots.txt, clean DOM).
- **L2 Semantic Extractability**: Assessed via SAGE clean chunking.
- **L3 Entity Clarity**: Assessed via SAGE AEO JSON-LD graphs.
- **L4 Citation Readiness**: Assessed via SAGE Citation Survival Proxy (CSP).
- **L5 Empirical AI Visibility**: Assessed via GEO-Scope live benchmark observations.

---

## 📦 Reproducibility & Open Data

All datasets, prompt records, raw completions, and calculated metrics are open source and cryptographically signed:

```bash
# Verify integrity
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Reproduce metrics locally
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

Explore the code and benchmark artifacts on [GitHub: tmolavi/geo-scope](https://github.com/tmolavi/geo-scope).
