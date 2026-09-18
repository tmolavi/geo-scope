# GEO-Scope Repository Reality Audit & Scientific Limitations

**Audit Date**: September 18, 2026  
**Auditor**: GEO-Scope Research & Integrity Team  
**Scope**: Whole Repository (`geo-scope`) Codebase, CLI, Datasets, Documentation, and Benchmarks  
**Status**: ACTIVE REALITY BASELINE

---

## 1. Executive Summary & Purpose

The purpose of this Reality Audit is to systematically document the exact technical capabilities, empirical boundaries, and known limitations of the GEO-Scope framework. 

GEO-Scope is defined and positioned as:
> **"An open measurement framework for observing brand visibility in answer engines and language model responses through reproducible experiments and verifiable evidence."**

GEO-Scope is **NOT**:
- A reverse-engineering tool that "cracks" proprietary search/AI algorithms.
- A tool that guarantees ranking factors or commercial SEO outcomes.
- A commercial market leaderboard based on simulated responses.

---

## 2. Capabilities Matrix (Claimed vs Verified vs Simulation-Only)

| Feature / Capability | Implementation State | Verification Status | Mode Boundary |
|---|---|---|---|
| **Multi-lingual Entity Registry** | Implemented (`geo_scope/entities/`) | **Verified**: Normalized Persian/Arabic text, alias matching, person vs brand separation | Shared |
| **Observation Parser** | Implemented (`geo_scope/parser/`) | **Verified**: Regex & token matching, negative homonym masking, intent gating | Shared |
| **5-Minute Terminal Demo** | Implemented (`geo_scope demo`) | **Verified Simulation**: Deterministic mock generation with `simulated_*` metrics | Simulation Only |
| **Live Measurement Execution** | Implemented (`geo_scope measure`) | **Verified Live**: Multi-provider async execution, zero silent fallback, writes `errors.jsonl` | Live Only |
| **Deterministic Offline Replay** | Implemented (`geo_scope replay`) | **Verified Replay**: Re-evaluates recorded `raw_responses.jsonl` with 0 network calls | Offline Replay |
| **Provider Classification** | Implemented (`geo_scope/providers/`) | **Verified**: Strictly separates `answer_engine` (search-grounded) from `llm` (direct text) | Live & Replay |
| **Standard Output Bundle** | Implemented (`geo_scope/measurement/`) | **Verified**: Writes 7 bundle files + SHA-256 `checksums.sha256` | Shared |
| **MAVI Layered Evaluation (L1–L5)** | Implemented (`geo_scope/mavi/`) | **Verified**: L1-L4 technical/semantic audit (via SAGE), L5 empirical observation | Shared |
| **Automated Search Ranking Factor Fit** | Legacy Heuristic Formula | **Research Prior Only**: Fixed weights ($w_1=0.32, w_2=0.24$, etc.) are conceptual hypotheses, not statistically fitted regression parameters | Conceptual / Educational |

---

## 3. Detailed Audit of Modes & Integrity Boundaries

### A. Demo Mode (`geo-scope demo`)
- **Actual Capability**: Runs 5 sample queries against 4 simulated model endpoints using an internal deterministic mock RAG generator.
- **Evidence Level**: Synthetic test fixture.
- **Strict Constraint**: Must never report `Share of Model`, `Market Ranking`, or `AI Search Visibility`. Must only output `simulated_mention_rate`, `simulated_recommendation_rate`, and `simulated_top1_rate` accompanied by an explicit simulation disclaimer.

### B. Live Measurement Mode (`geo-scope measure`)
- **Actual Capability**: Sends real prompts to live configured endpoints (Hamzad AI Gateway, Perplexity API, Google Gemini, OpenAI, Claude).
- **Integrity Rule**: **Zero Silent Fallback**. If a provider fails, times out, or returns an error, the raw record records `status: "failed"` and the error details are recorded in `errors.jsonl`. It is never replaced with simulated or fallback data.
- **Metric Partitioning**: 
  - `ai_search_visibility` is **ONLY** computed on providers classified as `answer_engine` (search grounding enabled).
  - `llm_brand_observation` is computed on direct completion `llm` providers.

### C. Replay Mode (`geo-scope replay`)
- **Actual Capability**: Reads `raw_responses.jsonl` from any previous execution and recomputes all entity matches, observation states, and metrics.
- **Integrity Rule**: **Zero Network Access**. Fully reproducible bit-for-bit with cryptographic verification.

---

## 4. Audit of Existing Datasets & Benchmark Releases

### Audit of `benchmark/releases/geo-seo-digital-agency-iran-2026.1`
- **Audit Findings**:
  1. `observed_prompts: 0`, `generated_prompts: 30` (all 30 queries were researcher-generated hypothesis templates, not observed user searches).
  2. `native_count: 0`, `fallback_count: 51`, `failed_count: 69` (Claude and Perplexity endpoints encountered gateway fallbacks to Groq Qwen; 69 calls failed).
  3. `citations: 0` (no live search citations captured).
- **Reality Determination**: This release is an **exploratory prototype / validation dataset**, NOT a live production market ranking of Iranian SEO agencies.
- **Required Action**: Clearly demarcate as a prototype validation dataset in documentation and release notes.

---

## 5. Summary of Recommended Language & Wording Changes

| Old Wording / Claim | Issue | Replacement Honest Terminology |
|---|---|---|
| *"Reverse engineering AI ranking algorithms"* | Overclaims access to proprietary internal weights of Google/OpenAI/Perplexity | *"Empirical observation of brand presence in AI-generated answers"* |
| *"AI Visibility Score formula ($V_{GEO}$)"* | Implies verified universal algorithm | *"Hypothetical Composite Weighting Prior"* |
| *"Market Ranking of SEO Agencies"* | Overclaims external authority from small/exploratory samples | *"Sample Entity Observation Distribution across Tested Prompts"* |
| *"1,000-query benchmark"* in mock demo | Conflates demo with large-scale live empirical runs | *"10-prompt deterministic simulation fixture"* |

---

## 6. Verification Checklist for Published Research

Before any dataset is cited as public empirical evidence:
- [x] Input prompts must distinguish `observed` user queries from `hypothesis` exploratory templates.
- [x] Provider metadata must state `requested_provider`, `actual_provider`, `model`, `provider_class`, and `search_grounded`.
- [x] Raw responses must be preserved unedited in `raw_responses.jsonl`.
- [x] Output bundle must include `checksums.sha256` matching all files.
- [x] Metric calculations must be reproducible offline via `geo-scope replay`.
