# GEO-Scope Releases & Scientific Milestones

This document records the official release timeline, methodology standards, golden sets, and published benchmark datasets for **GEO-Scope**.

**Scientific Foundation**: [docs/SCIENTIFIC_FOUNDATION_V1.md](SCIENTIFIC_FOUNDATION_V1.md)  
**Measurement Contract**: [docs/measurement-contract-v1.md](measurement-contract-v1.md)  
**Research Methods**: [docs/RESEARCH_METHODS.md](RESEARCH_METHODS.md)  

---

## 1. Release Timeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GEO-SCOPE SCIENTIFIC MILESTONES                       │
├────────────┬─────────────────────────────┬──────────────────────────────────┤
│ Date       │ Milestone / Release         │ Focus & Key Deliverable          │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-25 │ Scientific Foundation v1.0  │ Public scientific milestone &    │
│            │                             │ methodological formalization     │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-25 │ Measurement Contract v1.0   │ Formal JSON schema, axioms, and  │
│            │                             │ machine-readable comparability   │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-23 │ Golden Parser Dataset v1    │ N=220 human-annotated benchmark  │
│            │                             │ across 5 languages (F1 >= 99.7%) │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-19 │ global-ai-answers-2026.2    │ 500 prompts, 50 countries,       │
│            │                             │ 45,698 observations, 4 models    │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-19 │ global-ai-answers-2026.2-   │ 100 prompts, 10 countries,       │
│            │ pilot                       │ 8,940 observations, 4 models     │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-19 │ geo-seo-digital-agency-     │ 30 prompts, 5 intent strata,     │
│            │ iran-2026.1                 │ 120 completions, 4 models        │
├────────────┼─────────────────────────────┼──────────────────────────────────┤
│ 2026-09-18 │ global-ai-answers-2026.1    │ 34 prompts, 7 regions,           │
│            │                             │ Baseline empirical run           │
└────────────┴─────────────────────────────┴──────────────────────────────────┘
```

---

## 2. Standards & Methodology Releases

### Measurement Contract v1.0 (2026-09-25)
- **Specification**: [`docs/measurement-contract-v1.md`](measurement-contract-v1.md)
- **JSON Schema**: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)
- **Rationale**: [`docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md`](WHY_MEASUREMENT_CONTRACT_EXISTS.md)
- **Key Features**:
  - Response-level binary mentions ($\mathbf{y} \in \{0, 1\}$).
  - 4-way citation attribution (`entity_mentioned`, `target_domain_cited`, `target_url_cited`, `third_party_source_cited`).
  - Semantic recommendation gating (`mentioned != recommended`).
  - Strict numbered list rank extraction ($r \in \mathbb{N} \cup \{\text{null}\}$).
  - Explicit denominator and failure accounting ($N_{\text{attempted}}$, $N_{\text{successful}}$, $N_{\text{failed}}$).
  - Automated five-dimension comparability check.

### Golden Parser Dataset v1 (2026-09-23)
- **Directory**: [`benchmark/golden_sets/v1/`](../benchmark/golden_sets/v1/)
- **Methodology**: [`docs/GOLDEN_SET_METHODOLOGY.md`](GOLDEN_SET_METHODOLOGY.md)
- **Dataset Composition**: 220 human-labeled completions across 5 languages:
  - English (`en`): 60 examples
  - Persian (`fa`): 60 examples
  - Turkish (`tr`): 40 examples
  - Azerbaijani (`az`): 30 examples
  - Arabic (`ar`): 30 examples
- **Parser Verification Performance**:
  - Mention F1: `99.75%` (Precision: 99.51%, Recall: 100.00%)
  - Recommendation F1: `100.00%` (Precision: 100.00%, Recall: 100.00%)
  - Citation F1: `100.00%` (Precision: 100.00%, Recall: 100.00%)
  - Attribution F1: `91.56%` (Precision: 100.00%, Recall: 84.44%)
  - Homonym Disambiguation F1: `96.97%`
  - Rank Accuracy: `100.00%`

---

## 3. Published Empirical Benchmark Releases

All empirical benchmark datasets are immutable, cryptographically sealed, and available in `benchmark/releases/`.

### 3.1 `global-ai-answers-2026.2` (Major Benchmark Release)
- **Path**: [`benchmark/releases/global-ai-answers-2026.2/`](../benchmark/releases/global-ai-answers-2026.2/)
- **Documentation**: [Research Paper Draft](research/global-ai-answers-2026.2/global-ai-answers-paper.md) • [Roadmap](ROADMAP_GLOBAL_AI_ANSWERS_2026_2.md)
- **Prompts**: 500 prompts across 50 countries and 5 languages
- **Observations**: 45,698 discrete model observation records
- **Evaluated Providers**: OpenAI (`gpt-4o`), Perplexity (`sonar-pro`), Google (`gemini-1.5-pro`), Anthropic (`claude-3-5-sonnet`)
- **Measurement Contract Version**: `1.0`
- **Integrity**: SHA-256 verified (`checksums.sha256`)
- **Verification Command**:
  ```bash
  geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
  ```

### 3.2 `global-ai-answers-2026.2-pilot` (Pilot Validation Run)
- **Path**: [`benchmark/releases/global-ai-answers-2026.2-pilot/`](../benchmark/releases/global-ai-answers-2026.2-pilot/)
- **Documentation**: [Pilot Report](GLOBAL_AI_ANSWERS_2026_2_PILOT_REPORT.md)
- **Prompts**: 100 prompts across 10 countries
- **Observations**: 8,940 discrete observations
- **Measurement Contract Version**: `1.0`
- **Integrity**: SHA-256 verified (`checksums.sha256`)

### 3.3 `geo-seo-digital-agency-iran-2026.1` (Market-Specific Vertical Study)
- **Path**: [`benchmark/releases/geo-seo-digital-agency-iran-2026.1/`](../benchmark/releases/geo-seo-digital-agency-iran-2026.1/)
- **Documentation**: [Release Notes](releases/release-2026.1-geo-seo-digital-agency-iran.md)
- **Prompts**: 30 prompts stratified across 5 search intents
- **Completions**: 120 responses across 4 leading models
- **Focus**: Multilingual Iranian digital agency visibility, Persian entity resolution, and Perso-Arabic ZWNJ normalization
- **Measurement Contract Version**: `1.0`
- **Integrity**: SHA-256 verified (`checksums.sha256`)

### 3.4 `global-ai-answers-2026.1` (Baseline Multi-Region Run)
- **Path**: [`benchmark/releases/global-ai-answers-2026.1/`](../benchmark/releases/global-ai-answers-2026.1/)
- **Documentation**: [Methodology](global-ai-answers-methodology.md)
- **Prompts**: 34 prompts across 7 global regions
- **Focus**: Initial multi-region baseline feasibility study
- **Measurement Contract Version**: `1.0`
- **Integrity**: SHA-256 verified (`checksums.sha256`)

### 3.5 `geo-scope-ai-visibility-2026.1-synthetic` (Simulation Fixture)
- **Path**: [`benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic/`](../benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic/)
- **Type**: Mock / Simulation Dataset
- **Purpose**: Fast offline testing, CI integration, and demo exploration.
- **Guarantee**: Quarantined with `simulated_*` prefix and excluded from all empirical benchmark reports.

---

## 4. Verification & Reproduction Instructions

To independently verify any release:

```bash
# 1. Verify cryptographic checksums of a release bundle
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# 2. Perform zero-network offline replay and metrics recalculation
geo-scope replay \
  --bundle benchmark/releases/global-ai-answers-2026.2 \
  --out-dir output/audit_replay

# 3. Evaluate the parser against the human golden set
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

For full reproducibility guidelines, see [docs/SCIENTIFIC_FOUNDATION_V1.md](SCIENTIFIC_FOUNDATION_V1.md) and [docs/REPRODUCE_BENCHMARK.md](REPRODUCE_BENCHMARK.md).
