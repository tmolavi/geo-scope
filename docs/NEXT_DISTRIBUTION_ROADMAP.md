# Next Distribution Roadmap: PyPI, Hugging Face & Research Publications

**Scope**: Distribution strategy for the **Molavi AI Visibility & Agent Engineering Stack** across packaging registries, machine learning hubs, and scientific publication channels.

---

## 📦 1. PyPI Packaging & Distribution Readiness

| Package | PyPI Package Name | Build System | CLI Entrypoint | Test Suite Status | Publishing Readiness |
|---|---|---|---|:---:|:---:|
| **SAGE Audit** | `sage-audit` | `hatchling` / `pyproject.toml` | `sage` | 51 tests (PASS) | ✅ **100% Ready** (Trusted Publisher workflow configured) |
| **GEO-Scope** | `geo-scope` | `setuptools` / `pyproject.toml` | `geo-scope` | 130 tests (PASS) | ✅ **100% Ready** (CLI & MCP entrypoints verified) |
| **SiteProbe** | `siteprobe` | `setuptools` / `pyproject.toml` | `siteprobe` | 24 tests (PASS) | ✅ **100% Ready** (Autonomous remediation verified) |
| **AnswerPath GEO**| `answerpath-geo` | `flit_core` / `pyproject.toml` | `answerpath` | 4 tests (PASS) | ✅ **100% Ready** (Local question discovery verified) |
| **MCP GEO Server** | `mcp-geo-server` | `setuptools` / `pyproject.toml` | `mcp-geo-server` | 28 tests (PASS) | ✅ **100% Ready** (FastMCP JSON-RPC transport verified) |

### Action Checklist for PyPI Release:
- [ ] Configure GitHub Actions PyPI Trusted Publishing credentials across all 5 repositories.
- [ ] Verify clean installation in isolated environments (`pip install --dry-run`).
- [ ] Tag releases and trigger automated wheel/sdist builds.

---

## 🤗 2. Hugging Face Datasets & Spaces Readiness

The empirical datasets and diagnostic tools are architected for seamless integration into Hugging Face:

### A. Hugging Face Datasets
1. **`tmolavi/geo-seo-iran-2026`**:
   - **Data Format**: Parquet / JSONL containing 120 raw model observations and 30 intent-stratified prompts.
   - **Card**: Full empirical methodology, licensing (CC-BY-4.0 / MIT), and data schema.
2. **`tmolavi/answerpath-query-intents`**:
   - **Data Format**: Stratified query corpus categorized into `commercial`, `compare`, `trust`, `solve`, and `buy` strata.

### B. Hugging Face Spaces (Interactive Demos)
1. **SAGE Multi-Pillar Diagnostic Inspector** (`Streamlit` / `Gradio`):
   - Input: URL or raw HTML snippet.
   - Output: Visual 3-pillar breakdown (SEO 30%, AEO 35%, GEO 35%) with CSP diagnostic gauges.
2. **Molavi AI Visibility Index (MAVI) Dashboard**:
   - Interactive 5-layer waterfall chart demonstrating the fusion of static diagnostics (L1–L4) and empirical multi-model observations (L5).

---

## 📄 3. Research Publication & Technical Articles Readiness

### A. Academic Preprints & Whitepapers
1. **"Empirical Generative AI Visibility: A Methodology for Measuring Brand Mentions, Recommendations, and Grounding in Multi-Model Systems"**
   - **Target**: arXiv (cs.IR / cs.AI) or SSRN.
   - **Artifact Baseline**: [`docs/benchmark-methodology.md`](benchmark-methodology.md), [`reports/geo-seo-digital-agency-iran-2026.1-report.md`](../reports/geo-seo-digital-agency-iran-2026.1-report.md).
2. **"Citation Survival Proxy (CSP): Dense Retrieval Prominence and Semantic Entropy as Static Diagnostic Signals"**
   - **Target**: Information Retrieval & Web Search Conferences (SIGIR / WSDM / WWW workshop tracks).
   - **Artifact Baseline**: [`sage-audit/docs/methodology.md`](https://github.com/tmolavi/sage-audit/blob/main/docs/methodology.md).

### B. Industry Publications & Technical Case Studies (Already Scaffolded)
- [x] **Molavi.pro Research Hub**: [`reports/articles/molavi_pro_article.md`](../reports/articles/molavi_pro_article.md)
- [x] **Medium Deep Dive**: [`reports/articles/medium_article.md`](../reports/articles/medium_article.md)
- [x] **Reddit Technical Architecture Post**: [`reports/articles/reddit_technical_post.md`](../reports/articles/reddit_technical_post.md)
- [x] **LinkedIn Strategic Briefing**: [`reports/articles/linkedin_post.md`](../reports/articles/linkedin_post.md)

---

## 🛡️ Epistemic & Distribution Rules

1. **No Overclaiming**: Publications and dataset cards must emphasize that metrics reflect observed completions from specific routes, not reverse-engineered search ranking weights.
2. **Open Data Principles**: All published datasets must include exact reproduction commands and SHA-256 integrity checksums.
3. **Zero Secret Leakage**: Distribution packages must remain completely decoupled from private backend credentials or infrastructure endpoints.
