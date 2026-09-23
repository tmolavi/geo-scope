# Benchmark Reproduction & Runtime Environment

This document defines the computational runtime, dependencies, environment variables, expected cost estimations, and checksum verification procedures required to reproduce GEO-Scope benchmarks.

---

## 1. Runtime Specifications

* **Operating System**: macOS 13+ (Ventura, Sonoma, Sequoia), Ubuntu 22.04 LTS+, Debian 12+, Windows 11 with WSL2
* **Python Runtime**: Python `>=3.10` (Target reference: `Python 3.12`)
* **Architecture**: `x86_64` or `arm64` (Apple Silicon supported natively)

---

## 2. Dependency Pinning & Installation

### Option A: Direct Pip Installation
```bash
# Clone the repository
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install package with dev tools
pip install --upgrade pip
pip install -e ".[dev]"
```

### Option B: Deterministic Lockfile
```bash
pip install -r requirements.lock
```

### Key Pinned Dependencies:
* `fastapi>=0.110.0`
* `pydantic>=2.5.0`
* `httpx>=0.26.0`
* `numpy>=1.24.0`
* `pandas>=2.0.0`
* `scikit-learn>=1.3.0`
* `pyyaml>=6.0`
* `pytest>=8.0.0`
* `pytest-asyncio>=0.23.0`

---

## 3. Environment Variables Configuration

For live API execution, configure the following variables in `.env`:

| Variable | Description | Required For |
|:---|:---|:---|
| `PERPLEXITY_API_KEY` | Perplexity Sonar API token | `perplexity_sonar` |
| `GEMINI_API_KEY` | Google AI Studio API key | `gemini_grounding` |
| `OPENAI_API_KEY` | OpenAI Platform API key | `openai_completion`, `chatgpt_search` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | `claude_completion` |
| `HAMZAD_API_URL` | Hamzad Multi-Model Gateway base URL | Hamzad live routes |
| `HAMZAD_API_KEY` | Hamzad Gateway bearer token | Hamzad authenticated routes |

> [!NOTE]
> Offline verification and deterministic replay (`geo-scope benchmark verify`, `geo-scope benchmark replay`) require **zero API keys** and execute completely without network access.

---

## 4. Expected Runtime & Cost Estimates

| Benchmark Release | Mode | Prompts | Providers | Repeats ($k$) | Total Inferences | Expected Runtime | Estimated API Cost |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Global AI Answers 2026.2** | Offline Replay | 500 | 4 | 5 | 10,000 | ~3-5 seconds | $0.00 USD |
| **Global AI Answers 2026.2** | Live Execution | 500 | 4 | 5 | 10,000 | ~45-90 minutes | ~$20.00 - $45.00 USD |
| **Global 2026.2 Pilot** | Offline Replay | 100 | 3 | 5 | 1,500 | < 1 second | $0.00 USD |
| **Golden Parser v1** | Evaluator | 220 | 1 | 1 | 220 | < 0.5 seconds | $0.00 USD |

---

## 5. Checksum Verification Procedure

To verify data integrity against tampering or bitrot:

```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
```

All hashes are computed using standard SHA-256 over raw file bytes.
