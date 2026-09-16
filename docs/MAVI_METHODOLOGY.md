# Molavi AI Visibility Index (MAVI) — Measurement Engine v1.0

The **Molavi AI Visibility Index (MAVI)** is a multi-layer diagnostic and empirical measurement framework for Generative Engine Optimization (GEO).

Rather than relying on manually entered scores or arbitrary heuristics, MAVI v1 operates as an automated, measured index derived from two complementary research engines:
1. **SAGE (Structured AI Grounding & Extractability)**: Deterministic webpage analysis of crawler accessibility, semantic structure, entity graphs, and citation extractability (Layers L1–L4).
2. **GEO-Scope**: Empirical multi-model live benchmark observations across search-grounded and direct-completion AI engines (Layer L5).

---

## 1. Multi-Layer Architecture

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                      MAVI Composite Index (0 - 100)                        │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼───────────────────────────┐
         ▼                            ▼                           ▼
 ┌───────────────┐            ┌───────────────┐           ┌───────────────┐
 │   SAGE (L1)   │            │   SAGE (L2)   │           │   SAGE (L3)   │
 │ Technical     │            │ Semantic      │           │ Entity        │
 │ Accessibility │            │ Extractability│           │ Clarity       │
 └───────────────┘            └───────────────┘           └───────────────┘
         │                            │                           │
         └────────────────────────────┼───────────────────────────┘
                                      │
         ┌────────────────────────────┴───────────────────────────┐
         ▼                                                        ▼
 ┌───────────────┐                                        ┌───────────────┐
 │   SAGE (L4)   │                                        │ GEO-Scope (L5)│
 │ Retrieval &   │                                        │ Observed AI   │
 │ Citation Ready│                                        │ Visibility    │
 └───────────────┘                                        └───────────────┘
