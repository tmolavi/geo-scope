# Reproducing GEO-Scope Benchmarks

This document provides a step-by-step protocol for verifying, reproducing, and evaluating GEO-Scope benchmark releases and golden evaluation datasets.

GEO-Scope adheres to strict reproducible empirical standards: every published benchmark includes frozen raw responses (`raw_responses.jsonl`), entity definitions (`entities.json`), prompt metadata (`prompts.jsonl`), and cryptographic SHA-256 hashes (`checksums.sha256`).

---

## 1. Prerequisites & Environment Setup

### System Requirements
* Python 3.10+ (Python 3.11 or 3.12 recommended)
* Git

### Installation
```bash
# Clone the repository
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e ".[dev]"
```

---

## 2. Offline Verification & Deterministic Replay (Zero API Keys / Zero Network)

Anyone can independently verify and recalculate all metrics without calling external AI APIs or incurring costs.

### Step 2.1: Verify Cryptographic Checksums
Ensure none of the released data files have been altered or corrupted:

```bash
# Verify the full research benchmark
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# Or verify the pilot release
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot

# Or verify the golden parser dataset
geo-scope benchmark verify --dataset benchmark/golden_sets/v1
```

Expected output:
```text
✓ Checksum verification successful for all files in benchmark/releases/global-ai-answers-2026.2
```

### Step 2.2: Replay Observations & Metrics Deterministically
Re-run the entity observation parser against the frozen raw completions (`raw_responses.jsonl`) to regenerate `observations.jsonl`, `citations.jsonl`, and `metrics.json`:

```bash
geo-scope benchmark replay \
  --dataset benchmark/releases/global-ai-answers-2026.2 \
  --out-dir output/reproduced_2026_2
```

Compare `output/reproduced_2026_2/metrics.json` against `benchmark/releases/global-ai-answers-2026.2/metrics.json` to verify that parsed metrics match.

---

## 3. Golden Parser Evaluation Protocol

To benchmark and audit the parsing accuracy of GEO-Scope's entity resolution and semantic extraction engine:

```bash
geo-scope parser evaluate \
  --golden-set benchmark/golden_sets/v1 \
  --output output/parser_metrics.json
```

### Evaluated Dimensions:
1. **`mentioned`**: Entity presence in response (normalized alias matching, zero-width joiner handling, unspaced variant resolution).
2. **`recommended`**: Explicit ranking / endorsement in top recommendations.
3. **`cited`**: Grounding URL / domain hostname presence in model citations or prose.
4. **`attributed`**: Fact / quote sourcing attribution explicitly attributed to the entity in prose (separated from mere citation).
5. **`wrong_entity`**: Homonym collision rejection (e.g., rejecting historical poet *Rumi/Molavi* or *Bazaar Molavi* when tracking a tech founder).
6. **`rank`**: Accurate ordinal position extraction in structured list outputs.

---

## 4. Live Benchmark Execution Protocol (Live API Execution)

Executing a new empirical benchmark run requires live AI model API credentials.

### Provider Contract Registry (`providers.yml`)
GEO-Scope defines all active model providers and their measurement classes in [`providers.yml`](../providers.yml):
* **`answer_engine`**: Search-grounded models with dynamic web retrieval (e.g., `perplexity_sonar`, `gemini_grounding`, `chatgpt_search`).
* **`llm`**: Direct parametric completions without search retrieval (e.g., `openai_completion`, `claude_completion`, `deepseek_r1`).

### Environment Variables
Configure API keys in `.env` (copy from `.env.example`):

```bash
# Perplexity AI (Answer Engine)
PERPLEXITY_API_KEY="pplx-..."

# Google Gemini (Answer Engine / LLM)
GEMINI_API_KEY="AIzaSy..."

# OpenAI (Answer Engine / LLM)
OPENAI_API_KEY="sk-..."

# Anthropic (LLM)
ANTHROPIC_API_KEY="sk-ant-..."

# Hamzad AI Gateway (Unified Multi-Model Gateway)
HAMZAD_API_URL="https://api.hamzad.ai/v1"
HAMZAD_API_KEY="hz-..."
```

### Running a Live Benchmark
```bash
geo-scope measure \
  --prompts benchmark/releases/global-ai-answers-2026.2/prompts.jsonl \
  --entities benchmark/releases/global-ai-answers-2026.2/entities.json \
  --providers perplexity_sonar,gemini_grounding,openai_completion \
  --mode live \
  --repeats 5 \
  --out-dir output/live_benchmark_run
```

> [!IMPORTANT]
> **Repeat Protocol**: Empirical benchmark releases require `repeat_count >= 5` per prompt to account for probabilistic output variance across temperature settings.

### Cost & Runtime Estimation (Example for 500 Prompts × 3 Providers × 5 Repeats = 7,500 Invocations):
* **Execution Time**: ~45-90 minutes (with rate-limiting and concurrency of 5 workers).
* **Estimated API Cost**: ~$15.00 - $35.00 USD (depending on token length and web search grounding costs).

---

## 5. Benchmark Dataset Integrity Validation

Before publishing any benchmark release, validate it against the strict scientific measurement gate:

```bash
geo-scope benchmark validate-dataset --dataset output/live_benchmark_run
```

The validator enforces 8 critical integrity checks:
1. **Manifest Integrity**: Complete schema metadata with dataset version.
2. **File Completeness**: Presence of all 10 required artifacts (`manifest.json`, `prompts.jsonl`, `entities.json`, `raw_responses.jsonl`, `observations.jsonl`, `citations.jsonl`, `metrics.json`, `errors.jsonl`, `methodology.md`, `checksums.sha256`).
3. **Live / Simulation Isolation**: Zero simulated or synthetic responses in empirical releases.
4. **Prompt Neutrality Gate**: Rejection of loaded leading prompts in comparative intent categories.
5. **Observation Denominator Integrity**: Calculation of mention and recommendation rates over total attempted queries, including provider errors.
6. **Provider Class Separation**: Explicit tagging of `answer_engine` vs `llm`.
7. **Negative Homonym Validation**: Verification of homonym collision rules.
8. **Repeat Protocol Integrity**: Verification of `repeat_count >= 5` across prompt sets.

---

## 6. Audit & Evidence Trails

All raw payload responses are preserved in `raw_responses.jsonl`. Each payload contains:
* `id`: Unique completion ID.
* `prompt_id`: ID of the corresponding prompt.
* `provider`: Model adapter identifier.
* `provider_class`: `answer_engine` or `llm`.
* `execution_time_ms`: Exact API latency.
* `status`: `success`, `rate_limit`, `timeout`, or `error`.
* `raw_response_text`: Verbatim response string from provider.
* `raw_citations`: Provider-returned grounding citation objects.
