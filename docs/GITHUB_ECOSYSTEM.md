# Molavi AI Engineering & Visibility Ecosystem Map

**Architect**: [Taghi Molavi](https://molavi.pro)  
**Framework Overview**: Unified technical landscape connecting question discovery, empirical AI visibility benchmarks, static diagnostics, composite scoring, automated code remediation, and agent execution skills.

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             MOLAVI AI VISIBILITY STACK                           │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. QUESTION DISCOVERY & INTENT STRATIFICATION                                  │
│      └─▶ AnswerPath GEO (https://github.com/tmolavi/answerpath-geo)              │
│          • Mines owned chat logs, search queries, and exploratory templates      │
│          • Categorizes into commercial, compare, trust, solve, and buy intents   │
│                                      │                                           │
│                                      ▼                                           │
│   2. EMPIRICAL AI VISIBILITY BENCHMARK & MULTI-MODEL MEASUREMENT                 │
│      └─▶ GEO-Scope (https://github.com/tmolavi/geo-scope)                        │
│          • Executes standardized prompt suites across GPT-4o, Gemini, Claude,    │
│            and Perplexity Sonar                                                  │
│          • Tracks mentions, recommendations, top-1 share, and citation grounding │
│          • Full routing provenance, SHA-256 release datasets, and 95% bootstrap CIs│
│                                      │                                           │
│                                      ▼                                           │
│   3. STATIC 4-LAYER DIAGNOSTIC ENGINE                                            │
│      └─▶ SAGE Audit (https://github.com/tmolavi/sage-audit)                      │
│          • L1 Technical: robots.txt bot rules (GPTBot, PerplexityBot), clean DOM │
│          • L2 Semantic: 60–120 token chunk boundaries, text-to-code hygiene      │
│          • L3 Entity: JSON-LD graphs (Organization, FAQPage, sameAs Wikidata)    │
│          • L4 Citation Readiness: In-memory RAG simulation & Citation Survival   │
│            Proxy (CSP)                                                           │
│                                      │                                           │
│                                      ▼                                           │
│   4. COMPOSITE INDEXING                                                          │
│      └─▶ MAVI (Molavi AI Visibility Index)                                       │
│          • Balanced 5-layer composite index: L1 + L2 + L3 + L4 + L5              │
│          • Integrates static technical readiness with empirical model observation│
│                                      │                                           │
│                                      ▼                                           │
│   5. AUTONOMOUS REMEDIATION & VERIFICATION                                       │
│      └─▶ SiteProbe (https://github.com/tmolavi/siteprobe)                        │
│          • Automated crawler & safe source code fixer for SEO/GEO/a11y           │
│          • Injects /llms.txt, fixes robots.txt bot access, repairs JSON-LD       │
│          • In-memory snapshots, automatic rollback, and post-fix verification    │
│                                      │                                           │
│                                      ▼                                           │
│   6. PROTOCOL INTEGRATION & AGENT MCP SERVERS                                    │
│      └─▶ MCP GEO Server (https://github.com/tmolavi/mcp-geo-server)              │
│          • Model Context Protocol tools for Cursor, Claude Desktop, Antigravity  │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│                            AGENT ENGINEERING & SKILLS STACK                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   • MCP Agent Skills Hub (https://github.com/tmolavi/mcp-agent-skills-hub)       │
│     Curated production skills and MCP configuration templates for AI agents.     │
│                                                                                  │
│   • n8n Agent Skills (https://github.com/tmolavi/n8n-agent-skills)               │
│     Enterprise n8n workflow architecture, node routing, and linting patterns.    │
│                                                                                  │
│   • Lean Agent Skills (https://github.com/tmolavi/lean-agent-skills)             │
│     Token-efficient, low-context agent skills optimized for cost and speed.      │
│                                                                                  │
│   • Agent Project Discovery Skill (https://github.com/tmolavi/agent-project-discovery-skill)
│     Universal workspace orientation and context extraction skill for coding agents.│
│                                                                                  │
│   • Awesome Skills (https://github.com/tmolavi/awesome-skills)                   │
│     Community-curated repository of developer skills for AI coding assistants.   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATIONS & TOOLING LAYER                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   • Laravel AI Summary (https://github.com/tmolavi/laravel-ai-summary)           │
│     Multi-provider, fallback-ready text summarization package for Laravel.       │
│                                                                                  │
│   • GEO/AEO News Engine (https://github.com/tmolavi/geo-aeo-news-engine)         │
│     Autonomous news rewriting, digital PR syndication, and entity optimization.  │
│                                                                                  │
│   • IVNA App (https://github.com/tmolavi/ivna-app)                               │
│     Intelligent news aggregation and multilingual publishing application.        │
│                                                                                  │
│   • Hamzad AI Gateway Resources (https://github.com/tmolavi/hamzad-ai-gateway-resources)
│     Public routing specifications, fallback schemas, and latency optimization    │
│     patterns for provider-aware AI gateways.                                     │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Closed-Loop Lifecycle

Every component in the ecosystem is designed to interoperate without lock-in or hidden dependencies:

1. **Discover**: Extract genuine user questions using `answerpath-geo`.
2. **Benchmark**: Collect multi-model observations and compute empirical baseline metrics using `geo-scope`.
3. **Diagnose**: Identify technical, entity, and semantic chunking bottlenecks using `sage-audit`.
4. **Index**: Establish a composite baseline score using `MAVI`.
5. **Remediate**: Apply safe, atomic fixes and verify code using `siteprobe`.
6. **Re-measure**: Execute repeated benchmarks in `geo-scope` to quantify empirical lift ($\Delta SoM$, $\Delta Citations$).
