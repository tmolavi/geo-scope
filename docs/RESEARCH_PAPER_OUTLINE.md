# Empirical AI Answer Visibility: An Auditable Measurement Framework for Generative Information Retrieval

**Paper Outline & Technical Specification**  
**Repository**: `tmolavi/geo-scope`  
**Document Version**: 1.0  
**Target Publication**: Empirical Methods in Information Retrieval / AI Search Systems  

---

## Title

**Empirical AI Answer Visibility: A Reproducible Measurement Framework for Entity Mentions, Recommendations, and Citations in Generative AI Systems**

---

## Abstract

As generative artificial intelligence (AI) systems and search-grounded answer engines increasingly replace traditional ten-blue-link search engines for information discovery, empirical methodology for measuring entity visibility remains fragmented and unstandardized. Existing commercial tools frequently conflate mentions with recommendations, obscure provider failure denominators, and fail to preserve raw prompt provenance or unparsed model responses. 

In this work, we introduce **GEO-Scope**, an open-source, reproducible measurement framework designed to quantify and preserve auditable evidence of how generative AI systems surface commercial, informational, and personal entities. The framework establishes a strict taxonomic distinction between four independent visibility dimensions: **unprompted mentions**, **explicit recommendations**, **direct domain citations**, and **linguistic attributions**. We introduce a multi-lingual entity resolution engine capable of normalizing Unicode non-joiners and disambiguating homonyms across five languages (Arabic, English, Persian, Turkish, and Chinese), evaluated against a versioned 220-item human-labeled Golden Dataset. Furthermore, we formalize a repeat protocol ($k \ge 5$) to quantify response variability and enforce cryptographic SHA-256 artifact verification for zero-network replayability. We report baseline observational findings across 45,000+ observations from search-grounded answer engines and parametric foundation models.

---

## 1. Research Question

### Primary Research Questions (RQ)
- **RQ1 (Visibility Disambiguation)**: To what degree do search-grounded answer engines (e.g., Perplexity Sonar, Gemini Search Grounding) differ from parametric foundation LLMs (e.g., GPT-4o, Claude 3.7 Sonnet) in how entities are *mentioned* versus explicitly *recommended* or *cited*?
- **RQ2 (Attribution vs. Citation Separation)**: How frequently do generative AI models attribute factual statements to an organization or study by name without providing an explicit source URL/citation link, and vice versa?
- **RQ3 (Measurement Reproducibility & Stability)**: Under repeated sampling ($k \ge 5$) with identical neutral prompts, what is the observed variance in entity appearance rates across distinct model providers and search grounding classes?
- **RQ4 (Multi-Lingual Resolution Reliability)**: Can rule-based deterministic parsers with language-specific morphological normalization achieve $\ge 90\%$ F1-scores for entity identification, homonym filtering, and rank extraction across diverse language families without introducing non-deterministic neural parser drift?

---

## 2. Methodology

### 2.1 Prompt Provenance & Neutral Prompt Policy
- **Synthetic Domain Generation**: Standardized generation of multi-lingual queries across predefined topic taxonomies (e.g., B2B SaaS, digital marketing, consumer technology, travel, financial tools).
- **Zero-Steering Constraint**: Prompts are strictly formulated without target entity names, biased framing, or loaded adjectives that artificially induce specific brand mentions.
- **Intent Categorization**: Categorization of queries into *informational* (entity background, definitions), *investigative* (comparisons, alternatives), *recommendation-seeking* ("best tools for X"), and *navigational* (direct platform entry).

### 2.2 Provider Class Taxonomy
- **Search-Grounded Answer Engines** (`provider_class: answer_engine`): Systems that dynamically retrieve live web documents before answer generation (e.g., Perplexity Sonar, Gemini with Google Search Grounding).
- **Parametric Foundation Models** (`provider_class: llm`): Models generating completions strictly from internal training weights without dynamic search grounding tools.
- **Provider Governance & Identity Preservation**: Enforcement that `requested_provider` and `actual_provider` match exactly, with silent fallbacks disabled to prevent surrogate model contamination.

