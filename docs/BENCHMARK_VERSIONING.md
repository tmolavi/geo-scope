# GEO-Scope Benchmark Versioning Standard

This document establishes the semantic versioning and change management standard for GEO-Scope empirical benchmark releases.

---

## 1. Release Version Format

Benchmark datasets follow the version naming schema:

$$\mathbf{global\text{-}ai\text{-}answers\text{-}YYYY.N}$$

- **`YYYY`**: The calendar year of data collection.
- **`N`**: The sequential release number within that calendar year.

### Examples:
- `global-ai-answers-2026.1`: First 2026 release (34 prompts, 4 models, 7 categories, 9 languages).
- `global-ai-answers-2026.2`: Expanded 2026 release (500+ prompts, expanded provider matrix).

---

## 2. Change Classification & Bump Criteria

| Change Type | Impact | Versioning Action |
| :--- | :--- | :--- |
| **Prompt Matrix Expansion** | Adding new queries, categories, or localized language sets | Increment minor release number ($N+1$) |
| **Provider Matrix Update** | Adding new model checkpoints or answer engines | Increment minor release number ($N+1$) |
| **Entity Catalog Changes** | Adding new tracked entities or updating alias registries | Increment minor release number ($N+1$) |
| **Metric Formulation Update** | Modifying calculation formulas or confidence intervals | Increment major version ($YYYY+1$) or create dedicated revision document |
| **Parser Improvements** | Bug fixes to Unicode token matching or `do_not_confuse` rules | Increment patch/minor revision with full changelog |

---

## 3. Immutability & SHA-256 Lock

Once a benchmark dataset package is tagged and published under `benchmark/releases/<dataset-id>/`:
1. The raw files (`prompts.jsonl`, `raw_responses.jsonl`, `observations.jsonl`, `metrics.json`) become strictly **immutable**.
2. Any modification invalidates the `checksums.sha256` manifest.
3. Fixes or expansions require creating a new version directory (e.g. `global-ai-answers-2026.2`).

---

## 4. Release Bundle Standard Contents
Every release directory must contain:
1. `manifest.json`: Full release metadata, lineage, and provider classification.
2. `prompts.jsonl` & `prompts/`: Standardized prompt records.
3. `entities.json`: Tracked entity dictionary with aliases and disambiguation tokens.
4. `raw_responses.jsonl`: Raw unparsed model response logs.
5. `observations.jsonl`: Deterministic entity observation records.
6. `citations.jsonl`: Grounded source citations.
7. `metrics.json`: Empirical aggregated metrics.
8. `errors.jsonl`: Transparent failure log.
9. `checksums.sha256`: Cryptographic verification hashes.
10. `limitations.md`: Scope and methodology limitations.
11. `methodology.md` & `README.md`: Research documentation.
