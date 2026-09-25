# GEO-Scope AI Visibility Measurement Contract v1

**Version:** 1.0  
**Status:** Public Standard / Machine-Readable Specification  
**Canonical Schema:** [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)  
**Reference Example:** [`examples/measurement-contract-v1-example.json`](../examples/measurement-contract-v1-example.json)  

---

## 1. Why This Exists

Generative Engine Optimization (GEO) and AI visibility measurement platforms frequently report divergent visibility metrics for identical brands and topics. As articulated in foundational research on measurement methodology (e.g., [iPullRank on Accuracy vs. Precision](https://ipullrank.com/accuracy-vs-precision) and [Ahrefs on AI Visibility Metrics](https://help.ahrefs.com/en/articles/15501968-ai-visibility-metrics)), these discrepancies do not necessarily indicate measurement error; rather, they arise legitimately from differences in:

1. **Prompt Populations:** Query selection, domain intent distribution, and query framing (neutral prompts vs. forced recommendation lists).
2. **Sampling & Repetition Protocols:** Single-shot observations vs. $k$-repeat sampling over time.
3. **Provider & Model Configurations:** Model versioning, temperature settings, web-search grounding states, and geographical egress points.
4. **Metric Denominators:** Denominators based on total attempted queries vs. successful completions, and unweighted vs. search-demand-weighted calculations.
5. **Entity & Citation Extraction Logic:** Equating mere lexical mention with explicit commercial recommendation or source attribution.

GEO-Scope establishes this **Measurement Contract v1** as an open, machine-readable standard so that any researcher, data engineer, or auditor can understand, replicate, and compare empirical AI visibility observations with scientific precision.

---

## 2. Core Scientific Principle

> [!IMPORTANT]
> **Fundamental Axiom of AI Visibility**  
> *"AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."*

AI models do not possess a static, globally uniform "ranking table" analogous to traditional search engine result pages (SERPs). An observed AI visibility metric represents the empirical response distribution of a specific model configuration evaluated against a specific prompt universe at a specific moment in time.

---

## 3. Metric Definitions

GEO-Scope enforces strict, unambiguous definitions across all measured visibility dimensions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI RESPONSE OBSERVATION                           │
├────────────────────────┬──────────────────────────┬─────────────────────────┤
│        MENTION         │         CITATION         │     RECOMMENDATION      │
│  Binary Response-Level │ 4-Way Source Attribution │ Semantic Recommendation │
│  Occurrence (>=1 time) │ Target Domain / URL / 3P │ Explicit Endorsement    │
└────────────────────────┴──────────────────────────┴─────────────────────────┘
```

### 3.1. Mention (`mention`)
* **Definition:** A response-level binary observation indicating whether the target entity (or its declared aliases) appears at least once in the generated response.
* **Cardinality Rule:** Multiple occurrences of an entity within a single response **must NOT** count as multiple mentions. If entity $E$ is named 5 times in response $R_i$, $\text{Mention}(E, R_i) = 1$, not $5$.
* **Properties:**
  * `mentioned` (boolean): `true` if occurrence count $\ge 1$, else `false`.
  * `occurrence_count` (integer): Raw lexical count of entity aliases within the response text.
  * `matched_aliases` (array of strings): Specific string tokens matched by the entity registry.

### 3.2. Citation (`citation`)
Mentions and citations are distinct phenomena. A model may mention a brand without citing its website, or cite a third-party directory without mentioning the brand's official URL. GEO-Scope separates citation tracking into four distinct modalities:

* `entity_mentioned` (boolean): Whether the entity is named in the response body.
* `target_domain_cited` (boolean): Whether the target entity's verified root domain (e.g., `inten.asia`) appears in the search-grounding citation list or markdown hyperlinks.
* `target_url_cited` (boolean): Whether an exact target deep-link URL (e.g., `https://inten.asia/services/seo`) is explicitly cited.
* `third_party_source_cited` (boolean): Whether external sources (industry directories, review platforms, news portals) citing or discussing the entity are provided as grounding links.
* `cited_domains` (array of strings): All unique domain hostnames extracted from grounding citations.
* `cited_urls` (array of strings): All deep URLs cited.

### 3.3. Recommendation (`recommendation`)
* **Definition:** Evaluated as `true` only when the model's response semantically endorses, selects, or recommends the entity as a top solution (e.g., *"We recommend Brand X for enterprise SEO"* or placement under a list titled *"Top Recommended Agencies"*).
* **Reliability & Experimental Gating:** Mere descriptive co-occurrence (e.g., *"Company X was founded in 2015"*) does not constitute a recommendation. Where automated semantic classification cannot achieve $>0.90$ precision or encounters ambiguity, the observation must declare:
  * `recommendation_status`: `"confirmed"` | `"not_recommended"` | `"experimental"`
  * `recommendation_evidence`: Exact supporting phrase snippet.

### 3.4. Position / Rank (`position`)
* **Strict Ranking Contract:** Ranks are extracted **exclusively** from recognized, structured numbered lists (e.g., `1. `, `1- `, `#1 `).
* **Negative Rule:** Ranks **must never** be inferred from arbitrary paragraph order, appearance sequence, or bulleted lists.
* **Properties:**
  * `rank_position` (integer or null): $1$-indexed integer if in a numbered list, else `null`.
  * `is_top1` (boolean): `true` if and only if `rank_position == 1`.
  * `ranking_method` (string): `"numbered_list_only"` or `"unranked"`.

### 3.5. Share of Voice (`share_of_voice`)
GEO-Scope explicitly prohibits exposing undefined "visibility scores". Share of Voice must declare its mathematical denominator and weighting model:

* **Raw Mention Share (`raw_mention_share`):**
  $$\text{Raw Mention Share}(E) = \frac{\sum_{i=1}^{N_{\text{success}}} \mathbb{I}(\text{Mention}(E, R_i))}{N_{\text{success}}} \times 100$$
* **Weighted Share of Voice (`weighted_share_of_voice`):**
  $$\text{Weighted SOV}(E) = \frac{\sum_{i=1}^{N_{\text{success}}} w_i \cdot \mathbb{I}(\text{Mention}(E, R_i))}{\sum_{i=1}^{N_{\text{success}}} w_i} \times 100$$
  *Where $w_i$ represents the verified search demand weight for prompt $i$.*
* **Weighting Source (`weighting_source`):** Must explicitly document the provider or methodology (e.g., Google Keyword Planner search volume, AnswerPath impression index). If unweighted, `weighting_source` is `null`.
* **Denominator Accountability:** All calculations must state `denominator_definition` (e.g., *"Total successful model completions in prompt universe (N=100)"*).

---

## 4. Sampling & Prompt Universe Contract

Every benchmark dataset and study must declare its prompt population parameters:

```json
"prompt_universe": {
  "prompt_set_id": "geo-seo-digital-agency-iran-2026.1",
  "prompt_count": 100,
  "prompt_source": "Observed user search query distribution in Digital Marketing",
  "prompt_generation_method": "hybrid_stratified",
  "language": "fa",
  "country_or_market": "IR",
  "intent_distribution": {
    "recommendation": 0.50,
    "informational": 0.30,
    "navigational": 0.15,
    "comparison": 0.05
  },
  "collection_date": "2026-09-23T14:55:00Z",
  "strata": ["recommendation", "informational", "navigational", "comparison"]
}
```

* `prompt_generation_method` must be one of:
  * `observed_user_queries`: Real anonymized human search queries.
  * `expert_curated`: Human domain-expert authored questions.
  * `synthetic_templated`: Programmatically expanded linguistic templates.
  * `hybrid_stratified`: Stratified blend of observed and curated queries.

---

## 5. Model Observation Contract

Every observation record must capture the operational environment of the evaluating engine:

* `provider`: Provider identifier (e.g., `openai`, `google_gemini`, `perplexity`, `anthropic`, `hamzad`).
* `model`: Model name (e.g., `gpt-4o`, `gemini-2.5-pro`, `sonar-pro`, `claude-3-7-sonnet`).
* `model_version`: Specific model snapshot or build ID when available.
* `temperature`: Sampling temperature ($0.0$ for deterministic benchmark reproducibility).
* `timestamp`: ISO 8601 UTC observation timestamp.
* `location`: Egress country or region (e.g., `IR`, `US`, `DE`).
* `search_grounding_enabled` (boolean): Whether live web search retrieval was active during generation.
* `web_access_enabled` (boolean): General web browsing connectivity flag.
* `system_prompt_policy`: Default is `"neutral"` (no bias or steering). If queries force output formatting, declared as `"forced_list"`.
* `configuration_hash`: Cryptographic SHA-256 hash of complete provider execution parameters.

---

## 6. Repeated Observation Contract ($k$-Repeats)

Generative AI responses exhibit stochastic variability. GEO-Scope supports repeated observations ($k \ge 1$) per prompt:

* `observation_count` (integer): Total independent runs executed for this prompt ($k$).
* `repeat_index` (integer): $0$-indexed instance ID ($0 \dots k-1$).
* `first_observed_at` (ISO 8601): Earliest observation timestamp in the batch.
* `last_observed_at` (ISO 8601): Latest observation timestamp in the batch.

> [!WARNING]
> **Longitudinal Integrity Rule**  
> A single observation window ($k=1$ or single day) **must not** be represented as longitudinal visibility or historical trend analysis. Longitudinal comparisons require distinct observation epochs with declared temporal gaps.

---

## 7. Machine-Readable Comparability Rules

Two benchmark runs or external datasets are **directly comparable** if and only if all critical dimensions align:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DIRECT COMPARABILITY MATRIX                         │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ Dimension                         │ Requirement for comparable = true       │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 1. Prompt Universe                │ Identical prompt set or matched strata  │
│ 2. Market & Language              │ Same country ISO & language code        │
│ 3. Provider & Model Family        │ Same model architecture and grounding   │
│ 4. Measurement Definition         │ Identical binary mention/citation rules │
│ 5. Observation Window             │ Synchronized or declared temporal epoch │
└───────────────────────────────────┴─────────────────────────────────────────┘
```

If any dimension diverges, the contract requires:
* `comparable`: `false`
* `mismatch_reasons`: Array of explicit divergence descriptions (e.g., `["Differing prompt universes: 100 queries vs 500 queries", "Grounding mismatch: search_grounding active vs inactive"]`).

---

## 8. Raw Evidence & Privacy Constraints

To guarantee scientific reproducibility and auditability, every observation record must be traceable to underlying evidence:

* `prompt_id`: Unique prompt identifier.
* `observation_id`: Unique observation identifier.
* `raw_response`: Full or snippet text of the generated AI answer.
* `raw_response_reference`: Pointer to raw response repository file (e.g., `raw_responses.jsonl#p-001`).
* `response_hash_sha256`: Cryptographic SHA-256 checksum of the raw response payload.
* `extracted_entities`: Array of entities detected.
* `citations`: Extracted citations and references.
* `timestamp`: ISO 8601 UTC timestamp.
* `configuration_hash`: SHA-256 hash of execution settings.

### Privacy & Provider Terms Constraint
If commercial provider terms or data privacy agreements prohibit distributing full raw text outputs:
1. The full text may be omitted from public distribution.
2. The `response_hash_sha256` and `raw_response_reference` **must** be preserved.
3. The limitation must be documented under `privacy_or_provider_constraint` (e.g., *"Raw response text withheld under enterprise API terms; cryptographic hash provided for verification"*).

---

## 9. Known Scientific Limitations

Users and consumers of GEO-Scope data must account for the following inherent limitations:

1. **Stochastic Sampling Variance:** With temperature $> 0$, models produce varying text distributions across runs.
2. **Search Grounding Volatility:** Live search engines refresh index caches continually; identical queries may receive different citations across hours.
3. **Linguistic & Morphological Parsing:** Complex non-Latin scripts (e.g., Persian / Arabic / Chinese) require lemmatization; edge-case alias collisions are monitored via `is_ambiguous` flags.
4. **Provider-Side Interventions:** Model providers routinely deploy safety guardrails, system prompt updates, or routing changes without version increments.

---

## 10. Prescribed Public Language & Communication

Public reporting based on GEO-Scope measurement contracts must maintain scientific objectivity:

### ✅ Permitted Scientific Statements:
* *"Under the GEO-Scope Measurement Contract v1, we observed a 42.0% mention rate for Brand X across 100 Iranian SEO prompts on ChatGPT Search (March 2026). "*
* *"Within this declared prompt set, Brand Y was cited in 18.5% of grounded responses."*
* *"Under this measurement configuration, Brand A had a higher observed mention frequency than Brand B on Perplexity Sonar."*

### ❌ Prohibited Claims:
* *"Brand X has 42% true AI visibility across all AI platforms."*
* *"Competing Tool Y is inaccurate because its visibility score differs from GEO-Scope."*
* *"Brand A is universally ranked #1 in generative AI search."*

---

## 11. Schema & Validation Fixture

* **JSON Schema Specification:** [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)
* **10-Observation Working Fixture:** [`examples/measurement-contract-v1-example.json`](../examples/measurement-contract-v1-example.json)
* **Validation Test Suite:** [`tests/test_measurement_contract_v1.py`](../tests/test_measurement_contract_v1.py)
