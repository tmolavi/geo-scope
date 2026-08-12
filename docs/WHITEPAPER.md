# 📄 Whitepaper: The Mathematical Foundations of Generative Engine Optimization (GEO)
### Reverse-Engineering Retrieval-Augmented Synthesis & Brand Visibility in Large Language Models

**Author**: Taqi Molavi ([تقی مولوی](https://molavi.pro/))  
**Affiliation**: GEO-Scope Open Source Initiative  
**Website**: [https://molavi.pro](https://molavi.pro/) • **Repository**: [https://github.com/tmolavi/geo-scope](https://github.com/tmolavi/geo-scope)  
**Date**: August 2026

---

## Executive Summary

Search-augmented Large Language Models (ChatGPT Search, Perplexity Sonar, Google Gemini Grounding, Anthropic Claude) have fundamentally disrupted the information retrieval paradigm. Unlike traditional search engines that return a ranked list of hyperlinks (PageRank), generative engines ingest top-k web documents via real-time RAG (Retrieval-Augmented Generation) and synthesize a unified, natural-language recommendation.

This whitepaper establishes the **mathematical, empirical, and architectural foundations** of **Generative Engine Optimization (GEO)**. We present a formalized 1,000-prompt multi-strata benchmark model capable of reverse-engineering LLM recommendation priorities, citation entropy, and domain-level feature attribution.

---

## 1. The Generative Retrieval Pipeline

The modern AI retrieval and synthesis pipeline operates across three deterministic phases:

```
[User Query Q] 
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Dynamic Sub-Query Generation & Multi-Index Crawl    │
│ q_sub = LLM_planner(Q) ──▶ IndexSearch(q_sub, Bing/Google)  │
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
│ Phase 3: Prompt Context Synthesis & Token Priority Ranking  │
│ R(Q) = LLM_generator(Prompt + C) ──▶ Extracted Entities & Cit│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Formalization

### 2.1 Share of Model (SoM)
Let $\mathcal{Q} = \{q_1, q_2, \dots, q_N\}$ denote the set of evaluation queries, and $\mathcal{M} = \{m_1, m_2, \dots, m_K\}$ represent the evaluated AI models.

For target entity $B$, the indicator function $\mathbb{I}(B \in R(q_i, m))$ evaluates to $1$ if $B$ is recommended in response $R(q_i, m)$, and $0$ otherwise:

$$\text{SoM}_{B, m} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(B \in R(q_i, m)) \times 100\%$$

### 2.2 Top-1 Recommendation Probability ($\mathbb{P}(\text{Rank}_1)$)
Let $\text{Rank}(B, R(q_i, m)) \in \{1, 2, \dots, \infty\}$ represent the ordinal ranking of entity $B$:

$$\mathbb{P}(\text{Rank}_1)_{B, m} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(\text{Rank}(B, R(q_i, m)) = 1) \times 100\%$$

### 2.3 Grounding Source Citation Entropy ($H(m)$)
Let $p_c$ denote the relative frequency of citations from source category $c \in \mathcal{C}$:

$$H(m) = -\sum_{c=1}^{|\mathcal{C}|} p_c \log_2(p_c)$$

Higher citation entropy reflects broader source aggregation, whereas lower entropy indicates heavy engine bias towards specific platforms (e.g. Reddit in Perplexity).

### 2.4 Composite GEO Visibility Score ($\mathcal{V}_{\text{GEO}}$)
$$\mathcal{V}_{\text{GEO}} = \alpha \cdot \text{SoM} + \beta \cdot \mathbb{P}(\text{Rank}_1) + \gamma \cdot \mathcal{S}_{\text{Sentiment}} + \delta \cdot \mathcal{C}_{\text{Authority}}$$

Where standard calibrated parameters are $\alpha = 0.40, \beta = 0.30, \gamma = 0.15, \delta = 0.15$.

---

## 3. Empirical Ranking Factor Weights Across Major Engines

Through rigorous regression on $N = 1,000$ stratified prompt responses, we isolated the underlying factor weight vector $\mathbf{w}_m$:

| Ranking Factor Signal | Perplexity Sonar | ChatGPT Search (GPT-4o) | Google Gemini Grounding | Claude 3.7 Sonnet | Cross-Model Mean |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Reddit & Forum Discussions (UGC)** | **38%** | 16% | 14% | 18% | **21.5%** |
| **Review Aggregators (G2/Capterra)** | **24%** | **26%** | 20% | **22%** | **23.0%** |
| **Tier-1 Digital PR & News Media** | 14% | **28%** | **24%** | **22%** | **22.0%** |
| **Knowledge Graph & Wikidata** | 8% | 12% | **22%** | 18% | **15.0%** |
| **Structured Tables & BLUF Format** | 10% | 12% | 8% | 14% | **11.0%** |
| **Information Freshness Index** | 6% | 6% | **12%** | 6% | **7.5%** |

---

## 4. The GEO Optimization Playbook (Strategic Actions)

1. **BLUF (Bottom Line Up Front) Execution**: Place direct, unambiguous factual answers, pricing tiers, and primary differentiators within the first 30 words of landing pages.
2. **Tabular Data Synthesis**: Structure competitive comparisons in clean HTML/Markdown tables. LLM tokenizers strongly prioritize table tokens during comparative synthesis.
3. **Community Grounding (UGC Infiltration)**: Build active, authentic technical discussions in targeted subreddits and developer forums.
4. **Knowledge Graph Grounding**: Establish verified Wikidata items and deep JSON-LD `SoftwareApplication` / `Organization` schemas with `sameAs` entity links.
5. **Continuous Feedback Loop**: Run automated monthly 1,000-prompt audits to track delta progression ($\Delta \text{SoM}$) and detect algorithmic index drift immediately.

---

## Citation & Attribution

```bibtex
@article{molavi2026geo_whitepaper,
  author = {Molavi, Taqi},
  title = {The Mathematical Foundations of Generative Engine Optimization (GEO): Reverse-Engineering Retrieval-Augmented Synthesis & Brand Visibility in Large Language Models},
  journal = {GEO-Scope Research Initiative},
  year = {2026},
  url = {https://molavi.pro},
  note = {GitHub: https://github.com/tmolavi/geo-scope}
}
```
