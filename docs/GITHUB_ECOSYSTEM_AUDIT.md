# GitHub Ecosystem Authority Audit — All 15 Public Repositories

**Author**: [Taghi Molavi](https://molavi.pro)  
**Date**: September 2026  
**Scope**: Complete audit of all 15 public repositories under `@tmolavi`  
**Standard**: Evidence-driven, reproducible, no exaggerated marketing claims, strict public/private infrastructure separation.

---

## 1. Repository Audit Matrix

| Repository | Purpose | README | Tests | Docs | Examples | Topics | Status & Gaps Identified |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`geo-scope`** | Multi-model empirical AI visibility & recommendation benchmark engine | ✅ Complete (380+ lines) | ✅ 130 tests | ✅ Extensive | ✅ Full | ✅ Complete (12) | **Production / Benchmark Ready**: Published `2026.1` benchmark release with SHA-256 verification and 95% bootstrap CIs. |
| **`sage-audit`** | 3-Pillar static audit engine for Technical SEO, JSON-LD AEO, and GEO/CSP | ✅ Complete (520+ lines) | ✅ 45 tests | ✅ Complete | ✅ Yes | ✅ Complete (12) | **Production Ready**: 4 diagnostic layers (L1–L4) fully documented and integrated with MAVI composite index. |
| **`mcp-geo-server`** | FastMCP server exposing GEO/AEO audit tools for Claude, Cursor, and IDEs | ✅ Complete (180+ lines) | ✅ 12 tests | ✅ Complete | ⚠️ Basic | ✅ Complete (11) | **Active**: Needs standardized ecosystem architecture diagram and MAVI cross-references. |
| **`siteprobe`** | Autonomous website auditor & safe local code fixer for SEO/GEO/a11y | ✅ Complete (440+ lines) | ✅ 88 tests | ✅ Complete | ✅ Yes | ✅ Complete (20) | **Active / Action Layer**: Added "From Measurement To Action" closed-loop remediation workflow. |
| **`answerpath-geo`** | Privacy-first SEO/GEO question discovery and search intent mining engine | ✅ Complete (170+ lines) | ✅ 16 tests | ✅ Complete | ⚠️ Basic | ⚠️ Missing on GitHub | **Active / Discovery Layer**: Generated 30 benchmark prompts; needs GitHub topics & description sync. |
| **`geo-aeo-news-engine`** | Autonomous news rewriting, syndication, and digital PR GEO optimizer | ✅ Present (120 lines) | ⚠️ Missing | ⚠️ Basic | ✅ Yes | ✅ Present (7) | **Application Engine**: Needs standardized README sections, ecosystem links, and tests. |
| **`mcp-agent-skills-hub`** | Curated catalog of production AI agent skills & MCP server configurations | ✅ Present (180 lines) | ⚠️ N/A (Skill repo) | ✅ Complete | ⚠️ Basic | ✅ Complete (20) | **Active Catalog**: Needs updated cross-references to newer GEO and SAGE skills. |
| **`n8n-agent-skills`** | Production-grade n8n workflow patterns, node routing, and linting skills | ✅ Complete (310 lines) | ⚠️ N/A (Skill repo) | ✅ Complete | ✅ Yes | ✅ Complete (21) | **Active Catalog**: Needs standardized ecosystem architecture diagram and author credentials. |
| **`lean-agent-skills`** | Token-optimized, high-density agent skills for lower context overhead | ✅ Complete (240 lines) | ⚠️ N/A (Skill repo) | ✅ Complete | ⚠️ Basic | ✅ Complete (20) | **Active Catalog**: Needs standardized ecosystem links and evidence benchmarks. |
| **`agent-project-discovery-skill`**| Universal workspace startup & context discovery skill for coding agents | ✅ Present (210 lines) | ⚠️ N/A (Skill repo) | ⚠️ Basic | ✅ Yes | ✅ Present (12) | **Active Tool**: Needs standardized cross-repo links to the AI Visibility and Agent stacks. |
| **`awesome-skills`** | Curated list of agent skills, MCP tools, and LLM coding assistants | ✅ Fork upstream | ⚠️ N/A | ⚠️ Basic | ⚠️ Basic | ⚠️ Missing on GitHub | **Curated Fork**: Needs GitHub topics, ecosystem positioning, and link to profile index. |
| **`laravel-ai-summary`** | Provider-agnostic, multi-fallback AI summarization engine for Laravel | ✅ Present (150 lines) | ✅ 8 tests | ⚠️ Basic | ⚠️ Basic | ✅ Complete (11) | **Package**: Needs updated architecture diagram, live test examples, and ecosystem connections. |
| **`tmolavi`** | Root GitHub Profile README and authoritative public project directory | ⚠️ Needs Update | ⚠️ N/A | ⚠️ Basic | ⚠️ Basic | ⚠️ Missing on GitHub | **Profile Entry Point**: Needs restructuring into the 3 clear pillars (AI Visibility, Agent Engineering, Applications). |
| **`ivna-app`** | News aggregator client and media publishing app powered by AI tooling | ⚠️ Minimal (70 lines) | ⚠️ Basic | ⚠️ Basic | ⚠️ Basic | ⚠️ Missing on GitHub | **Application**: Needs complete standardized README explaining its architecture, AI summary pipeline, and features. |
| **`hamzad-ai-gateway-resources`**| Reusable templates, routing policies, and latency configs for AI gateways | ❌ Empty repo | ⚠️ None | ⚠️ None | ⚠️ None | ⚠️ Missing on GitHub | **Orphaned / Empty**: Needs complete scaffold with architectural patterns, gateway contracts, and sanitized routing specs. |

---

## 2. Gaps & Remediation Strategy

### Gap 1: Empty Repository (`hamzad-ai-gateway-resources`)
* **Problem**: Cloned empty, lacks README, architecture description, and examples.
* **Remediation**: Build a comprehensive, sanitized architectural repository containing provider routing templates, fallback schemas, latency optimization guides, and benchmark integration specifications without exposing private operational secrets.

### Gap 2: Missing Metadata & GitHub Topics
* **Problem**: `answerpath-geo`, `tmolavi`, `ivna-app`, `hamzad-ai-gateway-resources`, and `awesome-skills` lack GitHub descriptions or repository topics.
* **Remediation**: Execute `gh repo edit` across all 5 repositories to attach accurate descriptions, homepages, and categorized topics.

### Gap 3: Missing Cross-Repository Interlinking
* **Problem**: Standalone repositories (`laravel-ai-summary`, `ivna-app`, `mcp-geo-server`) do not clearly indicate how they fit into the broader Molavi AI engineering ecosystem.
* **Remediation**: Inject standardized `## Related Projects` sections linking to `docs/BENCHMARK_ECOSYSTEM.md` and related sibling engines.

### Gap 4: GitHub Profile Entry Point (`tmolavi`)
* **Problem**: Profile lists repositories without clear architectural clustering or evidence backing.
* **Remediation**: Re-author `tmolavi/README.md` as the unified entry point, grouping projects into **AI Visibility Stack**, **Agent Engineering Stack**, and **Applications & Tools**, backed by empirical benchmark results and multilingual accessibility.
