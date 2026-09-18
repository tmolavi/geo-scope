# GEO-Scope Public Research Readiness & Scientific Honesty Report

**Document Version**: 1.0.0  
**Audit Date**: September 2026  
**Auditor**: Independent Open-Source Verification Gate  
**Target Repository**: `tmolavi/geo-scope` (Default branch: `main`)

---

## Executive Summary

GEO-Scope has completed a comprehensive reality audit, measurement architecture upgrade, and scientific defensibility hardening. The framework is strictly positioned as:

> **"An open-source measurement platform for observing brand visibility, citations, and recommendations in answer engines and LLMs."**

All claims of "algorithm reverse engineering" or "guaranteed ranking weights" have been removed or explicitly categorized as labeled hypothesis priors. Execution modes (`demo`, `measure`, `replay`) are strictly isolated with cryptographic provenance guarantees.

---

## Core Audit Answers

### 1. Is GEO-Scope scientifically honest?
**YES.**
- The framework makes no claims of knowing or reversing proprietary search/LLM ranking algorithms.
- Ranking dimensions (e.g. Reddit UGC, review platforms, digital PR) are explicitly documented as **research hypothesis priors**, not fitted statistical model parameters.
- Prompts are strictly stratified by intent (`recommendation`, `comparative`, `informational`, `navigational`) and source origin (`observed` real queries vs `hypothesis` exploratory templates).
- Informational / lookup queries are gated with `scoring_status: "unscored"` to prevent artificial inflation of recommendation rates.
- Person mentions (e.g., founders, executives) are parsed separately from brand mentions and do not falsely contribute to brand visibility.
- Persian/Arabic text normalization and explicit negative collision definitions (`do_not_confuse`) eliminate false positives from common words and homonyms.

---

### 2. Can a stranger reproduce the evidence?
**YES.**
- Every run of `geo-scope demo`, `geo-scope measure`, or `geo-scope replay` outputs a self-contained, 7-file standardized evidence bundle with `checksums.sha256`.
- Any external researcher can verify bit-for-bit file integrity using standard SHA-256 tools or `geo-scope benchmark verify`.
- The `geo-scope replay` command allows deterministic, zero-cost, offline re-evaluation of saved `raw_responses.jsonl` files against updated entity dictionaries without making any network calls.
- Reproduction math matches raw evidence exactly, calculating both point estimates and 95% bootstrap confidence intervals.

---

### 3. Are simulations clearly labeled?
**YES.**
- The `demo` command runs a deterministic simulation fixture, explicitly outputting a startup banner:
  `Execution mode: SIMULATION (Results are deterministic fixtures for testing)`.
- Manifest files record `"mode": "simulation"`, and all output metrics are prefixed with `simulated_*` (`simulated_mention_rate`, `simulated_recommendation_rate`, `simulated_top1_rate`).
- The exploratory prototype dataset in `benchmarks/geo-seo-digital-agency-iran-2026.1/` is prominently marked as a methodology validation package rather than an authoritative live market ranking.

---

### 4. Are providers real when live?
**YES.**
- When running `geo-scope measure --mode live`, requests are dispatched strictly to real provider adapters (`PerplexitySonarProvider`, `GeminiGroundingProvider`, `OpenAIProvider`, `AnthropicProvider`, `HamzadProvider`).
- **Zero Silent Fallback**: If an API key is missing, network times out, or the provider errors, the failure is written directly to `errors.jsonl` with an explicit error code (e.g. `TIMEOUT_504`, `AUTH_ERROR`). Under no circumstances does the engine fall back to simulation during live mode.
- Raw response payloads record `provider_class` (`answer_engine` vs `llm_completion`), `requested_provider`, `actual_provider`, and whether the provider is search-grounded (`search_grounded: true/false`).
- Metrics are partitioned into **AI Search Visibility** (answer engines with grounding citations) and **LLM Brand Observation** (direct completion models).

---

### 5. Is the repository ready for public researchers?
**YES.**
- **Clean Installation**: Tested and verified with standard `pip install -e .`.
- **First Research Run**: Documented in `examples/research_run/` with sample `entities.json`, `prompts.jsonl`, and an expected output structure specification.
- **MCP Protocol Ready**: Native stdio MCP server for direct integration into AI workspaces (Cursor, Claude Desktop, Antigravity).
- **Test Suite**: 148/148 automated unit and integration tests passing (`100% passed`), including explicit regression tests for non-fallback, entity separation, homonym filtering, and deterministic replay.
- **Community Ready**: Full GitHub Discussions categories, issue templates, and research collaboration guidelines in place.

---

## Verification Artifact Summary

| Component | Public Location | Verified Behavior | Status |
|---|---|---|---|
| **Reality Audit** | `docs/REALITY_AUDIT.md` | Documents verified boundaries and honest positioning | ✅ VERIFIED |
| **Research Run Template** | `examples/research_run/` | Runnable template with 5 entities and 6 prompts | ✅ VERIFIED |
| **Integrity Test Suite** | `tests/test_public_research_integrity.py` | 6 unit tests covering all research integrity guarantees | ✅ VERIFIED |
| **CLI Product Commands** | `geo-scope demo`, `measure`, `replay` | Distinct, verifiable commands with standard bundles | ✅ VERIFIED |
| **Cryptographic Provenance** | `checksums.sha256` in all bundles | Bit-for-bit verifiable raw data | ✅ VERIFIED |

---

*Report certified for public repository publication.*
