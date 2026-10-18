# GEO-Scope Measurement Architecture Upgrade Audit

**Document Version:** 1.0.0  
**Date:** October 2026  
**Status:** Completed Baseline Audit  
**Author:** GEO-Scope Technical & Research Core  
**Axiom:** `Mention ≠ Citation ≠ Recommendation ≠ Position ≠ Share of Model`

---

## Executive Summary

GEO-Scope is a multi-engine measurement framework designed to evaluate brand and entity visibility across Generative AI engines (ChatGPT, Gemini, Google AI Overviews/Mode, Claude, Perplexity, and emerging models).

This audit conducts a thorough, critical assessment of GEO-Scope's existing measurement architecture prior to transitioning to **Minimum Measurement Contract v1.0**. Its purpose is to eliminate pseudo-deterministic outputs, disentangle conflated metrics, establish rigorous uncertainty bounds, enforce strict denominator accounting, and decouple infrastructure readiness from empirical observations.

---

## 1. Current Measurement Architecture Overview

The existing codebase consists of the following components:

1. **`geo_scope/measurement/engine.py` (`MeasurementEngine`)**:
   - Executes measurement batches in `live`, `simulation`, or `replay` modes.
   - Coordinates provider calls, collects raw text responses, and initiates parsing.
   - Outputs a research bundle containing `raw_responses.jsonl`, `observations.jsonl`, `summary.json`, and cryptographic checksums.

2. **`geo_scope/parser/observation_parser.py` (`ObservationParser`)**:
   - Evaluates LLM responses against entity definitions.
   - Performs intent recognition (`informational`, `recommendation`, `navigational`).
   - Extracts brand mentions, associated people, citations (matching official/related domains), and explicit linguistic recommendation phrases.

3. **`geo_scope/entities/registry.py` & `models.py` (`EntityRegistry`, `Entity`)**:
   - Stores entity IDs, brand names, executive names, official domains, and negative disambiguation phrases (`do_not_confuse`).
   - Provides text normalization (`normalize_text`) for Arabic/Persian letter unification, diacritics stripping, ZWNJ collapsing, and basic Turkish casing.

4. **`geo_scope/mavi/engine.py` (`MAVIEngine`)**:
   - Computes the Molavi AI Visibility Index (MAVI) across 5 layers:
     - L1: Technical Accessibility
     - L2: Semantic Extractability
     - L3: Entity Clarity
     - L4: Citation Readiness
     - L5: Observed AI Visibility
   - Currently aggregates active layers and computes a normalized 0–100 score even when L5 is partially or completely unmeasured.

5. **`geo_scope/engine/report_generator.py` & `export_manager.py`**:
   - Generates summary reports in Markdown, JSON, HTML, and CSV.

---

## 2. Location of Current Measurement Contract

Prior to this upgrade, GEO-Scope's measurement standards were defined in three separate locations:
- **`schemas/measurement-contract-v1.json`**: JSON Schema defining contract metadata, declarations, and prompt universe fields.
- **`docs/SCIENTIFIC_MEASUREMENT_GATE.md`**: Textual specification establishing the 7 gates of scientific integrity (Zero-Fallback, Engine Isolation, Stratified Intent, Exact Metric Definition, Provenance Preservation, Non-Claim of Determinism, Reproducibility).
- **`geo_scope/measurement/engine.py` (inline code)**: Hardcoded calculation logic for metrics, failure rates, and provider classes.

**Audit Finding:** The measurement contract lacked a unified, standalone, versioned specification document (`docs/MINIMUM_MEASUREMENT_CONTRACT.md`) and a formal **Metric Dictionary** (`docs/METRIC_DICTIONARY.md`) detailing strict mathematical formulas and explicit denominators.

---

## 3. Conflated and Ambiguous Metrics

The audit identified several areas where metrics were ambiguously defined or improperly combined:

1. **Citation Rate Denominator Ambiguity**:
   - *Current Implementation:* Computes citation rate by dividing answers with target domain citations by all valid returned responses (`target_citations / valid_runs`).
   - *Flaw:* If an engine or prompt did not trigger web search or retrieval (e.g. pure parametric memory generation), dividing citations by all responses artificially deflates the engine's citation behavior.
   - *Required Solution:* Formally decouple into:
     - **Citation Rate (All Answers)**: Target citations / All valid returned answers.
     - **Citation Rate (Retrieval-Evidence Answers)**: Target citations / Answers containing retrieval evidence (sources/URLs returned). Both must be reported side by side.

