# GEO-Scope Minimum Measurement Contract

**Version:** 1.0.0  
**Effective Date:** October 2026  
**Status:** Mandatory Standard for Empirical AI Visibility Measurements  
**Authority:** GEO-Scope Measurement & Integrity Architecture  
**Core Axiom:** `Mention ≠ Citation ≠ Recommendation ≠ Position ≠ Share of Model`

---

## 1. Scope and Purpose

The **GEO-Scope Minimum Measurement Contract (MMC v1.0)** defines the non-negotiable operational, statistical, and empirical standards required for collecting, analyzing, and publishing AI Visibility benchmarks and observations.

Under this contract, AI visibility is strictly treated as a **stochastic observation within an explicitly declared, reproducible measurement system**, never as an absolute or deterministic universal search ranking.

Any benchmark or measurement claiming compliance with GEO-Scope must satisfy every gate, schema requirement, repetition threshold, and denominator accounting rule set forth in this document.

---

## 2. Fixed, Versioned Prompt Universe

Every empirical benchmark must operate over an explicitly defined, immutable, and versioned prompt panel. Ad-hoc, ephemeral, or unversioned prompts cannot be used for reproducible visibility benchmarking.

### 2.1 Prompt Record Specification

Each prompt record in the benchmark universe must comply with the following schema:

```json
{
  "prompt_id": "prom-fa-comm-001",
  "prompt_version": "1.0",
  "text": "بهترین آژانس سئو برای کسب‌وکارهای تجارت الکترونیک در ایران کدام است؟",
  "language": "fa",
  "locale": "fa-IR",
  "market": "IR",
  "intent": "best_recommendation",
  "persona": "b2b_buyer",
  "funnel_stage": "consideration",
  "brand_named": false,
  "zero_prompt": true,
  "source": "research_generated",
  "created_at": "2026-10-12T00:00:00Z",
  "updated_at": "2026-10-12T00:00:00Z"
}
```

### 2.2 Field Definitions & Constraints

- `prompt_id` *(string, required)*: Stable identifier unique within the benchmark universe.
- `prompt_version` *(string, required)*: Semantic version of the prompt phrasing. Any modification to text, phrasing, or punctuation requires a version increment (e.g. `1.0` $\rightarrow$ `1.1`).
- `text` *(string, required)*: The verbatim prompt submitted to target AI engines.
- `language` *(string, required)*: ISO 639-1 two-letter code (`fa`, `tr`, `en`, `ar`, `az`).
- `locale` *(string, required)*: BCP-47 locale tag (`fa-IR`, `tr-TR`, `en-US`, `ar-SA`, `az-AZ`).
- `market` *(string, required)*: ISO 3166-1 alpha-2 market code (`IR`, `TR`, `US`, `SA`, `AZ`).
- `intent` *(string, required)*: Must be one of four commercial intent classes:
  - `best_recommendation`: Seeks recommendations or top vendor lists.
  - `comparison`: Compares two or more approaches, categories, or vendors.
  - `pricing_vendor_selection`: Evaluates commercial terms, costs, or selection criteria.
  - `criteria_guidance`: Inquires about evaluation methodologies or audit checklists.
- `persona` *(string, required)*: Assumed buyer persona (`b2b_buyer`, `marketing_director`, `smb_owner`).
- `funnel_stage` *(string, required)*: `awareness`, `consideration`, `decision`.
- `brand_named` *(boolean, required)*: `true` if the prompt mentions a specific brand by name; `false` for unbranded/neutral discovery prompts.
- `zero_prompt` *(boolean, required)*: `true` if executed in a fresh, ungrounded, zero-context session without conversational history.
- `source` *(string, required)*: `observed_user_queries`, `research_generated`, `client_supplied`.

### 2.3 Time Series Version Discipline

- When a prompt text is revised, observations from the new version must **not** be aggregated into legacy time series without explicit demarcation.
- Downstream reporting must record both `prompt_id` and `prompt_version`.

---

## 3. Repetition Policy & Statistical Significance

Generative LLMs produce probabilistic responses influenced by temperature, model drift, dynamic web retrieval, and real-time reranking. Single-observation benchmarks introduce severe pseudo-determinism and are scientifically invalid for ranking claims.

### 3.1 Observation Unit

The unit of replication is defined as:
$$\text{Observation Unit} = \text{Prompt} \times \text{Engine} \times \text{Language} \times \text{Locale} \times \text{Session}$$

