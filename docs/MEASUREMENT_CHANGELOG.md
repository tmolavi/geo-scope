# GEO-Scope Measurement Architecture Changelog

All notable technical and methodology updates to GEO-Scope's measurement architecture are documented in this file.

---

## [1.0.0] — 2026-10-12

### Added
- **Minimum Measurement Contract v1.0 (`docs/MINIMUM_MEASUREMENT_CONTRACT.md`)**:
  - Implemented versioned prompt panel schema (`prompt_id`, `prompt_version`, `brand_named`, `zero_prompt`, `market`, `intent`).
  - Formalized Repetition Policy: $\ge 5$ runs for `measured`, $2 \le k < 5$ for `directional`, $k=1$ for `single_observation`, $k=0$ for `not_measured`.
  - Implemented full provenance schema with transparent separation of `requested_model` vs `actual_model` and fallback tracking.
  - Strict fixture isolation rule (`eligible_for_public_benchmark = false`).
- **Metric Dictionary (`docs/METRIC_DICTIONARY.md`)**:
  - Formalized strict mathematical definitions, numerators, and denominators for:
    - `Mention Rate` (`valid_answers`)
    - `Citation Rate — All Answers` (`valid_answers`)
    - `Citation Rate — Retrieval-Evidence Answers` (`retrieval_evidence_answers`)
    - `Recommendation Rate` (`valid_answers`)
    - `Top Recommendation Rate` (`answers_with_recommendations`)
    - `Average First Mention Position` (`answers_with_target_mention`, strictly non-zero)
    - `Share of Model` (`all_tracked_entity_mentions`)
    - `Owned-Domain Citation Rate` (`retrieval_evidence_answers`)
    - `Source Influence` (strictly `not_measured`)
- **Statistical Module (`geo_scope/measurement/stats.py`)**:
  - Implemented 95% Wilson Score Confidence Interval calculator with mathematical safety for edge cases ($n=0$, $k=0$, $k=n$).
  - Implemented non-parametric Bootstrap Resampling confidence interval generator (1,000 resamples, deterministic seed).
  - Implemented overlapping confidence interval detector with standard uncertainty warning.
  - Implemented rule-based confidence label generator (`insufficient`, `directional`, `moderate`, `strong`).
- **Central Denominator Registry (`geo_scope/measurement/denominators.py`)**:
  - Created central ledger tracking attempted, completed, valid, retrieval-evidence, citation, recommendation, and mention denominators.
  - Added standardized `MetricRecord` model.
- **Multilingual Entity Normalizer (`geo_scope/entities/normalizer.py`)**:
  - Comprehensive multilingual normalization supporting Persian (`fa`), English (`en`), Turkish (`tr`), Azerbaijani Latin (`az`), and Arabic (`ar`).
  - Added 3-tier classification: `exact`, `normalized_exact`, and `probable`.
  - Implemented rule transformation auditing (`normalization_rules_applied`).
  - Added negative homonym filtering (`do_not_confuse`), collision filters (`excluded_aliases`), and parent-brand hierarchies (`parent_entity_id`).
- **MAVI Architecture Decoupling (`geo_scope/mavi/`)**:
  - Decoupled MAVI into Readiness (L1–L4) and Observed Visibility (L5).
  - Enforced strict null rule: `mavi_composite` is `null` when L5 is unmeasured.
  - Added sensitivity analysis engine (`engine.sensitivity_analysis()`).
- **UGC Fresh Data Readiness Audit (`geo_scope/audit/ugc_readiness.py`)**:
  - Standalone optional 14-point audit module evaluating publisher readiness for Google's UGC Fresh Data Program.
- **Export & Reporting Enhancements (`geo_scope/engine/export_manager.py`, `report_generator.py`)**:
  - Added `export_contract_v1_metrics_to_csv` function.
  - Integrated mandatory GSC AI Block Position and UGC readiness disclaimers into generated markdown and HTML reports.
- **Reference Examples & Schemas**:
  - `examples/measurement-contract-example.json`
  - `examples/mavi-result-example.json`
  - `examples/ugc-readiness-example.json`
  - `schemas/ugc-readiness-schema.json`

### Changed
- **`MeasurementEngine` (`geo_scope/measurement/engine.py`)**:
  - Upgraded `_compute_metrics()` to compute both legacy fields and Minimum Measurement Contract v1.0 metrics with Wilson CIs, Bootstrap CIs, and Engine $\times$ Intent $\times$ Language breakdown.
- **`ObservationParser` (`geo_scope/parser/observation_parser.py`)**:
  - Enhanced parsing to populate `match_type`, `normalization_rules_applied`, `owned_domain_cited`, `first_mention_position`, and `recommendation_evidence`.
- **`EntityRegistry` (`geo_scope/entities/registry.py`)**:
  - Integrated `MultilingualNormalizer` and added parent/child querying methods (`get_children`, `get_parents`).

### Preserved (Backward Compatibility)
- All existing CLI commands (`geo-scope measure`, `geo-scope replay`, `geo-scope demo`) remain completely functional.
- All legacy metric keys (`simulated_mention_rate`, `search_mention_rate`, `search_visibility_score`) remain intact.