2. **Mention vs. Recommendation**:
   - *Current Implementation:* Observation parser detects recommendations via linguistic patterns, but downstream reporting occasionally presented "Visibility" as an amorphous blend of mentions and recommendations.
   - *Flaw:* A brand can be mentioned critically or incidentally without being recommended.
   - *Required Solution:* Strict isolation: `Mention Rate` and `Recommendation Rate` must never be conflated.

3. **Position Conflation**:
   - *Current Implementation:* Average rank/position is calculated across observations.
   - *Flaw:* In conventional search, Position 1 indicates the top organic result. In Generative AI answers, "Position" refers to the chronological order of mention within synthesized prose. Furthermore, Google Search Console (GSC) reports "AI Overview Position" as the pixel or block rank on the SERP, which users confuse with citation rank within the generative text.
   - *Required Solution:* 
     - Metric renamed to **AI Block Position** for GSC data, with prominent disclaimers that it does not represent citation rank.
     - For generative answers, report **Average First Mention Position** and **First Recommendation Position** strictly computed on the subset of answers where the entity was mentioned/recommended.

4. **Source Influence**:
   - *Current Implementation:* Unmeasured.
   - *Flaw:* Premature attempts to calculate "source influence" solely from URL presence without verifying text absorption.
   - *Required Solution:* Explicitly mark `source_influence = not_measured` until token-level citation absorption models are implemented.

---

## 4. Missing Data Treated as Zero

A primary scientific risk in visibility benchmarking is confusing *absence of measurement* with *measured zero visibility*:

1. **Zero vs. Unmeasured in Rollups**:
   - When an engine, prompt category, or entity had zero observations (e.g., provider timed out or entity was not queried in a specific locale), existing rollups reported `0.0%` visibility.
   - *Impact:* An entity that was never queried appeared to have "0% visibility" (failing performance), rather than `not_measured`.
2. **MAVI Composite Score Distortion**:
   - In `MAVIEngine`, if L5 (Empirical AI Visibility) was unmeasured or synthetic, the engine redistributed weights across L1–L4 to output a 100-point composite score.
   - *Impact:* Clients with strong on-site technical SEO (L1–L4) received high MAVI scores (e.g., 75/100) without ever demonstrating visibility in actual AI engines!
   - *Required Solution:*
     - Distinguish status states: `not_measured`, `insufficient_data`, `provider_error`, `not_verified`, `fixture_only`.
     - When L5 is unmeasured, `mavi_composite` must be strictly `null`, reporting only `readiness_score`.

---

## 5. Entity Matching & Normalization Analysis

In `geo_scope/entities/registry.py`:
- `normalize_text()` implements Unicode NFKC, Arabic/Persian letter unification (ي/ی, ك/ک), diacritic removal, and ZWNJ removal.
- **Audit Gaps**:
  1. **Match Tiers:** The parser used a single binary boolean match. There was no distinction between `exact`, `normalized_exact`, and `probable`.
  2. **Rule Tracing:** Matches did not record which specific normalization rules were triggered (e.g., `persian_yeh_normalized`, `zwnj_collapsed`).
  3. **Multilingual Specifics:**
     - Turkish & Azerbaijani Latin: Dotted/dotless `İ`/`ı` and `I`/`i` casing was only partially handled; Azerbaijani `Ə`/`ə` lacked explicit ligature mappings.
     - Apostrophes: Straight (`'`) vs curly (`’`, `‘`) apostrophes were not unified.
     - Numerals: Persian (`۰-۹`), Arabic-Indic (`٠-٩`), and Latin (`0-9`) digits were not systematically unified across entity aliases.
  4. **Brand Hierarchy:** No parent-brand vs product/subsidiary aggregation model existed.

---

## 6. Repetition Levels & Statistical Uncertainty

1. **Repetition Policy**:
   - Historical pilot runs frequently executed $k=1$ or $k=2$ repetitions due to API cost constraints.
   - Generative LLM responses are non-deterministic stochastic distributions. Stating a brand's "visibility rank" based on 1 or 2 runs represents severe pseudo-determinism.
   - *Required Policy:*
     - $< 5$ runs per prompt-engine-locale cell: Must be categorized and labeled as `directional` or `single_observation`.
     - $\ge 5$ runs: Classified as `measured`.
     - Unexecuted: `not_measured`.