### 2.3 Denominator & Failure Accounting
- Explicit mathematical separation between:
  1. $N_{\text{attempted}}$: Total scheduled prompt execution runs.
  2. $N_{\text{successful}}$: HTTP 200 completion records successfully parsed.
  3. $N_{\text{failed}}$: Rate-limited, timed-out, or upstream API error records.
- All visibility proportions are computed over verified successful completions with $N_{\text{failed}}$ explicitly reported as provider error rate.

---

## 3. Dataset Description

### 3.1 Empirical Benchmark Releases
- **Global AI Answers Benchmark 2026.2**:
  - Scope: 500 prompts across 50 countries, 9 industry categories, and 26 language varieties.
  - Scale: 626 completion runs yielding 45,698 discrete entity observations across 73 tracked entities.
  - Formats: Preserved `prompts.jsonl`, `raw_responses.jsonl`, `observations.jsonl`, `metrics.json`, and `errors.jsonl`.
- **Pilot & Regional Releases**:
  - `global-ai-answers-2026.2-pilot`: Calibration dataset for cross-provider variance.
  - `geo-seo-digital-agency-iran-2026.1`: Regional dataset focused on Middle Eastern technology entities and Persian-language retrieval.

### 3.2 Evidence Chain & Preserved Artifacts
- **Payload Preservation**: Full raw JSON payloads from provider APIs (including token usage, latency, search metadata chunks, and timestamps) stored alongside extracted metrics.
- **Cryptographic Hashes**: Every benchmark package includes a `checksums.sha256` manifest guaranteeing bit-level immutability.

---

## 4. Measurement Framework

### 4.1 Visibility Metrics Formalization
Let $E$ be the target entity, $Q$ be the query set, and $R(q)$ be the set of valid model responses for query $q \in Q$ under provider $P$:

1. **Observed Mention Rate ($\text{OMR}$)**:
   $$\text{OMR}(E, P) = \frac{1}{|Q_{\text{successful}}|} \sum_{q \in Q_{\text{successful}}} \mathbb{I}(\text{Mentioned}(E, R(q)))$$

2. **Recommendation Share ($\text{RS}$)**:
   $$\text{RS}(E, P) = \frac{1}{|Q_{\text{successful}}|} \sum_{q \in Q_{\text{successful}}} \mathbb{I}(\text{Recommended}(E, R(q)))$$
   *(Strictly requires explicit endorsement phrasing or an ordered recommendation list structure; informational mentions do not qualify).*

3. **First-Rank Share ($\text{FRS}$)**:
   $$\text{FRS}(E, P) = \frac{1}{|Q_{\text{rec\_queries}}|} \sum_{q \in Q_{\text{rec\_queries}}} \mathbb{I}(\text{Rank}(E, R(q)) = 1)$$

4. **Direct Citation Rate ($\text{DCR}$)**:
   $$\text{DCR}(E, P) = \frac{1}{|Q_{\text{successful}}|} \sum_{q \in Q_{\text{successful}}} \mathbb{I}(\text{URL\_Cited}(E, R(q)))$$

5. **Attribution Sourcing Rate ($\text{ASR}$)**:
   $$\text{ASR}(E, P) = \frac{1}{|Q_{\text{successful}}|} \sum_{q \in Q_{\text{successful}}} \mathbb{I}(\text{Text\_Attributed}(E, R(q)))$$

---

## 5. Multi-Lingual Entity Resolution Engine

### 5.1 Text Normalization Pipeline
- **Unicode NFKC & Case Folding**: Canonical decomposition followed by canonical composition.
- **Persian & Arabic Orthographic Unification**: Unification of Arabic Kaf/Yeh (`ك`, `ي`) with Persian Keheh/Yeh (`ک`, `ی`), removal of Tatweel (`ـ`), and stripping of non-breaking spaces.
- **Zero-Width Non-Joiner (ZWNJ) Handling**: Flexible matching for compound words (e.g., `وب‌۲۴` matches `وب ۲۴`, `وب24`, and `Web24`).
- **Unspaced Continuous Matching**: Concatenation heuristics to resolve single-word variations of multi-word brand and personal names.

