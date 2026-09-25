# GEO-Scope Research Methods & Protocol

**Methodological Foundation**: [Measurement Contract v1](measurement-contract-v1.md)  
**Schema Specification**: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)  
**Integrity Gate**: [Scientific Measurement Gate](SCIENTIFIC_MEASUREMENT_GATE.md)  

---

## 1. Measurement Philosophy

The fundamental philosophy of GEO-Scope research is grounded in empirical falsifiability, cryptographic auditability, and epistemic modesty:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GEO-SCOPE RESEARCH PHILOSOPHY                         │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. Empirical Observation             │ We measure what models actually      │
│                                      │ generate, not what they "should" rank│
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 2. Epistemic Modesty                 │ No claims of universal ground truth; │
│                                      │ metrics are bounded by configuration │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 3. Cryptographic Provenance          │ Every number is traceable to raw     │
│                                      │ JSON payloads and SHA-256 checksums  │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 4. Deterministic Replay              │ Offline recomputation bit-for-bit    │
│                                      │ with zero network dependency         │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### The Measurement Axiom
> **"AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."**

AI search outputs are probabilistic distributions conditioned on prompt wording, temperature, geographic egress, retrieval grounding, and model versions. Research conducted under GEO-Scope rejects single "universal visibility scores" and instead reports bounded statistical estimates with 95% non-parametric bootstrap confidence intervals.

---

## 2. The Observation Unit

In GEO-Scope research, the fundamental atomic unit of measurement is the **Discrete Model Observation Record**:

$$\mathbf{Obs} = \langle p_i, E_j, P_k, M_m, t, \mathbf{y}, \mathbf{c}, r, \mathbf{h} \rangle$$

Where:
- $p_i \in \mathcal{P}$: Unique evaluated prompt from declared prompt universe $\mathcal{P}$.
- $E_j \in \mathcal{E}$: Target entity from verified entity dictionary $\mathcal{E}$.
- $P_k$: Evaluating provider (e.g., `openai`, `perplexity`, `gemini`, `claude`).
- $M_m$: Evaluating model snapshot and version (e.g., `gpt-4o`, `sonar-pro`).
- $t$: UTC observation timestamp.
- $\mathbf{y} \in \{0, 1\}$: Response-level binary mention indicator.
- $\mathbf{c} = \langle \text{TDC}, \text{TUC}, \text{3PC} \rangle$: 4-way citation attribution vector.
- $r \in \mathbb{N} \cup \{\text{null}\}$: Extracted rank position (strictly from numbered lists).
- $\mathbf{h}$: SHA-256 hash of the complete verbatim response payload.

### Binary Response-Level Rule
If entity $E_j$ is mentioned $k$ times ($k \ge 1$) within a single generated response, it is recorded as:
$$\text{Mention}(E_j, \text{Response}) = 1$$
Multiple mentions in a single answer do **not** artificially inflate response-level mention counts.

---

## 3. Sampling Assumptions & Prompt Stratification

Every GEO-Scope benchmark study must operate over a declared and stratified **Prompt Universe**:

```json
"prompt_universe": {
  "prompt_set_id": "geo-seo-digital-agency-iran-2026.1",
  "prompt_count": 100,
  "prompt_source": "Observed user search query distribution",
  "prompt_generation_method": "hybrid_stratified",
  "language": "fa",
  "country_or_market": "IR",
  "intent_distribution": {
    "recommendation": 0.50,
    "informational": 0.30,
    "navigational": 0.15,
    "comparison": 0.05
  },
  "collection_date": "2026-09-23T14:55:00Z"
}
```

### Stratification Taxonomies
1. **Commercial / Recommendation Direct**: Queries seeking top vendors or service selections (e.g., *"Best SEO agency in Tehran"*).
2. **Comparative (Head-to-Head)**: Tradeoff queries evaluating two or more entities (e.g., *"Brand A vs Brand B"*).
3. **Alternative & Migration**: Queries exploring replacements (e.g., *"Alternatives to Tool X"*).
4. **Informational & Technical**: Factual, how-to, or educational queries (e.g., *"What is schema markup?"*).
5. **Navigational**: Brand portal, login, or official asset queries.

