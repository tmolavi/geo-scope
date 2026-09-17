# Release 2026.1: GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark

### *Measuring AI Visibility, Recommendations, and Citation Presence Across Generative AI Platforms*

We are pleased to announce the official release of the **GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark (v2026.1)**, an open, fully reproducible empirical study conducted using the complete Molavi AI Visibility Stack (**AnswerPath GEO** → **GEO-Scope** → **Hamzad AI Gateway**).

---

## 🎯 Epistemic Grounding & Scientific Position

This benchmark does **not** claim to discover proprietary search algorithms or provide guaranteed rankings. Rather, it provides an open, empirical framework to measure:
- **Observed Brand Mentions**: How frequently specific brand entities are returned in completions across generative models.
- **Top-1 Recommendation Rate**: How frequently models designate a brand as their primary recommended entity.
- **Question Demand Stratification**: Explicit separation of genuine observed user queries (from AnswerPath GEO) from synthetic exploration prompt templates.
- **Execution Provenance**: Verifiable separation between native model completions and surrogate fallback routes with zero synthetic data injection.

---

## 📦 Dataset Package Structure

The benchmark artifacts are published under [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](../../benchmark/releases/geo-seo-digital-agency-iran-2026.1/):

| File | Description | Verification |
|------|-------------|--------------|
| `manifest.json` | Dataset metadata, execution parameters, and provider validation records | SHA-256 Verified |
| `prompts.jsonl` | Complete stratified prompt pool with AnswerPath question provenance | SHA-256 Verified |
| `prompts/observed.jsonl` | 15 observed real user queries across commercial, compare, trust, solve, buy | SHA-256 Verified |
| `prompts/generated.jsonl` | 15 generated exploration prompt hypotheses | SHA-256 Verified |
| `provenance.json` | Demand stratification breakdown and source reference index | SHA-256 Verified |
| `observations.jsonl` | Multi-provider raw response records with execution class and model provenance | SHA-256 Verified |
| `citations.jsonl` | Extracted verified citations from search grounding | SHA-256 Verified |
| `brands.json` | Target brands and evaluated competitor entities | SHA-256 Verified |
| `providers.json` | Evaluated provider configurations | SHA-256 Verified |
| `metrics.json` | Calculated visibility metrics with 95% bootstrap confidence intervals | SHA-256 Verified |
| `checksums.sha256` | Cryptographic checksums ensuring bit-for-bit integrity | SHA-256 Verified |

---

## 🔬 Key Architecture Innovations

1. **AnswerPath GEO Question Source Layer**:
   - Classifies search demand into 5 intent strata: `commercial`, `compare`, `trust`, `solve`, `buy`.
   - Tags every query with provenance (`source_type: "observed"` vs `"generated"`), preventing synthetic prompt leakage into real demand measurements.
2. **Hamzad AI Gateway Integration**:
   - Zero-secret client execution: GEO-Scope operates with zero stored provider API keys.
   - Dynamic model routing with explicit transparency: distinguishes native execution (`gemini-2.5-flash`, `gpt-4o`) from fallback surrogate routes (`qwen/qwen3.8-27b`).
3. **Molavi AI Visibility Index (MAVI) L5 Integration**:
   - Combines structural diagnostic layers (SAGE L1–L4) with live multi-model empirical measurements (GEO-Scope L5).

---

## 🔁 Reproduction & Verification

You can cryptographically verify and reproduce all calculations on your local machine:

```bash
# Verify bit-for-bit checksums
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Re-run mathematical aggregation and bootstrap confidence intervals
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

---

## 📄 Full Research Report & Articles

- [Full Benchmark Research Report](../../reports/geo-seo-digital-agency-iran-2026.1-report.md)
- [Benchmark Methodology Documentation](../../docs/benchmark-methodology.md)
- [Molavi.pro Publication](../../reports/articles/molavi_pro_article.md)
- [Medium Technical Deep Dive](../../reports/articles/medium_article.md)
