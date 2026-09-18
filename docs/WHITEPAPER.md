# 📄 Whitepaper: The Mathematical & Empirical Foundations of Generative Engine Optimization (GEO)
### Empirical Measurement of Brand Visibility, Recommendations, and Citations in Answer Engines & Large Language Models

> **Implementation Note**: GEO-Scope is an open-source measurement laboratory for observing how brands appear across answer engines and language models. Fixed factor weights and composite-score coefficients are research hypothesis priors, not fitted neural engine weights or validated causal effects. Seeded simulation is deterministic for testing; live generation is variable and requires direct provider credentials.

**Author**: Taqi Molavi ([تقی مولوی](https://molavi.pro/))  
**Affiliation**: GEO-Scope Open Source Initiative  
**Website**: [https://molavi.pro](https://molavi.pro/) • **Repository**: [https://github.com/tmolavi/geo-scope](https://github.com/tmolavi/geo-scope)  
**Date**: September 2026

---

## Executive Summary

Search-augmented Large Language Models (ChatGPT Search, Perplexity Sonar, Google Gemini Grounding, Anthropic Claude) have fundamentally altered the information retrieval paradigm. Unlike traditional search engines that return a ranked list of hyperlinks (PageRank), generative answer engines ingest retrieved web documents via real-time RAG (Retrieval-Augmented Generation) and synthesize unified, natural-language recommendations.

**GEO-Scope** is an open-source measurement laboratory for observing how brands appear across answer engines and language models. We present a formalized empirical measurement methodology for observing brand recommendation frequencies, citation entropy, and entity-level presence in generative AI outputs without asserting speculative "ranking algorithm reverse engineering" claims.

---

## 1. Evidence Levels & Methodology Guardrails

GEO-Scope enforces strict, uncompromised separation between three levels of evidence. Different evidence levels must **never** be mixed:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GEO-Scope Evidence Levels                          │
├───────────────────┬───────────────────────────────┬─────────────────────────┤
│ Level 1: Fixture  │ Level 2: Recorded Replay      │ Level 3: Live Measure   │
├───────────────────┼───────────────────────────────┼─────────────────────────┤
│ • Deterministic   │ • Deterministic offline audit │ • Direct provider APIs  │
│ • Simulation data │ • Re-evaluates raw responses  │ • Real-time completions │
│ • CI / Onboarding │ • Zero network access         │ • Full raw provenance   │
│ • simulated_* tag │ • Cryptographic SHA-256 hash  │ • Zero silent fallback  │
└───────────────────┴───────────────────────────────┴─────────────────────────┘
```

### Level 1: Simulation Fixture (`geo-scope demo`)
- **Purpose**: CI testing, education, parser verification, and local development.
- **Data Nature**: Deterministic simulation fixtures with simulated citations.
- **Classification**: **SIMULATION FIXTURE — NOT LIVE MODEL OUTPUT — NOT MARKET BENCHMARK**.
- **Metrics**: Strictly prefixed with `simulated_*` (`simulated_mention_rate`, etc.).

### Level 2: Recorded Response Replay (`geo-scope replay`)
- **Purpose**: Deterministic, zero-cost re-evaluation of previously recorded raw AI responses against modified entity dictionaries or disambiguation rules.
- **Data Nature**: Offline parsing of existing `raw_responses.jsonl`. Zero network calls permitted.
- **Provenance**: Cryptographically bound to the original execution bundle via SHA-256 checksums.

### Level 3: Live Provider Measurement (`geo-scope measure`)
- **Purpose**: Empirical observation of live answer engines and language models.
- **Requirements**: Real provider credentials, full raw response payload persistence, exact UTC timestamps, and provider class separation (`answer_engine` with grounding vs `llm_completion`).
- **Failure Policy**: Strict **zero silent fallback**. API timeouts or authentication errors are recorded directly in `errors.jsonl` rather than masked with synthetic responses.

---

## 2. The Generative Retrieval Pipeline

The modern AI retrieval and synthesis pipeline operates across three observed phases:

```
[User Query Q] 
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Dynamic Sub-Query Generation & Multi-Index Crawl    │
│ q_sub = LLM_planner(Q) ──▶ IndexSearch(q_sub, Web/Bing/G)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Documents D = {d_1, d_2, ..., d_k}
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Authority Filtering & Consensus Aggregation         │
│ D_filtered = Filter(D | DomainAuthority, UGC, Reviews, Wiki)│
└──────────────────────────────┬──────────────────────────────┘
                               │ Filtered Tokens & Context C
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Prompt Context Synthesis & Token Recommendation    │
│ R(Q) = LLM_generator(Prompt + C) ──▶ Extracted Entities & Cit│
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical Formalization

### 3.1 Observed Mention Rate & Share of Model (SoM)
Let $\mathcal{Q} = \{q_1, q_2, \dots, q_N\}$ denote the set of evaluation queries, and $\mathcal{M} = \{m_1, m_2, \dots, m_K\}$ represent the evaluated AI models.

For target brand entity $B$, the indicator function $\mathbb{I}(B \in R(q_i, m))$ evaluates to $1$ if $B$ is observed in response $R(q_i, m)$, and $0$ otherwise:

$$\text{SoM}_{B, m} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(B \in R(q_i, m)) \times 100\%$$

### 3.2 Top-1 Recommendation Probability ($\mathbb{P}(\text{Rank}_1)$)
Let $\text{Rank}(B, R(q_i, m)) \in \{1, 2, \dots, \infty\}$ represent the ordinal position of recommended entity $B$ (evaluated only for queries with `scoring_status: "scored"`):

$$\mathbb{P}(\text{Rank}_1)_{B, m} = \frac{1}{N_{\text{scored}}} \sum_{i=1}^{N_{\text{scored}}} \mathbb{I}(\text{Rank}(B, R(q_i, m)) = 1) \times 100\%$$

### 3.3 Grounding Source Citation Entropy ($H(m)$)
Let $p_c$ denote the relative frequency of citations from source category $c \in \mathcal{C}$ in search-grounded answer engines:

$$H(m) = -\sum_{c=1}^{|\mathcal{C}|} p_c \log_2(p_c)$$

Higher citation entropy reflects diverse source aggregation across domains; lower entropy indicates concentration on specific platforms.

### 3.4 Composite GEO Visibility Score ($\mathcal{V}_{\text{GEO}}$)
$$\mathcal{V}_{\text{GEO}} = \alpha \cdot \text{SoM} + \beta \cdot \mathbb{P}(\text{Rank}_1) + \gamma \cdot \mathcal{S}_{\text{Sentiment}} + \delta \cdot \mathcal{C}_{\text{Authority}}$$

Where illustrative research hypothesis prior parameters are $\alpha = 0.40, \beta = 0.30, \gamma = 0.15, \delta = 0.15$. These weights are configurable hypothesis priors, not proprietary neural weights.

---

## 4. Research Hypothesis Factor Profiles (Priors)

*(Note: Factor profiles are structured hypothesis priors used to organize observational inquiries; they do NOT represent verified causal algorithms).*

| Research Hypothesis Dimension | Perplexity Sonar | ChatGPT Search | Google Gemini Grounding | Claude 3.7 | Cross-Model Prior Mean |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Community & Forum UGC (Reddit/Quora)** | **38%** | 16% | 14% | 18% | **21.5%** |
| **Review Aggregators (G2/Capterra)** | **24%** | **26%** | 20% | **22%** | **23.0%** |
| **Tier-1 Digital PR & News Media** | 14% | **28%** | **24%** | **22%** | **22.0%** |
| **Knowledge Graph & Wikidata** | 8% | 12% | **22%** | 18% | **15.0%** |
| **Structured Tables & Direct BLUF Content** | 10% | 12% | 8% | 14% | **11.0%** |
| **Information Freshness & Recency** | 6% | 6% | **12%** | 6% | **7.5%** |

---

## 5. Strategic Optimization Heuristics

1. **BLUF (Bottom Line Up Front) Structure**: Position direct factual answers, pricing points, and core entity attributes within the opening section of informational pages for clean retrieval extraction.
2. **Tabular Synthesizability**: Present comparison matrices and structured specifications using standard semantic HTML/Markdown tables.
3. **Third-Party Footprint**: Ensure verified presence on independent review directories and community discussions referenced during grounding sub-queries.
4. **Structured Schema Grounding**: Implement accurate `Organization` and `SoftwareApplication` JSON-LD schemas with authoritative `sameAs` entity identifiers.
5. **Continuous Empirical Verification**: Periodically benchmark visibility against observed user prompt sets to monitor longitudinal visibility trends.

---

## Citation & Attribution

```bibtex
@article{molavi2026geo_whitepaper,
  author = {Molavi, Taqi},
  title = {The Mathematical & Empirical Foundations of Generative Engine Optimization (GEO): Empirical Measurement of Brand Visibility, Recommendations, and Citations in Answer Engines & Large Language Models},
  journal = {GEO-Scope Research Initiative},
  year = {2026},
  url = {https://molavi.pro},
  note = {GitHub: https://github.com/tmolavi/geo-scope}
}
```
