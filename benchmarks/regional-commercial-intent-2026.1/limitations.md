# Limitations & Scientific Gating

**Benchmark Identifier:** `regional-commercial-intent-2026.1`  
**Markets:** Iran (`fa-IR`), Türkiye (`tr-TR`)  
**Status:** Reproducible Research Pilot (`NOT_RUN` Pending Live Provider Authentication)

---

## 1. Exploratory Nature & Statistical Non-Representativeness

This benchmark is an **exploratory regional pilot** inspired by intent-based AI visibility measurement architectures (such as the Peak Ace 2026 methodology). 

- **Sample Size:** 24 unique buyer prompts (12 for Iran, 12 for Türkiye) distributed equally across 4 intent strata (3 prompts per stratum per market).
- **Sampling Matrix:** 24 prompts × 3 grounded engines × 2 repetitions = 144 planned observations.
- **Statistical Boundary:** A sample of 24 prompts provides directional calibration and pipeline verification for commercial queries, but **it cannot and does not claim statistical representativeness** of the entire Iranian or Turkish generative search query universe.
- **Uncertainty Bounds:** Proportions derived from exploratory pilots must be reported with appropriate uncertainty intervals (e.g., Wilson score intervals at 95% confidence).

---

## 2. Market & Linguistic Delimitations

1. **Linguistic Autonomy:** Prompts were created natively in Persian (`fa-IR`) and Turkish (`tr-TR`) by domain specialists. They are **not mechanical translations** of one another. Each prompt reflects the idioms, commercial phrasing, and vendor evaluation terminology typical of enterprise and SME buyers in its respective market.
2. **Local Infrastructure Nuances:**
   - **Iran (`fa-IR`):** Localized web access involves distinct regional routing, domestic search engines, and restricted access to certain global services, influencing how search engines (Bing, Google) index Persian corporate sites.
   - **Türkiye (`tr-TR`):** High mobile and search engine saturation with distinct Turkish digital marketing and PR ecosystems.
3. **Non-Generalizability:** Observations in these two markets cannot be extrapolated to Western, European, or pan-Arab commercial queries.

---

## 3. Strict Provider Identity & Grounding Integrity

GEO-Scope enforces strict measurement rules regarding AI search grounding:

- **Approved Search Engines:** Only engines with verified live search grounding tools (`chatgpt_search`, `gemini_grounding`, `perplexity_sonar`) are approved for this benchmark.
- **Zero Fallback / Zero Substitution Policy:** Substituting a non-grounded parametric LLM (e.g., base GPT-4o, base Claude 3.7) while labeling it "search-grounded" or "AI search" is scientifically deceptive and prohibited by `providers.yml` governance.
- **Execution State:** In environments where live search-grounded API credentials are not provisioned, provider adapters are explicitly marked `PROVIDER_UNAVAILABLE`, and benchmark execution status is recorded as `NOT_RUN`.
- **Zero Fabrication:** Simulated or synthetic responses are never mixed into empirical release packages.

---

## 4. Temporal Dynamics & Engine Volatility

Generative engine answers are inherently non-deterministic and dynamic:
1. Retrieval indices (Google Search, Bing Search, Perplexity Index) update continuously.
2. Grounding pipelines and model weights change without public changelog notification.
3. Observations reflect specific timestamped executions, not immutable rankings.

---

## 5. Methodological Incomparability with Peak Ace 2026

While this pilot adopts an intent-based structure inspired by the Peak Ace AI Visibility LLM Benchmark 2026, **direct comparison of raw visibility percentages between the two studies is scientifically invalid**:

| Dimension | Peak Ace 2026 Benchmark | GEO-Scope Regional Pilot 2026.1 | Methodological Impact |
| :--- | :--- | :--- | :--- |
| **Sample Size** | Tens of thousands of queries across multi-industry corpora | 24 curated commercial queries (144 planned observations) | Different statistical power and confidence bounds |
| **Markets & Language** | US, UK, DACH (English, German) | Iran (`fa-IR`), Türkiye (`tr-TR`) | Disparate indexing depth, linguistic tokenization, local competition |
| **Intent Scope** | Broad consumer & enterprise ecommerce/informational | B2B Commercial buying cycle (SEO, GEO, Technical Audit, PR) | B2B queries exhibit lower variance and distinct entity densities |
| **Observation Timing** | Longitudinal snapshot across earlier 2025/2026 windows | Independent 2026 observation window | Search engines and models evolve continuously |

Researchers must cite Peak Ace as a conceptual and methodological inspiration for intent grouping, rather than comparing numerical visibility percentages as if both studies drew from the same population.
