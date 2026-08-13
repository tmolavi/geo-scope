# 🧪 Experiment: [Title of Your Experiment]

- **Author**: [Your Name / GitHub Username / Organization]
- **Date**: [YYYY-MM-DD]
- **Experiment ID**: `EXP-[TIMESTAMP]`
- **Repository**: [Link to Fork or Issue]

---

## 1. Hypothesis

*State your scientific hypothesis clearly:*
- *Example: "We hypothesize that publishing verified 4.5+ star reviews on G2 increases ChatGPT Search recommendation rate by at least 15% for comparative intent queries."*

---

## 2. Experimental Setup

- **Target Brand**: `[Brand Name]`
- **Competitors**: `[Comp A, Comp B, Comp C]`
- **Industry / Vertical**: `[e.g. SaaS / Developer Tools / Local Services]`
- **Total Prompts**: `[e.g. 100 / 500 / 1000]`
- **Language / Market**: `[e.g. English (US) / Persian (IR)]`
- **Models Evaluated**: `[Perplexity Sonar, ChatGPT Search, Gemini Grounding, Claude 3.7]`
- **Grounding Mode**: `[Live Search APIs / Deterministic Benchmark]`

---

## 3. Reproduction Command

```bash
geo-scope run \
  --brand "[Your Brand]" \
  --competitors "[Comp A, Comp B]" \
  --prompts "[path/to/prompts.csv]" \
  --out "results/[experiment_name]/"
```

---

## 4. Empirical Observations & Results

### Share of Model (SoM) Summary
| AI Model | Baseline SoM (%) | Post-Change SoM (%) | Delta ($\Delta$) | Top-1 Rank Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Perplexity Sonar** | 45.0% | 62.0% | **+17.0%** | 35.0% |
| **ChatGPT Search**   | 50.0% | 58.0% | **+8.0%** | 30.0% |
| **Google Gemini**    | 40.0% | 46.0% | **+6.0%** | 22.0% |
| **Claude 3.7**       | 52.0% | 55.0% | **+3.0%** | 28.0% |

### Citation Domain Distribution
- **Top Domain #1**: `reddit.com/r/...` (34% of all links)
- **Top Domain #2**: `g2.com/...` (24% of all links)
- **Top Domain #3**: `techcrunch.com/...` (18% of all links)

---

## 5. Findings, Limitations & Disclaimers

### Key Findings
1. [Finding 1]
2. [Finding 2]

### Limitations & Threats to Validity
- *Correlation does not imply direct causation.*
- *Search index freshness may introduce temporal variance.*
- *Prompt phrasing nuance can alter retrieval sub-queries.*

---

## 6. Artifacts & Evidence Files
- 📄 `summary.md`: Attached
- 📊 `queries.csv`: Attached
- 🔗 `citations.csv`: Attached
