# GitHub Pinned Repositories Guide

**Profile**: [github.com/tmolavi](https://github.com/tmolavi)  
**Positioning**: AI Systems Architect & GEO / AI Visibility Researcher

---

## Recommended Pinned Repositories & Order

To ensure an external visitor immediately grasps the unified AI Systems Architecture and empirical research stack, configure the **6 Pinned Repositories** in the following exact order:

| Position | Repository | Tier | Role in Architecture |
| :---: | :--- | :--- | :--- |
| **1** | [`tmolavi/geo-scope`](https://github.com/tmolavi/geo-scope) | **Flagship 1** | **Measurement**: Multi-model empirical AI answer visibility measurement framework. |
| **2** | [`tmolavi/sage-audit`](https://github.com/tmolavi/sage-audit) | **Flagship 2** | **Diagnostics**: 3-Pillar static audit engine for technical SEO, JSON-LD AEO, and GEO citation readiness. |
| **3** | [`tmolavi/siteprobe`](https://github.com/tmolavi/siteprobe) | **Flagship 3** | **Remediation**: Autonomous crawler and AST-level safe code remediation engine. |
| **4** | [`tmolavi/hamzad-ai-gateway-resources`](https://github.com/tmolavi/hamzad-ai-gateway-resources) | **Flagship 4** | **Infrastructure**: High-throughput AI inference gateway specifications, routing policies, and fallback contracts. |
| **5** | [`tmolavi/mcp-agent-skills-hub`](https://github.com/tmolavi/mcp-agent-skills-hub) | **Flagship 5** | **Distribution**: Reusable agent skills catalog and MCP integrations for AI coding agents. |
| **6** | [`tmolavi/mcp-geo-server`](https://github.com/tmolavi/mcp-geo-server) | **Protocol** | **Protocol Layer**: Model Context Protocol (MCP) server connecting AI search audits with LLM tooling. |

---

## Architectural Rationale

This exact pinning configuration establishes an intuitive, end-to-end engineering narrative:

```text
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 1. GEO-Scope    │ ──▶  │ 2. SAGE Audit   │ ──▶  │ 3. SiteProbe    │
│  (Measurement)  │      │  (Diagnostics)  │      │  (Remediation)  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 6. MCP Protocol │ ◀──  │ 5. Skills Hub   │ ◀──  │ 4. Hamzad OS    │
│  (Integration)  │      │ (Distribution)  │      │(Infrastructure) │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

1. **Measurement (`geo-scope`)**: Benchmark empirical brand visibility across Perplexity, Gemini, Claude, and GPT-4o with zero silent fallback.
2. **Diagnostics (`sage-audit`)**: Understand and diagnose why pages fail to be cited (DOM extraction, JSON-LD graphs, citation survival proxies).
3. **Remediation (`siteprobe`)**: Safely crawl and apply AST-level code fixes to improve crawler access, schemas, and `/llms.txt`.
4. **Infrastructure (`hamzad-ai-gateway-resources`)**: Route queries reliably with multi-provider latency budgets, fallback policies, and token optimization.
5. **Distribution (`mcp-agent-skills-hub`)**: Equip AI coding agents with production-tested skills and MCP tools.
6. **Protocol (`mcp-geo-server`)**: Expose SEO/AEO/GEO diagnostics natively to Claude Desktop, Cursor, and autonomous agents over MCP.

---

## How to Set Pinned Repositories (GitHub UI Steps)

Since GitHub repository pinning is managed via the GitHub Web UI or GraphQL user profile mutations:

1. Navigate to your public GitHub profile: [github.com/tmolavi](https://github.com/tmolavi).
2. Scroll to the **Pinned** section at the top of the profile.
3. Click **Customize your pins** (or the edit pencil icon).
4. Uncheck any older, deprecated, or miscellaneous repositories.
5. Select the 6 repositories listed above:
   - [x] `geo-scope`
   - [x] `sage-audit`
   - [x] `siteprobe`
   - [x] `hamzad-ai-gateway-resources`
   - [x] `mcp-agent-skills-hub`
   - [x] `mcp-geo-server`
6. Drag and drop the cards into the recommended 1–6 order.
7. Click **Save pins**.
