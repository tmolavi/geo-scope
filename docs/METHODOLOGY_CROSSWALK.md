# AI Visibility Measurement Methodology Crosswalk

This document provides a factual, evidence-led crosswalk comparing the measurement architecture of **GEO-Scope** with publicly documented industry practices in AI search and answer visibility measurement.

---

## Why this document exists

AI visibility and Generative Engine Optimization (GEO) measurements are only scientifically interpretable when their underlying methodology is explicitly documented. A reported visibility percentage or recommendation score is meaningless without establishing:

1. **Prompt Provenance**: Whether prompts represent real observed user queries, semantic expansions, or experimental research templates.
2. **Provider Classification**: Whether models are evaluated with live search grounding (`answer_engine`) or as parametric text completion models (`llm`).
3. **Temporal Execution Metadata**: The exact date, timestamp, and model snapshot tested, given the rapid release cycles of generative AI systems.
4. **Raw Evidence Preservation**: Whether raw, unedited API completion payloads are preserved to enable independent verification and auditability.
5. **Entity Disambiguation Rules**: How brand names, personal names, aliases, and negative homonym collisions are parsed.
6. **Aggregation and Statistical Methods**: How descriptive rates, confidence intervals, and error exclusions are computed.

This crosswalk provides a transparent comparison between GEO-Scope's open research framework and the publicly documented methodology of commercial AI visibility systems (specifically [Ahrefs Brand Radar](https://ahrefs.com/blog/brand-radar-methodology/) and the [Ahrefs AI Visibility Checker](https://ahrefs.com/ai-visibility-checker)).

---

## Public methodology comparison

The table below contrasts the measurement dimensions implemented in GEO-Scope with the publicly documented methodology of Ahrefs Brand Radar:

| Measurement Dimension | GEO-Scope Implementation | Ahrefs Brand Radar (Publicly Documented) | Evidence / Source | Methodological Boundary / Limitation |
|:---|:---|:---|:---|:---|
| **Prompt Provenance** | Explicitly records `source_category` (`observed_user_questions` vs `research_questions`), search intent strata, language, region, and country ISO code for every prompt. | Combines Google People Also Ask (PAA) queries for behavioral relevance with semantic fanout for topic completeness from Ahrefs' 110B keyword corpus. | GEO-Scope: [`geo_scope/questions/models.py`](../geo_scope/questions/models.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Data collection") | Sampled prompt cohorts reflect curated research or search strata, not total population-level AI chatbot prompt volume. |
| **Search-Backed / Observed-Demand Prompts** | Includes real-world mined user questions ($60\%$ in benchmark releases) tagged as `observed_user_questions`. | Generates prompt sets using Google People Also Ask (PAA) based on real keywords searched by real people. | GEO-Scope: [`geo_scope/engine/query_loader.py`](../geo_scope/engine/query_loader.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("PAA") | Search engine query volume is a modeled proxy; public methodology does not claim a validated link to chatbot query frequency. |
| **Research / Systematic Prompts** | Supports exploratory comparative templates ($40\%$ in benchmark releases) tagged as `research_questions` across 9 concern categories. | Uses semantic fanout to generate structured sub-questions covering full topic architecture regardless of user search volume. | GEO-Scope: [`geo_scope/engine/query_generator.py`](../geo_scope/engine/query_generator.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Fanout") | Synthetic or template prompts evaluate model capability on structured topics, not natural conversational user phrasing. |
| **Provider Identification** | Explicitly logs provider adapter name, provider class, model identifier, execution latency, and HTTP status in every completion record. | Publicly documents tracking ChatGPT, Perplexity, Gemini, Microsoft Copilot, Google AI Overviews, AI Mode, and Grok. | GEO-Scope: [`geo_scope/providers/models.py`](../geo_scope/providers/models.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Data collection") | Public web interfaces and API routing are subject to dynamic backend model updates and prompt modifications by AI vendors. |
| **Search-Grounded vs Base-LLM Separation** | Strictly partitions models into `answer_engine` (web-grounded) and `llm` (direct text completion); metrics are maintained as separate families. | Executes across web interfaces of search-augmented and chatbot tools; provides platform-specific metrics and aggregated "All platforms" reporting. | GEO-Scope: [`geo_scope/providers/models.py`](../geo_scope/providers/models.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Data modeling") | Search-grounded answer engines and raw language models rely on fundamentally different retrieval and synthesis mechanics. |
| **Raw Response Preservation** | Preserves verbatim, unedited completion payloads in `raw_responses.jsonl` in all published benchmark packages. | Stores raw responses in an internal corpus so users can search through text and links to identify brand occurrences. | GEO-Scope: [`geo_scope/engine/persistence.py`](../geo_scope/engine/persistence.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Data collection") | Preserving raw text requires storage management and sanitization of credentials and PII. |
| **Mention Extraction** | Multi-type entity parsing with exact matching, alias normalization, negative homonym exclusion (`do_not_confuse`), and founder/brand separation. | Searches response corpus for exact string matches and brand terms. | GEO-Scope: [`geo_scope/parser/observation_parser.py`](../geo_scope/parser/observation_parser.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Data collection") | Simple string matching risks homonym collisions; entity registries require explicit negative constraints. |
| **Citation Extraction** | Extracts grounding URLs, normalizes domains, and records citation frequency in `citations.jsonl`. | Surfaces linked URLs and citations from response bodies; tracks "Found, but not cited" scenarios. | GEO-Scope: [`geo_scope/parser/observation_parser.py`](../geo_scope/parser/observation_parser.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("How to interpret the data") | AI-generated citations may include hallucinated or malformed URLs that reflect model behavior. |
| **Error / Timeout Preservation** | Logs API errors, rate limits, and timeouts to `errors.jsonl` with zero silent fallback to synthetic fixtures. | Not established from the cited public documentation. | GEO-Scope: [`geo_scope/measurement/engine.py`](../geo_scope/measurement/engine.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) | Masking or discarding failed requests can artificially inflate observed entity visibility rates. |
| **Reproducible Offline Replay** | Deterministically recomputes observations and metrics from saved `raw_responses.jsonl` via `geo-scope replay` with zero network access. | Not established from the cited public documentation. | GEO-Scope: [`geo_scope/measurement/replay.py`](../geo_scope/measurement/replay.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) | Replay validates metric calculation determinism; it does not re-query external live APIs. |
| **Integrity Checks / Checksums** | Generates SHA-256 cryptographic manifests (`checksums.sha256`) verified via `geo-scope benchmark verify`. | Not established from the cited public documentation. | GEO-Scope: [`geo_scope/benchmark/hasher.py`](../geo_scope/benchmark/hasher.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) | Cryptographic checksums verify file integrity against tampering; they do not validate external factual accuracy of model text. |
| **Geographic / Language Metadata** | Prompts contain ISO country codes, regional identifiers, and verified language codes (`language`, `region`, `country_iso`). | Parameterizes query sampling according to country and language distribution in Ahrefs keyword database. | GEO-Scope: [`geo_scope/questions/models.py`](../geo_scope/questions/models.py)<br>Ahrefs: [Brand Radar Methodology](https://ahrefs.com/blog/brand-radar-methodology/) ("Locale") | Keyword database geographical distributions do not directly represent per-country AI chatbot user demographics. |
| **Public Release Artifacts** | Distributes self-contained open research packages under `benchmark/releases/` with open MIT license, raw logs, and checksums. | Delivers continuous SaaS dashboard monitoring (AI Share of Voice, Estimated Impressions) and a free AI Visibility Checker tool. | GEO-Scope: [`benchmark/releases/`](../benchmark/releases/)<br>Ahrefs: [AI Visibility Checker](https://ahrefs.com/ai-visibility-checker) | Static benchmark packages provide immutable historical snapshots; SaaS platforms provide continuous longitudinal monitoring. |

---

## What GEO-Scope measures

GEO-Scope measures observable empirical outputs from configured AI systems across five distinct categories:

1. **Mention Visibility**: The empirical frequency and proportion of model completions in which an entity (or its documented aliases) appears in the generated text (`mention_rate_pct`).
2. **Recommendation Position**: Whether an entity is explicitly presented as an endorsed solution or choice in response to comparative or recommendation prompts (`recommendation_rate_pct`), including primary recommendation placement (`top1_rate_pct`).
3. **Citations**: The web domains, URLs, and source references provided in search-grounded answer engine completions (`citations.jsonl`).
4. **Attribution**: Instances where an entity is identified as the author, originator, or authority behind a specific statement, dataset, or methodology.
5. **Provider-Specific Observations**: Partitioned visibility observations comparing search-grounded answer engines (`gemini-2.5-flash`, `sonar-pro`) and parametric language models (`gpt-4o-mini`, `claude-3.5-sonnet`) independently.

---

## What GEO-Scope does NOT establish

To prevent ungrounded interpretation, GEO-Scope explicitly establishes the following boundaries:

* **No universal ranking-factor claims**: GEO-Scope does not claim to establish universal or permanent ranking factors for generative engine optimization.
* **No inference about proprietary model internals**: Observations describe empirical output tokens and citations; they do not reveal proprietary model weights, internal architecture, or confidential search indices.
* **No prediction of future rankings**: AI answer outputs are probabilistic and subject to continuous model, system prompt, and index updates.
* **No assumption that prompt samples equal population-level demand**: Curated prompt sets reflect specific experimental cohorts, not the full distribution of all questions asked by global users.
* **No claim that visibility equals commercial performance**: High entity visibility or recommendation rates do not guarantee user traffic, conversions, revenue, or brand sentiment.

---

## Reproduction

Published GEO-Scope benchmark releases can be verified and replayed offline using the built-in CLI commands:

```bash
# 1. Verify cryptographic integrity of the Global AI Answers 2026.2 dataset
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# 2. Deterministically replay and recompute all metrics from raw response evidence
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2

# 3. Verify the Global AI Answers 2026.2 Pilot dataset
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# 4. Replay the Pilot dataset offline with zero network calls
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```

---

## Citation & Author

Developed by **[Taqi Molavi](https://molavi.pro)** (Senior SEO Strategist & GEO Systems Architect).  
Canonical Homepage: [molavi.pro](https://molavi.pro/)  
GitHub Repository: [github.com/tmolavi/geo-scope](https://github.com/tmolavi/geo-scope)

### BibTeX

```bibtex
@software{molavi2026geoscope,
  author = {Molavi, Taqi},
  title = {GEO-Scope: Empirical AI Answer Visibility Measurement Framework},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tmolavi/geo-scope}},
  note = {Personal Homepage: https://molavi.pro/}
}
```
