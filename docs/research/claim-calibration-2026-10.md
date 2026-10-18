# GEO-Scope Scientific Claim Calibration & Evidence Audit (October 2026)

**Document Identifier:** `GEO-SCOPE-CAL-2026-10`  
**Scope:** Repository-wide scientific claim audit, citation provenance re-verification, and claim calibration for Release 2026.1  
**Status:** Canonical Scientific Integrity Baseline  
**Auditor:** GEO-Scope Research & Scientific Integrity Group  

---

## 1. Executive Summary & Objective

In accordance with the GEO-Scope Scientific Measurement Gate and the prime axiom:
$$\text{Mention} \neq \text{Citation} \neq \text{Recommendation} \neq \text{Position} \neq \text{Share of Model}$$
this audit systematically reviews the empirical dataset of **Benchmark 2026.1** (`benchmarks/regional-commercial-intent-2026.1/`), evaluates all public claims against raw stored evidence, and re-calibrates language to prevent academic overclaiming, statistical inflation, and misleading commercial assurances.

---

## 2. Empirical Verification of Benchmark 2026.1

Every assertion published in the 2026.1 release was checked directly against `prompts.jsonl`, `raw_responses.jsonl`, `observations.jsonl`, and `summary.json`.

| Dimension | Reported Claim | Verified Raw Reality | Status & Calibration |
| :--- | :--- | :--- | :--- |
| **Unique Prompts** | 24 unique commercial prompts | Exactly 24 unique prompt records across `fa-IR` (12) and `tr-TR` (12). | **VERIFIED** |
| **Intent Groups** | 4 commercial intent groups | 3 prompts $\times$ 4 intents $\times$ 2 markets = 24 prompts. | **VERIFIED** |
| **Live Completions** | 144 live completions | Exactly 144 completions in `raw_responses.jsonl` ($24 \times 3 \text{ engines} \times 2 \text{ runs}$). | **VERIFIED** |
| **Error Rate** | 0.0% execution errors | 0 network timeouts, 0 HTTP 5xx, 0 synthetic fallbacks in `raw_responses.jsonl`. | **VERIFIED** (Execution error rate, not factual accuracy) |
| **Manual QA Sample** | 20 records (10 IR, 10 TR) | 20 stratified records manually verified for entity parsing accuracy. | **VERIFIED** (Sample $n=20$ for extraction accuracy) |
| **Reported Citations** | "2,291 verified URLs" | **2,291 citation occurrences**, NOT 2,291 unique URLs. | **DISCREPANCY CALIBRATED** |
| **Unique Citation URLs** | Conflated with total citations | Exactly **1,013 unique URL strings** in `raw_responses.jsonl`. | **DISCREPANCY CALIBRATED** |
| **Intermediary Redirects** | Unreported in original summary | **944 of 2,291 occurrences (41.2%)** are Google Cloud redirect URLs (`vertexaisearch.cloud.google.com`). | **DISCREPANCY CALIBRATED** |
| **True Direct Domains** | Over-reported domain count | Top domain reported was `vertexaisearch.cloud.google.com` (460 IR + 484 TR = 944), which is an API gateway proxy, not an organic content domain. | **DISCREPANCY CALIBRATED** |

---

## 3. Discrepancy Breakdown & Calibration Rules

### 3.1 Total Citation Occurrences vs. Unique URLs vs. Intermediary Tokens

- **Audit Finding:** The headline metric in `README.md` and `benchmarks/regional-commercial-intent-2026.1/README.md` stated:
  > *"Verified Citations: 2,291 URLs"*
- **Evidence Verification:**
  - Total citation tokens extracted: **2,291**.
  - Total unique URL strings: **1,013**.
  - Citations from Google Gemini Grounding (`gemini-2.5-flash`): **944**.
  - All 944 Gemini citations point to the intermediary proxy domain:
    `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`
  - When Gemini grounding returns search citations, it provides signed redirect tokens rather than direct destination domain URLs.
  - Treating `vertexaisearch.cloud.google.com` as the "#1 Top Cited Domain" (as done in `summary.json`) is methodologically invalid because Vertex AI Search is an intermediary infrastructure endpoint, not a third-party citation source.
