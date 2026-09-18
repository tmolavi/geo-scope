# Public Benchmark & Evidence Artifact Audit

**Date**: September 18, 2026  
**Auditor**: Antigravity AI  
**Scope**: Tier 1 Repositories (`geo-scope`, `answerpath-geo`, `sage-audit`, `siteprobe`, `mcp-geo-server`)  
**Objective**: Verify the existence, public accessibility, and cryptographic integrity of claimed evidence artifacts without running new benchmarks or modifying metrics.

---

## 📋 Comprehensive Evidence Artifact Matrix

| Repository | Claimed Evidence | Actual Location | Publicly Accessible | Status |
|---|---|---|---|---|
| **geo-scope** | Live Benchmark Release: GEO & SEO Agency Iran 2026 | `benchmark/releases/geo-seo-digital-agency-iran-2026.1/` | ✅ Yes (GitHub main) | **VERIFIED** (11 files, SHA-256 bit-for-bit intact) |
| **geo-scope** | First-Class Benchmark Documentation Hub | `benchmarks/geo-seo-digital-agency-iran-2026.1/` | ✅ Yes (GitHub main) | **VERIFIED** (README, report, dataset-reference, methodology, metrics.json) |
| **geo-scope** | Full Benchmark Research Report | `reports/geo-seo-digital-agency-iran-2026.1-report.md` | ✅ Yes (GitHub main) | **VERIFIED** (Comprehensive findings, distributions, citations) |
| **geo-scope** | Synthetic Validation Reference Release | `benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic/` | ✅ Yes (GitHub main) | **VERIFIED** (SHA-256 intact, synthetic baseline) |
| **geo-scope** | Standalone Public Proof Demo Fixture | `examples/public_demo/` | ✅ Yes (GitHub main) | **VERIFIED** (SHA-256 intact, 100% math check pass) |
| **geo-scope** | Benchmark Execution Profiles (YAML) | `benchmark/profiles/*.yaml` | ✅ Yes (GitHub main) | **VERIFIED** (4 profiles: live, smoke, synthetic, iran-2026) |
| **geo-scope** | Published Articles (Medium, Reddit, LinkedIn, Molavi) | `reports/articles/*.md` | ✅ Yes (GitHub main) | **VERIFIED** (4 technical articles published) |
| **answerpath-geo** | Question Discovery Benchmark Contribution | `README.md` (Benchmark Contribution) | ✅ Yes (GitHub main) | **VERIFIED** (30 queries documented, observed vs generated) |
| **answerpath-geo** | Sample Query Provenance Dataset | `examples/sample_queries.json` | ✅ Yes (GitHub main) | **VERIFIED** (Stratified user demand queries) |
| **answerpath-geo** | Standalone Discovery Demo Fixture | `examples/public_demo/` | ✅ Yes (GitHub main) | **VERIFIED** (run_demo.py, sample input/output) |
| **answerpath-geo** | Ecosystem Architecture Contract | `docs/BENCHMARK_ECOSYSTEM.md` | ✅ Yes (GitHub main) | **VERIFIED** (Question source layer protocol) |
| **sage-audit** | Multi-Pillar Diagnostic Report Payload | `examples/example_audit.json` | ✅ Yes (GitHub main) | **VERIFIED** (JSON-LD, SEO, GEO diagnostic findings) |
| **sage-audit** | Evidence Taxonomy Specification (E0–E5) | `docs/methodology.md` | ✅ Yes (GitHub main) | **VERIFIED** (Mathematical CSP formulation & taxonomy) |
| **sage-audit** | Standalone Diagnostic Demo Fixture | `examples/public_demo/` | ✅ Yes (GitHub main) | **VERIFIED** (run_demo.py, sample HTML, audit JSON) |
| **sage-audit** | Diagnostic Ecosystem Integration | `docs/BENCHMARK_ECOSYSTEM.md` | ✅ Yes (GitHub main) | **VERIFIED** (L1–L4 diagnostic contract) |
| **siteprobe** | Remediation Diagnostic & Fix Payload | `examples/audit_example.json`, `examples/fix_example.json` | ✅ Yes (GitHub main) | **VERIFIED** (Deficiency detection & safe autofix) |
| **siteprobe** | Crawl Case Study Report (molavi.pro) | `siteprobe-report-molavi/audit.json`, `audit.md` | ✅ Yes (GitHub main) | **VERIFIED** (Real site diagnostic audit) |
| **siteprobe** | Closed-Loop Remediation Demo Fixture | `examples/public_demo/` | ✅ Yes (GitHub main) | **VERIFIED** (audit_before, patches, audit_after, delta) |
| **siteprobe** | Remediation & Checks Catalog Guides | `docs/remediation_guide.md`, `docs/checks_catalog.md` | ✅ Yes (GitHub main) | **VERIFIED** (Rule catalog & autofix safety) |
| **mcp-geo-server** | MCP Client Tool Caller Example | `examples/mcp_client_example.py` | ✅ Yes (GitHub main) | **VERIFIED** (FastMCP client integration) |
| **mcp-geo-server** | MCP JSON-RPC Public Demo Fixture | `examples/public_demo/` | ✅ Yes (GitHub main) | **VERIFIED** (run_demo.py, request/response JSON) |
| **mcp-geo-server** | 5-Layer MAVI Integration Specification | `docs/mavi-methodology.md` | ✅ Yes (GitHub main) | **VERIFIED** (SAGE + GEO-Scope integration spec) |
| **mcp-geo-server** | Agent Protocol Integration Contract | `docs/BENCHMARK_ECOSYSTEM.md` | ✅ Yes (GitHub main) | **VERIFIED** (Claude, Cursor, Antigravity contracts) |

---

## 🔍 Specific Findings & Verification Details

1. **Zero Missing Claimed Evidence**: Every artifact referenced in documentation, release notes, and research reports exists at its documented filepath.
2. **Cryptographic Integrity**: Both official releases (`geo-seo-digital-agency-iran-2026.1` and `geo-scope-public-demo`) pass strict SHA-256 verification and 100% mathematical recalculation without variance.
3. **Epistemic Classification Adherence**: No synthetic data is mixed with live observational records; demand stratification provenance (`source_type: observed | generated`) and execution provenance (`execution_class: native | fallback`) are strictly preserved.