### 5.2 Homonym Collision Filtering
- Negative constraints (`do_not_confuse` dictionaries) to eliminate false positives arising from common nouns, geographical places, or historical homonyms (e.g., distinguishing modern digital agencies from historical poet references or physical retail markets).

---

## 6. Parser Evaluation on Golden Dataset

### 6.1 Evaluation Methodology
- **Dataset**: `benchmark/golden_sets/v1/` comprising 220 human-labeled examples across 5 languages (Arabic, English, Persian, Turkish, Chinese) and 18 diverse entities.
- **Evaluation Protocol**: Deterministic execution of `ObservationParser` with binary scoring (Precision, Recall, F1) per attribute.

### 6.2 Empirical Parser Metrics

| Evaluation Field | Precision | Recall | F1-Score | Support ($N$) | Notes |
|:---|:---|:---|:---|:---|:---|
| **Mentioned** | 99.51% | 100.00% | **99.75%** | 203 | High accuracy across all 5 languages |
| **Recommended** | 100.00% | 100.00% | **100.00%** | 82 | Zero false positives on informational queries |
| **Cited (URL)** | 100.00% | 100.00% | **100.00%** | 112 | Exact domain/subdomain matching |
| **Attributed (Text)** | 100.00% | 84.44% | **91.56%** | 45 | High precision; recall impacted by complex syntax |
| **Wrong Entity (Homonym)**| 100.00% | 94.12% | **96.97%** | 17 | Robust homonym filtering |
| **Rank Extraction** | 100.00% | 100.00% | **100.00%** | 77 | Perfect ordinal position identification |

---

## 7. Limitations

1. **Non-Causal Associational Boundary**:
   - The framework measures observed outputs under documented prompts; it does not claim to uncover the internal proprietary ranking weights or algorithmic scoring functions of commercial providers.
2. **Attribution Syntax Variability**:
   - Linguistic attribution in natural prose exhibits rich stylistic diversity; indirect or passive attribution phrasing can produce false negatives ($\approx 8\text{--}15\%$) in complex non-English text.
3. **Single-Turn Scope**:
   - The primary evaluation protocol operates on discrete single-turn queries, without modeling multi-turn conversational context drift or user chat feedback loops.
4. **Provider Interface Volatility**:
   - Upstream API parameter shifts, undocumented model version updates, and dynamic web search index updates introduce temporal volatility into longitudinal observations.

---

## 8. Reproducibility & Audit Protocol

- **Zero-Network Offline Replay**:
  - `geo-scope replay <release_directory>` re-executes all feature extraction and metric computations directly from preserved `raw_responses.jsonl` without calling external APIs.
- **Cryptographic Verification**:
  - Independent auditors can verify bit-level file integrity using standard SHA-256 tools (`sha256sum -c checksums.sha256`).
- **Open Implementation**:
  - Complete Python codebase, JSON schemas (`schemas/v0.3/`), CLI tooling, and test suites are released under the MIT License.

---

## 9. Future Work

1. **Multi-Turn Conversational Visibility**:
   - Extending the measurement protocol to track entity persistence, displacement, and brand decay across multi-turn dialogue sessions.
2. **Contextual Synthetic Grounding**:
   - Measuring how variations in document indexing speed, schema markup, and authoritative knowledge graph entries correlate with observed citation frequency.
3. **Automated Continuous Replay CI**:
   - Integration of scheduled automated re-evaluation jobs against public archival snapshots to track visibility drifts over time.
4. **Expanded Multi-Lingual Golden Corpora**:
   - Scaling the human-labeled Golden Dataset to 1,000+ examples across 15+ global languages.

---

## References & Standards
- NIST AI Risk Management Framework (AI RMF 1.0)
- JSON Schema Draft 2020-12 Specifications
- Unicode Consortium Standard Annex #15 (Unicode Normalization Forms)
