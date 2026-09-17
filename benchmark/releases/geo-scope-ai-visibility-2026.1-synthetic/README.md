# GEO-Scope AI Visibility Benchmark 2026.1 (Synthetic Validation Package)

**Dataset ID**: `geo-scope-ai-visibility-2026.1-synthetic`  
**Execution Mode**: `synthetic`  
**Research Status**: `demo_only`  
**Methodology Version**: `1.0.0`  

> [!NOTE]  
> This package is a deterministic synthetic validation dataset used for pipeline verification, schema validation, and reproducibility testing. For live multi-model execution telemetry, refer to the live execution pipeline (`scripts/run_live_hamzad_benchmark.py`).

---

## Package Contents
```text
benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic/
├── manifest.json         # Dataset metadata, hashes, provider list, and execution status (synthetic)
├── prompts.jsonl         # 100 stratified queries (Discovery, Comparison, Commercial, Educational)
├── brands.json           # 8 audited industry brands (Semrush, Ahrefs, Moz, Surfer SEO, etc.)
├── providers.json        # Provider descriptors & model bindings
├── observations.jsonl    # 400 normalized synthetic observation records
├── citations.jsonl       # Extracted domain citations and simulated grounding evidence
├── metrics.json          # Pre-computed benchmark metrics, bootstrap CIs, and visibility matrix
├── methodology.md        # Formal methodology, epistemic constraints, and reproduction steps
└── checksums.sha256      # SHA-256 cryptographic checksums for all package files
```

---

## How to Verify and Reproduce

### 1. Verification of File Hashes
```bash
geo-scope benchmark verify-checksums benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```

### 2. Full Reproducibility Check
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```
