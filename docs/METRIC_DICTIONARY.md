# GEO-Scope Metric Dictionary

**Version:** 1.0.0  
**Effective Date:** October 2026  
**Status:** Canonical Scientific Specification of AI Visibility Metrics  
**Axiom:** `Mention ≠ Citation ≠ Recommendation ≠ Position ≠ Share of Model`

---

## Overview

In Generative Engine Optimization (GEO) and AI Visibility measurement, presenting vague aggregate numbers harms scientific reproducibility and misleads decision-makers. Different AI engines behave differently depending on whether they retrieve live web sources, rely on parametric pretraining memory, or apply post-generation safety rerankers.

This document establishes the official definitions, formulas, numerators, denominators, and interpretation rules for every metric calculated by GEO-Scope.

---

## Core Denominator Standard

Every metric in GEO-Scope is coupled with an explicit denominator from the **Central Denominator Registry**. A metric value without its corresponding numerator, denominator, sample size, coverage, and confidence interval is considered malformed and non-compliant.

```json
{
  "metric": "owned_domain_citation_rate",
  "value": 0.061,
  "numerator": 117,
  "denominator": 1901,
  "denominator_type": "retrieval_evidence_answers",
  "sample_size": 1901,
  "coverage": 0.99,
  "status": "measured",
  "ci_method": "wilson",
  "confidence_level": 0.95,
  "ci_lower": 0.051,
  "ci_upper": 0.073
}
```

---

## 1. Mention Rate

### Definition
The proportion of valid generated answers that contain an explicit, validated textual mention of the target entity (brand name or defined aliases).

### Formula
$$\text{Mention Rate} = \frac{\text{Valid Answers Containing Entity Mention}}{\text{All Valid Returned Answers}}$$

### Denominator
- **Numerator:** Count of valid responses containing at least one confirmed mention of the target entity (matching tier `exact` or `normalized_exact`).
- **Denominator:** `valid_answers` (all successfully returned responses where `status = "success"` and content was non-empty).
- **Denominator Type:** `valid_answers`

### Interpretation Rules
- A mention simply indicates that the entity appeared in the AI model's output text.
- **A mention is NOT an endorsement, recommendation, or citation.** Mentions can be incidental, negative, or part of a broad list.

---

## 2. Citation Rate

AI engines with live search or retrieval grounding may display citations, source cards, or embedded reference links. Citation rates must be reported under **two distinct denominators** to prevent distorting models that do not perform web search on every prompt.

### 2.1 Citation Rate — All Answers

#### Definition
The proportion of all valid returned answers that contain at least one web citation or source link pointing to the target entity's domain(s).

#### Formula
$$\text{Citation Rate (All Answers)} = \frac{\text{Answers Citing Target Domain}}{\text{All Valid Returned Answers}}$$

#### Denominator Type: `valid_answers`

### 2.2 Citation Rate — Retrieval-Evidence Answers

#### Definition
The proportion of answers that *actually triggered web search and returned retrieval sources* that cited the target entity's domain(s).

#### Formula
$$\text{Citation Rate (Retrieval-Evidence)} = \frac{\text{Answers Citing Target Domain}}{\text{Answers Containing Retrieval Evidence}}$$

#### Denominator Type: `retrieval_evidence_answers`

### Interpretation Rules
- Both metrics must be reported side by side.
- Never substitute one denominator for the other.
- If an engine executed 100 prompts but only retrieved sources for 20 prompts, dividing 5 citations by 100 yields 5% (All Answers), but dividing by 20 yields 25% (Retrieval-Evidence). Hiding this distinction misrepresents the engine's retrieval bias.

---

## 3. Recommendation Rate

### Definition
The proportion of valid answers in which the target entity is explicitly endorsed or recommended by the AI as an advisable solution, choice, or vendor.

### Formula
$$\text{Recommendation Rate} = \frac{\text{Answers Containing Validated Recommendation of Entity}}{\text{All Valid Returned Answers}}$$

### Denominator Type: `valid_answers`

### Parsing & Verification Rules
- The presence of the brand name alone **never** constitutes a recommendation.
- The parser must verify that the entity was framed by explicit endorsement markers (e.g., *"We recommend"*, *"Top pick"*, *"بهترین گزینه"*, *"önerilen ajans"*).
- The parser must record a rule-based linguistic trace (`recommendation_evidence`) identifying the exact sentence and trigger phrase.

---

## 4. Top Recommendation Rate (First-Choice Recommendation)

### Definition
The proportion of recommendation-bearing answers in which the target entity is presented as the very first recommended choice or top-ranked solution.

### Formula
$$\text{Top Recommendation Rate} = \frac{\text{Answers Where Target Entity is First Recommended Option}}{\text{Answers Containing At Least One Recommendation}}$$

### Denominator Type: `answers_with_recommendations`

### Interpretation Rules
- The denominator is strictly restricted to answers that contained at least one recommended entity. Answers that merely explained concepts without recommending any vendor are excluded from this denominator.

---

## 5. Average First Mention Position

### Definition
The arithmetic mean position (1-indexed order of appearance) of the target entity among all entities mentioned within an answer, calculated **only across answers where the entity was mentioned**.

