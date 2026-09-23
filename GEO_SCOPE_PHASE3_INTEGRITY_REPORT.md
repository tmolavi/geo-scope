# GEO-Scope Phase 3 — Benchmark Integrity, Provider Governance & Release Gate Report

**Date**: 2026-09-23  
**Repository**: `tmolavi/geo-scope`  
**Phase**: Phase 3 (Benchmark Integrity, Provider Governance & Release Gate)  
**Status**: COMPLETE  

---

## 1. Implemented Capabilities

### A. Provider Identity Integrity Gate
* Every live observation and raw response records:
  ```json
  {
    "requested_provider": "...",
    "requested_model": "...",
    "actual_provider": "...",
    "actual_model": "...",
    "provider_class": "answer_engine | llm | recorded",
    "search_grounded": true | false,
    "fallback_used": false
  }
  ```
* In empirical benchmark runs, if `requested_provider != actual_provider`, `requested_model != actual_model`, or `fallback_used == true`, the record is marked `status = "fallback_or_mismatch"` and is excluded from official benchmark metrics.

### B. Benchmark Release Quality Gate (`geo_scope/release_gate.py`)
* Implemented `evaluate_release_gate(dataset_dir, output_report=...)` and CLI command `geo-scope benchmark release-gate --dataset <path>`.
* Enforces 7 strict quality checks:
  1. Evidence Artifacts Completeness (`manifest.json`, `prompts.jsonl`, `raw_responses.jsonl`, `observations.jsonl`, `metrics.json`, `errors.jsonl`, `checksums.sha256`, `methodology.md`, `limitations.md`, `entities.json`)
  2. Manifest Metadata Conformance (`schema_version`, `benchmark_version`, `execution_mode`, `provider_matrix`, `prompt_policy`, `repeat_count`, `comparison_batch_id`)
  3. Cryptographic Checksum Verification (SHA-256 verification of all files)
  4. Simulation & Synthetic Contamination Gate (zero simulation records, zero fixture domains)
  5. Provider Identity & Fallback Integrity (requested == actual, fallback_used == false)
  6. Repeat Protocol Enforcement ($k \ge 5$ for empirical releases)
  7. Failure Denominator & Visibility Accounting (separating provider errors from negative entity visibility)

### C. Citation vs Attribution Verification
* Strictly separates `cited` (domain/URL grounding presence in citations or body) from `attributed` (explicit sourcing grammar in prose across English, Persian, Arabic, Turkish, and Chinese).
* Comprehensive regression tests added.

### D. Golden Set Integrity Audit & Methodology (`docs/GOLDEN_SET_METHODOLOGY.md`)
* Detailed documentation of ground-truth annotation rules, multi-lingual normalization handling, homonym collision filtering, and epistemic boundaries.

### E. Enhanced Parser Evaluation Reporting (`geo_scope/parser/evaluator.py`)
* Output includes `dataset_size`, `languages`, `entities`, `fields_evaluated`, `precision`, `recall`, `f1`, `confidence_notes`, `limitations`, and prominent warning: *"Evaluation results depend on the composition of the golden dataset."*

### F. Versioned Schemas (`schemas/v0.3/`)
* Created formal JSON Schemas conforming to Draft 2020-12:
  - `schemas/v0.3/manifest.schema.json`
  - `schemas/v0.3/prompt.schema.json`
  - `schemas/v0.3/response.schema.json`
  - `schemas/v0.3/observation.schema.json`
  - `schemas/v0.3/metrics.schema.json`

### G. Reproducibility Environment & Checklist
* Created `docs/REPRODUCE_ENVIRONMENT.md` with Python runtime, dependency lockfile (`requirements.lock`), environment variables, runtime, and cost ranges.
* Updated `docs/EXTERNAL_REVIEW_CHECKLIST.md` addressing all 6 independent auditor questions.
* Added 6-layer Benchmark Trust Model to `README.md`.

---

## 2. Test Suite & Validation Results

* **Pytest Suite**: **162 passed, 8 skipped** (0 failures).
* **Golden Parser Evaluation (v1)**:
  - Total Evaluated Records: 220
  - `mentioned`: 99.75% F1
  - `recommended`: 100.00% F1
  - `cited`: 100.00% F1
  - `attributed`: 91.56% F1
  - `wrong_entity`: 96.97% F1
  - `Rank Accuracy`: 100.00% (77/77 exact matches)

---

## 3. Remaining Limitations

1. **Golden Set Scope**: v1 contains 220 curated records covering 5 languages and 18 entities. Additional long-tail domains and languages will be added in future versions.
2. **Intent Classification**: Uses multi-lingual regex pattern heuristics; fine-grained open-ended intents require continuous corpus monitoring.
3. **External API Volatility**: Live API results depend on external model provider stability and temperature settings, necessitating repeated trials ($k \ge 5$).

---

## 4. Release Status & Metadata

* **Schema Version**: `v0.3` (`schemas/v0.3/`)
* **CI Status**: Updated `.github/workflows/ci.yml` with test suite and golden evaluator checks.
* **Commit**: `feat(release): add benchmark integrity gates and provider governance`
* **Target Branch**: `main`
