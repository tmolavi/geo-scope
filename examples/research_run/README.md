# GEO-Scope Research Run Template

This directory provides the canonical template for configuring, executing, and publishing empirical AI visibility research runs with GEO-Scope.

---

## 🔬 Core Scientific Principles

1. **Observed vs. Hypothesis Prompts**:
   - `source_type: "observed"`: Real user searches mined from logs, analytics, or search queries. **Observed questions are the ONLY acceptable input for public market comparisons.**
   - `source_type: "hypothesis"`: Exploratory queries authored by researchers to probe edge cases or comparative rankings.

2. **Entity & Disambiguation Rules**:
   - Separate personal brand mentions (`people`) from company brand mentions (`names`).
   - Define `do_not_confuse` homonyms to prevent false-positive matches (e.g. "بازار مولوی", "نوین چرم").

3. **Provider Metric Partitioning**:
   - **AI Search Visibility**: Calculated only on search-grounded answer engines (`answer_engine`).
   - **LLM Brand Observation**: Calculated on direct text generation LLMs (`llm`).

---

## 🚀 Execution Instructions

### 1. Execute Live Measurement (Zero Fallback)

```bash
geo-scope measure \
  --entities examples/research_run/entities.json \
  --prompts examples/research_run/prompts.jsonl \
  --providers perplexity_sonar,gemini_grounding \
  --mode live \
  --out-dir output/research_run_2026_01
```

### 2. Verify Output Cryptographic Integrity

```bash
geo-scope benchmark verify --dataset output/research_run_2026_01
```

### 3. Reproduce Metrics Offline (Deterministic Replay)

```bash
geo-scope replay \
  --input output/research_run_2026_01 \
  --entities examples/research_run/entities.json \
  --out-dir output/research_run_2026_01_replayed
```
