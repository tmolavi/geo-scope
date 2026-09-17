# GEO-Scope Public Benchmark & Evidence Dataset Methodology v1

## 1. Executive Summary & Epistemic Positioning
GEO-Scope provides a standardized, reproducible public benchmark framework for measuring generative AI search visibility, Share of Model (SoM), top-recommendation positioning, and citation provenance.

### Core Epistemic Commitments:
1. **Empirical Measurement over Algorithmic Speculation**: LLMs and generative search engines are complex, probabilistic systems. GEO-Scope does **not** claim to "reverse-engineer proprietary AI ranking algorithms." Instead, it conducts controlled empirical experiments and reports observed statistical associations.
2. **Deterministic Reproducibility**: All benchmark datasets are versioned, SHA-256 hashed, and include raw JSONL observation records enabling any researcher to verify and recompute metrics bit-for-bit.
3. **Rigorous Uncertainty Bounds**: All visibility rates (Mention Rate, Top-1 Rate, Share of Model) are reported alongside **95% non-parametric bootstrap confidence intervals**.
4. **Strict Live vs. Synthetic Separation**: Synthetic / simulated evaluations are permanently tagged with `execution_mode: "synthetic"` and `research_status: "demo_only"`. Only experiments executed against real live provider APIs with verifiable provenance receive `research_status: "peer_review_ready"` or `"published"`.

---

## 2. Dataset Architecture & File Taxonomy

Every versioned benchmark release resides under `benchmark/<dataset_id>/` and follows this schema:

| File | Format | Description |
|------|--------|-------------|
| `manifest.json` | JSON | Dataset metadata, git commit, parser version, sample counts, and SHA-256 hashes. |
| `prompts.jsonl` | JSONL | Stratified evaluation queries with intent labels and entity parameters. |
| `brands.json` | JSON | Evaluated target brands and competitor entities with verified domains. |
| `providers.json` | JSON | Target LLM engines and search providers (ChatGPT, Perplexity, Gemini, Claude). |
| `observations.jsonl` | JSONL | Raw model responses, parsed mention ranks, sentiment, latency, and status. |
| `citations.jsonl` | JSONL | Extracted citation URLs, source domains, and attribution anchors. |
| `metrics.json` | JSON | Computed benchmark metrics with point estimates and 95% bootstrap CIs. |
| `methodology.md` | Markdown | Experiment methodology specification for the dataset release. |
| `README.md` | Markdown | Dataset introduction and quickstart reproduction instructions. |
| `checksums.sha256` | Text | Standard SHA-256 checksums file for cryptographic verification. |

---

## 3. Sampling & Prompt Stratification

To prevent domain bias and benchmark hacking, prompts are stratified across five distinct search intent categories:

1. **Commercial Direct**: High-intent buyer queries seeking top tools or category recommendations (e.g., *"Best CRM software for B2B startups"*).
2. **Comparative (Head-to-Head)**: Direct comparison queries evaluating feature tradeoffs (e.g., *"HubSpot vs Salesforce pricing and ease of use"*).
3. **Alternative & Migration**: Replacement and transition queries (e.g., *"Top alternatives to Salesforce with lower cost"*).
4. **Feature & Technical Capability**: Functional queries testing specific feature support (e.g., *"Which CRM has the best native email automation?"*).
5. **Pricing & ROI**: Commercial evaluations focused on budget, tiers, and hidden fees (e.g., *"HubSpot pricing breakdown for small teams"*).

---

## 4. Metric Definitions & Mathematical Formulation

### 4.1 Mention Rate ($R_{	ext{mention}}$)
The proportion of successful multi-model observations in which the brand was explicitly identified:
$$R_{	ext{mention}} = rac{\sum_{i=1}^{N_{	ext{success}}} \mathbb{I}(	ext{brand} \in 	ext{Observation}_i)}{N_{	ext{success}}}$$

*Semantics Rule*: If $N_{	ext{success}} = 0$, $R_{	ext{mention}} = 	ext{null}$ (`status: "insufficient_data"`).

