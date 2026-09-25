# GEO-Scope Scientific Foundation v1.0

**Standard Specification**: [Measurement Contract v1](measurement-contract-v1.md)  
**Schema Definition**: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)  
**Research Methods**: [docs/RESEARCH_METHODS.md](RESEARCH_METHODS.md)  
**Releases Timeline**: [docs/RELEASES.md](RELEASES.md)  
**Author**: [Taqi Molavi](https://molavi.pro)  

---

## 1. Purpose

**GEO-Scope** provides an open-source, empirical measurement framework for observing and quantifying how entities, brands, and sources surface within Generative AI completions and search-grounded answer engines.

The purpose of this scientific foundation is to establish a rigorous, reproducible, and verifiable methodology for Generative Engine Optimization (GEO) and AI answer visibility research. Rather than relying on ungrounded commercial visibility metrics, proprietary scoring algorithms, or simulated ranking models, GEO-Scope grounds all analysis in **verifiable empirical observations**, **explicit machine-readable contracts**, and **zero-network cryptographic auditability**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEO-SCOPE SCIENTIFIC FOUNDATION ARCHITECTURE             │
├────────────────────────┬──────────────────────────┬─────────────────────────┤
│  1. FORMAL CONTRACT    │   2. EVIDENCE CHAIN      │  3. EMPIRICAL REPLAY    │
│  Declarative JSON      │   Immutable raw payloads │  Bit-for-bit offline    │
│  schemas & axioms      │   & SHA-256 checksums    │  recomputation & eval   │
└────────────────────────┴──────────────────────────┴─────────────────────────┘
```

---

## 2. Methodological Components

The GEO-Scope scientific foundation consists of five core methodological pillars:

### 2.1 Measurement Contract v1
The [Measurement Contract v1](measurement-contract-v1.md) (`schemas/measurement-contract-v1.json`) is the declarative specification governing all visibility measurements:
- **Response-Level Binary Mentions**: An entity is recorded as mentioned ($\mathbf{y} = 1$) if it appears $\ge 1$ times in the generated response text. Multiple mentions in a single completion do not artificially inflate response-level mention counts.
- **Strict 4-Way Citation Separation**: Disentangles lexical mentions from grounding citations:
  - `entity_mentioned`: Lexical presence in generated completion.
  - `target_domain_cited`: Root domain present in provider grounding/citations.
  - `target_url_cited`: Specific URL / deep link cited.
  - `third_party_source_cited`: External third-party authority domain cited.
- **Recommendation Gating**: Strict semantic validation ensuring that an entity is only flagged as `recommended` when the model explicitly endorses, selects, or recommends it in response to a recommendation intent query (`mentioned != recommended`).
- **Structured Rank Extraction**: Rank ($r \in \mathbb{N}$) is extracted strictly from valid ordered/numbered lists. Informational mentions receive `rank: null` to avoid artificial rank distortion.
- **Denominator & Failure Accounting**: Explicit reporting of $N_{\text{attempted}}$, $N_{\text{successful}}$, and $N_{\text{failed}}$, ensuring timeouts and API errors are transparently accounted for in all metrics.
- **Machine-Readable Comparability**: Automated parity verification across prompt universes, markets, languages, model families, and observation windows before datasets can be directly compared.

### 2.2 The Evidence Pipeline
GEO-Scope enforces complete cryptographic provenance for every reported data point:
- **Verbatim Raw Payload Capture**: Full, unmodified JSON responses from model APIs—including token usage, latency, and grounding chunks—are permanently stored in `raw_responses.jsonl`.
- **Zero Silent Fallback**: Live runs enforce exact provider and model execution (`requested_provider == actual_provider`). If a provider endpoint fails or returns a degraded response, the error is recorded honestly rather than silently routed to a surrogate model.
- **Cryptographic Hashing**: Every observation record references the SHA-256 hash of the complete verbatim response payload (`response_hash_sha256`), and all release files are sealed in `checksums.sha256`.

### 2.3 Entity Resolution & Multilingual Normalization
Accurate observation in generative completions requires resilient NLP normalization:
- **Unicode NFKC Normalization**: Consistent character representation across all scripts.
- **Perso-Arabic Script Unification**: Handles Persian/Arabic character variants (e.g., `ک`/`ك`, `ی`/`ي`) and Zero-Width Non-Joiner (ZWNJ / `\u200c`) segmentation.
- **Canonical Alias Resolution**: Matches brand names, authorized domain stems, and founder names to a unified entity dictionary.
- **Negative Homonym & Collision Filtering**: Disambiguates common nouns, dictionary words, and unrelated entities to eliminate false-positive mentions.

### 2.4 Golden Parser Evaluation
The deterministic parser (`ObservationParser`) is continuously evaluated against human-annotated ground truth datasets without relying on subjective LLM-as-a-judge evaluators:
- **Multi-Lingual Golden Dataset (`v1`)**: 220 human-labeled examples across 5 languages (English, Persian, Turkish, Azerbaijani, Arabic).
- **Verified Benchmark Performance**:
  - **Mention F1**: `99.75%` (Precision: 99.51%, Recall: 100.00%)
  - **Recommendation F1**: `100.00%` (Precision: 100.00%, Recall: 100.00%)
  - **Citation F1**: `100.00%` (Precision: 100.00%, Recall: 100.00%)
  - **Attribution F1**: `91.56%` (Precision: 100.00%, Recall: 84.44%)
  - **Homonym Disambiguation F1**: `96.97%`
  - **Rank Accuracy**: `100.00%`

### 2.5 Reproducible Benchmark Releases
All benchmark releases (`benchmark/releases/`) are published as immutable, self-contained bundles containing:
1. `manifest.json`: Execution metadata, provider configurations, and `measurement_contract_version: "1.0"`.
2. `prompts.jsonl`: Neutral, stratified prompt universe.
3. `raw_responses.jsonl`: Raw API responses with cryptographic hashes.
4. `observations.jsonl`: Extracted granular observations.
5. `metrics.json`: Aggregated metrics with bootstrap confidence intervals.
6. `checksums.sha256`: SHA-256 integrity manifest.

---

## 3. Scientific Boundaries

To preserve academic integrity and prevent misleading commercial claims, GEO-Scope explicitly defines what it does and does **not** claim:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GEO-SCOPE SCIENTIFIC BOUNDARIES                       │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ ❌ NO Universal Truth Claim          │ AI visibility is an observation under │
│                                      │ a declared configuration, not truth. │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ ❌ NO Causal Ranking Claims          │ Observed correlations do not prove   │
│                                      │ internal algorithmic ranking factors.│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ ❌ NO Reverse Engineering            │ External completions do not reveal   │
│                                      │ private model weights or algorithms. │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

1. **No Universal AI Visibility Truth Claim**:
   - Generative AI outputs are non-deterministic, probabilistic completions conditioned on temperature, prompt phrasing, search-grounding freshness, and geographical egress.
   - GEO-Scope never claims an entity has an absolute "universal visibility score." All reported figures must be stated as: *"Under prompt universe $\mathcal{P}$ and configuration $\mathcal{C}$ at timestamp $t$, the observed metric was $X \pm \delta$."*
2. **No Causal Ranking Claims**:
   - GEO-Scope measures observational outputs. It does not claim that specific on-page optimizations, schema markup, or link profiles *cause* higher AI ranking.
   - Descriptive statistical association must not be conflated with algorithmic causality.
3. **No Proprietary Model Reverse Engineering**:
   - GEO-Scope treats generative models as black-box probabilistic generators. It does not claim to inspect internal attention mechanisms, proprietary RAG rerankers, or hidden training corpora.

---

## 4. Reproduction Path

External researchers and auditors can independently reproduce, audit, and verify any GEO-Scope benchmark release using the following 5-step protocol:

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                           REPRODUCTION PROTOCOL                         │
  │                                                                         │
  │  Step 1: Understand Contract ──> Step 2: Inspect Benchmark Metadata     │
  │                                                  │                      │
  │  Step 5: Evaluate Parser    <── Step 4: Replay  <── Step 3: Verify      │
  │          Against Golden Set             Offline             Checksums   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Understand the Measurement Contract
Review the formal JSON schema and operational definitions:
- Specification: [`docs/measurement-contract-v1.md`](measurement-contract-v1.md)
- JSON Schema: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)
- Why Contract Exists: [`docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md`](WHY_MEASUREMENT_CONTRACT_EXISTS.md)

### Step 2: Inspect Benchmark Metadata
Inspect the target benchmark release manifest (`manifest.json`):
```bash
cat benchmark/releases/global-ai-answers-2026.2/manifest.json | jq .
```
Verify declared prompt counts, intent stratification, market coverage, and provider configurations.

### Step 3: Verify Cryptographic Checksums
Confirm that all raw response files and dataset assets are bit-for-bit intact and uncorrupted:
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
```
Or verify directly via standard Unix utilities:
```bash
cd benchmark/releases/global-ai-answers-2026.2 && sha256sum -c checksums.sha256
```

### Step 4: Replay Observations Offline (Zero-Network Recomputation)
Recompute all observations, citations, mentions, and summary metrics directly from preserved `raw_responses.jsonl` without executing live API calls:
```bash
geo-scope replay \
  --bundle benchmark/releases/global-ai-answers-2026.2 \
  --out-dir output/audit_replay_2026_2
```
Compare the newly generated `metrics.json` against the published release `metrics.json` to confirm 100% deterministic reproducibility.

### Step 5: Evaluate Parser Against the Golden Dataset
Validate the deterministic parser's precision, recall, and F1 performance against human ground truth:
```bash
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

---

## 5. Related Documentation & Scientific Assets

- 📄 **Research Methods & Protocol**: [`docs/RESEARCH_METHODS.md`](RESEARCH_METHODS.md)
- 📄 **Research Paper Outline**: [`docs/RESEARCH_PAPER_OUTLINE.md`](RESEARCH_PAPER_OUTLINE.md)
- 📊 **Releases Timeline & Benchmark Catalog**: [`docs/RELEASES.md`](RELEASES.md)
- 🔬 **Scientific Benchmark Methodology**: [`docs/benchmark-methodology.md`](benchmark-methodology.md)
- 📊 **Methodology Crosswalk**: [`docs/METHODOLOGY_CROSSWALK.md`](METHODOLOGY_CROSSWALK.md)
- 🛡️ **Scientific Measurement Gate**: [`docs/SCIENTIFIC_MEASUREMENT_GATE.md`](SCIENTIFIC_MEASUREMENT_GATE.md)
- 🔒 **Security Audit Report**: [`docs/SECURITY_AUDIT.md`](SECURITY_AUDIT.md)