2. **Lack of Confidence Intervals**:
   - Proportions were reported as single point estimates (e.g., `42.5%`).
   - *Required Solution:* Every binomial proportion must be accompanied by a **95% Wilson Score Interval** (`ci_lower`, `ci_upper`).
   - Continuous and comparative distributions must support **Bootstrap Resampling** confidence intervals.
   - When confidence intervals of two entities overlap, the UI and API must explicitly state: *"The observed difference is within the uncertainty range of this sample."*

---

## 7. Provenance Completeness & Fallback Transparency

1. **Model Provenance**:
   - Providers often have auto-routing or fallback logic (e.g., falling back from `gpt-4o` to `gpt-4o-mini`, or using ungrounded fallbacks).
   - Some adapters recorded `requested_model` and `actual_model` as the same string, obscuring silent server-side fallbacks.
2. **Cryptographic Integrity**:
   - While batch hash manifests existed, individual observation records did not uniformly include the SHA-256 hash of the exact raw text response.
   - *Required Policy:* Separate raw responses from scored metrics; record cryptographic hashes on every observation; flag unverified models as `actual_model = "not_verified"`.

---

## 8. Required Architectural Shifts for Minimum Measurement Contract v1.0

To achieve scientific validity, the following architectural upgrades are enacted:

| Component | Legacy State | Upgrade Target (Contract v1.0) |
|---|---|---|
| **Measurement Specification** | Dispersed in code & docs | Unified `docs/MINIMUM_MEASUREMENT_CONTRACT.md` & `docs/METRIC_DICTIONARY.md` |
| **Statistical Rigor** | Point estimates | 95% Wilson Score CIs for binomials, Bootstrap for continuous |
| **Denominators** | Ad-hoc divisions | Central `DenominatorRegistry` returning numerator, denominator, sample size, coverage |
| **Entity Normalization** | Single-tier regex string search | 3 Match Tiers (`exact`, `normalized_exact`, `probable`) with rule traces and 5-language support |
| **MAVI Architecture** | 5-layer normalized composite | Decoupled Readiness (L1–L4) vs Observed Visibility (L5); `mavi_composite = null` if L5 unmeasured |
| **GSC Metric Alignment** | "AI Position" (ambiguous) | Renamed to "AI Block Position" with strict directional & non-citation disclaimer |
| **Audit Extensions** | Monolithic SAGE | Standalone optional UGC Fresh Data Readiness audit module |
| **Missing Data** | `0.0%` default | Explicit `not_measured`, `insufficient_data`, `provider_error`, `fixture_only` |

---

## 9. Backward Compatibility Strategy

To ensure existing integrations, CLI scripts, and workflows remain functional:
1. **CLI Commands (`geo-scope measure`, `replay`, `demo`)**: Retain all existing parameter flags (`--prompts`, `--entities`, `--mode`, `--providers`, `--repeat`, `--out-dir`). New statistical and denominator outputs will augment the existing output dictionary without deleting legacy keys (`mention_rate`, `citation_rate`).
2. **Schema Evolution**: Maintain existing schema structures while adding nested `uncertainty`, `denominators`, and `breakdowns` objects.
3. **Data Accessors**: Properties on models (such as `mavi_score`) will remain accessible, returning the calculated readiness or composite score with deprecation/clarification metadata attached.

---

## 10. Migration Risks & Mitigations

1. **Risk:** Consumers expecting simple scalar percentages might break if encountering objects with confidence intervals.
   - *Mitigation:* Keep top-level numeric fields (e.g. `mention_rate: 0.314`) and nest statistical metadata under `mention_rate_stats: { ... }` or parallel structures.
2. **Risk:** Disallowing composite MAVI without L5 might surprise users who only ran technical audits.
   - *Mitigation:* Explicitly label the output `readiness_score: 72`, set `observed_visibility: { status: "not_measured" }`, and provide clear explanation in the report.
3. **Risk:** Performance overhead from Bootstrap resampling.
   - *Mitigation:* Use optimized vector/array resampling with fixed random seeds ($n=1,000$ iterations) and cached computations.

---

*End of Measurement Architecture Upgrade Audit.*
