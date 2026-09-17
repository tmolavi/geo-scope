# How We Benchmarked Brand Visibility Across Leading AI Engines (Without Fabricated Data or False Promises)

### An empirical look at how Generative AI assistants mention, rank, and cite digital agencies in 2026.

**By Taqi Molavi** · *Founder & AI Search Architect*

---

If you browse LinkedIn or Twitter today, you will see endless claims about "cracking the AI search algorithm" and "guaranteed #1 ranking in ChatGPT Search." 

Most of these claims suffer from two fatal flaws:
1. **Conflating correlation with algorithmic secrets**: LLMs are probabilistic text generators with RAG pipelines, not static search indexers.
2. **Synthetic / fabricated benchmarks**: Many "studies" either test 3 cherry-picked queries or generate synthetic test responses locally.

To address these shortcomings, we released the **GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark (`geo-seo-digital-agency-iran-2026.1`)** as an open-source, fully reproducible research study.

Here is how we built the methodology, the open architecture behind it, and what the data actually tells us.

---

## The Stack: From Question Mining to Zero-Secret Multi-Model Execution

To run a scientifically rigorous benchmark, you cannot simply write 20 prompts in a spreadsheet and copy-paste answers. You need a 3-stage verifiable pipeline:

### 1. Question Discovery & Intent Stratification (`AnswerPath GEO`)
Before measuring visibility, you must know what people actually ask AI engines. Using **AnswerPath GEO**, we mined and stratified queries into two separate pools:
- **Observed User Inquiries (15 Prompts)**: Real conversational queries extracted from logs and search data across 5 intents (`commercial`, `compare`, `trust`, `solve`, `buy`).
- **Generated Exploration Prompts (15 Prompts)**: Structured templates designed to stress-test specific agency capabilities.

Crucially, **AnswerPath GEO separates observed demand from generated hypotheses**. We never mix the two into a single blended score without distinct labels.

### 2. Zero-Secret Model Gateway (`Hamzad AI Gateway`)
Client applications should never store raw API keys. GEO-Scope connects to **Hamzad AI Gateway**, which manages key rotation, budget limits, and multi-provider routing across:
- Google Gemini 2.5 Flash
- OpenAI GPT-4o
- Anthropic Claude 3.5 Sonnet
- Perplexity Sonar Pro

### 3. Transparent Execution Provenance (`GEO-Scope`)
When querying AI gateways, fallbacks occur (e.g., when an upstream provider throttles and routes to a high-throughput surrogate model like Qwen 3.8 27B). 

Instead of hiding or discarding fallback completions, GEO-Scope records **full execution provenance**:
- `requested_model` (e.g. `claude-3-5-sonnet`)
- `actual_model` (e.g. `qwen/qwen3.8-27b`)
- `execution_class` (`native` vs `fallback` vs `failed`)

---

## What the Observations Reveal

When analyzing responses across top Iranian digital marketing and SEO agencies (Web24, Novin, Dimarketing, Triboon, DMN Agency):

1. **Entity Disambiguation is Non-Negotiable**: Brands that maintain unambiguous entity schemas (Organization schema with `sameAs` pointers to Wikidata, Crunchbase, and official media) are consistently recognized and cited across models without hallucination.
2. **Direct Answer Paragraphs Win Grounding**: In search-grounded models (like Gemini and Sonar), agencies with clean, high-density case summaries (BLUF format: Bottom Line Up Front) were quoted verbatim in recommendations.
3. **Intent Shapes Recommendation Stance**: Commercial comparison queries triggered structured bullet points with pros/cons, whereas solving queries highlighted technical depth.

---

## Reproduce It Yourself

Science is only science if anyone can run it. Every observation in this benchmark is committed with its SHA-256 hash:

```bash
# Clone the open repo
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Verify bit-for-bit dataset integrity
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1

# Recompute the metrics and bootstrap confidence intervals
geo-scope benchmark reproduce --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```

Check out the full open-source repository at [github.com/tmolavi/geo-scope](https://github.com/tmolavi/geo-scope) and the research hub at [molavi.pro](https://molavi.pro).
