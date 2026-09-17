# GEO-Scope Research Transparency & Limitations

## 1. Research Scope & Epistemic Boundaries

GEO-Scope is an open experimental framework for measuring brand visibility, citation presence, and model response variations across generative AI search providers.

### What GEO-Scope Measures:
- **Share of Model (SoM)**: Relative proportion of brand mentions in multi-model evaluation query sets.
- **Top-1 Recommendation Rate**: Proportion of queries where a target brand is returned as the primary/top recommendation.
- **Citation Attribution & Provenance**: Grounded web domains and URLs explicitly cited by search-augmented models.
- **Response Latency & Status**: Measurable API latency and reliability across providers.
- **Empirical Associations**: Statistical correlations ($r_s$) and effect sizes ($d$) between prompt strata / features and observed visibility.

### What GEO-Scope Does NOT Measure:
- **Internal Proprietary Ranking Algorithms**: LLMs and generative search engines do not publish deterministic ranking weights. GEO-Scope makes **no claim** to "reverse-engineer" black-box proprietary ranking algorithms.
- **Consumer Web Interface Equivalence**: API model completions may differ from logged-in consumer web search sessions (e.g. ChatGPT web UI, Perplexity Pro web UI) due to personalization, continuous A/B testing, conversational history, and differing system prompts.
- **Universal Ranking Factors**: No factor analyzed in GEO-Scope is claimed to be a universal causal factor. All factors are categorized as **"Observed associations"** with explicit uncertainty bounds.

---

## 2. Strict Live vs. Synthetic Mode Separation

GEO-Scope enforces strict, immutable boundaries between synthetic demo runs and live empirical observations:

| Dimension | Synthetic Mode | Live Mode |
|-----------|----------------|-----------|
| `execution_mode` | `"synthetic"` | `"live"` |
| `research_status` | `"demo_only"` | `"experimental_observation"` / `"peer_review_ready"` |
| Provider Inference | Deterministic pseudo-random simulation | Real network requests to provider APIs |
| Scientific Validity | None (Demo and test purposes only) | Verifiable with raw persisted response hashes |
| Fallback Policy | N/A | **Zero silent fallback** to simulation on provider error |

---

## 3. Provider Failures & Denominator Integrity

When a live provider encounters a 429 rate limit, 500 server error, or network timeout:
1. The attempt is preserved in `observations.jsonl` with `status: "failed"` and structured error details.
2. The failed attempt is **excluded from visibility and mention rate denominators**.
3. Zero-success metrics return `null` (`insufficient_data`) rather than `0.0%`, ensuring unobserved failures are never conflated with true measured zero-visibility.

---

## 4. Cryptographic Reproducibility & Integrity Verification

Every published dataset package includes a bit-level `checksums.sha256` manifest. Independent researchers can verify and reproduce findings locally:

```bash
# Verify bit-for-bit file integrity
geo-scope benchmark verify --dataset benchmark/geo-scope-benchmark-2026.1-live

# Recompute point estimates and 95% bootstrap confidence intervals
geo-scope benchmark reproduce --dataset benchmark/geo-scope-benchmark-2026.1-live
```