### 3.2 Repetition Tiers

For each observation unit, the number of independent executions ($k$) determines its measurement status:

| Runs ($k$) | Measurement Status | Interpretation & Publication Guidelines |
|:---|:---|:---|
| $k = 0$ | `not_measured` | No data collected. Must **never** be reported as 0% visibility. |
| $k = 1$ | `single_observation` | Exploratory probe only. Cannot be used for comparative or public ranking claims. |
| $2 \le k < 5$ | `directional` | Preliminary directional trend. Must include standard disclaimer: *"This result is directional and lacks sufficient sample size for definitive conclusions."* |
| $k \ge 5$ | `measured` | Statistically sufficient empirical observation. Eligible for public reporting with 95% Confidence Intervals. |
| Incomplete | `insufficient_data` | Session terminated, ratelimited, or payload corrupted. Excluded from valid denominators. |

### 3.3 Multi-Window Execution

Where feasible, repetitions should span across multiple independent time windows (e.g., peak vs. off-peak hours, or different days) to capture temporal variance in live search grounding.

---

## 4. Complete Provenance Schema

To guarantee auditability and forensic reproducibility, every single execution must record complete provenance. Silent provider rerouting or server-side fallbacks are strictly prohibited.

```json
{
  "experiment_id": "exp-2026-regional-pilot",
  "run_id": "run-f8a1290b-934c",
  "prompt_id": "prom-fa-comm-001",
  "prompt_version": "1.0",
  "requested_provider": "openai",
  "requested_model": "gpt-4o",
  "actual_provider": "openai",
  "actual_model": "gpt-4o-2024-11-20",
  "engine": "chatgpt_search",
  "surface": "chat_with_search",
  "language": "fa",
  "locale": "fa-IR",
  "market": "IR",
  "geography": "Tehran/IR",
  "execution_mode": "live",
  "grounding_enabled": true,
  "search_triggered": true,
  "authenticated_session": false,
  "timestamp": "2026-10-12T14:30:00.000Z",
  "latency_ms": 3412.5,
  "input_tokens": 128,
  "output_tokens": 512,
  "estimated_cost": 0.0041,
  "raw_response_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "parser_version": "1.0.0",
  "normalizer_version": "1.0.0",
  "measurement_contract_version": "1.0"
}
```

### 4.1 Model Verification & Fallback Integrity

- `requested_model` and `actual_model` must be recorded independently.
- If a provider silently redirects to a fallback model or fails to ground in live search, the record must be flagged as `actual_model = "not_verified"` and `fallback_used = true`.
- Records with unverified models receive a reduced confidence rating.

### 4.2 Fixture Isolation

- Test fixtures and synthetic data must be explicitly flagged with:
  ```json
  "execution_mode": "fixture",
  "eligible_for_public_benchmark": false
  ```
- Fixture data must never be committed to or aggregated into public benchmark results.

---

## 5. Raw Evidence Separation & Immutability

Raw inference data must be maintained separately from downstream parsed metrics to enable independent verification and parser re-evaluation.

### 5.1 Evidence Bundle Structure

Every benchmark run produces an immutable evidence bundle directory containing:
1. `raw_responses.jsonl`: Verbatim response text, raw citation URLs, token counts, timestamps, and model headers.
2. `observations.jsonl`: Parsed entity mentions, citation domain extractions, recommendation phrases, match types, and rule traces.
3. `manifest.json`: Cryptographic SHA-256 checksums of every file in the bundle.
4. `summary.json`: Aggregated metrics with Wilson 95% Confidence Intervals and Central Denominator Registry.

### 5.2 Cryptographic Integrity

Each observation record links directly to the `raw_response_hash` computed over the canonical UTF-8 bytes of the inference response.

---

## 6. Denominator Transparency & Missing Data Rules

- Every metric reported must state its **numerator**, **denominator**, **denominator type**, **sample size**, and **coverage**.
- Absence of measurement is strictly recorded as `not_measured`, never `0%`.
- If an entity was never observed due to provider error, it must be marked `provider_error`.

---

## 7. Compliance Verification

Benchmark runs must pass the automated gate check:
```bash
geo-scope verify-contract --run-dir benchmarks/my-run/
```
Runs failing contract checks cannot be certified as GEO-Scope Compliant.

---

*GEO-Scope Minimum Measurement Contract v1.0 — Setting the standard for scientific AI visibility measurement.*
