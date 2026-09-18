# Public Proof Roadmap & Demonstration Strategy

**Author**: [Taghi Molavi](https://molavi.pro)  
**Standard**: Independent verification, reproducible command lines, zero fake claims, strict public/private infrastructure boundaries.

---

## 1. Public Proof Demonstration Strategy Matrix

| Repository | Demo Goal | Input | Output | Reproducibility Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **`geo-scope`** | Reproduce complete empirical AI visibility metrics & 95% bootstrap CIs from raw multi-model completions without network dependencies. | `examples/public_demo/` (Manifest, prompts, 20 completions) | Mention rates, recommendation rates, top-1 share, citation graph, verified checksums. | **100% Offline Deterministic**: Verifiable via `geo-scope benchmark reproduce --dataset examples/public_demo`. |
| **`answerpath-geo`** | Discover search questions, categorize into 5 intent strata, and preserve observed vs generated provenance tags. | Topic string or query logs (e.g., `"GEO agency Iran"`) | Stratified question clusters, intent tags (`commercial`, `compare`, `trust`, `solve`, `buy`), and JSON payload. | **100% Offline Deterministic**: Verifiable via `python examples/public_demo/run_demo.py`. |
| **`sage-audit`** | Audit technical accessibility (L1), semantic extractability (L2), JSON-LD entity clarity (L3), and Citation Survival Proxy (L4). | Live URL or local HTML snapshot fixture (`sample_page.html`) | 3-Pillar diagnostic scorecard (0–100), MAVI layer breakdown, generated `/llms.txt`. | **100% Offline Deterministic**: Verifiable via `python examples/public_demo/run_demo.py`. |
| **`siteprobe`** | Demonstrate the complete closed loop from audit finding to safe atomic code fix and post-fix verification. | Target project fixture & `audit_before.json` | `recommended_changes.json`, applied atomic code diffs, `audit_after.json` score lift. | **100% Offline Deterministic**: Verifiable via `python examples/public_demo/run_demo.py`. |
| **`mcp-geo-server`** | Expose FastMCP tool catalog and execute SAGE audit tools over JSON-RPC for Claude Desktop and Cursor. | MCP Tool Call (`audit_html` / `get_capabilities`) | Structured JSON-RPC diagnostic payload and evidence level classifications (E0–E5). | **100% Offline Deterministic**: Verifiable via `python examples/public_demo/run_mcp_demo.py`. |

---

## 2. Epistemic Classification of Evidence Artifacts

Every artifact in the ecosystem is explicitly tagged with its evidence category:
1. **Live Peer-Reviewed Benchmark Releases** (`benchmark/releases/`): Real multi-provider completions collected through gateway routing, cryptographically signed with SHA-256 hashes.
2. **Demonstration & Verification Fixtures** (`examples/public_demo/`): Lightweight, offline datasets enabling developers to test CLI tools and mathematical reproductions in <10 seconds.
3. **Synthetic Validation Tests** (`tests/`): Unit test fixtures designed to stress-test error handlers, edge cases, and parser fallbacks.