### Formula
$$\text{Average First Mention Position} = \frac{\sum_{i \in \text{Mentions}} \text{Position}_i(E)}{N_{\text{Answers With Mention}}}$$

### Denominator Type: `answers_with_target_mention`

### Strict Non-Zero Rule
- **If an entity was NOT mentioned in an answer, its position is NOT zero ($0$).**
- Unmentioned observations must be strictly **excluded** from the position average; otherwise, an entity mentioned in 1 prompt at position 1 and unmentioned in 9 prompts would appear to have an average position of $0.1$, which is mathematically absurd.
- The proportion of answers contributing to the position average must be reported as `mention_coverage`.

---

## 6. Share of Model (Share of Voice in Model)

### Definition
The proportion of all tracked entity mentions captured by the target entity across a defined prompt cohort and observation window.

### Formula
$$\text{Share of Model} = \frac{\text{Total Mentions of Target Entity}}{\sum_{j \in \text{All Tracked Entities}} \text{Total Mentions of Entity}_j}$$

### Denominator Type: `all_tracked_entity_mentions`

### Reporting Breakdown
- Must be reported broken down by:
  - `engine` (e.g. ChatGPT Search vs. Gemini Grounding vs. Perplexity Sonar)
  - `intent` (e.g. Best/Recommendation vs. Comparison vs. Pricing vs. Criteria)
  - `language` (`fa`, `tr`, `en`, `ar`, `az`)
  - `locale` (`fa-IR`, `tr-TR`, etc.)
  - `time_window` (observation batch)

---

## 7. Owned-Domain Citation Rate

### Definition
The proportion of retrieval-evidence answers where the AI cites the entity's own official, primary domain rather than third-party aggregators, directories, social profiles, or press releases.

### Formula
$$\text{Owned-Domain Citation Rate} = \frac{\text{Retrieval-Evidence Answers Citing Entity's Owned Domain}}{\text{All Retrieval-Evidence Answers}}$$

### Denominator Type: `retrieval_evidence_answers`

### Distinction
- Brand mention $\ne$ Owned-domain citation.
- An AI engine frequently mentions a brand based on a review or directory without linking to the brand's official domain.

---

## 8. Source Influence

### Definition & Scientific Status
Source Influence measures the causal textual impact or absorption that a cited URL exerted on the generated synthesis.

### Official Status: `not_measured`
$$\text{Source Influence} = \text{not\_measured}$$

### Scientific Justification
- Merely having a URL listed in a model's citation tray does **not** prove that the model extracted or absorbed factual tokens from that specific webpage.
- Models frequently perform retrieval over multiple documents, synthesize an answer from parametric memory or third-party text, and attach citations based on post-hoc URL matching.
- Until verified token-level attribution or attention-weight extraction is available across closed-source APIs, claiming to measure "Source Influence" or "Source Weight" is pseudoscience. GEO-Scope strictly marks this metric as `not_measured`.

---

## 9. Google Search Console Metric Alignment: AI Block Position

When ingesting Search Console or SERP layout data:

### Definition
**AI Block Position** is the vertical pixel or ordinal block ranking of the Generative AI feature (e.g., Google AI Overview) on the search engine results page.

### Strict Governance Rules
1. **Never Report as Citation Rank:** AI Block Position indicates where the *AI container* sits on Google's search page; it conveys zero information regarding where or if a brand's URL is cited inside the AI snippet.
2. **Directional Quality Only:** Must be labeled `measurement_quality = "directional"`.
3. **No Double Counting:** Impressions from Generative AI blocks must not be added onto standard organic search impressions without explicit separation.
4. **Mandatory UI Disclaimer:**
   > *"AI Block Position reflects the position of the AI Overview block on the search results page. It does not measure citation ranking or brand prominence inside the generated text."*

---

## 10. Summary Table of Metrics & Denominators

| Metric | Official Denominator Type | Required Uncertainty Interval | Publication Quality Requirement |
|:---|:---|:---|:---|
| **Mention Rate** | `valid_answers` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Citation Rate (All Answers)** | `valid_answers` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Citation Rate (Retrieval-Evidence)** | `retrieval_evidence_answers` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Recommendation Rate** | `valid_answers` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Top Recommendation Rate** | `answers_with_recommendations` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Average First Mention Position** | `answers_with_target_mention` | Bootstrap (1,000 resamples) | Must exclude unmentioned (non-zero) |
| **Share of Model** | `all_tracked_entity_mentions` | Bootstrap (1,000 resamples) | Sliced by Engine $\times$ Intent $\times$ Language |
| **Owned-Domain Citation Rate** | `retrieval_evidence_answers` | 95% Wilson Score | Measured ($k \ge 5$) or Directional ($k < 5$) |
| **Source Influence** | N/A | None | Strictly `not_measured` |
| **AI Block Position (GSC)** | SERP Queries | None | Strictly `directional` (SERP layout only) |

---

*GEO-Scope Metric Dictionary v1.0 — Empirical rigor, unambiguous denominators, and honest uncertainty.*
