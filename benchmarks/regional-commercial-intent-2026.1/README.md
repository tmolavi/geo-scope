# GEO-Scope Regional Commercial AI Visibility Pilot 2026.1

**Identifier:** `regional-commercial-intent-2026.1`  
**Markets:** Iran (`fa-IR`), Türkiye (`tr-TR`)  
**Methodological Inspiration:** [Peak Ace AI Visibility LLM Benchmark 2026](https://peakace.agency/en/latest/ai-visibility-llm-benchmark-2026/)  
**Execution Status:** `NOT_RUN` (Reproducible Pilot Fixtures Prepared; Live Grounding Adapters Unauthenticated)

---

## 1. Overview

This directory contains the specification, fixtures, prompt datasets, entity definitions, and quality verification gates for the **GEO-Scope Regional Commercial AI Visibility Pilot (Iran & Türkiye)**.

Inspired by Peak Ace's 2026 intent-based benchmark design, this independent study introduces a standardized measurement pilot for commercial AI visibility across two key Middle Eastern markets:
- **Iran (`fa-IR`):** Persian commercial queries in SEO, GEO, technical audit, and PR sectors.
- **Türkiye (`tr-TR`):** Turkish commercial queries across agency selection, GEO consulting, and search tools.

---

## 2. Directory Layout & Evidence Files

```
benchmarks/regional-commercial-intent-2026.1/
├── README.md               # This project documentation
├── methodology.md          # Scientific methodology & Peak Ace comparison
├── limitations.md          # Sample size, provider, & market limitations
├── run-config.json         # Execution configuration & cost budget ($10 cap)
├── manifest.json           # Benchmark package metadata (conforms to schema v0.3)
├── prompts.jsonl           # 24 unique unbranded neutral buyer prompts
├── entities.json           # Target brand & agency profiles for IR and TR
├── metrics.json            # Metrics package with denominator accounting
├── raw_responses.jsonl     # Evidence archive for raw responses
├── observations.jsonl      # Scored observation records
├── errors.jsonl            # Traceable provider error log
└── checksums.sha256        # SHA-256 cryptographic hashes of all files
```

---

## 3. Sampling Design

| Parameter | Value | Details |
| :--- | :--- | :--- |
| **Unique Prompts** | 24 | 12 Iran (`fa-IR`) + 12 Türkiye (`tr-TR`) |
| **Intent Groups** | 4 | Best/recommendation (6), Comparison (6), Pricing/selection (6), Criteria/guidance (6) |
| **Target Engines** | 3 | ChatGPT Search, Gemini Grounding, Perplexity Sonar |
| **Repetitions ($k$)** | 2 | 2 runs per prompt per engine |
| **Planned Observations** | 144 | $24 \text{ prompts} \times 3 \text{ engines} \times 2 \text{ repeats}$ |
| **Pilot Budget Cap** | \$10.00 | Hard budget ceiling |
| **Estimated Cost** | \$2.64 | \$0.005/query (Perplexity) + \$0.035/query (Gemini) + \$0.015/query (ChatGPT) |

---

## 4. Provider Governance & Current State

- **Current Status:** `NOT_RUN`  
- **Provider Status:** `chatgpt_search`, `gemini_grounding`, and `perplexity_sonar` are marked `PROVIDER_UNAVAILABLE` because live search-grounded API keys are not provisioned in the local execution session.
- **Scientific Integrity Policy:** GEO-Scope rules strictly forbid substituting non-grounded models (e.g. standard GPT-4o or Claude completions) while labeling them as search-grounded. Furthermore, synthetic data is never fabricated to simulate live responses.

---

## 5. How to Reproduce & Execute Live

Once valid API keys are configured in your `.env` or shell environment:

```bash
# 1. Provide API credentials for live search-grounded engines
export PERPLEXITY_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# 2. Verify provider availability
geo-scope providers

# 3. Run the regional benchmark
geo-scope measure \
  --prompts benchmarks/regional-commercial-intent-2026.1/prompts.jsonl \
  --entities benchmarks/regional-commercial-intent-2026.1/entities.json \
  --mode live \
  --providers chatgpt_search,gemini_grounding,perplexity_sonar \
  --repeat 2 \
  --out-dir benchmarks/regional-commercial-intent-2026.1/
```

---

## 6. Citation

If referencing this pilot in academic or industry research:

```bibtex
@misc{geoscope_regional_pilot_2026,
  author = {Molavi, Taqi and GEO-Scope Contributors},
  title = {GEO-Scope Regional Commercial AI Visibility Pilot 2026.1: An Independent Intent-Based Evaluation in Iran and Türkiye},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/tmolavi/geo-scope}}
}
```
