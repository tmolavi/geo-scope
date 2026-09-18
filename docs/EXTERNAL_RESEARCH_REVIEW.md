# External Research Reviewer Checklist & Verification Guide

This checklist is designed for independent peer reviewers, researchers, and engineers auditing the **GEO-Scope** repository and the **Global AI Answers Benchmark 2026** (`global-ai-answers-2026.1`).

---

## Evaluation Checklist

Please verify each item using the provided terminal commands and file paths:

### 1. Distinguish Simulation Fixture from Live Measurement
- [ ] **Verification**: Run `geo-scope demo` and inspect stdout.
- [ ] **Expectation**: Output clearly displays `SIMULATION FIXTURE — NO LIVE MODEL WAS QUERIED`, and all metrics use the `simulated_*` prefix. Live measurement (`geo-scope measure`) never silently falls back to simulation on provider error.
- [ ] **Reference**: [test_public_research_integrity.py](tests/test_public_research_integrity.py)

### 2. Reproduce Deterministic Replay Results
- [ ] **Verification**: Run `geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.1`
- [ ] **Expectation**: All metrics and bootstrap confidence intervals match `metrics.json` bit-for-bit from recorded raw records with zero network calls.
- [ ] **Reference**: [docs/REPRODUCE_GLOBAL_AI_ANSWERS.md](docs/REPRODUCE_GLOBAL_AI_ANSWERS.md)

### 3. Inspect Raw Observations & Payloads
- [ ] **Verification**: Inspect `benchmark/releases/global-ai-answers-2026.1/raw_responses.jsonl` and `observations.jsonl`.
- [ ] **Expectation**: Complete unedited model completions, latency timings, and deterministic entity token spans are stored transparently.
- [ ] **Reference**: [benchmark/releases/global-ai-answers-2026.1/](benchmark/releases/global-ai-answers-2026.1/)

### 4. Verify Cryptographic SHA-256 Checksums
- [ ] **Verification**: Run `geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1`
- [ ] **Expectation**: All 13 release files match their SHA-256 hashes in `checksums.sha256`.
- [ ] **Reference**: [geo_scope/benchmark/hasher.py](geo_scope/benchmark/hasher.py)

### 5. Validate Scope & Research Limitations
- [ ] **Verification**: Read [docs/global-ai-answers-limitations.md](docs/global-ai-answers-limitations.md).
- [ ] **Expectation**: Clear demarcation that the benchmark measures observed model output distributions, not human merit, ranking of humanity, or reverse-engineered black-box algorithms.
- [ ] **Reference**: [limitations.md](benchmark/releases/global-ai-answers-2026.1/limitations.md)

### 6. Run Complete Test Suite
- [ ] **Verification**: Run `pytest -v`
- [ ] **Expectation**: 150+ tests pass with zero failures.
- [ ] **Reference**: [tests/](tests/)

---

## Summary Statement
GEO-Scope adheres to empirical measurement standards:
> *"Demo outputs are simulation fixtures. Benchmark results come from recorded measurement runs."*