```

---

## 2. Layer Definitions & Measurement Methodology

### L1: Technical Accessibility
- **Source Engine**: `SAGE`
- **Default Methodology Weight**: `15%` ($w_1 = 0.15$)
- **What is Measured**:
  - **HTTP Status**: Returns `100.0` for HTTP 200, `70.0` for redirects, `0.0` for client/server errors.
  - **Meta Robots & Crawler Access**: Detects `noindex`, `none`, and explicit AI crawler blocks (`GPTBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`).
  - **Canonical URL Integrity**: Validates presence of self-referential or authoritative canonical tag.
  - **Renderability & Text-to-DOM Density**: Evaluates text token density relative to overall HTML payload (optimal $\ge 8.0\%$).
  - **Protocol Security**: HTTPS compliance.

### L2: Semantic Extractability
- **Source Engine**: `SAGE`
- **Default Methodology Weight**: `20%` ($w_2 = 0.20$)
- **What is Measured**:
  - **Heading Structure & Hierarchy**: Validates single `<h1>` main heading, hierarchical `<h2>`/`<h3>` sectioning.
  - **RAG Chunk Quality**: Counts self-contained, high-information paragraph units (15–120 words).
  - **BLUF (Bottom Line Up Front) Direct Answers**: Detects clear definitions and assertive summary statements in the opening section.
  - **Semantic Density**: Evaluates lexical diversity and vocabulary uniqueness across content tokens.

### L3: Entity Clarity
- **Source Engine**: `SAGE`
- **Default Methodology Weight**: `20%` ($w_3 = 0.20$)
- **What is Measured**:
  - **JSON-LD Schema Markup**: Evaluates presence and diversity of structured schemas (`Organization`, `Product`, `SoftwareApplication`, `Article`, `FAQPage`).
  - **Entity Disambiguation (`sameAs`)**: Identifies grounding links to authoritative entity graphs (`Wikidata`, `Wikipedia`, `LinkedIn`, `Crunchbase`).
  - **Entity Name Consistency**: Matches target brand across `<title>`, `<h1>`, `<meta name="description">`, and JSON-LD schema names.
  - **Attribution & Publisher Identity**: Verifies explicit organization/author entity models.

### L4: Retrieval / Citation Readiness
- **Source Engine**: `SAGE`
- **Default Methodology Weight**: `20%` ($w_4 = 0.20$)
- **What is Measured**:
  - **Structured Data Tables**: Measures presence of HTML `<table>` and markdown comparison matrices.
  - **Quantitative Statistics & Proof Points**: Counts empirical metrics, percentages, benchmark figures, and currency values.
  - **Citation-Ready Quote Passages**: Identifies declarative, assertive sentences structured for LLM quote extraction.
  - **DOM Container Isolation**: Verifies semantic `<main>` or `<article>` containers isolating primary text from navigation boilerplate.

### L5: Observed AI Visibility
- **Source Engine**: `GEO-Scope LIVE Experiments`
- **Default Methodology Weight**: `25%` ($w_5 = 0.25$)
- **What is Measured**:
  - **Share of Model (SoM)**: Target brand mention rate across evaluated prompts in successful inferences.
  - **Top-1 Recommendation Pick Rate**: Frequency of brand appearing as primary recommendation (#1 position).
  - **Multi-Model Provider Coverage**: Proportion of AI engines citing/recommending the target brand.
  - **Zero Fabrication Policy**: If no live benchmark experiment has been executed, L5 is explicitly returned as `null` with status `not_measured`. No synthetic score is fabricated.

---

## 3. Weighting & Normalization Methodology

### Default Methodology Weights
Weights are versioned and labeled as **methodology defaults** (not claimed as universally fitted constants):

$$\mathcal{W} = \{L_1: 0.15, L_2: 0.20, L_3: 0.20, L_4: 0.20, L_5: 0.25\} \quad \left(\sum w_i = 1.00\right)$$

Custom weights can be configured via CLI (`--weights`) or API/MCP.

### Partial MAVI Scoring
When some layers have not been measured (e.g., L1–L4 measured from HTML without an L5 experiment), MAVI computes a normalized score:

$$\text{Raw Measured Score} = \sum_{i \in \text{active}} w_i \cdot \text{Score}_i$$

$$\text{Normalized MAVI} = \frac{\text{Raw Measured Score}}{\sum_{i \in \text{active}} w_i}$$

Example:
- Layers Measured: 4/5 (L1, L2, L3, L4)
- Active Weight Sum: $0.15 + 0.20 + 0.20 + 0.20 = 0.75$
- Raw Score: $60.5 / 75.0$
- Normalized MAVI: **$80.7 / 100$** (Grade: **A**)
- Normalization Basis: `"Normalized across 4/5 measured layers (L1, L2, L3, L4); active weight sum = 0.75"`

---

## 4. Measurement Confidence Rating

MAVI confidence is computed from data completeness rather than arbitrary sentiment:

$$\text{Confidence Score} = 0.40 \cdot \mathcal{C}_{\text{layers}} + 0.35 \cdot \mathcal{C}_{\text{L5}} + 0.25 \cdot \mathcal{C}_{\text{SAGE}}$$

- **Layer Completeness ($\mathcal{C}_{\text{layers}}$)**: Ratio of measured layers ($k / 5$).
- **L5 Observation Completeness ($\mathcal{C}_{\text{L5}}$)**: Scaled by volume ($\ge 50$ inferences $= 1.0$) and provider diversity ($\ge 3$ providers $= 1.0$).
- **SAGE Depth ($\mathcal{C}_{\text{SAGE}}$)**: Scaled by token count and schema count.

| Confidence Score | Confidence Level | Interpretation |
| :---: | :---: | :--- |
| $\ge 0.75$ | **High** | Full 5-layer measurement with statistical AI observation sample. |
| $0.50 - 0.74$ | **Medium** | Partial measurement (e.g. SAGE L1-L4 complete, L5 pending or small sample). |
| $0.25 - 0.49$ | **Low** | Limited audit data (e.g. partial HTML snippet only). |
| $< 0.25$ | **Insufficient** | No layers measured or severe data deficit. |

---

## 5. Provenance & Audit Trail

Every layer result includes an explicit provenance record:

```json
{
  "layer_id": "L5",
  "layer_name": "Observed AI Visibility",
  "score": 76.5,
  "status": "measured",
  "provenance": {
    "source": "geo-scope",
    "metric_version": "1.0.0",
    "timestamp_utc": "2026-09-17T00:30:00Z",
    "evidence_count": 95,
    "experiment_id": "EXP-1789592107"
  }
}
```

---

## 6. CLI & MCP Usage

### CLI Commands

```bash
# 1. Audit a URL using SAGE (L1-L4)
geo-scope mavi --url https://www.hubspot.com/products/crm --brand HubSpot

# 2. Audit a local HTML file
geo-scope mavi --html landing_page.html --brand HubSpot

# 3. Complete 5-layer audit (SAGE L1-L4 + GEO-Scope L5 experiment)
geo-scope mavi --html landing_page.html --brand HubSpot --experiment results/experiment.json

# 4. Output structured JSON
geo-scope mavi --html landing_page.html --brand HubSpot --format json --out mavi_report.json

# 5. Custom layer weights
geo-scope mavi --html landing_page.html --weights '{"L1": 0.10, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.30}'
```

### MCP Tool: `measure_mavi`

```json
{
  "name": "measure_mavi",
  "arguments": {
    "url": "https://www.hubspot.com/products/crm",
    "html_content": "<html>...</html>",
    "brand": "HubSpot",
    "experiment_data": { ... }
  }
}
```
