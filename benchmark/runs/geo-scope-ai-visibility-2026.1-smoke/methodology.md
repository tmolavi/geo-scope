# GEO-Scope Benchmark Methodology (geo-scope-ai-visibility-2026.1-smoke)

## Overview
This benchmark evaluates Generative Engine Optimization (GEO) performance, brand visibility, and citation presence across multi-model AI engines.

## Execution Mode & Status
- **Execution Mode**: `live`
- **Research Status**: `experimental_observation`
- **Strict Separation**: Synthetic simulation runs are explicitly marked `demo_only` and must not be cited as real provider behavior.

## Measured Metrics
1. **Share of Model (SoM)**: Percentage of total observed brand mentions attributed to the brand.
2. **Mention Rate**: Percentage of successful multi-model observations containing the brand (with 95% bootstrap CI).
3. **Top-1 Primary Rate**: Percentage of successful observations where the brand is the first/primary recommendation.
4. **Citation Rate**: Percentage of observations citing the brand or authoritative third-party source.

## Statistical Bounds & Language Guardrails
- All confidence intervals are non-parametric 95% percentile bootstrap estimates (1,000 resamples).
- Factor analyses report **observed empirical correlations** only, avoiding speculative "AI ranking algorithm" assertions.
