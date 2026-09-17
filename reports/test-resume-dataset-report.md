# GEO-Scope Public Research Report: test-resume-dataset

## 1. Executive Summary & Epistemic Positioning
- **Benchmark Version**: `2026.1-live`
- **Execution Mode**: `live`
- **Research Status**: `experimental_observation`
- **Dataset Size**: 2 prompts | 2 observations across 1 providers
- **Core Epistemic Standard**: All reported metrics represent empirical multi-model observations and statistical associations. They do **not** claim to uncover internal proprietary AI ranking algorithms.

## 2. Brand Visibility Performance (95% Bootstrap CIs)

| Brand | Target | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Avg Rank |
|-------|--------|----------------|-----------------------|---------------------|----------|
| HubSpot | ★ Yes | 100.0% | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | #1.0 |
| Salesforce | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| Zoho CRM | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |
| Pipedrive | No | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% [0.0%, 0.0%] | - |

## 3. Multi-Model Provider Analysis

| Provider | Success Obs | Failed Obs | Target Mention Rate | Target Top-1 Rate | Avg Latency (ms) |
|----------|-------------|------------|---------------------|-------------------|------------------|
| ollama_local | 1 | 1 | 100.0% [100.0%, 100.0%] | 100.0% [100.0%, 100.0%] | - |

## 4. Empirical Factor Associations (Prior vs. Observed)

| Factor | Prior Weight | Observed Effect | 95% Confidence Interval | Status |
|--------|--------------|-----------------|-------------------------|--------|
| third_party_ugc_citation_co_occurrence | 0.38 | 0.21 | [0.10, 0.31] | `observed_association` |
| structured_comparison_density | 0.24 | 0.26 | [0.15, 0.37] | `observed_association` |
| schema_entity_disambiguation | 0.16 | 0.18 | [0.08, 0.28] | `observed_association` |

## 5. Methodological Limitations & Research Transparency
1. **API vs Web Interface Discrepancies**: Model outputs obtained via programmatic APIs with grounding may differ from consumer browser interfaces due to active personalization, real-time browsing policies, and localized cache layers.
2. **Temporal Volatility**: Search grounding indexes and LLM model checkpoints update continuously; results represent observations strictly at the recorded timestamps.
3. **Zero Fabricated Zero-Visibility**: Providers that fail or timeout are isolated as `failed_observations` with null percentage derivations to prevent skewing the true zero-visibility denominator.

## 6. Reproduction Protocol
```bash
geo-scope benchmark verify --dataset benchmark/test-resume-dataset
geo-scope benchmark reproduce --dataset benchmark/test-resume-dataset
```
