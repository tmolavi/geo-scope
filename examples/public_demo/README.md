# GEO-Scope Public Demo Fixture

`[STANDALONE_DEMO_FIXTURE]` — **Ephemeral Mock Fixture for Offline Verification & Educational Demonstrations**

This directory contains a self-contained, offline benchmark fixture designed to demonstrate cryptographic integrity verification, metric recomputation, and factor analysis without making external network calls or requiring API keys.

---

## Dataset Files

| File | Purpose |
|------|---------|
| `manifest.json` | Dataset metadata, schema specification, and execution mode |
| `prompts.jsonl` | Seed questions with AnswerPath discovery provenance metadata |
| `observations.jsonl` | Captured raw model responses with latency, entity mentions, and rankings |
| `citations.jsonl` | URL and domain-level citations linked to prompt executions |
| `entities.json` | Evaluated brands/agencies monitored in the benchmark |
| `providers.json` | Providers and models tested across the execution runs |
| `metrics.json` | Pre-computed benchmark metrics with 95% bootstrap confidence intervals |
| `checksums.sha256` | SHA-256 cryptographic hashes ensuring bit-for-bit immutability |

---

## 🚀 How to Verify & Reproduce (Under 60 Seconds)

### Step 1: Verify Cryptographic Integrity (SHA-256)
Ensure that none of the benchmark files have been altered or corrupted:

```bash
geo-scope benchmark verify --dataset examples/public_demo
```

### Step 2: Reproduce All Metrics from Raw Records
Recalculate every metric (mention rate, top-1 recommendation share, citations, and bootstrap confidence intervals) directly from `observations.jsonl` and compare against `metrics.json`:

```bash
geo-scope benchmark reproduce --dataset examples/public_demo
```

### Expected Output
```text
======================================================================
GEO-Scope Benchmark Verification & Reproduction: public_demo
======================================================================
• Execution Mode    : standalone_demo_fixture
• Research Status   : demo_only
• SHA-256 Checksums : VERIFIED (Bit-for-bit intact)
• Metric Math Check : VERIFIED (Recomputed from raw records)
• Prompts / Obs     : 4 prompts / 8 observations
• Brands Evaluated  : Web24, Novin, Dimarketing, Inten
----------------------------------------------------------------------
✓ All observations, citations, and bootstrap confidence intervals successfully reproduced.
======================================================================
```
