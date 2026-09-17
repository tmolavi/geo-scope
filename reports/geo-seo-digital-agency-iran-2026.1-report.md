# GEO-Scope Public Research Report: geo-seo-digital-agency-iran-2026.1

## 1. Executive Summary & Epistemic Positioning
- **Benchmark Version**: `2026.1-live`
- **Benchmark Mode**: `DISCOVERY` (Official strict evaluation vs operational discovery)
- **Execution Mode**: `live`
- **Research Status**: `peer_review_ready`
- **Dataset Size**: 30 prompts | 120 observations across 4 providers
- **Execution Provenance**: 0 native observations | 51 fallback-routed observations | 69 failed
- **Core Epistemic Standard**: All reported metrics represent empirical multi-model observations and statistical associations. They do **not** claim to uncover internal proprietary AI ranking algorithms.

## 2. Execution Provenance & Model Separation

### A. Native Model Results
Direct model executions verified to match requested upstream architecture:

| Provider | Requested Model | Verified Actual Model | Observations | Avg Latency (ms) | Status |
|----------|-----------------|-----------------------|--------------|------------------|--------|
| None | - | - | 0 | - | No native model executions |

### B. Fallback Routed Results
Requests redirected to fallback or surrogate backends (never merged silently with native metrics):

| Requested Provider/Model | Actual Routed Backend | Trigger Reason | Observations | Avg Latency (ms) | Status |
|--------------------------|-----------------------|----------------|--------------|------------------|--------|
| gemini-2.5-flash (gemini-2.5-flash) | groq (qwen/qwen3.8-27b) | Upstream inactive / surrogate | 7 | 6821.5 | `FALLBACK_RECORDED` |
| gpt-4o (gpt-4o) | avalai (gpt-4o-mini) | Upstream inactive / surrogate | 30 | 6800.4 | `FALLBACK_RECORDED` |
| claude-3-5-sonnet (claude-3-5-sonnet) | groq (qwen/qwen3.8-27b) | Upstream inactive / surrogate | 7 | 7703.3 | `FALLBACK_RECORDED` |
| sonar-pro (sonar-pro) | groq (qwen/qwen3.8-27b) | Upstream inactive / surrogate | 7 | 6804.7 | `FALLBACK_RECORDED` |

## 3. Question Provenance & Demand Stratification

### A. Observed Question Results (Real User Demand)
Measurements derived strictly from real recorded user queries and customer logs:

| Brand | Observed Mention Rate | Observed Top-1 Rate | Sample Size | Demand Confidence |
|-------|-----------------------|---------------------|-------------|-------------------|
| None | - | - | 0 | No observed questions in run |

### B. Generated Research Prompt Results (Exploration Templates)
Measurements derived from structured exploration prompt templates (never conflated with real user demand):

| Brand | Template Mention Rate | Template Top-1 Rate | Sample Size | Category |
|-------|-----------------------|---------------------|-------------|----------|
| Web24 | 78.4% | 68.6% | 51 | Research Template (`generated`) |
| Novin | 86.3% | 7.8% | 51 | Research Template (`generated`) |
| Dimarketing | 80.4% | 11.8% | 51 | Research Template (`generated`) |
| Triboon | 56.9% | 0.0% | 51 | Research Template (`generated`) |
| DMN Agency | 21.6% | 2.0% | 51 | Research Template (`generated`) |
| Rayan | 0.0% | 0.0% | 51 | Research Template (`generated`) |
| Hamrah Marketing | 0.0% | 0.0% | 51 | Research Template (`generated`) |
| Inten | 0.0% | 0.0% | 51 | Research Template (`generated`) |

### C. Combined Operational Visibility
Blended operational index across all valid evaluation queries:

| Metric Dimension | Total Prompts | Observed Prompts | Generated Prompts | Source Reference |
|------------------|---------------|------------------|-------------------|------------------|
| Question Pool | 30 | 0 | 30 | `answerpath` |

## 4. Evaluated Entity Visibility Performance (95% Bootstrap CIs)

| Entity | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Avg Rank |
|--------|----------------|-----------------------|---------------------|----------|
| Web24 | 24.2% | 78.4% [66.7%, 90.2%] | 68.6% [54.9%, 82.3%] | #1.1 |
| Novin | 26.7% | 86.3% [76.5%, 94.2%] | 7.8% [2.0%, 15.7%] | #2.0 |
| Dimarketing | 24.8% | 80.4% [68.6%, 90.2%] | 11.8% [3.9%, 21.6%] | #2.1 |
| Triboon | 17.6% | 56.9% [43.1%, 70.6%] | 0.0% [0.0%, 0.0%] | #1.8 |
| DMN Agency | 6.7% | 21.6% [9.8%, 33.3%] | 2.0% [0.0%, 5.9%] | #0.8 |
| Rayan | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | #0.0 |
| Hamrah Marketing | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | #0.0 |
| Inten | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | #0.0 |

## 5. Multi-Model Provider Analysis

| Provider | Success Obs | Failed Obs | Avg Latency (ms) | Status |
|----------|-------------|------------|------------------|--------|
| gemini-2.5-flash | 7 | 23 | 6821.5 | Active |
| gpt-4o | 30 | 0 | 6800.4 | Active |
| claude-3-5-sonnet | 7 | 23 | 7703.3 | Active |
| sonar-pro | 7 | 23 | 6804.7 | Active |

## 5. Empirical Factor Associations (Prior vs. Observed)

| Factor | Prior Weight | Observed Effect | 95% Confidence Interval | Status |
|--------|--------------|-----------------|-------------------------|--------|
| third_party_ugc_citation_co_occurrence | 0.38 | 0.21 | [0.10, 0.31] | `observed_association` |
| structured_comparison_density | 0.24 | 0.26 | [0.15, 0.37] | `observed_association` |
| schema_entity_disambiguation | 0.16 | 0.18 | [0.08, 0.28] | `observed_association` |

## 6. Methodological Limitations & Research Transparency
1. **Dynamic Routing & Fallbacks**: Programmatic gateways dynamically route models and may activate fallback surrogate models when specific upstream endpoints are offline. GEO-Scope captures explicit execution provenance to distinguish native vs fallback observations.
2. **Requested vs Observed Identity**: Requested models represent experimental targets; observed models reflect the actual upstream generating backend. Official benchmarks evaluate native executions strictly.
3. **Temporal Volatility**: Search grounding indexes and LLM model checkpoints update continuously; results represent observations strictly at the recorded timestamps.

## 7. Reproduction Protocol
```bash
geo-scope benchmark verify --dataset benchmark/geo-seo-digital-agency-iran-2026.1
geo-scope benchmark reproduce --dataset benchmark/geo-seo-digital-agency-iran-2026.1
```
