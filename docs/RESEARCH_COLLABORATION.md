# Research Collaboration Framework: Empirical AI Visibility & GEO Measurement

**Scope**: Open scientific collaboration on Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and AI visibility benchmarking.

---

## 🧭 Core Epistemic Principles

1. **Observed Behavior, Not Search Engine Truth**:
   All benchmark results represent **empirically observed completions** from specific models at specific points in time. They are **not** claims about proprietary ranking algorithms, secret weights, or guaranteed ranking factors.

2. **Full Provenance Transparency**:
   Research datasets must distinguish between:
   - **Observed User Demand** (mined queries) vs. **Exploratory Hypothesis Templates** (generated prompts).
   - **Native Model Completions** vs. **Gateway Surrogate Fallback Routes**.

3. **Bit-for-Bit Reproducibility**:
   Every research submission must publish raw observations (`observations.jsonl`), prompt seeds (`prompts.jsonl`), and cryptographic hashes (`checksums.sha256`).

---

## 🤝 How Researchers Can Collaborate

### 1. Contributing New Industry Prompt Datasets
* **Using AnswerPath GEO**: Mine genuine search and conversational questions within specific industries or locales.
* **Stratification**: Categorize queries into standard intent strata (`commercial`, `compare`, `trust`, `solve`, `buy`).
* **Format**: Submit structured datasets following the `prompts.jsonl` schema.

### 2. Provider Routing & Multi-Model Evaluation
* Propose evaluations across new frontier models (e.g. Claude 3.7 Sonnet, DeepSeek V3/R1, Gemini 2.0 Pro, Perplexity Sonar Reasoning).
* Validate provider routing integrity with zero surrogate fallback obfuscation.

### 3. Metric Design & Statistical Validation
* Propose new empirical metrics for entity mention prominence, citation survival, or grounding quality.
* Enhance bootstrap confidence interval methodologies ($N=1000$ iterations) and stratified error analysis.

### 4. Replicating and Auditing Published Releases
* Run independent replications of published datasets (`geo-scope benchmark reproduce --dataset benchmark/releases/...`).
* Submit replication reports and identify distribution shifts over time.

---

## 📬 Research Proposal Submission Process

1. Open a discussion in [GitHub Discussions (Research Category)](https://github.com/tmolavi/geo-scope/discussions/categories/research).
2. Detail the experimental design: target industry, sample size, candidate entities, models tested, and hypothesis.
3. Once reviewed by maintainers, open a PR with the proposed dataset and documentation under `benchmarks/` or `benchmark/profiles/`.
