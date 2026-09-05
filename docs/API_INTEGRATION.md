# Live provider integration

GEO-Scope uses the same execution contract in CLI, HTTP and MCP. `simulate` is a seeded, offline demo. `live` calls the selected providers and fails explicitly if configuration, connectivity or inference fails. There is no automatic simulated fallback.

```bash
geo-scope providers
geo-scope run --mode simulate --seed 42 --count 10 --brand HubSpot
geo-scope run --mode live --models perplexity_sonar --count 3 --brand HubSpot
```

Set credentials in your process environment or your host's secret manager. `.env` files are not automatically loaded. Never commit real keys.

| Provider ID | Environment | Response capability |
| --- | --- | --- |
| `perplexity_sonar` | `PERPLEXITY_API_KEY`, optional `PERPLEXITY_MODEL` | Search-enabled Sonar; provider citations retained |
| `gemini_grounding` | `GEMINI_API_KEY`, optional `GEMINI_MODEL` | Google Search tool enabled; grounding metadata retained |
| `openai_completion` | `OPENAI_API_KEY`, optional `OPENAI_MODEL` | Direct completion; not a ChatGPT Search benchmark |
| `claude_completion` | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL` | Direct completion; not a Claude web-search benchmark |
| `ollama_local` | Optional `OLLAMA_HOST`, `OLLAMA_MODEL` | Actual local inference without a cloud key; no web search |
| `openrouter_free` | `OPENROUTER_API_KEY`, optional `OPENROUTER_MODEL` | Free direct-completion models on your own account |
| `mlvoca_public` | `GEO_SCOPE_NONCOMMERCIAL=1` | Optional public noncommercial research endpoint; no key, no web search |

`chatgpt_search` and `claude_3_7` remain compatibility aliases in live mode. Prefer the canonical completion IDs. Simulation uses the four historical profile IDs. Provider API outputs should not be treated as identical to consumer search products.

Select a model available to your account using its model environment variable. Model lifecycle, pricing and quotas are controlled by each provider. No fixed cost per query or completion-time guarantee is made. Actual usage metadata is retained when provided. A 429 or other provider failure stops the run; do not rotate accounts or keys to evade limits.

## Without a cloud key

See [Free and local access](FREE_ACCESS.md). Install and start Ollama separately, pull a model suitable for your machine, set `OLLAMA_MODEL` to its installed name, then run:

```bash
geo-scope run --mode live --models ollama_local --count 3 --brand HubSpot
```

## Recorded-response analysis

Each successful CLI run exports all prompts, raw responses, parsed records, CSVs, and experiment metadata. Reanalyze without any API call:

```bash
geo-scope run --responses results/raw_responses.json --brand HubSpot --out replay
```

Imports are labeled `imported` and preserve their claimed source mode. Importing a file does not independently authenticate its origin. The expected schema is an array of objects with `query_item` (`id`, `query`, `target_brand`, `expected_entities`), `model`, `response_text`, and optional `provenance`.

## Codex / MCP

Launch the installed `geo-scope mcp` command as a stdio MCP server. Call `audit_ai_visibility` with explicit parameters:

```json
{"brand":"HubSpot","prompt_count":3,"mode":"live","models":["ollama_local"],"seed":42}
```

MCP defaults to simulation for an offline first run. Its results include execution mode and response records. The legacy `reverse_engineer_ranking_factors` tool returns labeled research priors, not newly estimated engine weights.

## Interpretation

`search_enabled` means the adapter requested a search-capable API/tool. Inspect grounding metadata for evidence that a particular answer used search. Text URLs alone are unverified references. Direct-completion responses, simulations and grounded answers must be distinguished in any comparison.
