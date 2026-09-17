# Empirical Case Study: AI Visibility Baseline for Digital Marketing Agencies in Iran (2026)

**Benchmark Reference**: `geo-seo-digital-agency-iran-2026.1`  
**Dataset**: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](../../benchmark/releases/geo-seo-digital-agency-iran-2026.1/)  
**Framework**: [Molavi AI Visibility Stack](../BENCHMARK_ECOSYSTEM.md)  
**Status**: Peer-Reviewed Empirical Baseline

---

## 1. Objective

Generative AI assistants (ChatGPT, Gemini, Claude, Perplexity) increasingly serve as first-stop conversational search engines for B2B procurement, agency evaluation, and digital marketing advisory queries.

The objective of this empirical study is **not** to declare a "winning agency" or claim reverse-engineered AI ranking factors. Rather, this study establishes an **open, reproducible baseline measurement** of how generative AI systems mention, recommend, and cite digital marketing and SEO agencies in Iran across standardized search queries.

This baseline forms Phase 1 of the closed-loop optimization cycle:
$$\text{Baseline Measurement (GEO-Scope)} \longrightarrow \text{Audit \& Remediation (SAGE + SiteProbe)} \longrightarrow \text{Re-measurement}$$

---

## 2. Methodology

The study adheres strictly to empirical observation principles:
1. **Question Stratification via AnswerPath GEO**: 30 queries divided into 15 observed user demand questions from real query logs and 15 exploratory hypothesis templates across 5 intent categories (`commercial`, `compare`, `trust`, `solve`, `buy`).
2. **Multi-Model Provider Matrix**: 4 distinct generative engine routes (Gemini 2.5 Flash, GPT-4o, Claude 3.5 Sonnet, Perplexity Sonar Pro) yielding $N = 120$ live completions.
3. **Neutral Multi-Entity Detection**: 8 established agency entities evaluated simultaneously under identical prompt conditions: Web24, Novin, Dimarketing, Triboon, DMN Agency, Rayan, Hamrah Marketing, and Inten.
4. **Statistical Rigor**: 95% non-parametric bootstrap confidence intervals (1,000 resamples) computed for all mention and recommendation metrics.

---

## 3. Dataset Profile

* **Prompt Count**: 30 (15 observed demand, 15 generated templates)
* **Total Completions ($N$)**: 120
* **Execution Mode**: Live Gateway Inference (Zero synthetic records)
* **Cryptographic Integrity**: SHA-256 verified package in `benchmark/releases/geo-seo-digital-agency-iran-2026.1/`

---

## 4. AI Providers Tested & Routing Provenance

| Provider Route | Configured Model | Actual Executed Model | Routing Class | Completions |
| :--- | :--- | :--- | :---: | :---: |
| **Google Gemini** | `gemini-2.5-flash` | `gemini-2.5-flash` | Native | 30 |
| **OpenAI** | `gpt-4o` | `gpt-4o` | Native | 30 |
| **Anthropic Claude** | `claude-3-5-sonnet` | `claude-3-5-sonnet` | Native | 30 |
| **Perplexity Sonar** | `sonar-pro` | `sonar-pro` / `qwen-27b` | Native / Fallback | 30 |

*Note: All fallback routes are explicitly flagged in `observations.jsonl` and separated during strict peer-review filtering.*

---

## 5. Observed Results

### A. Evaluated Entity Visibility Distribution

| Entity Name | Observed Mentions | Mention Rate [95% CI] | Recommendations | Rec Rate [95% CI] | Top-1 Recs | Top-1 Share |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Web24** (وب۲۴) | 26 | 21.7% [14.2%, 29.2%] | 25 | 20.8% [13.3%, 28.3%] | 14 | 11.7% |
| **Novin** (نوین) | 23 | 19.2% [12.5%, 26.7%] | 23 | 19.2% [12.5%, 26.7%] | 8 | 6.7% |
| **Dimarketing** | 8 | 6.7% [2.5%, 11.7%] | 8 | 6.7% [2.5%, 11.7%] | 4 | 3.3% |
| **Triboon** (تریبون) | 6 | 5.0% [1.7%, 9.2%] | 6 | 5.0% [1.7%, 9.2%] | 0 | 0.0% |
| **DMN Agency** | 5 | 4.2% [0.8%, 7.5%] | 5 | 4.2% [0.8%, 7.5%] | 0 | 0.0% |
| **Rayan** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 | 0.0% |
| **Hamrah Marketing** | 1 | 0.8% [0.0%, 2.5%] | 1 | 0.8% [0.0%, 2.5%] | 0 | 0.0% |
| **Inten** | 0 | 0.0% [0.0%, 0.0%] | 0 | 0.0% [0.0%, 0.0%] | 0 | 0.0% |

### B. Analysis of Entity Baselines: The Case of Inten

A foundational tenet of empirical AI visibility research is full reporting transparency. In this baseline run, **Inten** registered 0 observed mentions across 120 prompts (0.0% observed visibility).

Rather than viewing this as a negative ranking, the Molavi AI Visibility Stack treats 0.0% as a **clear diagnostic baseline** for targeted optimization:
1. **Diagnosis via SAGE**:
   - Check L1: Is `robots.txt` blocking AI crawlers (GPTBot, PerplexityBot, ClaudeBot)?
   - Check L2: Are key service offerings formatted in extractable 60–120 token semantic chunks?
   - Check L3: Does the site publish complete JSON-LD `Organization` schemas with `sameAs` entity links?
   - Check L4: Are comparison and case-study pages optimized for direct answer retrieval (CSP)?
2. **Remediation via SiteProbe**:
   - Generate and host `/llms.txt`.
   - Update structured data and entity disambiguation.
   - Refactor key landing pages to use bottom-line-up-front (BLUF) formatting.

---

## 6. Limitations

1. **Sample Size ($N=120$)**: Represents an initial empirical benchmark across 30 prompt variants; broader quarterly benchmarks ($N \ge 1,000$) will capture longer-tail queries.
2. **Temporal Model Drift**: Generative models update their retrieval indexes and training weights continuously; visibility rates are dynamic snapshots in time.
3. **Gateway Fallbacks**: When upstream provider rate-limits trigger fallbacks, completions are tracked as fallback classes rather than purely native inferences.

---

## 7. Future Re-Measurement Plan

1. **Action Phase (Q4 2026)**: Implement technical and semantic remediations using SAGE and SiteProbe across lower-visibility entities.
2. **Re-measurement Phase (Benchmark 2026.2)**: Execute a repeated benchmark study using the identical 30-prompt AnswerPath test suite to empirically measure visibility delta ($\Delta SoM$, $\Delta RR$, $\Delta Citations$).
3. **Longitudinal Tracking**: Publish tracking graphs showing visibility trajectories over time.
