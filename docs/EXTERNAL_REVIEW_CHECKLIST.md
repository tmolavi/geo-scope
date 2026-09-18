# External Reviewer Retest & Verification Checklist

This document provides a concise, step-by-step reproduction sequence for independent external reviewers evaluating GEO-Scope.

---

## 1. Clean Environment Installation

In an empty directory:

```bash
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 2. Automated Test Suite Execution

Run the complete test suite:

```bash
pytest -v
```

**Expected Result**: All tests pass (`140+ passed`, 0 failed).

---

## 3. Quickstart Demo (Simulation Fixture)

Run the simulation onboarding demo:

```bash
geo-scope demo
```

**What to Check**:
- Confirms banner: `Execution mode: SIMULATION FIXTURE — NO LIVE MODEL WAS QUERIED`
- Confirms `output/demo_latest/metrics.json` uses `simulated_*` metric prefixes.
- Confirms bundle includes `manifest.json`, `raw_responses.jsonl`, `observations.jsonl`, `metrics.json`, and `checksums.sha256`.

---

## 4. Run a Custom Research Run (Offline Simulation Mode)

Execute measurement using the research template in simulation mode:

```bash
geo-scope measure \
  --entities examples/research_run/entities.json \
  --prompts examples/research_run/prompts.jsonl \
  --providers perplexity_sonar,gemini_grounding \
  --mode simulation \
  --out-dir output/review_run
```

**What to Check**:
- Generates standard 7-file bundle in `output/review_run/`.
- `manifest.json` indicates `"mode": "simulation"`.

---

## 5. Offline Replay Verification (Zero Network Calls)

Re-evaluate the recorded responses against entity definitions:

```bash
geo-scope replay \
  --bundle output/review_run \
  --entities examples/research_run/entities.json \
  --out-dir output/review_replay
```

**What to Check**:
- Operates strictly offline with 0 API calls.
- Recomputes entity observations deterministically.
- `output/review_replay/checksums.sha256` verifies cleanly.

---

## 6. Live Measurement (Requires Provider API Keys)

If API keys are configured in `.env` (e.g. `PERPLEXITY_API_KEY`, `GEMINI_API_KEY`):

```bash
geo-scope measure \
  --entities examples/research_run/entities.json \
  --prompts examples/research_run/prompts.jsonl \
  --providers perplexity_sonar \
  --mode live \
  --out-dir output/live_run
```

**What to Check**:
- If an API key is missing, failure is logged in `output/live_run/errors.jsonl`.
- **Zero Fallback**: The engine does NOT silently fall back to simulation when live provider calls fail.

---

## 7. Public Dataset Integrity Verification

Verify cryptographic checksums and reproduce bootstrap metrics for the prototype release:

```bash
# Verify bit-for-bit SHA-256 hashes
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Reproduce metrics and bootstrap confidence intervals
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

**What to Check**:
- `Checksum verification PASSED` (11/11 files intact).
- Bootstrap confidence intervals recomputed directly from raw observations.
