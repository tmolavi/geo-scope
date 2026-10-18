# GEO-Scope Measurement Architecture Migration Guide

**Target Version:** Minimum Measurement Contract v1.0  
**Effective Date:** October 2026  
**Audience:** Data Engineers, SEO Specialists, Platform Integrators, and Benchmarking Teams  

---

## 1. Overview of Changes

The transition to **Minimum Measurement Contract v1.0** upgrades GEO-Scope from an experimental heuristic tracker into a scientifically auditable, multi-engine measurement architecture.

### Key Architectural Shifts
1. **Metric Disentanglement:** `Mention Rate`, `Citation Rate (All Answers)`, `Citation Rate (Retrieval-Evidence)`, `Recommendation Rate`, `Top Recommendation Rate`, `Average First Mention Position`, and `Share of Model` are now strictly separated.
2. **Central Denominator Accounting:** Every metric is backed by explicit numerator, denominator, sample size, and coverage fields.
3. **Statistical Uncertainty:** 95% Wilson Score Confidence Intervals are required for all binomial rates; non-parametric Bootstrap intervals for continuous distributions.
4. **Decoupled MAVI:** Technical Readiness (L1–L4) is formally decoupled from Observed Visibility (L5). `mavi_composite` is `null` if L5 is unmeasured.
5. **GSC Realignment:** `AI Position` is renamed to `AI Block Position` and tagged as directional SERP layout data, never as a citation rank.
6. **Multilingual Normalization:** 3-tier entity matching (`exact`, `normalized_exact`, `probable`) with rule-level transformation tracing.

---

## 2. Entity Registry Migration

### Legacy Schema
```json
{
  "id": "inten",
  "names": ["Inten", "اینتن"],
  "domains": ["inten.asia"],
  "people": ["Taghi Molavi"]
}
```

### Upgraded Contract v1.0 Schema
```json
{
  "entity_id": "brand-inten",
  "canonical_name": "InTen",
  "entity_type": "organization",
  "parent_entity_id": null,
  "names": ["Inten", "اینتن"],
  "aliases": [
    { "value": "اینتن", "language": "fa", "match_type": "exact" },
    { "value": "Inten", "language": "en", "match_type": "case_insensitive" }
  ],
  "excluded_aliases": ["intent"],
  "do_not_confuse": ["اینترنت", "بازار مولوی"],
  "domains": ["inten.asia"],
  "related_domains": ["molavi.pro"],
  "same_as": ["https://wikidata.org/wiki/Q..."],
  "normalization_version": "1.0"
}
```

### Python API Usage
```python
from geo_scope.entities.registry import EntityRegistry
from geo_scope.entities.models import Entity

registry = EntityRegistry.load_from_file("entities.json")
# Backward-compatible: registry.all(), registry.get("inten"), registry.ids() continue working.

# New features:
children = registry.get_children(parent_entity_id="alphabet")
matches = registry.find_matches(text="شرکت اینتن خدمات سئو ارائه می‌دهد", language="fa")
for m in matches:
    print(m.entity_id, m.match_type, m.normalization_rules_applied)
```

---

## 3. Metric Consumption & API Migration

### Legacy Structure
```json
{
  "mention_rate": 0.45,
  "citation_rate": 0.30
}
```

### Upgraded Contract v1.0 Structure
```json
{
  "mention_rate": 0.45,
  "contract_v1_metrics": {
    "mention_rate": {
      "value": 0.45,
      "numerator": 9,
      "denominator": 20,
      "denominator_type": "valid_answers",
      "sample_size": 20,
      "coverage": 1.0,
      "status": "measured",
      "ci_method": "wilson",
      "confidence_level": 0.95,
      "ci_lower": 0.258,
      "ci_upper": 0.658,
      "ci_width": 0.400
    },
    "citation_rate_all_answers": {
      "value": 0.30,
      "numerator": 6,
      "denominator": 20,
      "denominator_type": "valid_answers",
      "sample_size": 20,
      "coverage": 1.0,
      "status": "measured",
      "ci_lower": 0.145,
      "ci_upper": 0.519
    },
    "citation_rate_retrieval_evidence": {
      "value": 0.60,
      "numerator": 6,
      "denominator": 10,
      "denominator_type": "retrieval_evidence_answers",
      "sample_size": 10,
      "coverage": 0.50,
      "status": "measured",
      "ci_lower": 0.313,
      "ci_upper": 0.832
    },
    "confidence_label": "moderate"
  }
}
```

> **Backward Compatibility Guarantee:** Legacy root scalar fields (`mention_rate`, `citation_rate`) are retained to prevent breaking existing dashboards. All new uncertainty and denominator metadata are exposed under `contract_v1_metrics`.

---

## 4. MAVI Architecture Migration

### Decoupled Reporting
When measuring MAVI without live L5 observations:

```python
from geo_scope.mavi import MAVIEngine

engine = MAVIEngine()
report = engine.measure(
    html_content=html,
    url="https://inten.asia",
    target_brand="InTen",
    experiment_data=None  # L5 not run
)

# New Decoupled Outputs:
print("Readiness Score (L1-L4):", report.readiness_score)  # e.g., 74.2
print("Observed Visibility (L5):", report.observed_visibility["status"])  # "not_measured"
print("MAVI Composite:", report.mavi_composite)  # None
print("Composite Reason:", report.composite_reason)  # "Live empirical visibility has not been measured."

# Sensitivity Analysis:
sensitivity = engine.sensitivity_analysis(report, delta=0.10)
```

---

## 5. Google Search Console & SERP Alignment

1. **Rename Key:** Change any reference to `ai_position` or `ai_rank` to `ai_block_position`.
2. **Tag Quality:** Tag records with `measurement_quality = "directional"`.
3. **Mandatory Disclaimer:** Display the disclaimer in UI/reports:
   > *"AI Block Position reflects the position of the AI Overview block on the search results page. It does not measure citation ranking or brand prominence inside the generated text."*

---

*End of Migration Guide.*
