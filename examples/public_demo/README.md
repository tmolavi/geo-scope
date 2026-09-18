# GEO-Scope Public Proof Demonstration Fixture

`[STANDALONE_DEMO_FIXTURE]` — **Educational & Verification Fixture (Offline)**

> [!IMPORTANT]
> **What This Dataset Demonstrates**:
> - Benchmark package schema and file layout.
> - Bit-for-bit SHA-256 cryptographic verification.
> - Deterministic metric recomputation directly from raw observation logs.
> - End-to-end evaluation pipeline execution without external API dependencies.
>
> **What This Dataset Does NOT Represent**:
> - **NOT a live market ranking** or commercial agency scorecard.
> - **NOT an AI provider performance ranking**.
> - **NOT a real-time AI visibility measurement**.
> - **NOT a claim of "best agency", "market winner", or search engine ranking truth.**
>
> For peer-reviewed, multi-provider empirical research studies, see the official releases under [`benchmark/releases/`](../../benchmark/releases/) and [`benchmarks/`](../../benchmarks/).

---

## 📁 Dataset Files

| File | Purpose |
|------|---------|
| `manifest.json` | Dataset metadata, schema specification, and execution mode (`demonstration`) |
| `prompts.jsonl` | Seed questions with AnswerPath discovery provenance metadata |
| `observations.jsonl` | Captured raw model responses with latency, entity mentions, and rankings |
| `citations.jsonl` | URL and domain-level citations linked to prompt executions |
| `entities.json` | Evaluated brands/agencies monitored in the fixture |
| `providers.json` | Providers and models tested across the execution runs |
| `metrics.json` | Pre-computed benchmark metrics with 95% bootstrap confidence intervals |
| `checksums.sha256` | SHA-256 cryptographic hashes ensuring bit-for-bit immutability |
| `run_demo.py` | Standalone executable runner for one-click verification |

---

## 🚀 How to Verify & Reproduce (Under 10 Seconds)

### Step 1: Verify Cryptographic Integrity (SHA-256)
Ensure that none of the fixture files have been modified or corrupted:

```bash
geo-scope benchmark verify --dataset examples/public_demo
```

### Step 2: Reproduce All Metrics from Raw Records
Recalculate every metric (mention rate, top-1 recommendation share, citations, and bootstrap confidence intervals) directly from `observations.jsonl` and compare against `metrics.json`:

```bash
geo-scope benchmark reproduce --dataset examples/public_demo
```

### Alternatively: Run Standalone Python Script
```bash
python examples/public_demo/run_demo.py
```

### Expected Output
```text
======================================================================
GEO-Scope Benchmark Verification & Reproduction: geo-scope-public-demo
======================================================================
• Execution Mode    : demonstration
• Research Status   : demo_only
• SHA-256 Checksums : VERIFIED (Bit-for-bit intact)
• Metric Math Check : VERIFIED (Recomputed from raw records)
• Prompts / Obs     : 5 prompts / 10 observations
• Brands Evaluated  : Web24, Novin, Dimarketing, Triboon
----------------------------------------------------------------------
✓ All observations, citations, and bootstrap confidence intervals successfully reproduced.
======================================================================
```
