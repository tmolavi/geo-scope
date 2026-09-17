# Benchmark Methodology: GEO, SEO & Digital Marketing Agency Iran 2026

## 1. Epistemic Principles
* **Empirical Observation, Not Algorithm Claims**: This benchmark does not claim to reverse-engineer proprietary AI ranking algorithms. It strictly measures and reports empirical completions returned by AI providers.
* **Neutral Multi-Entity Evaluation**: Evaluates 8 established entities under identical conditions without target-brand bias.
* **Separation of Priors & Observations**: Prompt hypotheses are never reported as measured user demand.

---

## 2. Experimental Design

### A. Question Discovery & Intent Strata (AnswerPath GEO)
The benchmark prompt bank consists of 30 standardized queries:
- **Observed Demand ($N=15$)**: Real user questions extracted from search and chatbot query logs.
- **Generated Templates ($N=15$)**: Systematic exploratory variations covering all major decision stages.

Queries are stratified across 5 distinct intents:
1. `commercial`: General agency recommendations and evaluation.
2. `compare`: Direct head-to-head comparisons and alternatives.
3. `trust`: Agency reliability, contract integrity, and track record.
4. `solve`: Technical SEO migration, penalty recovery, and schema fixes.
5. `buy`: Enterprise procurement, retainer pricing, and quotes.

### B. Multi-Provider Execution Matrix
Completions are collected across 4 AI routes:
1. `gemini` (`gemini-2.5-flash`)
2. `openai` (`gpt-4o`)
3. `claude` (`claude-3-5-sonnet`)
4. `perplexity` (`sonar-pro`)

Total completions: $30 \times 4 = 120$ observations.

### C. Execution Provenance & Routing Classes
Every completion records:
- `requested_provider` & `requested_model`
- `actual_provider` & `actual_model`
- `fallback_active` (boolean)
- `execution_class`:
  - `native`: Executed directly on requested provider/model.
  - `fallback`: Route redirected due to upstream rate limits/failover.
  - `failed`: Network or API failure (excluded from denominator).

---

## 3. Metrics & Statistical Formulas

### Brand Mention Rate ($MR_e$)
$$MR_e = \frac{\sum_{i=1}^N \mathbb{I}(e \in \text{Mentions}_i)}{N}$$

### Recommendation Rate ($RR_e$)
$$RR_e = \frac{\sum_{i=1}^N \mathbb{I}(e \in \text{Recommendations}_i)}{N}$$

### Top-1 Recommendation Share ($T1_e$)
$$T1_e = \frac{\sum_{i=1}^N \mathbb{I}(\text{Top1}_i = e)}{N}$$

### 95% Bootstrap Confidence Intervals
Confidence intervals are computed using 1,000 non-parametric bootstrap resamples ($\alpha = 0.05$):
$$\text{CI}_{95\%} = [\hat{\theta}^*_{(25)}, \hat{\theta}^*_{(975)}]$$

---

## 4. Integrity & Reproducibility Guarantees
1. **Cryptographic Checksums**: Every release artifact includes a `checksums.sha256` manifest.
2. **Raw Evidence Retention**: Full completion texts, token usages, and timestamps are stored in `observations.jsonl`.
3. **Deterministic Math Verification**: The `geo-scope benchmark reproduce` command recomputes all metrics from raw completions without network access.
