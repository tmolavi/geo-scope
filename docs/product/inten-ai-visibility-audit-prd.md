# Product Requirement Document (PRD): InTen AI Visibility Evidence Audit

**Document Identifier:** `INTEN-PRD-AIVIS-2026.1`  
**Product Name:** InTen AI Visibility Evidence Audit  
**Target Repository & Integration:** `aether-nexus-site` (InTen client portal & admin suite)  
**Proposed Route:** `/client/tools/ai-visibility-audit` (or `tools.ai-visibility-audit.tsx`)  
**Status:** Feature Flagged (`FEATURE_AI_VISIBILITY_AUDIT_ENABLED=true`, Read-Only MVP)  
**Author:** InTen Product & AI Visibility Research Team  

---

## 1. Executive Summary & Product Vision

### 1.1 The Market Problem
Existing generative engine optimization (GEO) tools in the regional market suffer from two major flaws:
1. **Black-box scores without verifiable evidence:** Tools like GPTDoctors present arbitrary 0–100 composite scores without disclosing underlying prompts, sample sizes, confidence intervals, or raw responses.
2. **On-page heuristics disguised as AI visibility:** Tools like RankGen calculate an "AI Visibility Score" by merely crawling the customer's HTML pages, never querying live AI search engines to observe real recommendations.

### 1.2 The InTen Value Proposition
**InTen AI Visibility Evidence Audit** is the first evidence-first, auditable AI visibility platform built specifically for regional commercial markets (Iran, Türkiye, Azerbaijan, UAE).
- It strictly separates **Heuristic Technical Readiness (L1–L4)** from **Empirical Observed Visibility (L5)**.
- It delivers bit-for-bit reproducible evidence, cryptographic raw response logs, and Wilson 95% confidence intervals.
- **Foundational Axiom:**
  $$\text{Mention} \neq \text{Citation} \neq \text{Recommendation} \neq \text{Position} \neq \text{Share of Model}$$

---

## 2. Free Tier MVP Specification

### 2.1 Scope & Constraints
- **Target User:** Prospective clients, SEO specialists, digital agency marketing leads.
- **Input Parameters:**
  - `domain`: Target company domain (e.g. `novin.com`, `webtures.com`).
  - `locale`: Primary target market (`fa-IR`, `tr-TR`, `en-US`, `az-AZ`, `ar-AE`).
- **Cost Ceiling:** $0.00 (Zero external paid API calls).
- **Execution Mode:** Local heuristic scan and entity consistency analysis.

### 2.2 Free MVP Audit Modules
1. **Technical AI Readiness Scan:**
   - Evaluates on-page semantic structure (Title, H1, H2/H3 hierarchy, schema.org JSON-LD).
   - Evaluates `llms.txt` and `robots.txt` AI crawler accessibility (GPTBot, PerplexityBot, Google-Extended).
   - UGC Fresh Data readiness check (dates, author credentials, structured QA blocks).
2. **Entity Consistency & Ambiguity Detection:**
   - Multi-lingual name normalization across Persian, Turkish, Arabic, and English.
   - Negative homonym risk assessment (flags collisions like brand name colliding with generic vocabulary or geographic locations).
3. **Explicit Separation of Readiness vs. Empirical Findings:**
   - Free report clearly displays:
     - **Technical Readiness Score:** Heuristic (0–100) based on verified crawler capabilities.
     - **Observed Live AI Visibility:** Clearly marked as **`NOT_MEASURED (Requires Live Empirical Sampling)`**.
     - No misleading estimated visibility numbers without real completions.

---

## 3. Paid Phase Specification (Scheduled Live Benchmarking)

### 3.1 Scheduled Multi-Provider Measurements
- **Target Search-Grounded Engines:**
  - ChatGPT Search (`gpt-4o` web search)
  - Google Gemini Grounding (`gemini-2.5-flash`)
  - Perplexity Sonar (`sonar-pro`)
  - Claude with Search (when search capability is enabled)
  - Hamzad AI Gateway (regional inference router)
- **Controlled Prompt Matrix:**
  - 12–24 localized commercial buyer intent prompts per locale (Best/Recommendation, Comparison, Pricing/Vendor Selection, Criteria/Guidance).
  - Repeated sampling ($k \ge 2$) to capture probabilistic output variance.

### 3.2 High-Fidelity Metrics (with Explicit Denominators & Confidence Intervals)
Every reported metric includes $(k/N)$, denominator type, and Wilson 95% confidence interval:
- **Brand Mention Rate (%):** Rate at which the brand appears in answer text.
- **Explicit Recommendation Rate (%):** Rate of active linguistic endorsements (e.g. "We recommend...", "Top choice").
- **Citation Rate (%):** Frequency of hyperlinked citations pointing to owned domains.
- **Source Domain Provenance:** Breakdown of domains cited, separating direct publisher URLs from intermediary redirect tokens (e.g., `vertexaisearch.cloud.google.com`).
- **First Mention Position:** Earliest paragraph or list index where the entity is named.
- **Share of Voice (SOV %):** Brand mentions relative to all competitor mentions across the prompt suite.

### 3.3 Raw Evidence Preservation & Verification
- Clients can inspect the full, unedited prompt and raw AI response for every single observation.
- Cryptographic SHA-256 bundle verification allows third-party auditors to verify that results were not altered.

### 3.4 Longitudinal Tracking & Actionable Prioritization
- Historical trend lines comparing visibility, recommendation rate, and citation share across weekly or monthly runs.
- **Prioritized Task Backlog:**
  1. *Ecosystem Outreach:* Identify top cited third-party directories/blogs where competitors are cited but customer is missing.
  2. *Schema & Entity Fixes:* Repair missing Organization, Product, and SameAs entity linkages.
  3. *UGC & Editorial Freshness:* Content recommendations designed to trigger AI retrieval freshness thresholds.

---

## 4. Product Guardrails & Ethical Non-Negotiables

1. **No Guaranteed AI Rankings:** InTen will never guarantee that a client will be recommended by an LLM. AI models are non-deterministic, probabilistic systems.
2. **Zero Synthetic Fabrication:** No mock or simulated data will ever be presented as live measurement.
3. **Explicit API Budget Controls:** No paid model API execution without explicit client confirmation and credit balance reservation.
4. **No Automated Live Deployments:** The client tool runs strictly read-only and under permission-based role gates.

---

## 5. Technical Architecture & InTen Codebase Alignment

- **Host Repository:** `aether-nexus-site`
- **Application Architecture:** Vite + React + TanStack Router (`routeTree.gen.ts`).
- **Styling & Design System:** Tailwind CSS, Lucide icons, Dark/Light mode theme tokens consistent with InTen brand.
- **State & Access Control:**
  - Authentication: `src/admin/auth.tsx`
  - Permissions: `src/admin/permissions.tsx` (`can(user, 'view_analytics')`)
  - Feature Flag: `FEATURE_AI_VISIBILITY_AUDIT_ENABLED`
