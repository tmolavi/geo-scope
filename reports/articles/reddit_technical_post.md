# Reddit Technical Post: Open Benchmark Framework for Measuring AI Search Visibility (No Fabricated Datasets)

**Subreddits**: r/SEO, r/MachineLearning, r/artificial

**Title**: [Open Source] We built a reproducible benchmark pipeline to measure brand visibility across LLMs (Gemini, GPT-4o, Claude, Perplexity) – dataset & methodology inside

Hey everyone,

There has been a huge amount of hype around "Generative Engine Optimization (GEO)" and "AI SEO", but almost zero reproducible empirical benchmarks. Most articles are either based on small subjective tests or don't disclose the raw completions.

We open-sourced **GEO-Scope** and published a complete empirical benchmark: **GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark (`geo-seo-digital-agency-iran-2026.1`)**.

### How the Pipeline Works

1. **Question Discovery & Intent Stratification (`AnswerPath GEO`)**:
   - Queries are categorized into 5 intent strata: `commercial`, `compare`, `trust`, `solve`, `buy`.
   - Explicit separation between *observed user demand* (mined from conversational logs) and *generated research hypotheses*. We don't mix synthetic prompts into user demand metrics.

2. **Zero-Secret Gateway Execution (`Hamzad AI Gateway`)**:
   - GEO-Scope never stores API keys locally. All requests route through Hamzad Gateway to Gemini 2.5 Flash, GPT-4o, Claude 3.5 Sonnet, and Perplexity Sonar.

3. **Execution Provenance & Fallback Tracking**:
   - Upstream gateways sometimes fallback to surrogate models when rate limits hit. Instead of silently discarding or mislabeling completions, GEO-Scope logs `requested_model`, `actual_model`, and `execution_class` (`native` vs `fallback`).

4. **Cryptographic Reproducibility**:
   - All 120 raw model completions, response SHA-256 hashes, prompt records, and metrics are stored in git with a `checksums.sha256` manifest.
   - Anyone can verify the package and re-run the 95% bootstrap confidence interval math locally:
     ```bash
     geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
     geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
     ```

### Epistemic Stance
We do not claim to "reverse engineer proprietary ranking algorithms". LLMs with search-grounding are stochastic pipelines. We measure **observed associations and recommendation frequencies** with statistical confidence bounds.

GitHub: https://github.com/tmolavi/geo-scope  
Research Report & Details: https://molavi.pro

Would love feedback from engineers, researchers, and SEO practitioners on metric formulation and question stratification!
