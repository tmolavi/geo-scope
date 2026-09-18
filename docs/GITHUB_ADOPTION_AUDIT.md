# GitHub Ecosystem Adoption Audit — Usability & Verification Matrix

**Author**: [Taghi Molavi](https://molavi.pro)  
**Scope**: 15 Public Repositories under `@tmolavi`  
**Standard**: 5-minute developer onboarding, verifiable local execution, reproducible datasets, zero fake metrics.

---

## 1. Ecosystem Usability & Adoption Matrix

| # | Repository | Install | Quick Start | Example | Tests | CI | Demo | Release | Status |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | [**`geo-scope`**](https://github.com/tmolavi/geo-scope) | `pip install -e .` | `geo-scope --help` | `examples/01_quickstart.py` | 130 Passed | ✅ Active | ✅ Terminal Demo | v2026.1.1 | **Adoption Ready**: Instant 5-min demo, verified release package, SHA-256 integrity, 95% bootstrap CIs. |
| **2** | [**`answerpath-geo`**](https://github.com/tmolavi/answerpath-geo) | `pip install -e .` | `answerpath "Topic"` | `examples/sample_queries.json` | 4 Passed | ✅ Active | ✅ CLI Discovery | v2026.1.1 | **Adoption Ready**: 30 stratified benchmark queries, clean observed vs generated provenance tags. |
| **3** | [**`sage-audit`**](https://github.com/tmolavi/sage-audit) | `pip install -e .` | `sage https://example.com` | `examples/example_audit.json` | 51 Passed | ✅ Active | ✅ Static 3-Pillar | v2026.1.1 | **Adoption Ready**: Deterministic L1–L4 diagnostics, llms.txt generator, Citation Survival Proxy (CSP). |
| **4** | [**`siteprobe`**](https://github.com/tmolavi/siteprobe) | `pip install -e .` | `siteprobe audit <url>` | `examples/fix_example.json` | 24 Passed | ✅ Active | ✅ Audit→Fix→Verify | v2026.1.1 | **Adoption Ready**: Safe local file modifier with in-memory snapshots and rollback proof. |
| **5** | [**`mcp-geo-server`**](https://github.com/tmolavi/mcp-geo-server) | `pip install -e .` | `mcp-geo-server` | `examples/mcp_client_example.py`| 28 Passed | ✅ Active | ✅ MCP Inspector | v2026.1.1 | **Adoption Ready**: FastMCP server with standard JSON-RPC tools for Claude, Cursor, and Antigravity. |
| **6** | [**`mcp-agent-skills-hub`**](https://github.com/tmolavi/mcp-agent-skills-hub) | Skill copy | Copy to `.agents/skills` | Indexed tables | Specs | ⚠️ Spec | ✅ Multi-agent | v1.0.0 | **Usable Catalog**: 270+ curated skills with categorized index and security guardrails. |
| **7** | [**`n8n-agent-skills`**](https://github.com/tmolavi/n8n-agent-skills) | Skill copy | Copy to agent dir | Workflow JSONs | Specs | ⚠️ Spec | ✅ n8n Routing | v1.0.0 | **Usable Catalog**: Production n8n patterns, linting rules, and MCP tool routers. |
| **8** | [**`lean-agent-skills`**](https://github.com/tmolavi/lean-agent-skills) | Skill copy | Copy to agent dir | Context specs | Specs | ⚠️ Spec | ✅ Token Frugal | v1.0.0 | **Usable Catalog**: Token-optimized skills designed for low context overhead. |
| **9** | [**`agent-project-discovery-skill`**](https://github.com/tmolavi/agent-project-discovery-skill) | Single file | Add `AGENTS.md` | `examples/*.md` | Specs | ⚠️ Spec | ✅ Sleep-Well | v1.2.0 | **Usable Tool**: Universal codebase startup & context discovery for autonomous coding agents. |
| **10**| [**`awesome-skills`**](https://github.com/tmolavi/awesome-skills) | Curated list | Browse index | Markdown list | N/A | ⚠️ Spec | ✅ Agent Directory | Main | **Curated Catalog**: Community index of Agent Skills, MCP servers, and LLM tools. |
| **11**| [**`geo-aeo-news-engine`**](https://github.com/tmolavi/geo-aeo-news-engine) | `pip install -r reqs` | `python generate_press_pack.py` | `templates/*.json` | Scripts | ⚠️ Manual | ✅ Word Packaging | v1.0.0 | **Usable Engine**: 100-angle editorial matrix with automated `.docx` styling and media integration. |
| **12**| [**`laravel-ai-summary`**](https://github.com/tmolavi/laravel-ai-summary) | `composer require` | `AiSummary::text(...)` | Controller sample | 8 Passed | ✅ Active | ✅ Livewire Demo | v1.0.0 | **Adoption Ready**: Multi-provider fallback summarization engine with built-in caching. |
| **13**| [**`ivna-app`**](https://github.com/tmolavi/ivna-app) | `flutter run` | Download APK / Bazaar | Store listing | App UI | ⚠️ Mobile | ✅ Mobile Reader | v1.0.0 | **Public Client**: Production Flutter app with SQLite caching and AI summary ingestion. |
| **14**| [**`hamzad-ai-gateway-resources`**](https://github.com/tmolavi/hamzad-ai-gateway-resources) | Schema import | `jsonschema validate` | `examples/*.yaml` | Schemas | ✅ Active | ✅ Route Validation| v1.0.0 | **Specification**: Formal JSON Schema v1.0, YAML fallback policies, latency profiles. |
| **15**| [**`tmolavi`**](https://github.com/tmolavi) | Profile View | Browse entry point | Stack tables | N/A | N/A | ✅ Multilingual | Live | **Authoritative Index**: 3-pillar ecosystem entry point with 5-language navigation. |

---

## 2. Adoption Friction & Remediation Plan

### Friction 1: Missing Runnable Examples in Tier 1
* **Problem**: New developers exploring `answerpath-geo`, `sage-audit`, and `siteprobe` lacked concrete sample output files in `examples/`.
* **Fix**: Provide verified sample JSON outputs (`examples/sample_queries.json`, `examples/example_audit.json`, `examples/fix_example.json`, `examples/mcp_client_example.py`).

### Friction 2: Missing Automated CI Workflows
* **Problem**: `answerpath-geo` and `sage-audit` lacked `.github/workflows/test.yml`, giving visitors no visual proof of passing builds.
* **Fix**: Added GitHub Actions workflows executing mocked, deterministic unit tests on Python 3.10/3.11/3.12 with zero secret requirements.

### Friction 3: Missing Community Issue & PR Templates
* **Problem**: Contributors had no structured issue templates for bug reports and feature requests.
* **Fix**: Standardized `.github/ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`), `PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md`, and `SECURITY.md` across Tier 1 repositories.
