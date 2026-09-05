# Free and local access

Reviewed against operator documentation on 2026-09-06. Availability can change. GEO-Scope does not collect shared secret keys or silently switch services.

| Option | Key needed? | Scope and conditions | Integration |
| --- | --- | --- | --- |
| Ollama on your machine | No cloud key | Uses your hardware and an installed model; model licenses apply | `ollama_local` |
| OpenRouter free models | Your own API key | Account quotas apply; only `:free` models or `openrouter/free` accepted | `openrouter_free` |
| MLVoca public API | No | Operator explicitly prohibits commercial use; limited shared hardware | `mlvoca_public`, explicit noncommercial opt-in |
| Pollinations | Yes, currently | Generation requires account/app authorization; old anonymous examples are outdated | Not integrated as a no-key service |
| Recorded responses | No | Analyze responses you are entitled to use; provenance remains user supplied | `--responses` |

## Public noncommercial evaluation

The [MLVoca operator repository](https://github.com/mlvoca/free-llm-api) publishes its endpoint and expressly allows free access, while prohibiting commercial use without permission. This is an optional research path, not a production service guarantee. To use it for an eligible noncommercial evaluation, set `GEO_SCOPE_NONCOMMERCIAL=1` in your environment, then:

```bash
geo-scope run --mode live --models mlvoca_public --count 1 --brand HubSpot
```

Do not use this option for client audits or business workloads without the operator's permission. Prompts go to a third-party public host. Provider errors stop execution; no other accounts or services are tried. Neither this endpoint nor local Ollama measures web-search grounding.

## OpenRouter

Create your own key through the operator's account flow. Set `OPENROUTER_API_KEY` privately. The optional `OPENROUTER_MODEL` can select a specific `:free` model. Default `openrouter/free` can route different requests to different models; the returned model is recorded and comparisons require reviewing it. Free access is limited and is not a promise of unlimited production capacity.

## Operator sources

- [Ollama local authentication](https://docs.ollama.com/api/authentication)
- [Ollama generation API](https://docs.ollama.com/api/generate)
- [OpenRouter FAQ and free-model quotas](https://openrouter.ai/docs/faq)
- [OpenRouter free router](https://openrouter.ai/openrouter/free/)
- [MLVoca endpoint and usage conditions](https://github.com/mlvoca/free-llm-api)
- [Pollinations current API authentication](https://gen.pollinations.ai/docs)
- [Pollinations terms](https://enter.pollinations.ai/terms)
