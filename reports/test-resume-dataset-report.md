# GEO-Scope Public Research Report: test-resume-dataset

## 1. Executive Summary & Epistemic Positioning
- **Benchmark Version**: `2026.1-live`
- **Benchmark Mode**: `DISCOVERY` (Official strict evaluation vs operational discovery)
- **Execution Mode**: `live`
- **Research Status**: `experimental_observation`
- **Dataset Size**: 2 prompts | 2 observations across 1 providers
- **Execution Provenance**: 0 native observations | 0 fallback-routed observations | 1 failed
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
| None | - | - | 0 | - | Zero fallback routing detected |

## 3. Brand Visibility Performance (95% Bootstrap CIs)

| Brand | Target | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Avg Rank |
|-------|--------|----------------|-----------------------|---------------------|----------|
| HubSpot | ★ Yes | 100.0% | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | #1.0 |
| Salesforce | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| Zoho CRM | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| Pipedrive | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |

## 4. Multi-Model Provider Analysis

| Provider | Success Obs | Failed Obs | Target Mention Rate | Target Top-1 Rate | Avg Latency (ms) |
|----------|-------------|------------|---------------------|-------------------|------------------|
| ollama_local | 1 | 1 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | - |

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
geo-scope benchmark verify --dataset benchmark/test-resume-dataset
geo-scope benchmark reproduce --dataset benchmark/test-resume-dataset
```
