# Global AI Answers Benchmark 2026.2 Pilot: Methodology

## 1. Pipeline Architecture
```
AnswerPath GEO
      ↓
Question Discovery (60% Observed User Questions + 40% Research Templates)
      ↓
GEO-Scope Measurement Engine
      ↓
Hamzad AI Gateway (Audited, Isolated Live API Execution)
      ↓
Deterministic Entity Extraction (Multi-Type: People, Companies, Countries, Universities, Tech, Communities)
      ↓
Descriptive Metrics & Cryptographic Release Bundle
```

## 2. Epistemic Principles
- **No Rankings of Humanity**: All metrics measure observed entity mention frequencies without normative scoring.
- **Provenance Tracking**: Prompts preserve `source_reference: "answerpath"` and explicit `source_category` partitions.
- **Provider Class Separation**: `answer_engine` (search-grounded) metrics are strictly isolated from `llm` (pure parametric) metrics.
