# Reproducing the Global AI Answers Benchmark

This guide outlines how independent researchers and developers can reproduce the **Global AI Answers Benchmark 2026** (`global-ai-answers-2026.1`) both offline (cryptographic & metric reproduction) and live (new measurement runs).

---

## 1. Quick Verification (Integrity & Checksums)

Ensure the dataset package has not experienced bit-level corruption or unauthorized modification:

```bash
# Verify all package SHA-256 signatures
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1

# Run comprehensive dataset quality & secret check
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.1
```

**Expected Output**:
```
✓ Checksum Verification PASSED: 13 files verified intact in 'benchmark/releases/global-ai-answers-2026.1'
```

---

## 2. Offline Deterministic Reproduction

Offline reproduction recalculates all entity mentions, recommendation rates, citation presence, and bootstrap confidence intervals directly from the recorded `raw_responses.jsonl` and `observations.jsonl` files **without making network calls**.

```bash
# Replay and recompute all metrics
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.1
```

Alternatively, use the core `replay` engine:

```bash
geo-scope replay \
  --input benchmark/releases/global-ai-answers-2026.1 \
  --entities benchmark/releases/global-ai-answers-2026.1/entities.json \
  --out output/reproduced_global_2026
```

**Expected Result**:
- Exact mathematical match for all entity mention counts, recommendation rates, and provider breakdowns stored in `metrics.json`.

---

## 3. Live Reproduction (Executing New Measurements)

To conduct a new live measurement run across frontier AI providers using your own credentials or Hamzad AI Gateway:

### Step 1: Configure Environment Variables
```bash
export HAMZAD_GATEWAY_URL="https://api.molavi.pro"
export HAMZAD_API_KEY="your-api-key"
```

### Step 2: Execute Live Measurement
```bash
geo-scope measure \
  --entities benchmark/releases/global-ai-answers-2026.1/entities.json \
  --prompts benchmark/releases/global-ai-answers-2026.1/prompts.jsonl \
  --mode live \
  --providers perplexity_sonar,gemini_grounding,openai,claude \
  --out output/my_live_benchmark_run
```

### Step 3: Validate & Replay Your New Dataset
```bash
# Verify zero fallback occurred and inspect new metrics
geo-scope replay \
  --input output/my_live_benchmark_run \
  --entities benchmark/releases/global-ai-answers-2026.1/entities.json \
  --out output/my_replayed_run
```

---

## 4. Troubleshooting & Notes
- If one provider experiences a timeout, GEO-Scope records the failure in `errors.jsonl` and continues with other models without falling back to synthetic data.
- Live results will naturally exhibit slight variation due to temperature sampling and search index updates.
