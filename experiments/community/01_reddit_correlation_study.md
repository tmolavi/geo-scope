# 🧪 Experiment: Reddit UGC Discussion Density vs AI Recommendation Rate

- **Author**: GEO-Scope Research Initiative
- **Date**: 2026-08-12
- **Experiment ID**: `EXP-REDDIT-001`
- **Status**: Baseline Established (Open for Replication)

---

## 1. Hypothesis
Active brand presence in upvoted Reddit community threads positively correlates with higher recommendation rates in Perplexity Sonar compared to traditional search engines.

---

## 2. Experimental Setup
- **Industry**: CRM & Sales Software (`crm_sales`)
- **Brands Tested**: HubSpot (Target) vs Salesforce, Zoho CRM, Pipedrive
- **Prompts Tested**: 200 comparative and commercial queries
- **Models**: Perplexity Sonar, ChatGPT Search, Gemini Grounding, Claude 3.7

---

## 3. Results Summary
- **Perplexity Sonar**: 38% of all cited grounding links were `reddit.com/r/sales` or `reddit.com/r/entrepreneur`.
- **ChatGPT Search**: 16% Reddit links, 28% High-DR PR media links.
- **Observed Correlation**: Brands with positive consensus in top 3 upvoted Reddit comments achieved a 2.4x higher primary recommendation rate (#1 pick) in Perplexity.

---

## 4. Replicate This Experiment

```bash
geo-scope run --niche crm_sales --brand HubSpot --count 200 --out results/reddit_study/
```