### Prompt Policy
- **Neutral Policy (Default)**: Prompts are passed to models without steering, leading instructions, or forced formatting.
- **Forced List Policy**: Used only when studying ranking sensitivity; explicitly declared in prompt metadata (`prompt_policy: "forced_list"`).

---

## 4. Comparability Rules & Validation

Two distinct benchmark studies or temporal runs are **directly comparable** if and only if all five critical dimensions align:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FIVE-DIMENSION COMPARABILITY CHECK                     │
├─────────────────────────┬───────────────────────────────────────────────────┤
│ Dimension               │ Parity Requirement for Direct Comparison          │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ 1. Prompt Universe      │ Identical prompt set ID or matched strata counts  │
│ 2. Market & Language    │ Matching ISO country code and language code       │
│ 3. Provider & Model     │ Identical model family and search-grounding state │
│ 4. Measurement Standard │ Both conforming to Measurement Contract v1.0      │
│ 5. Observation Window   │ Synchronized execution window or declared gap     │
└─────────────────────────┴───────────────────────────────────────────────────┘
```

When any dimension diverges, the study must machine-readably output:
```json
"comparability": {
  "comparable": false,
  "mismatch_reasons": [
    "Prompt universe mismatch: N=100 vs N=500",
    "Search grounding state mismatch: active vs inactive"
  ]
}
```

---

## 5. The Cryptographic Evidence Chain

To ensure unassailable research credibility, GEO-Scope implements a closed-loop evidence chain:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Live Model Run  │  ───> │ raw_responses   │  ───> │ observations    │
│ API Dispatch    │       │ .jsonl (Raw)    │       │ .jsonl (Parsed) │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │                         │
                                   ▼                         ▼
                          ┌─────────────────┐       ┌─────────────────┐
                          │ checksums       │ <───  │ metrics.json    │
                          │ .sha256 (Hash)  │       │ (Bootstrap CIs) │
                          └─────────────────┘       └─────────────────┘
```

1. **Payload Capture**: Verbatim raw JSON response payloads from provider APIs (including token usage, latency, and grounding chunks) are permanently written to `raw_responses.jsonl`.
2. **Deterministic Extraction**: The open-source `ObservationParser` parses entity occurrences, 4-way citations, and list ranks without LLM-assisted subjectivity.
3. **Cryptographic Locking**: SHA-256 hashes of all artifacts are sealed into `checksums.sha256`.
4. **Zero-Network Verification**: External researchers can verify results via:
   ```bash
   geo-scope benchmark verify --dataset <release_path>
   geo-scope replay --bundle <release_path> --out-dir output/replay_audit
   ```

---

## 6. Prohibited Research Claims

All scientific publications, reports, and communications derived from GEO-Scope must adhere to strict epistemic guardrails:

* ❌ **Prohibited**: Claiming that an entity has "X% universal AI visibility".
* ❌ **Prohibited**: Claiming that GEO-Scope has "reverse-engineered proprietary AI ranking algorithms".
* ❌ **Prohibited**: Asserting causal ranking factors from observational correlation data.
* ❌ **Prohibited**: Labeling third-party tools as "inaccurate" due to differing prompt sampling or definitions.
* ✅ **Required**: Framing all numbers as: *"Under the declared prompt set and measurement configuration, we observed..."*

---

## 7. Related Standards & References

- 📄 **Measurement Contract Specification**: [docs/measurement-contract-v1.md](measurement-contract-v1.md)
- ❓ **Why Measurement Contract Exists**: [docs/WHY_MEASUREMENT_CONTRACT_EXISTS.md](WHY_MEASUREMENT_CONTRACT_EXISTS.md)
- 📄 **Research Paper Outline**: [docs/RESEARCH_PAPER_OUTLINE.md](RESEARCH_PAPER_OUTLINE.md)
- 🔬 **Benchmark Methodology**: [docs/benchmark-methodology.md](benchmark-methodology.md)
- 🛡️ **Integrity Gate**: [docs/SCIENTIFIC_MEASUREMENT_GATE.md](SCIENTIFIC_MEASUREMENT_GATE.md)
