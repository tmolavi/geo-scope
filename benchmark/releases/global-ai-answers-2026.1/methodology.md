# Global AI Answers Benchmark 2026: Methodology

## 1. Research Question
When people worldwide query leading generative AI systems regarding critical life decisions—such as acquiring skills, international career migration, founding a digital business, managing personal finances, adopting emerging technology, and educational pathways—**what entities, organizations, platforms, and recommendations are surfaced?**

---

## 2. Epistemic Principles & Anti-Hype Constraints
1. **Empirical Measurement, Not Algorithm Deconstruction**: We observe and record model responses as emitted; we make no unsubstantiated claims regarding inner weights or proprietary ranking mechanics.
2. **Value-Neutral Multi-Type Extraction**: Entities are classified across organizations, technologies, destinations, platforms, and products without normative scoring or judgment.
3. **Cultural Adaptation Over Literal Translation**: Inquiries were localized to reflect authentic socioeconomic contexts rather than robotic word-for-word translation.
4. **Homonym Disambiguation**: The entity parser enforces `do_not_confuse` filters to prevent false positive entity attribution.
5. **Separation of Search Grounding from Parametric Memory**: Providers are categorized into `answer_engine` (search-grounded real-time engines) and `llm` (parametric completion models) to isolate web retrieval effects from internal parametric knowledge.

---

## 3. Sampling & Matrix Design
- **Categories (7)**:
  - `learning_skills`: Foundational programming, data science, and AI tool adoption.
  - `career_migration`: Global mobility, work visas, and talent attraction hubs.
  - `business_entrepreneurship`: Low-capital online ventures, scalable SaaS, and digital services.
  - `technology_adoption`: Generative AI tools and enterprise software workflows.
  - `personal_finance`: Diversified index investing, inflation hedging, and wealth preservation.
  - `health_lifestyle`: Burnout prevention, ergonomics, and evidence-based knowledge worker routines.
  - `education`: University degree vs. self-directed portfolio learning paths.
- **Geographic Dimensions (7)**: Middle East, North America, Europe, Asia, Africa, Latin America, and Global.
- **Languages (9)**: Arabic, German, English, Spanish, Persian, French, Japanese, Portuguese, Chinese.
- **Models Evaluated**:
  - `gemini-2.5-flash` (via Hamzad Gateway `hamzad_gemini`)
  - `sonar-pro` (via Hamzad Gateway `hamzad_perplexity`)
  - `gpt-4o-mini` (via Hamzad Gateway `hamzad_openai`)
  - `anthropic/claude-3.5-sonnet` (via Hamzad Gateway `hamzad_claude`)

---

## 4. Execution & Parser Pipeline
1. **Execution**: Prompts are dispatched sequentially to the Hamzad AI Gateway. Raw completions, status codes, latency, and HTTP metadata are logged directly to `raw_responses.jsonl`.
2. **Normalization & Extraction**: The `ObservationParser` scans response tokens with Unicode-aware boundary matching, Persian character normalization, alias resolution, and homonym exclusion.
3. **Metric Formulation**:
   $$\text{Mention Rate} = \frac{\sum_{i=1}^N \mathbb{I}(\text{Entity} \in \text{Response}_i)}{N}$$
   $$\text{Share of Observed Visibility (SOV)} = \frac{\text{Total Mentions of Entity}}{\sum_{e \in E} \text{Total Mentions of } e}$$

---

## 5. Limitations & Future Work
- Snapshot observations reflect model versions active in September 2026.
- Temperature and sampling parameters introduce slight response variance across runs.
- Subsequent iterations will expand the query set to longitudinal tracking across seasonal hiring and educational cycles.
