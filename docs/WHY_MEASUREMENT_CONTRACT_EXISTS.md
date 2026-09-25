# Why the Measurement Contract Exists

**Canonical Standard:** [`docs/measurement-contract-v1.md`](measurement-contract-v1.md)  
**Schema Definition:** [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)  

---

## 1. The Core Problem: Why AI Visibility Numbers Differ

As generative AI engines (ChatGPT Search, Perplexity, Google Gemini, Claude) become primary answer engines for consumers and enterprises, various SEO and GEO platforms have introduced "AI Visibility" metrics.

However, researchers and practitioners quickly notice that **different platforms legitimately produce different visibility numbers for the exact same brand**.

This discrepancy is not necessarily a bug or measurement error. As outlined in seminal research on measurement methodology (e.g., [iPullRank on Accuracy vs. Precision](https://ipullrank.com/accuracy-vs-precision) and [Ahrefs on AI Visibility Metrics](https://help.ahrefs.com/en/articles/15501968-ai-visibility-metrics)), differences stem from five fundamental structural divergences:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHY AI VISIBILITY METRICS DIVERGE                        │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Dimension             │ Cause of Divergence                                 │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ 1. Prompt Sampling    │ Distinct query populations, strata, and wording     │
│ 2. Providers & Models │ Different model families, versions, and temperatures│
│ 3. Time Windows       │ Real-time search engine grounding cache volatility  │
│ 4. Metric Definitions │ Equating mention with recommendation or citation    │
│ 5. Denominators       │ Total queries vs. successful completions            │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

### 1. Prompt Sampling Differs
One tool evaluates 20 generic head terms (e.g., *"best CRM"*), while another evaluates 500 long-tail, localized, or comparison queries (e.g., *"CRM software with Persian RTL support for startup sales teams"*). A brand may dominate long-tail technical queries while being absent from broad generic head prompts.

### 2. Providers and Model Versions Differ
An observation on `gpt-4o` with search grounding active produces a completely different answer distribution than `claude-3-7-sonnet` without web access, or `perplexity-sonar` synthesizing real-time web citations. Even within the same provider, model snapshot versions behave differently.

### 3. Time Windows and Grounding Volatility Differ
Generative search engines query live index caches. A breaking news event, algorithmic index update, or forum discussion can alter citations within hours. Observations taken in January are not directly comparable to observations in March without temporal synchronization.

### 4. Metric Definitions Differ
- **Platform A** counts every time a brand name appears in text as a "visibility point" (even in negative or descriptive contexts).
- **Platform B** only counts top-ranked recommendations.
- **Platform C** requires a clickable grounding hyperlink citation.

### 5. Denominators & Weightings Differ
Some tools calculate percentage over total attempted queries (including rate-limited or failed API calls), while others calculate over successful responses, or apply undisclosed proprietary search-volume weighting.

---

## 2. The GEO-Scope Approach

> [!IMPORTANT]
> **Transparent Measurement > Unsupported Universal Scores**  
> GEO-Scope rejects the premise that any tool can provide a single, universal "True AI Visibility Score." Instead, GEO-Scope provides an open, deterministic, scientifically auditable measurement contract.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GEO-SCOPE PHILOSOPHY                             │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ ❌ Proprietary "Visibility Scores"   │ ✅ Declared Measurement Contract     │
│ ❌ Universal Ground-Truth Claims     │ ✅ Configuration-Bounded Observation │
│ ❌ Black-Box Web Scrapers            │ ✅ Cryptographic Evidence & Replay   │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

Under the **GEO-Scope Measurement Contract v1**:
1. **Every observation is bounded by declared metadata:** Prompt set ID, language, location, model version, temperature, grounding state, and timestamp.
2. **Every metric is mathematically explicit:**
   - **Mention:** Binary response-level presence ($\ge 1$). Multiple mentions in a single answer do not inflate scores.
   - **Citation:** Strict 4-way separation (target domain, deep URL, 3rd-party source, body mention).
   - **Recommendation:** Evaluated only on explicit linguistic selection; ambiguous cases are marked `experimental`.
   - **Share of Voice:** Denominators and weighting sources are declared in full.
3. **Every public result is verifiable:** Zero-network offline replay allows anyone to re-verify published metrics bit-for-bit from preserved raw responses (`raw_responses.jsonl`).

---

## 3. The Core Epistemic Axiom

> **"AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."**

When communicating GEO-Scope findings publicly:
- **Use:** *"We measured a 38.0% mention rate under the declared prompt universe (N=100) on ChatGPT Search (Q1 2026)."*
- **Avoid:** *"Brand X has 38% true AI market share."*
- **Avoid:** *"Tool Y is inaccurate because its visibility metric differs from GEO-Scope."*

---

## 4. Related Resources

- 📄 **Full Specification**: [`docs/measurement-contract-v1.md`](measurement-contract-v1.md)
- 📐 **JSON Schema**: [`schemas/measurement-contract-v1.json`](../schemas/measurement-contract-v1.json)
- 🧪 **Example Validation Fixture**: [`examples/measurement-contract-v1-example.json`](../examples/measurement-contract-v1-example.json)
- 🛡️ **Integrity Gate**: [`docs/SCIENTIFIC_MEASUREMENT_GATE.md`](SCIENTIFIC_MEASUREMENT_GATE.md)
