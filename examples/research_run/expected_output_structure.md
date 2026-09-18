# Expected Research Output Bundle Contract

Every measurement or replay run executed with GEO-Scope produces a standard, self-contained evidence bundle:

```text
output/research_run_2026_01/
├── manifest.json         # Run metadata, provider classes, and execution timestamps
├── prompts.jsonl          # Input prompt records with source_type and intent metadata
├── raw_responses.jsonl    # Verifiable raw model payloads and latency/usage logs
├── observations.jsonl     # Disambiguated entity observation states
├── metrics.json           # Aggregated metrics separated by metric family
├── errors.jsonl           # Explicit failure logs for any provider timeouts
└── checksums.sha256       # SHA-256 cryptographic hashes for all bundle files
```

## Manifest Schema (`manifest.json`)

```json
{
  "mode": "live",
  "created_at": "2026-09-18T12:00:00Z",
  "n_prompts": 6,
  "n_completions": 12,
  "n_observations": 60,
  "n_errors": 0,
  "providers": ["perplexity_sonar", "gemini_grounding"],
  "provider_classes": {
    "perplexity_sonar": "answer_engine",
    "gemini_grounding": "answer_engine"
  },
  "prompt_source_breakdown": {
    "observed": 4,
    "hypothesis": 2
  },
  "raw_responses_path": "raw_responses.jsonl"
}
```

## Observation Schema (`observations.jsonl`)

Each line represents an independent observation of a specific entity in a specific AI response:

```json
{
  "entity_id": "inten",
  "prompt_id": "q-obs-001",
  "prompt": "بهترین شرکت سئو در ایران برای طراحی سایت فروشگاهی کدام است؟",
  "source_type": "observed",
  "provider": "perplexity_sonar",
  "model": "sonar-pro",
  "provider_class": "answer_engine",
  "execution_mode": "live",
  "status": "success",
  "mentioned": true,
  "person_mentioned": false,
  "recommended": true,
  "top1": true,
  "rank": 1,
  "cited": true,
  "attributed": true,
  "confused_with": [],
  "wrong_entity": false,
  "parser_confidence": 0.95,
  "scoring_status": "scored",
  "intent_type": "recommendation",
  "evidence_snippets": ["Matched brand names: ['اینتن']"]
}
```
