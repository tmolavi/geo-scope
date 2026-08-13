# 🥊 Challenge Our Findings

> **"Don't trust GEO claims. Test them."**

---

## 🎯 Why Disagreement is a Feature of GEO-Scope

The search and generative AI landscape is filled with unverified assertions, theoretical playbooks, and speculative advice.

At **GEO-Scope**, we believe that **empirical reproducibility is the only standard that matters**.

If our baseline experiment observed that:
- *Perplexity cites Reddit in 38% of cases*
- *ChatGPT relies 28% on high-DR PR media*
- *Structured comparison tables increase recommendation probability*

...Your experiment in a different industry, language, or time period **may observe something completely different**.

**That is not a failure of GEO-Scope — that is valuable scientific discovery.**

---

## 🚀 How to Challenge a Finding

1. **Fork the Repository**:
   ```bash
   git clone https://github.com/tmolavi/geo-scope.git
   cd geo-scope
   pip install -e .
   ```

2. **Define Your Experimental Setup**:
   Create a custom prompt dataset (`my_prompts.csv`) reflecting your specific niche, market, or language.

3. **Execute Your Benchmark**:
   ```bash
   geo-scope run \
     --brand "Your Brand" \
     --competitors "Competitor 1, Competitor 2" \
     --prompts my_prompts.csv \
     --out results/challenge_experiment/
   ```

4. **Publish Your Replication**:
   - Open an issue using the **[Contradictory Finding Issue Template](https://github.com/tmolavi/geo-scope/issues/new?template=contradictory_finding.yml)**.
   - Attach your `summary.md`, `experiment.json`, and `citations.csv`.
   - Submit a PR adding your study to `experiments/community/`.

---

## 🔬 What We Look For in Community Challenges

- **Reproducibility**: Clear prompt sets, configuration, and execution metadata.
- **Transparency**: Distinction between live cloud APIs and simulated benchmarks.
- **Scientific Rigor**: Avoiding claims of direct causation without controlled multi-sample testing.

```text
Bring your own prompts.
Run your own experiments.
Build your own evidence.
```
