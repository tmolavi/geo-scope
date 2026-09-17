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
| Web24 | 0.0% | 0.0% | 51 | Research Template (`generated`) |
| Novin | 0.0% | 100.0% | 51 | Research Template (`generated`) |
| Dimarketing | 0.0% | 0.0% | 51 | Research Template (`generated`) |
| Triboon | 0.0% | 0.0% | 51 | Research Template (`generated`) |
| DMN Agency | 0.0% | 0.0% | 51 | Research Template (`generated`) |

### C. Combined Operational Visibility
Blended operational index across all valid evaluation queries:

| Metric Dimension | Total Prompts | Observed Prompts | Generated Prompts | Source Reference |
|------------------|---------------|------------------|-------------------|------------------|
| Question Pool | 30 | 0 | 30 | `answerpath` |

## 4. Brand Visibility Performance (95% Bootstrap CIs)

| Brand | Target | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Avg Rank |
|-------|--------|----------------|-----------------------|---------------------|----------|
| Web24 | ★ Yes | N/A | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | #0.0 |
| Novin | No | N/A | 0.0% [0.0%, 0.0%] | 100.0% [100.0%, 100.0%] | - |
| Dimarketing | No | N/A | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| Triboon | No | N/A | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| DMN Agency | No | N/A | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |

## 4. Multi-Model Provider Analysis

| Provider | Success Obs | Failed Obs | Target Mention Rate | Target Top-1 Rate | Avg Latency (ms) |
|----------|-------------|------------|---------------------|-------------------|------------------|
| gemini-2.5-flash | 7 | 23 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 6821.5 |
| gpt-4o | 30 | 0 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 6800.4 |
| claude-3-5-sonnet | 7 | 23 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 7703.3 |
| sonar-pro | 7 | 23 | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | 6804.7 |

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
