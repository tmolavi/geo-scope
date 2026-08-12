# 🔬 Scientific Methodology: Reverse-Engineering AI Visibility

## 1. Abstract & Problem Statement

Generative AI Search Engines (Perplexity, ChatGPT Search, Google Gemini Grounding, Anthropic Claude) construct direct answers using **Retrieval-Augmented Generation (RAG)** instead of traditional PageRank search result links.

Traditional SEO ranking metrics (Keywords, SERP positions 1-10) fail to capture LLM visibility. **GEO-Scope** introduces an empirical, multi-sample benchmarking methodology designed to reverse-engineer:
1. **Share of Model (SoM)**: The probability that a brand entity is included in the synthesized context.
2. **Top-1 Recommendation Likelihood**: The probability that an LLM places a brand as the primary recommended solution.
3. **Citation Graph Attribution**: The domain-level distribution of grounding sources selected by the LLM retrieval sub-queries.
4. **Ranking Factor Weights**: The statistical correlation between on-page/off-page attributes and recommendation priority.

---

## 2. The 1,000-Prompt Benchmark Design

To achieve statistical power ($p < 0.01$, confidence interval $\pm 2.8\%$), we synthesize a stratified sample of **$N = 1,000$ distinct prompts** across five search intent strata:

```
Intent Strata Distribution (N = 1,000):
┌─────────────────────────────────────────────────────────────┐
│ 1. Commercial Direct (30%, n = 300)                         │
│    "Best CRM software for startups in 2026"                 │
├─────────────────────────────────────────────────────────────┤
│ 2. Comparative & Alternative (25%, n = 250)                 │
│    "HubSpot vs Salesforce feature comparison and ROI"       │
├─────────────────────────────────────────────────────────────┤
│ 3. Problem Solving & Use-Case (20%, n = 200)                │
│    "How to automate sales pipeline without manual data entry"│
├─────────────────────────────────────────────────────────────┤
│ 4. Long-Tail & Niche Constraint (15%, n = 150)              │
│    "Cloud CRM under $50/mo with open API for 5-person team" │
├─────────────────────────────────────────────────────────────┤
│ 5. Reputation & Community Sentiment (10%, n = 100)          │
│    "Reddit discussions and complaints about HubSpot in 2026"│
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Controlled Experimental Variables

When running multi-model evaluation pipelines:
- **Temperature & Top_p**: Fixed across deterministic runs ($\text{Temperature} = 0.2$ for reproducible synthesis).
- **Temporal Synchronization**: Prompts are executed concurrently across models to eliminate recency drift.
- **Geographic Grounding**: Defaulted to global/neutral grounding with configurable regional subtags.
- **Entity Alias Normalization**: Brand names are mapped via regex matching both canonical names and common variations (e.g., `HubSpot`, `hubspot`, `هاب‌اسپات`).

---

## 4. Citation Extraction & Domain Categorization

All URLs extracted from Markdown links `[Anchor](URL)` and footnote references are parsed into root domains and classified into 6 primary grounding classes:

1. **`ugc_forums`**: Reddit, Quora, HackerNews, StackExchange, Virgool.
2. **`review_aggregators`**: G2, Capterra, Trustpilot, ProductHunt, Gartner.
3. **`tech_media_pr`**: TechCrunch, Forbes, The Verge, Wired, Digiato, Zoomit.
4. **`knowledge_base_wiki`**: Wikipedia, Wikidata, official developer documentation.
5. **`blogs_industry`**: Long-form authoritative SEO blogs, Substack, Medium.
6. **`other_web`**: Generic web crawl sources.

---

## 5. Confidence Bounds & Reproducibility

For a sample of $N = 1,000$ prompts with sample proportion $\hat{p}$ (e.g. $\hat{p} = 0.70$):
$$\text{Margin of Error} = Z_{\alpha/2} \times \sqrt{\frac{\hat{p}(1 - \hat{p})}{N}} = 1.96 \times \sqrt{\frac{0.70 \times 0.30}{1000}} \approx \pm 2.84\%$$

This ensures high confidence when reporting Share of Model and comparing model behaviors.
