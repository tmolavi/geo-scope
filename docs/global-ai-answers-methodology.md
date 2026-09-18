# Global AI Answers Benchmark 2026: Scientific Methodology

**Measuring How Generative AI Systems Respond to Human Concerns Across Regions**  
*Benchmark Release*: `global-ai-answers-2026.1`  
*Research Status*: Live Empirical Benchmark (Peer-Review Ready)  
*Measurement Engine*: [GEO-Scope](https://github.com/tmolavi/geo-scope)  
*Execution Layer*: Hamzad AI Gateway (`https://api.molavi.pro`)  
*Discovery Lineage*: AnswerPath GEO  

---

## 1. Executive Summary & Research Question

As generative AI answer engines and foundation models become primary interfaces for human inquiry, they mediate responses to critical life decisions: acquiring technical skills, international career migration, launching digital businesses, adopting AI software, managing personal finances, avoiding workplace burnout, and choosing between formal degrees or self-directed learning.

### Primary Research Question
> **When people around the world query leading AI answer engines and foundation models with essential life, career, technology, and business questions, what entities, organizations, platforms, countries, and recommendations are surfaced?**

### Scientific & Epistemic Boundaries
To uphold scientific transparency and eliminate marketing bias:
- **No "Global Winner" or "Humanity Ranking"**: The benchmark does not rank "best country", "smartest human", or "best provider".
- **Empirical Observation, Not Algorithm Deconstruction**: Records model responses as emitted; makes no claims of reverse-engineering internal model weights or hidden indexing formulas.
- **Value-Neutral Multi-Type Extraction**: Extracts entities across organizations, destinations, software, and institutions without normative scoring.
- **Separation of Search Grounding from Parametric Retrieval**: Answer engines with live web grounding (`hamzad_gemini`, `hamzad_perplexity`) are explicitly analyzed separately from parametric completion models (`hamzad_openai`, `hamzad_claude`).

---

## 2. End-to-End Dataset Pipeline

The benchmark methodology follows a 7-stage verifiable pipeline:

```
AnswerPath GEO
      ↓
Question Discovery (Cultural & intent-mined query clusters)
      ↓
GEO-Scope
      ↓
Measurement Engine (Prompt orchestration & model routing)
      ↓
Hamzad Gateway (Audited, isolated API execution)
      ↓
Raw Response Storage (Unedited response logs with HTTP latency & timestamps)
      ↓
Entity Extraction (Unicode normalization & homonym disambiguation)
      ↓
Metrics & Cryptographic Bundling (SHA-256 integrity manifest & distributions)
```

1. **AnswerPath GEO**: Discovers authentic user query clusters and formulates localized inquiries reflecting cultural dilemmas rather than robotic translations.
2. **GEO-Scope Core**: Manages prompt matrix dispatching, concurrency control, and zero-fallback integrity rules.
3. **Hamzad AI Gateway**: Serves as the audited execution layer with private key isolation, latency tracking, and model identity verification.
4. **Raw Response Storage**: Captures byte-for-byte unparsed response bodies, headers, and token timings to `raw_responses.jsonl`.
5. **Entity Parser & Normalizer**: Applies Persian/Arabic letter unification, boundary matching, and `do_not_confuse` token exclusions.
6. **Metrics Engine**: Computes empirical mention rates, recommendation rates, citation presence, and regional cross-tabulations.
7. **Integrity & Checksum Layer**: Writes canonical `manifest.json` and computes SHA-256 digests across all release files.

---

## 3. Sampling Dimensions & Matrix Design

The `global-ai-answers-2026.1` benchmark evaluates **34 localized prompts** across **7 categories**, **7 regions**, **9 languages**, and **4 provider models**, generating **136 model completions** and over **1,850 evaluated entity observation states**.

### 3.1 Human Concern Categories (7)
| Category | Focus Area | Example Intent |
| :--- | :--- | :--- |
| `learning_skills` | High-value technical & analytical skills | Modern programming, ML engineering, system design |
| `career_migration` | International work, tech visas, relocation | Tech hubs, points-based visas, digital nomad hubs |
| `business_entrepreneurship` | Low-capital digital ventures & SaaS | Micro-SaaS, digital agency models, e-commerce |
| `technology_adoption` | Emerging AI tool workflows | Generative AI integration, enterprise LLM adoption |
| `personal_finance` | Wealth preservation & index investing | Inflation protection, global index funds, DCA |
| `health_lifestyle` | Burnout prevention & knowledge work health | Evidence-based routines, sleep science, focus |
| `education` | University degrees vs. self-directed learning | Portfolio-based hiring vs. formal computer science degrees |

### 3.2 Geographic & Linguistic Distribution
- **Geographic Regions (7)**: Middle East, North America, Europe, Asia, Africa, Latin America, Global Baseline.
- **Languages (9)**: Arabic (`ar`), German (`de`), English (`en`), Spanish (`es`), Persian (`fa`), French (`fr`), Japanese (`ja`), Portuguese (`pt`), Chinese (`zh`).

### 3.3 Provider Models Evaluated (4)
- **Search-Grounded Answer Engines (`provider_class: answer_engine`)**:
  - `hamzad_gemini` (`gemini-2.5-flash` with Google Search grounding)
  - `hamzad_perplexity` (`sonar-pro` with live web citations)
- **Parametric Foundation Models (`provider_class: llm`)**:
  - `hamzad_openai` (`gpt-4o-mini`)
  - `hamzad_claude` (`anthropic/claude-3.5-sonnet`)

### 3.4 Multi-Type Entity Catalog (24 Entities)
- **Companies & Cloud Providers**: Google, Microsoft, OpenAI, Anthropic, Apple, Amazon, Meta, NVIDIA, LinkedIn.
- **Countries & Destinations**: Germany, Canada, United Arab Emirates, United States, Singapore, Australia.
- **Technologies & Languages**: Python, Docker, PyTorch, ChatGPT.
- **Learning Platforms & Communities**: GitHub, Coursera, edX, Kaggle.
- **Institutions & Organizations**: World Health Organization (WHO), MIT.

---

## 4. Empirical Metrics Definitions & Formulations

All metrics are strictly observational and descriptive. Normative terms such as *"winner"*, *"best"*, or *"most influential"* are banned.

### 4.1 Mention Rate (`mention_rate`)
*Definition*: **Percentage of measured responses where an entity appeared.**
$$\text{Mention Rate}(e) = \frac{\sum_{i=1}^N \mathbb{I}(e \in R_i)}{N}$$
*Terminology*: "Highest observed mention rate", "Most frequently mentioned in sample".

### 4.2 Recommendation Rate (`recommendation_rate`)
*Definition*: **Percentage of responses where an entity was explicitly recommended.**
$$\text{Recommendation Rate}(e) = \frac{\sum_{i=1}^N \mathbb{I}(e \text{ recommended in } R_i)}{N}$$

### 4.3 Citation Rate (`citation_rate`)
*Definition*: **Percentage of answers containing identifiable source references.**
$$\text{Citation Rate}(e) = \frac{\sum_{i=1}^N \mathbb{I}(\text{citations}(R_i) \cap \text{domains}(e) \neq \emptyset)}{N}$$

### 4.4 Top-1 Recommendation Rate (`top1_rate`)
*Definition*: **Percentage of responses where an entity appeared as the first recommended choice.**
$$\text{Top-1 Rate}(e) = \frac{\sum_{i=1}^N \mathbb{I}(\text{first\_recommended}(R_i) = e)}{N}$$

---

## 5. Cryptographic Integrity & Verification

```bash
# Verify bit-for-bit SHA-256 package checksums
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.1

# Recompute all metrics deterministically from raw observations
geo-scope benchmark reproduce --dataset benchmark/releases/global-ai-answers-2026.1
```

---

## 6. Limitations Summary
For the full limitations disclosure, see [Research Limitations](global-ai-answers-limitations.md).
