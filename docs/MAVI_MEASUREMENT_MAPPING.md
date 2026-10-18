# MAVI Measurement Architecture & Layer Decoupling Specification

**Version:** 1.0.0  
**Effective Date:** October 2026  
**Status:** Mandatory Standard for Molavi AI Visibility Index (MAVI)  
**Authority:** Molavi GEO Pyramid & Empirical Measurement Gate  
**Axiom:** `Readiness ≠ Observed Visibility`

---

## 1. Executive Summary

The Molavi AI Visibility Index (MAVI) was originally conceptualized as a multi-layer framework spanning site infrastructure to live search visibility. However, earlier versions occasionally allowed on-page technical readiness (Layers 1–4) to mask or substitute for actual empirical visibility in AI search engines (Layer 5).

Under this specification, **MAVI is strictly decoupled into two independent pillars**:
1. **Readiness (Audit Layers L1–L4)**: Evaluates whether a domain's technical, semantic, entity, and retrieval assets are primed for crawler extraction and AI citation.
2. **Observed Visibility (Empirical Benchmark Layer L5)**: Measures actual empirical presence, citations, and recommendations across live AI models under Minimum Measurement Contract v1.0.

---

## 2. The Two Decoupled Pillars

```
┌────────────────────────────────────────────────────────────────────────┐
│                      MOLAVI GEO PYRAMID MAPPING                        │
├────────────────────────────────────────────────────────────────────────┤
│  PILLAR 1: READINESS (SAGE / Crawler Audit Engine)                     │
│  ├── L1: Technical Accessibility (Crawlability, Robots, WAF, Latency)   │
│  ├── L2: Semantic Extractability (JSON-LD, HTML structure, Q&A)        │
│  ├── L3: Entity Clarity (Knowledge Graph, sameAs, Brand Ambiguity)     │
│  └── L4: Retrieval / Citation Readiness (Direct Quotes, CSP, Stats)    │
│                                                                        │
│  Output: readiness_score (0–100)                                       │
├────────────────────────────────────────────────────────────────────────┤
│  PILLAR 2: OBSERVED VISIBILITY (GEO-Scope Empirical Benchmark)        │
│  └── L5: Empirical AI Visibility (Live LLM Multi-Engine Observations)  │
│      ├── Mention Rate & 95% Wilson CI                                  │
│      ├── Citation Rate (All vs Retrieval-Evidence) & 95% Wilson CI     │
│      ├── Recommendation Rate & Top Recommendation Rate                 │
│      ├── Average First Mention Position (Non-Zero)                     │
│      └── Share of Model                                                │
│                                                                        │
│  Output: observed_visibility_metrics & status                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Strict Non-Zero Missing Data Rule for Composite MAVI

A website with perfect technical SEO cannot be claimed to have high AI visibility if its presence in AI answers has never been empirically tested.

### The Decoupling Invariant
**If Layer 5 (Observed AI Visibility) has not been measured with live empirical data, the final `mavi_composite` MUST BE `null`.**

The system must output:
```json
{
  "entity_id": "brand-inten",
  "readiness_score": 72.4,
  "readiness_layers": {
    "L1": { "score": 85.0, "status": "measured", "weight": 0.15 },
    "L2": { "score": 70.0, "status": "measured", "weight": 0.20 },
    "L3": { "score": 68.0, "status": "measured", "weight": 0.20 },
    "L4": { "score": 65.0, "status": "measured", "weight": 0.15 }
  },
  "observed_visibility": {
    "status": "not_measured",
    "metrics": null,
    "confidence_label": "insufficient"
  },
  "mavi_composite": null,
  "reason": "Live empirical visibility has not been measured."
}
```

### Prohibited Anti-Patterns
1. **Never set L5 = 0 when unmeasured:** Treating unmeasured as zero would artificially crush a brand's readiness score.
2. **Never re-normalize across L1–L4 to output a 100-point composite without L5:** Doing so presents a technical audit as an AI visibility score, misleading stakeholders into believing they are visible in ChatGPT and Gemini.

---

## 4. Status Values for Observed Visibility

Layer 5 must record one of the following explicit status values:

| Status Value | Meaning | Composite MAVI Calculation |
|:---|:---|:---|
| `measured` | Full empirical benchmark executed with $k \ge 5$ runs per prompt unit. | `mavi_composite` computed with standard weighting. |
| `directional` | Benchmark executed with $2 \le k < 5$ runs. | `mavi_composite` computed with prominent directional warning. |
| `single_observation` | Only 1 run executed ($k=1$). | `mavi_composite = null` (insufficient for index). |
| `not_measured` | No empirical benchmark executed. | `mavi_composite = null`. |
| `insufficient_data` | Run aborted, rate-limited, or valid responses $< 50\%$. | `mavi_composite = null`. |
| `provider_error` | Target AI engines failed or returned auth errors. | `mavi_composite = null`. |
| `not_verified` | Model provenance or search grounding unverified. | `mavi_composite = null`. |
| `fixture_only` | Synthetic or replay test fixtures used. | `mavi_composite = null` (unfit for public report). |

---

## 5. Weighting Architecture & Sensitivity Analysis

### 5.1 Canonical Weighting Models

Weights are versioned and immutable once published:

```json
{
  "version": "1.0.0",
  "name": "standard_balanced_2026",
  "weights": {
    "L1_technical_accessibility": 0.15,
    "L2_semantic_extractability": 0.20,
    "L3_entity_clarity": 0.20,
    "L4_citation_readiness": 0.15,
    "L5_observed_ai_visibility": 0.30
  },
  "sum": 1.00
}
```

Alternative versioned profiles include:
- `empirical_heavy_2026`: L1: 0.10, L2: 0.10, L3: 0.10, L4: 0.10, L5: 0.60.
- `readiness_only_2026`: L1: 0.25, L2: 0.30, L3: 0.25, L4: 0.20, L5: 0.00 (`mavi_composite` disabled).

### 5.2 Sensitivity Analysis Output
Reports must support weight perturbation sensitivity tests ($\pm 10\%$ shift between Readiness and Empirical layers) to demonstrate score stability.

---

*MAVI Measurement Architecture & Layer Decoupling Specification v1.0.*
