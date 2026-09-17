# GEO-Scope Benchmark Release Checklist

Use this checklist before publishing or updating any public GEO-Scope benchmark dataset.

---

## 1. Experiment Execution & Provenance
- [ ] **Execution Mode Tagging**: Verify `execution_mode` is accurately set (`live` for real API calls, `synthetic` for simulation runs).
- [ ] **Research Status Assignment**: Set `research_status: "demo_only"` for synthetic/demo data; `research_status: "peer_review_ready"` for auditable live experiments.
- [ ] **Provider Integrity**: Confirm no silent simulation fallbacks occurred during live execution.
- [ ] **Raw Evidence Persistence**: Ensure `observations.jsonl` contains raw provider responses, latency numbers, and token usage where available.
- [ ] **No Secret Exposure**: Verify all API keys, bearer tokens, and private identifiers have been sanitized from `observations.jsonl` and `citations.jsonl`.

---

## 2. Dataset Structure & Schema
- [ ] All 10 required dataset files are present in `benchmark/<dataset_id>/`:
  - `manifest.json`
  - `prompts.jsonl`
  - `brands.json`
  - `providers.json`
  - `observations.jsonl`
  - `citations.jsonl`
  - `metrics.json`
  - `methodology.md`
  - `README.md`
  - `checksums.sha256`
- [ ] `manifest.json` includes valid git commit hash, parser version, sample counts, and dataset description.

---

## 3. Cryptographic Verification & Tamper Detection
- [ ] Run `geo-scope benchmark verify --dataset benchmark/<dataset_id>` to confirm `checksums.sha256` passes.
- [ ] Run `geo-scope benchmark reproduce --dataset benchmark/<dataset_id>` to confirm all metrics recompute bit-for-bit with 0 differences.

---

## 4. Statistical Rigor & Epistemic Guardrails
- [ ] All percentage rates are accompanied by 95% bootstrap confidence intervals.
- [ ] If zero successful observations occurred for any metric, confirm it reports `null` / `insufficient_data` instead of `0.0%`.
- [ ] Factor analyses strictly use "Observed association" and include sample sizes ($N$), confidence intervals, and effect sizes.
- [ ] No sensationalized claims claiming to have "reverse-engineered AI algorithms."

---

## 5. Documentation & Metadata
- [ ] `CITATION.cff` is updated with current benchmark version and dataset DOI / URL.
- [ ] `README.md` references the latest benchmark dataset and reproduction commands.
- [ ] `notebooks/benchmark_analysis.py` runs cleanly against the dataset package.