- **Calibration Rule:**
  - Distinctly report:
    1. **Total Citation Occurrences:** 2,291
    2. **Unique URLs Encountered:** 1,013
    3. **Intermediary Grounding Redirects:** 944 (`vertexaisearch.cloud.google.com`)
    4. **Direct Organic Publisher Domains:** Top domains among direct search engines are `agencies.semrush.com` (24), `iranweblife.com` (21), `frac.tl` (20), `edvido.com` (16), `pr.net.tr` (16).

---

### 3.2 Extraction Accuracy vs. Factual Accuracy

- **Audit Finding:** The release documentation reported:
  > *"Manual QA Audit Accuracy: 100.0%"*
- **Evidence Verification:**
  - The manual QA protocol audited whether `ObservationParser` correctly identified brand mentions, entity boundaries, and negative homonyms from the model's textual completion.
  - The parser correctly extracted the 20 audited cases (100% extraction accuracy on $n=20$).
  - However, this does **NOT** mean the LLM's statements or recommendations were factually accurate, up-to-date, or verified against corporate registries.
- **Calibration Rule:**
  - Explicitly label this metric as **Parser Extraction Fidelity ($n=20$)**, not "Benchmark Accuracy" or "Factual Accuracy".
  - Add explicit disclaimer: *"Extraction accuracy measures parser reliability against raw LLM text; it does not validate the truth, objectivity, or market validity of the LLM's claims."*

---

### 3.3 Execution Errors vs. Factual Errors

- **Audit Finding:** The documentation reported:
  > *"Error Rate: 0.0% (0 errors)"*
- **Evidence Verification:**
  - This metric reflected framework transport execution: zero HTTP failures, zero timeout drops, and zero provider adapter crashes across 144 API calls.
  - It did not measure model reasoning errors, hallucinations, outdated information, or omission of major commercial players.
- **Calibration Rule:**
  - Explicitly label this metric as **Transport & API Execution Error Rate: 0.0% (0/144 calls failed)**.

---

### 3.4 Calibration of Unsupported Public Superlatives

The following uncalibrated claims have been audited and replaced across all public documentation:

| Uncalibrated Phrase | Scientific Vulnerability | Calibrated Replacement |
| :--- | :--- | :--- |
| **"First comprehensive benchmark"** | Sample size of 24 prompts across 2 countries is an exploratory pilot, not an exhaustive national census. | **"Exploratory Regional Commercial AI Visibility Pilot"** |
| **"Gold standard for GEO research"** | Self-awarded superlatives violate scientific objectivity and peer-review ethics. | **"Standardized, Evidence-Backed Open Pilot Protocol"** |
| **"100% verified URLs"** | 944 citations are opaque Google Vertex redirect tokens whose final destination status codes were not crawled live. | **"100% Search-Grounded Citation Records (1,013 Unique URLs, 944 Intermediary Redirects)"** |
| **"Zero hallucinations"** | Search-grounded models can and do generate hallucinated syntheses from web snippets. GEO-Scope measured framework execution, not semantic truth. | **"Zero Synthetic Framework Fallbacks (100% Live Grounded Completions)"** |
| **"100% accuracy"** | Small audit sample ($n=20$) for extraction regex, easily misinterpreted as 100% predictive truth. | **"100% Parser Extraction Fidelity on Audited Stratified Sample ($n=20$)"** |

---

## 4. Preservation of Core Research Assets

The following core assets are confirmed untouched and preserved:
1. **Raw Evidence:** `raw_responses.jsonl` (4.4 MB) contains exact timestamps, provider signatures, prompt texts, and completion payloads.
2. **Cryptographic Signatures:** SHA-256 hashes in `checksums.sha256` remain bit-for-bit intact.
3. **Open-Source License:** Full MIT License preserved.
4. **Interactive Demos & MCP Tooling:** Preserved and validated.
