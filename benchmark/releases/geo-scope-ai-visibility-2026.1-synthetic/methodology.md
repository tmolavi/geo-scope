# Methodology: GEO-Scope AI Visibility Benchmark 2026.1 (Synthetic Validation)

## 1. Scope & Purpose
This dataset serves as a deterministic synthetic validation artifact. It verifies the calculation of metrics, bootstrap confidence intervals, matrix dimensions, and checksum hashing across the GEO-Scope pipeline without incurring live model inference costs.

### Research Category
- **Domain**: AI SEO / Generative Engine Optimization (GEO) / AI Search Visibility Software
- **Simulated Brands**: Semrush, Ahrefs, Moz, Surfer SEO, Clearscope, MarketMuse, Conductor, SAGE.
- **Simulated Engines**: Google Gemini, Perplexity Sonar, OpenAI ChatGPT, Anthropic Claude.
- **Execution Mode**: `synthetic` (Validation Baseline)
- **Research Status**: `demo_only`

---

## 2. Epistemic Constraints & Non-Claims (Synthetic Disclaimer)
- **Synthetic Data**: This dataset contains simulated observations generated with deterministic seeding (seed=20260917) and must NOT be interpreted as real live model telemetry.
- **No Algorithm Discovery Claim**: This benchmark does NOT claim reverse engineering of internal neural ranking algorithms.
- **No Causal Guarantee**: Co-occurrence reflects generated baseline distributions for validation purposes only.

---

## 3. Stratified Sampling Design
The query distribution spans 100 queries stratified across 4 distinct user intent strata:
1. **Discovery (30%)**: Broad market exploration and platform discovery.
2. **Comparison (30%)**: Direct pairwise and multi-brand competitive comparisons.
3. **Commercial Intent (25%)**: Purchase, pricing, and enterprise procurement queries.
4. **Educational (15%)**: Conceptual understanding of GEO and AI search mechanisms.

---

## 4. Statistical Estimation
- **Sample Size**: 100 prompts x 4 providers = 400 total observations.
- **Confidence Intervals**: 95% non-parametric bootstrap confidence intervals (1,000 resamples) for all rate metrics.
- **Missing Data Handling**: Failed requests are explicitly excluded from denominators; unobserved states are never treated as zeros without evidence.

---

## 5. Reproduction Instructions
To reproduce and verify this synthetic validation package bit-for-bit:
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```
Or programmatically:
```python
from geo_scope.benchmark.reproducer import BenchmarkReproducer
reproducer = BenchmarkReproducer(tolerance=0.01)
result = reproducer.verify_and_reproduce("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
assert result["success"] is True
```
