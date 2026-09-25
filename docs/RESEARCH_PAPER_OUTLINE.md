# Research Paper Outline: Empirical Generative Engine Optimization (GEO) & AI Answer Visibility

**Title**: *Measuring Generative AI Visibility: A Standardized Measurement Contract, Evidence Pipeline, and Multi-Model Empirical Benchmark*  
**Authors**: Taqi Molavi, et al.  
**Repository**: [`https://github.com/tmolavi/geo-scope`](https://github.com/tmolavi/geo-scope)  
**Methodological Foundation**: [`docs/measurement-contract-v1.md`](measurement-contract-v1.md)  
**Schema Standard**: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)  

---

## Abstract
As generative AI systems and search-grounded answer engines replace traditional search interfaces, quantifying how entities, brands, and sources surface in AI-generated answers has become a critical research challenge. Existing visibility tools produce conflicting numbers due to ad-hoc definitions, unstandardized sampling, and lack of reproducible evidence. 

This paper introduces the **GEO-Scope AI Visibility Measurement Contract v1**, a formal, machine-readable measurement standard and deterministic evidence pipeline for empirical generative AI observation. We formalize response-level binary mentions, 4-way citation attribution, semantic recommendation gating, and structured list ranking. We evaluate our deterministic multi-lingual parser on a 5-language human-annotated Golden Dataset ($N=220$, achieving $99.75\%$ Mention F1, $100\%$ Recommendation F1, and $100\%$ Citation F1) and demonstrate end-to-end zero-network replayability across public benchmark datasets.

---

## 1. Introduction & The Problem

### 1.1 The Shift from Traditional Search to Generative Answer Engines
- Traditional search engines return ranked lists of uniform URLs evaluated by stable crawling and indexing paradigms.
- Generative answer engines (ChatGPT Search, Perplexity, Google Gemini, Claude) generate synthesized natural language completions combining parametric memory with real-time search-retrieval grounding.

### 1.2 The Problem: Lack of Standardized Observable Definitions
Current commercial and academic AI visibility platforms produce divergent, non-comparable numbers for identical entities. These discrepancies stem from:
1. **Unstandardized Observable Definitions**: Equating mere lexical mention in text with explicit commercial recommendation or source citation.
2. **Ad-Hoc Prompt Sampling**: Comparing head queries against long-tail queries without declared prompt universes or intent distributions.
3. **Proprietary "Black-Box" Visibility Scores**: Aggregating observations into ungrounded composite scores without transparent denominators or weighting models.
4. **Lack of Verifiable Evidence Chains**: Presenting aggregated percentages without preserved raw API payloads, cryptographic hashes, or offline replay capabilities.

---

## 2. Methodological Foundation: Measurement Contract v1

### 2.1 Core Epistemic Axiom
> *"AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."*

GEO-Scope establishes that AI visibility cannot be claimed as a universal constant. Every valid measurement is an empirical observation bounded by:
- A declared **Prompt Universe** (count, source, intent strata, language, market).
- A declared **Model Configuration** (provider, model snapshot, temperature, search grounding state).
- An explicit **Measurement Contract** defining extraction rules, failure denominators, and comparability criteria.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEO-SCOPE THREE-PILLAR METHODOLOGY                       │
├────────────────────────┬──────────────────────────┬─────────────────────────┤
│  MEASUREMENT CONTRACT  │    EVIDENCE PIPELINE     │  REPRODUCIBLE BENCHMARK │
│  Machine-Readable JSON │  Raw Payload Capture &   │  Immutable Datasets &   │
│  Schema & Axioms       │  Cryptographic Hashes    │  Zero-Network Replay    │
└────────────────────────┴──────────────────────────┴─────────────────────────┘
```

### 2.2 Provider Class Taxonomy & Execution Modes
- **Search-Grounded Answer Engines** (`provider_class: answer_engine`): Retrieval-augmented generation querying live web sources (e.g., Perplexity Sonar, Gemini Search Grounding).
- **Parametric Foundation Models** (`provider_class: llm`): Generating strictly from model weights without search tools.
- **Provider Neutrality & Governance**: Enforcing exact provider identity (`requested_provider == actual_provider`), disabling surrogate fallbacks, and using neutral system prompts by default.

### 2.3 Denominator & Failure Accounting
- Explicit mathematical reporting:
  - $N_{\text{attempted}}$: Total scheduled query dispatches.
  - $N_{\text{successful}}$: HTTP 200 responses successfully parsed.
  - $N_{\text{failed}}$: Rate-limited, timed out, or API error dispatches.
- If $N_{\text{successful}} = 0$, visibility is reported as `insufficient_data` / `null`, never artificially as `0.0%`.

---

## 3. Standardized Metrics Formalization

Under Measurement Contract v1, GEO-Scope separates observable outputs into five distinct mathematical metrics:

### 3.1 Observed Mention Rate ($\text{OMR}$) — Binary Response-Level
A response-level binary indicator $\mathbb{I}(\text{Mention}(E, R_i)) \in \{0, 1\}$. Multiple occurrences of entity $E$ in response $R_i$ count as exactly $1$ response mention:
$$\text{OMR}(E) = \frac{1}{N_{\text{successful}}} \sum_{i=1}^{N_{\text{successful}}} \mathbb{I}(\text{Mention}(E, R_i)) \times 100$$

### 3.2 4-Way Citation Attribution
Separates citations into four mutually exclusive observable states:
1. **Target Domain Cited ($\text{TDC}$)**: Target entity's verified root domain cited in web grounding links.
2. **Target URL Cited ($\text{TUC}$)**: Specific deep URL cited.
3. **Third-Party Source Cited ($\text{3PC}$)**: External reviews, news, or directory URLs cited.
4. **Entity Mentioned Without Citation**: Lexical mention in text without grounding links.

### 3.3 Recommendation Share ($\text{RS}$) & Experimental Gating
$$\text{RS}(E) = \frac{1}{N_{\text{successful}}} \sum_{i=1}^{N_{\text{successful}}} \mathbb{I}(\text{Recommended}(E, R_i)) \times 100$$
- Evaluated as `1` only when the completion explicitly endorses or selects the entity.
- Informational or historical mentions are strictly scored as `0`.
- Ambiguous classifications are gated with `recommendation_status: "experimental"`.

### 3.4 First-Rank Share ($\text{FRS}$) & Position
- Ranks are assigned strictly from recognized numbered list patterns (`1. `, `1- `, `#1 `).
- Unranked paragraphs or bulleted lists yield $\text{Rank} = \text{null}$.
- $\text{FRS}(E)$ measures the percentage of recommendation queries where entity $E$ occupies rank 1.

