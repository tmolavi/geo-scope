# Global AI Answers Benchmark 2026.2 Pilot Report

**Release Identifier**: `global-ai-answers-2026.2-pilot`  
**Execution Mode**: `live` (Executed via audited private Hamzad AI Gateway)  
**Research Status**: `peer_review_ready`  
**Publication Date**: September 2026  

> [!IMPORTANT]
> **Core Scientific Disclaimer**:  
> *This pilot validates methodology and pipeline behavior. It is not a global ranking or assertion of superiority.*

---

## 1. Executive Summary

The **Global AI Answers Benchmark 2026.2 Pilot** is a controlled, live empirical study validating the complete 7-stage measurement pipeline for observing generative AI answer patterns around human concerns across cultures and languages.

```
AnswerPath GEO (Discovery)
        ↓
Question Discovery (60% Observed User Questions + 40% Research Templates)
        ↓
GEO-Scope Measurement Engine (Core Framework)
        ↓
Hamzad AI Gateway (Isolated Live Execution Layer)
        ↓
Deterministic Multi-Type Entity Extraction (Aliases & Negative Constraints)
        ↓
Descriptive Metrics & Provider Breakdown (Answer Engine vs. LLM)
        ↓
Cryptographic Release Bundle (`benchmark/releases/global-ai-answers-2026.2-pilot/`)
```

---

## 2. Dataset & Scope Metrics

| Dimension | Pilot Value | Description |
| :--- | :--- | :--- |
| **Total Prompts** | **100** | 55 Observed User Questions (`observed_user_questions`), 45 Research Questions (`research_questions`) |
| **Question Source** | AnswerPath GEO | Verified provenance with `source_reference: "answerpath"` |
| **Countries Covered** | **10** | Iran (`IRN`), Turkey (`TUR`), Germany (`DEU`), United Kingdom (`GBR`), United States (`USA`), India (`IND`), Japan (`JPN`), Saudi Arabia (`SAU`), Brazil (`BRA`), Nigeria (`NGA`) |
| **Languages** | **8** | Persian (`fa`), Turkish (`tr`), German (`de`), English (`en`), Hindi (`hi`), Japanese (`ja`), Arabic (`ar`), Portuguese (`pt`) |
| **Categories** | **5** | `future_skills_learning`, `career_migration`, `entrepreneurship_business`, `ai_adoption`, `education_choices` |
| **Tracked Entities** | **30** | Multi-type registry: People, Companies, Countries, Universities, Technologies, Communities |
| **Active Models** | **4** | `gemini-2.5-flash` (`answer_engine`), `sonar-pro` (`answer_engine`), `gpt-4o-mini` (`llm`), `claude-3.5-sonnet` (`llm`) |
| **Completions** | **202** | Live execution records stored without synthetic fallback |
| **Observations** | **6,262** | Deterministically evaluated observation tuples |

---

## 3. Epistemic Guardrails & Metric Principles

1. **Descriptive, Not Normative**: GEO-Scope strictly reports observed rates (`mention_rate`, `recommendation_rate`, `top1_rate`, `citation_rate`). No scores, subjective leaderboards, or "best person/country" rankings are calculated.
2. **Strict Provider Class Separation**: Search-grounded answer engines (`answer_engine`) are evaluated independently from parametric language models (`llm`).
3. **Question Type Isolation**: Real user inquiries from AnswerPath GEO are analyzed separately from synthetic research probes to prevent conflating organic visibility with edge-case tests.
4. **Homonym Gating**: Entities with overlapping meanings use negative constraint filters to eliminate false positives.

---

## 4. Release Package Artifacts

The immutable release package resides at `benchmark/releases/global-ai-answers-2026.2-pilot/`:

- `manifest.json`: Machine-readable metadata, provider mappings, schema declarations, and lineage.
- `prompts.jsonl`: Full 100-prompt catalog with cultural context annotations.
- `prompts/observed.jsonl`: Filtered 55 observed user questions.
- `prompts/research.jsonl`: Filtered 45 research templates.
- `entities.json`: 30 multi-type entity definitions with aliases, domains, and `do_not_confuse` rules.
- `raw_responses.jsonl`: 202 unredacted (secret-free) model completion records.
- `observations.jsonl`: 6,262 parsed entity observation records.
- `citations.jsonl`: Observed URL citations with domain attribution.
- `metrics.json`: Aggregated mention rates by entity, country, category, and provider class.
- `errors.jsonl`: Honest recording of network/gateway timeout events.
- `limitations.md`: Complete statement of research boundaries and non-goals.
- `methodology.md`: Full architectural specification of the measurement pipeline.
- `checksums.sha256`: SHA-256 hashes of all 13 package files.

---

## 5. Verification & Deterministic Reproduction

The benchmark release can be verified by any third party using the GEO-Scope CLI:

```bash
# 1. Cryptographic Checksum Verification
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# 2. Quality & Security Schema Validation
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# 3. Deterministic Metric Replay & Mathematical Verification
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```
