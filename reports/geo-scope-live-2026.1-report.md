# GEO-Scope Public Research Report: geo-scope-benchmark-2026.1-live

## 1. Executive Summary & Epistemic Positioning
- **Benchmark Version**: `2026.1-live`
- **Execution Mode**: `live`
- **Research Status**: `experimental_observation`
- **Dataset Size**: 30 prompts | 120 observations across 4 providers
- **Epistemic Standard**: All reported metrics represent empirical multi-model observations and statistical associations. They do **not** claim to uncover internal proprietary AI ranking algorithms.

---

## 2. Brand Visibility Performance (95% Non-Parametric Bootstrap CIs)

| Brand | Target | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Citation Rate (95% CI) | Avg Rank |
|-------|--------|----------------|-----------------------|---------------------|------------------------|----------|
| HubSpot | ★ Yes | 28.2% | 73.7% [66.1%, 80.5%] | 26.3% [18.6%, 34.8%] | 79.7% [72.0%, 86.4%] | #1.9 |
| Salesforce | No | 23.9% | 62.7% [53.4%, 71.2%] | 46.6% [37.3%, 55.9%] | 61.0% [52.5%, 70.3%] | #2.4 |
| Zoho CRM | No | 24.6% | 64.4% [55.9%, 72.9%] | 17.8% [11.0%, 24.6%] | 30.5% [22.0%, 39.0%] | #2.5 |
| Pipedrive | No | 23.3% | 61.0% [52.5%, 69.5%] | 9.3% [5.1%, 14.4%] | 33.9% [25.4%, 42.4%] | #2.5 |

---

## 3. Multi-Model Provider Breakdown

| Provider | Success Obs | Failed Obs | Target Mention Rate (95% CI) | Target Top-1 Rate (95% CI) | Mean Latency (ms) |
|----------|-------------|------------|------------------------------|----------------------------|-------------------|
| perplexity_sonar | 30 | 0 | 73.3% [56.7%, 86.7%] | 26.7% [10.0%, 43.3%] | 1030.4 |
| gemini_grounding | 29 | 1 | 75.9% [58.6%, 93.1%] | 17.2% [3.5%, 31.1%] | 1141.6 |
| openai_completion | 30 | 0 | 76.7% [60.0%, 93.3%] | 30.0% [13.3%, 46.7%] | 1276.7 |
| claude_completion | 29 | 1 | 69.0% [51.7%, 86.2%] | 31.0% [13.8%, 48.3%] | 1135.0 |

---

## 4. Empirical Factor Associations (Prior vs. Observed)

| Factor | Prior Weight | Observed Effect | 95% Confidence Interval | Effect Size (Cohen's d) | Status |
|--------|--------------|-----------------|-------------------------|-------------------------|--------|
| third_party_ugc_citation_co_occurrence | 0.38 | 0.21 | [0.10, 0.31] | 0.49 | `observed_association` |
| structured_comparison_density | 0.24 | 0.26 | [0.15, 0.37] | 0.58 | `observed_association` |
| schema_entity_disambiguation | 0.16 | 0.18 | [0.08, 0.28] | 0.44 | `observed_association` |

---

## 5. Methodological Limitations & Research Transparency
1. **API vs Web Consumer Interface**: Programmatic completions with retrieval may diverge from consumer web UI sessions due to dynamic multi-step search loops and localized user personalization.
2. **Provider Failures as Distinct Data**: Network errors and provider rate limits are recorded as `failed` observations and strictly excluded from rate denominators, preventing artificial zero-visibility biases.
3. **Observation Timeframe**: All observations represent model and citation outputs captured at the recorded timestamps (`2026-03-16`).

---

## 6. Deterministic Reproduction Instructions
```bash
# 1. Verify SHA-256 Checksums
geo-scope benchmark verify --dataset benchmark/geo-scope-benchmark-2026.1-live

# 2. Recompute all metrics from raw observations
geo-scope benchmark reproduce --dataset benchmark/geo-scope-benchmark-2026.1-live
```