### 3.5 Attribution Sourcing Rate ($\text{ASR}$)
$$\text{ASR}(E) = \frac{1}{N_{\text{successful}}} \sum_{i=1}^{N_{\text{successful}}} \mathbb{I}(\text{Text\_Attributed}(E, R_i)) \times 100$$
- Measures textual credit linking specific claims or statistics to the source entity.

---

## 4. Multi-Lingual Entity Resolution & Parser Engine

### 4.1 Normalization Pipeline
- **Unicode NFKC & Case Folding**: Canonical decomposition and recomposition.
- **Perso-Arabic Orthographic Unification**: Unifying Arabic Kaf/Yeh (`ك`, `ي`) with Persian Keheh/Yeh (`ک`, `ی`), stripping Tatweel (`ـ`), and normalizing Zero-Width Non-Joiners (ZWNJ).
- **Unspaced Concatenation Matching**: Resolving single-token variants of multi-word names.

### 4.2 Homonym Collision Filtering
- Negative boundary rules (`do_not_confuse` dictionaries) preventing false positives from common words, geographical locations, or historical figures.

---

## 5. Golden Dataset & Parser Evaluation

### 5.1 Evaluation Setup
- **Dataset**: `benchmark/golden_sets/v1/` ($N=220$ human-labeled instances across Arabic, English, Persian, Turkish, Chinese across 18 entities).
- **Deterministic Metric**: Precision, Recall, and F1 per attribute.

### 5.2 Empirical Evaluation Results

| Attribute | Precision | Recall | F1-Score | Support ($N$) | Evaluation Notes |
|:---|:---|:---|:---|:---|:---|
| **Mentioned** | 99.51% | 100.00% | **99.75%** | 203 | Robust across all 5 evaluated languages |
| **Recommended** | 100.00% | 100.00% | **100.00%** | 82 | Zero false positives on informational queries |
| **Cited (URL)** | 100.00% | 100.00% | **100.00%** | 112 | Exact domain/subdomain matching |
| **Attributed (Text)** | 100.00% | 84.44% | **91.56%** | 45 | High precision; syntax variability affects recall |
| **Wrong Entity (Homonym)**| 100.00% | 94.12% | **96.97%** | 17 | Verified negative constraint filtering |
| **Rank Extraction** | 100.00% | 100.00% | **100.00%** | 77 | Perfect ordinal position identification |

---

## 6. Dataset Releases & Zero-Network Replay Protocol

### 6.1 Preserved Benchmark Releases
- **Global AI Answers Benchmark 2026.2**: 500 prompts across 50 countries, 45,698 discrete entity observations.
- **Regional Benchmark 2026.1**: Focused on Middle Eastern technology and digital agency ecosystems.

### 6.2 Zero-Network Offline Replayability
- Any independent auditor can reproduce published benchmark metrics bit-for-bit without executing API calls:
  ```bash
  geo-scope replay --bundle benchmark/releases/global-ai-answers-2026.2 --out-dir output/audit_replay
  ```
- File integrity is cryptographically locked via `checksums.sha256`.

---

## 7. Methodological Limitations

GEO-Scope research operates under explicit epistemic boundaries:

1. **No Universal AI Ranking Truth**: Observed metrics reflect specific prompt sets and model configurations; they do not represent global search engine market share or static rankings.
2. **No Causal Claims**: Observed correlations between entity features and mention frequencies are exploratory associations, not proven causal factors.
3. **No Proprietary Algorithm Reverse-Engineering**: GEO-Scope measures external observable outputs, not internal model weights or proprietary retrieval heuristics.
4. **Temporal & Grounding Volatility**: Live search-grounded models depend on dynamic search index caches, producing temporal variance across observation epochs.

---

## 8. Future Directions

1. **Multi-Turn Conversational Visibility**: Tracking entity decay and reinforcement across continuous multi-turn dialogue trees.
2. **Longitudinal Shift Tracking**: Continuous automated replay against scheduled archival web snapshots.
3. **Expanded Multi-Lingual Golden Corpora**: Scaling human-labeled validation sets to 15+ low-resource languages.

---

## References & Standards
- NIST AI Risk Management Framework (AI RMF 1.0)
- JSON Schema Draft 2020-12 Specifications
- Unicode Consortium Standard Annex #15 (Unicode Normalization Forms)
- [GEO-Scope Scientific Foundation Release v1.0](SCIENTIFIC_FOUNDATION_V1.md)
- [GEO-Scope Measurement Contract v1](measurement-contract-v1.md)
- [GEO-Scope Releases & Milestones Timeline](RELEASES.md)
- [Why the Measurement Contract Exists](WHY_MEASUREMENT_CONTRACT_EXISTS.md)