### 4.2 Top-1 Primary Recommendation Rate ($R_{	ext{top1}}$)
The proportion of successful multi-model observations where the brand was ranked as the primary (#1) recommended option:
$$R_{	ext{top1}} = rac{\sum_{i=1}^{N_{	ext{success}}} \mathbb{I}(	ext{Rank}(	ext{brand}) = 1)}{N_{	ext{success}}}$$

### 4.3 Share of Model / Share of Voice ($	ext{SoM}$)
The share of total brand mentions across all evaluated competitors captured by the target brand:
$$	ext{SoM} = rac{M_{	ext{target}}}{\sum_{b \in 	ext{Brands}} M_b} 	imes 100\%$$

### 4.4 Citation Rate ($R_{	ext{citation}}$)
The percentage of observations where the brand's primary domain or direct authoritative coverage was cited as a grounded source.

### 4.5 95% Bootstrap Confidence Intervals
Confidence intervals are estimated via non-parametric percentile bootstrap:
1. Resample $N_{	ext{success}}$ observations with replacement $B = 1,000$ times.
2. Compute the mean metric $\hat{	heta}^{*b}$ for each replicate $b \in [1, B]$.
3. Set $	ext{CI}_{95} = [\hat{	heta}^{*}_{(0.025)}, \hat{	heta}^{*}_{(0.975)}]$.

---

## 5. Statistical Factor Analysis Guardrails

When analyzing factors correlating with high generative visibility:
- Terminology must strictly use **"Observed association"** or **"Empirical correlation"**.
- Causal terms like "ranking factor", "algorithm weight", or "guaranteed booster" are forbidden.
- Analyses must report Spearman rank correlation ($r_s$), 95% confidence intervals, Cohen's $d$ effect sizes, and sample sizes.

---

---

## 6. Dual Benchmark Modes & Model Provenance

When evaluating AI search engines through gateways or multi-provider routes, underlying routing layers may employ fallback models (e.g. proxying an unavailable upstream model to an open-weights fallback). To guarantee scientific integrity and complete transparency without hiding operational realities, GEO-Scope implements **Dual Benchmark Modes**:

### 6.1 Benchmark Execution Modes

| Mode | Target Use Case | Fallback Behavior | Provenance Tagging |
|------|-----------------|-------------------|--------------------|
| **`STRICT`** | Official benchmark releases & peer-reviewed benchmarks | **Rejected**: Fallback responses are marked `status: "failed"` and `execution_class: "failed"`. Excluded from official visibility metrics. | Full provenance recorded with failure reason `fallback_detected`. |
| **`DISCOVERY`** | Operational AI visibility & ecosystem research | **Accepted**: Fallback responses are accepted (`status: "success"`, `execution_class: "fallback"`). | Full provenance recorded (`requested_provider`, `requested_model`, `actual_provider`, `actual_model`, `fallback_active`). |

### 6.2 Model Provenance Schema

Every observation record stores unambiguous provenance fields:
- `requested_provider`: The target provider identifier specified in the benchmark profile (e.g. `claude-3-5-sonnet`).
- `requested_model`: The target model requested.
- `actual_provider`: The provider that physically generated the completion (e.g. `openrouter` / `avalai`).
- `actual_model`: The exact model string returned by gateway metadata (e.g. `qwen/qwen3.8-27b`).
- `fallback_active`: Boolean flag indicating whether gateway fallback routing occurred.
- `execution_class`: One of `"native"`, `"fallback"`, or `"failed"`.

### 6.3 Metric Stratification

Benchmark metrics in GEO-Scope are stratified into distinct tiers:
1. **`native_visibility`**: Computed exclusively over observations where `execution_class == "native"`. Guarantees zero fallback contamination.
2. **`fallback_visibility`**: Computed exclusively over observations where `execution_class == "fallback"`. Measures fallback route behavior.
3. **`total_observed_visibility`**: Blended visibility across all successful responses (`native` + `fallback`).
4. **`execution_class_breakdown`**: Counts of `native`, `fallback`, and `failed` observations with proportions.

### 6.4 Research Report Structure

Automated benchmark reports explicitly segment findings into:
- **Native Model Results**: Primary verified benchmark scores.
- **Fallback Routed Results**: Transparent disclosure of gateway fallback behaviors, explicitly attributing outputs to the `actual_model`.

---

---

## 7. Question Source Layer & Demand Provenance (AnswerPath GEO)

To eliminate benchmark prompt fabrication and prevent synthetic exploration queries from being misattributed to real consumer search demand, GEO-Scope integrates **AnswerPath GEO** as its question discovery layer.

### 7.1 Separation of Responsibilities

- **AnswerPath GEO**: Discovers raw user questions from owned chat logs, CRM exports, and search logs; classifies intent (`learn`, `compare`, `buy`, `trust`, `solve`); clusters semantic duplicates; and synthesizes structured exploration templates.
- **GEO-Scope**: Ingests prompts, executes multi-provider LLM evaluations, extracts entities and citations, records model execution provenance, and computes stratified visibility metrics.

### 7.2 Question Provenance Schema

Every evaluation prompt is tagged with origin provenance:
```json
{
  "prompt_id": "PRM-001",
  "question": "best GEO agency in Iran",
  "source_type": "observed",
  "source_reference": "answerpath:observed",
  "intent": "commercial",
  "category": "GEO",
  "entities": ["Target Brand"],
  "confidence": 0.95
}
```

### 7.3 Demand Stratification in Reports & Metrics

Research reports and computed `metrics.json` strictly segment:
1. **Observed Question Results**: Performance on genuine recorded user queries.
2. **Generated Research Prompt Results**: Performance on exploratory research templates.
3. **Combined Operational Visibility**: Blended multi-query index.

---

## 8. Verification & Reproduction Protocol

Any published GEO-Scope benchmark can be verified locally:
```bash
# 1. Discover user questions and candidate prompt clusters
geo-scope prompts discover "GEO Agency" --out results/prompts-pool

# 2. Prepare a versioned benchmark dataset with separated observed and generated prompts
geo-scope benchmark prepare --topic "GEO Agency" --brand "My Brand" --out benchmark

# 3. Check live provider routing & fallback integrity
geo-scope benchmark providers-check --profile benchmark/profiles/geo-scope-live-2026.1.yaml

# 4. Run benchmark in discovery or strict mode
geo-scope benchmark run --profile benchmark/profiles/geo-scope-live-2026.1.yaml --mode discovery
geo-scope benchmark run --profile benchmark/profiles/geo-scope-live-2026.1.yaml --mode strict

# 5. Cryptographic file integrity verification
geo-scope benchmark verify --dataset benchmark/geo-scope-benchmark-2026.1

# 6. Metric reproduction and bootstrap recalculation
geo-scope benchmark reproduce --dataset benchmark/geo-scope-benchmark-2026.1
```
