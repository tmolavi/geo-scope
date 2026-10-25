# Benchmark Methodology: Iranian Food Industry & FMCG AI Benchmark 2026

## 1. Epistemic Principles
* **Empirical Multi-Provider Observations**: All findings reflect actual text and citation outputs returned by LLM reasoning engines and search routes.
* **Neutral Multi-Entity Evaluation**: Evaluates 8 established entities under identical prompt conditions without target-brand bias.
* **Separation of Priors & Observations**: Prompt hypotheses are never reported as measured user demand.

---

## 2. Experimental Design

### A. Question Discovery & Intent Strata
The benchmark prompt bank consists of 180 standardized queries across 5 categories:
1. `dairy_nutrition`: Questions regarding low-preservative milk, probiotic yogurt, protein content (Kalleh vs Mihan vs Choopan).
2. `pasta_cereals`: Durum wheat semolina quality, export standards, whole wheat alternatives (Zar Macaron, Mana).
3. `sauces_condiments`: Healthiest salad dressings, non-sugar ketchup, traditional vs pasteurized mayonnaise (Mahram, Behrouz, Delpazir).
4. `pantry_staples`: Non-GMO cooking oils, premium Tarom/Hashemi rice grading, tea provenance (Golestan, Tabiat, Mohsen).
5. `confectionery_snacks`: High-cocoa ice cream, sugar-free desserts, sports protein bars.

### B. Multi-Provider Execution Matrix
Completions are evaluated across 4 AI routes:
1. `openai` (`gpt-4o` with Search grounding)
2. `perplexity` (`sonar-pro`)
3. `google` (`gemini-2.5-flash` with Google Grounding)
4. `anthropic` (`claude-3-5-sonnet`)

Total observations: $180 \times 4 = 720$ completions.

---

## 3. Metrics & Statistical Formulas

### Mention Rate ($MR_e$)
$$MR_e = \frac{\sum_{i=1}^N \mathbb{I}(e \in \text{Mentions}_i)}{N}$$

### Top-1 Recommendation Share ($T1_e$)
$$T1_e = \frac{\sum_{i=1}^N \mathbb{I}(\text{Top1}_i = e)}{N}$$

### Owned-Domain Citation Rate ($CR_e$)
$$CR_e = \frac{\sum_{i=1}^N \mathbb{I}(\text{Domain}_e \in \text{Citations}_i)}{N}$$

### 95% Bootstrap Confidence Intervals
Confidence intervals are computed using 1,000 non-parametric bootstrap resamples ($\alpha = 0.05$):
$$\text{CI}_{95\%} = [\hat{\theta}^*_{(25)}, \hat{\theta}^*_{(975)}]$$
