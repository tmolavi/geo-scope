# Competitive Methodology Review: Regional & International GEO Audit Tools (October 2026)

**Document Identifier:** `GEO-SCOPE-COMP-2026-10`  
**Scope:** Independent technical capability and methodology audit of publicly available GEO/AI Visibility tools (`GPTDoctors.ir` and `RankGen.net/geo-score`) compared to the GEO-Scope framework  
**Status:** Canonical Competitive Review  
**Auditor:** GEO-Scope Research & Industry Benchmark Group  

---

## 1. Executive Summary & Objective

As generative engine optimization (GEO) and AI visibility scoring transition from emerging concepts into commercial software products, multiple tools have entered the market with differing architectures, scoring models, and validation claims.

The purpose of this review is to conduct an **objective, evidence-based audit** of the publicly documented capabilities of two prominent tools in the Iranian and global GEO landscape:
1. **GPTDoctors / Aramis GEO AI** (`https://www.gptdoctors.ir/`)
2. **RankGen AI Visibility Score** (`https://rankgen.net/geo-score`)

This audit records publicly stated claims, independently verified capabilities, disclosed methodologies, validation evidence, and unknown technical attributes without inferring malicious intent or fraudulent misrepresentation.

---

## 2. Independent Audit: GPTDoctors / Aramis GEO AI (`gptdoctors.ir`)

### 2.1 Product Overview
- **Domain:** `https://www.gptdoctors.ir/`
- **Branding / Platform Name:** Aramis GEO AI / GPTDoctors
- **Target Market:** Iranian businesses, content teams, digital agencies (`fa-IR`)
- **Stated Positioning:** "AI Website Analysis & GEO Audit — چرا هوش مصنوعی رقیب شما را پیشنهاد می‌دهد، اما برند شما را نه؟"

### 2.2 Public Claims Made
1. **Multi-Model Coverage:** Claims to analyze brand visibility across ChatGPT, Google Gemini, and Perplexity.
2. **Tri-Partite Scoring:** Reports three distinct scores out of 100:
   - SEO Score (`امتیاز سئو`): e.g., 78/100
   - Content Quality Score (`کیفیت محتوا`): e.g., 84/100
   - AI Visibility (`رؤیت‌پذیری در AI`): e.g., 61/100
3. **Instant Free Audit:** Offers an input form where entering a domain name (e.g., `example.com`) generates an immediate analysis without requiring credentials.
4. **Actionable Recommendations:** Claims to deliver specific roadmap steps for content and technical GEO optimization.
5. **Commercial Pricing Tiers:**
   - Starter: $120 / month
   - Professional: $290 / month
   - Enterprise: Custom

### 2.3 Features Independently Verified
- **Frontend Architecture:** Built using modern Next.js (App Router, Tailwind CSS, Persian RTL typography).
- **Public Entry Flow:** Accessible URL input form for single-domain analysis.
- **Marketing & Social Proof:** Surfaces agency case references (e.g., Noah brand marketing team).

### 2.4 Methodology Disclosed
- **Black-Box Composite Score:** The specific mathematical relationship between the 3 reported sub-scores (SEO, Content Quality, AI Visibility) and any underlying prompt completions is not publicly published.
- **Query Strategy:** The public documentation does not disclose:
  - Which specific prompts are executed;
  - Whether live API completions are initiated in real time upon domain entry or retrieved from pre-indexed heuristics;
  - How entity name collisions or negative homonyms (e.g., brand name identical to a generic noun) are handled.
- **Grounding & Provider Verification:** No proof of search grounding or raw completion logs are provided to the end user.

### 2.5 Validation Evidence Available
- Public customer testimonials on landing page.
- No public cryptographic checksums, raw observation logs, or open reproducibility datasets are published.

### 2.6 Technical Unknowns
- Are live queries sent to ChatGPT/Gemini/Perplexity for each free domain audit, or is the free audit a heuristic static analysis of on-page HTML?
- Does the system calculate binomial confidence intervals (e.g., Wilson 95% CI) to account for LLM sampling variance?
- How are failed provider calls or model rate limits accounted for in the denominator?

---

## 3. Independent Audit: RankGen AI Visibility Score (`rankgen.net/geo-score`)

### 3.1 Product Overview
- **Domain:** `https://rankgen.net/geo-score`
- **Company:** RankGen
- **Target Market:** Global English-language digital marketers and enterprise brands
- **Stated Positioning:** "AI Visibility Score Methodology — How RankGen Scores Your Brand (0–100)"

