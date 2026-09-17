# Methodology: GEO-Scope AI Visibility Benchmark 2026.1

## 1. Research Scope & Objectives
This benchmark provides reproducible, observational measurements of brand mention rates, recommendation rankings, share of model, and citation presence across leading AI search engines and conversational assistants.

### Target Research Category
- **Domain**: AI SEO / Generative Engine Optimization (GEO) / AI Search Visibility Software
- **Analyzed Brands**: Semrush, Ahrefs, Moz, Surfer SEO, Clearscope, MarketMuse, Conductor, SAGE.
- **Participating Engines**: Google Gemini, Perplexity Sonar, OpenAI ChatGPT, Anthropic Claude.
- **Execution Architecture**: GEO-Scope via Hamzad AI Gateway (Zero-Secret Proxy Layer).

---

## 2. Epistemic Constraints & Non-Claims (What is NOT Measured)
- **No Algorithm Discovery Claim**: This benchmark does NOT claim reverse engineering of internal neural ranking algorithms.
- **No Causal Guarantee**: High brand visibility or citation co-occurrence reflects observed empirical association within the tested query distribution, not a deterministic ranking factor.
- **No Probabilistic Citation Promise**: Scores represent historical benchmark observational performance, not a guarantee of being cited on unobserved future queries.

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
To reproduce and verify this benchmark package bit-for-bit:
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1
```
Or programmatically:
```python
from geo_scope.benchmark.reproducer import BenchmarkReproducer
reproducer = BenchmarkReproducer(tolerance=0.01)
result = reproducer.verify_and_reproduce("benchmark/releases/geo-scope-ai-visibility-2026.1")
assert result["success"] is True
```
