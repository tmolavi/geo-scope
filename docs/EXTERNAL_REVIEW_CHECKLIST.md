# Independent Reviewer Audit & Verification Checklist

This checklist provides an independent external auditor with the exact criteria and reproduction sequence to verify the scientific and empirical integrity of GEO-Scope.

---

## 1. Six Core Reviewer Questions

| # | Audit Question | Verification Command / Evidence Path | Expected Reviewer Confirmation |
|:---|:---|:---|:---|
| **1** | **Can a stranger reproduce a benchmark?** | `geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2` | Recomputes all entity observations deterministically offline without API keys or external network calls. |
| **2** | **Can they identify exact provider/model?** | Inspect `providers.yml`, `manifest.json`, and `raw_responses.jsonl` | Explicit `requested_provider`, `requested_model`, `actual_provider`, `actual_model`, and `provider_class` preserved on every completion. |
| **3** | **Can they distinguish live vs simulation?** | Check `execution_mode` in `manifest.json` & `raw_responses.jsonl` | Simulation runs are explicitly marked (`execution_mode="simulation"`, metric prefix `simulated_*`); live runs reject all synthetic fixtures and fallbacks. |
| **4** | **Can they inspect raw evidence?** | Inspect `raw_responses.jsonl`, `observations.jsonl`, `citations.jsonl`, `errors.jsonl` | Full unparsed model completion strings, token latencies, citation URLs, and provider error traces are preserved verbatim. |
| **5** | **Can they understand limitations?** | Read `docs/research-transparency.md`, `limitations.md`, `docs/GOLDEN_SET_METHODOLOGY.md` | Explicit epistemic boundaries: no claim of search algorithm reverse engineering, causal ranking predictors, or guaranteed visibility improvements. |
| **6** | **Can they verify checksums?** | `geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2` | Cryptographic bit-for-bit SHA-256 verification confirms zero file tampering or bitrot. |

---

## 2. Step-by-Step Review Sequence

### Step 1: Clean Installation
```bash
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### Step 2: Run Full Test Suite
```bash
pytest -v
```
*Expected: 155+ unit and integration tests passing.*

### Step 3: Run Golden Parser Evaluation
```bash
geo-scope parser evaluate \
  --golden-set benchmark/golden_sets/v1 \
  --output output/parser_metrics.json
```
*Expected: Evaluates precision/recall across 220 multilingual records covering Persian, English, Arabic, Turkish, and Chinese.*

### Step 4: Audit Benchmark Release Quality Gate
```bash
geo-scope benchmark release-gate \
  --dataset benchmark/releases/global-ai-answers-2026.2
```
*Expected: Passes all checks (evidence completeness, zero simulation contamination, provider identity integrity, repeat protocol, checksum verification).*

### Step 5: Verify Offline Replay
```bash
geo-scope benchmark replay \
  --dataset benchmark/releases/global-ai-answers-2026.2-pilot \
  --out-dir output/audit_replay
```
*Expected: Deterministically re-extracts entity observations with zero network calls.*