### 3.2 Public Claims Made
1. **8-Dimension Heuristic Score:** Claims an authoritative 0–100 score calculated across 8 specific dimensions:
   - Category Clarity (0–15 pts)
   - Educational Depth (0–20 pts)
   - Comparison Content (0–15 pts)
   - Authority Tone (0–10 pts)
   - FAQ Presence (0–10 pts)
   - Brand Repetition (0–10 pts)
   - Structured Content / JSON-LD (0–10 pts)
   - Geographic Clarity (0–10 pts)
2. **Empirical Correlation Claim:** States that these 8 dimensions "research and empirical testing have shown to correlate with AI brand recommendation frequency."
3. **AI Enhancement Layer:** Claims an AI layer evaluates semantic relevance beyond raw keyword counts.

### 3.3 Features Independently Verified
- **Transparent Formula Weights:** Full point breakdown (15 + 20 + 15 + 10 + 10 + 10 + 10 + 10 = 100) is openly published with exact threshold criteria (e.g., page word count brackets, H1/title category placement).
- **Comprehensive Reference Documentation:** Extensive glossary, methodology breakdown, and dimension explanations.

### 3.4 Methodology Disclosed
- **Crucial Architectural Revelation:** RankGen's AI Visibility Score is explicitly an **on-page crawler heuristic**, NOT an empirical measurement of live AI responses!
- As stated in their own documentation:
  > *"The AI Visibility Score is a heuristic composite score calculated by crawling and analyzing a brand's website. It evaluates eight dimensions..."*
- RankGen crawls the customer's HTML pages and evaluates content attributes. It does not measure whether ChatGPT or Gemini actually mentions or recommends the brand when asked neutral buyer queries.

### 3.5 Validation Evidence Available
- Published methodology page with rule definitions.
- No statistical regression coefficients, sample sizes, $p$-values, or benchmark datasets proving the claimed correlation between the 8 heuristic dimensions and actual LLM visibility are provided.

### 3.6 Technical Unknowns
- What empirical dataset was used to derive the 15/20/15/10/10/10/10/10 weighting schema?
- Is there an empirical verification phase where live LLM queries validate the on-page score against observed AI search rankings?

---

## 4. Comparative Synthesis Matrix: GEO-Scope vs. Competitors

| Dimension | GPTDoctors / Aramis GEO AI | RankGen (`rankgen.net`) | GEO-Scope (`tmolavi/geo-scope`) |
| :--- | :--- | :--- | :--- |
| **Measurement Type** | Instant Domain Audit (Composite) | On-Page HTML Crawler Heuristic | Multi-Model Empirical Observation & Evidence |
| **Methodology Transparency** | Proprietary / Black-Box | Fully Disclosed On-Page Heuristics | Open-Source Contract v1.0 & Formal Metric Dictionary |
| **Actual AI Query Execution** | Claimed across ChatGPT/Gemini/Perplexity | None (Crawl-only heuristic) | Verified Live Search-Grounded APIs (144 runs in 2026.1) |
| **Metric Separation** | Single composite score | Single 0–100 score | Strict Separation: $\text{Mention} \neq \text{Citation} \neq \text{Rec} \neq \text{Position}$ |
| **Uncertainty & Sample Size** | Not reported | Not applicable (Deterministic formula) | Explicit $n$, Wilson 95% CI, Bootstrap CI on all metrics |
| **Raw Evidence Preserved** | None provided | None | Complete `raw_responses.jsonl` with timestamps & signatures |
| **Offline Reproducibility** | No | Partially (re-crawl HTML) | Full offline replay via `geo-scope replay` (0 network calls) |
| **Regional Language Support** | Persian (`fa-IR`) | English (`en-US`) | Multilingual: `fa-IR`, `tr-TR`, `az-AZ`, `ar-AE`, `en-US` |
| **Entity Disambiguation** | Unknown | Keyword substring | 3 Match Tiers, ZWNJ, Casing, Negative Homonym masking |

---

## 5. Strategic Takeaway for InTen

1. **Market White Space:** Competitors either rely on black-box composite scores without raw evidence (GPTDoctors) or purely on-page crawling heuristics disguised as AI visibility scores (RankGen).
2. **The "Readiness vs. Observed" Opportunity:** By clearly distinguishing between **Technical Readiness (Heuristic)** and **Observed Visibility (Empirical Live Evidence)**, InTen can deliver the market's first scientifically honest, auditable, and transparent GEO product.
