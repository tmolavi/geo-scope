# Query Fan-Out Brand Introduction Benchmark

## Objective & Hypothesis
We test the empirical AI search mechanism:
> **BRANDS INTRODUCED BY THE ENGINE'S OWN SEARCH/FAN-OUT QUERIES MAY BE MUCH MORE LIKELY TO APPEAR IN THE FINAL ANSWER.**

This benchmark replicates and assesses the boundaries of the external July 2026 observation (which reported that search-introduced brands reached final answers 68.9% of the time vs 2.1% for retrieved-only brands).

## Experimental Design
- **Total Conversations**: 50
- **Commercial Sectors**: 5 non-branded discovery domains (CRM, Project Management, Cloud Infrastructure, Email Marketing, Customer Support).
- **Prompt Policy**: Non-branded commercial/discovery queries where multiple brands could plausibly satisfy the request. No self-promotional (Taqi Molavi / InTen) queries.
- **Engine Trace Observability**: Engine search queries, retrieval traces (metadata, snippets, URLs), final generated answers, and grounding citations are recorded in `raw/`.

## Frozen Classification Definitions
1. **USER_NAMED**: Brand explicitly present in the original user prompt.
2. **ENGINE_QUERY_INTRODUCED**: Brand absent from user prompt AND explicitly present in observable engine-generated search queries.
3. **RETRIEVED_ONLY**: Brand absent from user prompt AND absent from observable queries, but present in retrieved result/page metadata.
4. **NOT_RETRIEVED**: Brand absent from user prompt, generated queries, and retrieved items.

Mention (`final_answer_mentioned`) and Citation (`final_answer_cited`) are tracked strictly as separate outcomes.

## Empirical Results Summary
- **Total Brand Observations**: 300
- **ENGINE_QUERY_INTRODUCED count**: 70
- **RETRIEVED_ONLY count**: 122
- **Engine-Introduced Mention Rate**: 65.7% (46/70)
- **Retrieved-Only Mention Rate**: 13.1% (16/122)
- **Mention Rate Ratio**: 5.0107x
- **Engine-Introduced Citation Rate**: 52.9% (37/70)
- **Retrieved-Only Citation Rate**: 7.4% (9/122)
- **Manual Validation Accuracy (N=25 sample)**: 100.0%
- **Result Classification**: `REPRODUCED_DIRECTIONALLY`

## Interpretation & Boundaries
- We observed the same directional pattern: within this sample, brands introduced during observable query fan-out were mentioned significantly more often than retrieved-only brands (5.0107x).
- *Strict scientific boundary*: Query fan-out correlation does NOT prove causality. These fields are maintained as experimental diagnostic metrics and are excluded from composite visibility scoring.
