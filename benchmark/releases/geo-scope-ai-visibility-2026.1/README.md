# GEO-Scope AI Visibility Benchmark 2026.1 (Release Package)

**Dataset ID**: `geo-scope-ai-visibility-2026.1`  
**Execution Mode**: `live`  
**Research Status**: `experimental_observation`  
**Methodology Version**: `1.0.0`  

---

## Overview
This public benchmark release evaluates brand visibility, share of model (SoM), top-1 recommendation frequency, and domain citations across 4 major AI search providers (Google Gemini, Perplexity Sonar, OpenAI ChatGPT, Anthropic Claude) in the **AI SEO / GEO Tools** category.

---

## Package Contents
```text
benchmark/releases/geo-scope-ai-visibility-2026.1/
├── manifest.json         # Dataset metadata, hashes, provider list, and execution status
├── prompts.jsonl         # 100 stratified queries (Discovery, Comparison, Commercial, Educational)
├── brands.json           # 8 audited industry brands (Semrush, Ahrefs, Moz, Surfer SEO, etc.)
├── providers.json        # Provider descriptors & model bindings
├── observations.jsonl    # 400 normalized model execution records
├── citations.jsonl       # Extracted domain citations and grounding evidence
├── metrics.json          # Pre-computed benchmark metrics, bootstrap CIs, and visibility matrix
├── methodology.md        # Formal methodology, epistemic constraints, and reproduction steps
└── checksums.sha256      # SHA-256 cryptographic checksums for all package files
```

---

## How to Verify and Reproduce

### 1. Verification of File Hashes
```bash
geo-scope benchmark verify-checksums benchmark/releases/geo-scope-ai-visibility-2026.1
```

### 2. Full Reproducibility Check
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1
```

### 3. Inspect Metrics
All metrics including the **Category Visibility Matrix (Brand x Provider)** and **95% Bootstrap Confidence Intervals** are stored in `metrics.json`.
