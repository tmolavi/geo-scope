# Dataset Reference: `geo-seo-digital-agency-iran-2026.1`

This document details the file formats, schemas, and fields included in the official release package under `benchmark/releases/geo-seo-digital-agency-iran-2026.1/`.

---

## File Structure

```
benchmark/releases/geo-seo-digital-agency-iran-2026.1/
├── manifest.json              # Benchmark metadata and provenance
├── prompts.jsonl              # All 30 prompts with AnswerPath metadata
├── prompts/
│   ├── observed.jsonl         # 15 real user demand questions
│   └── generated.jsonl        # 15 exploratory hypothesis templates
├── observations.jsonl         # 120 raw multi-model provider completions
├── citations.jsonl            # Extracted citation groundings and URLs
├── entities.json              # Evaluated entities & brand aliases
├── providers.json             # Provider validation and routing metadata
├── metrics.json               # Recomputed statistical metrics and CIs
└── checksums.sha256           # SHA-256 cryptographic checksums
```

---

## Data Schemas

### 1. `manifest.json`
```json
{
  "name": "geo-seo-digital-agency-iran-2026.1",
  "title": "GEO, SEO & Digital Marketing Agency Iran 2026 Benchmark",
  "version": "2026.1",
  "created_at": "2026-09-17T21:40:00Z",
  "execution_mode": "live",
  "prompt_count": 30,
  "observation_count": 120,
  "status": "peer_review_ready"
}
```

### 2. `prompts.jsonl`
```json
{
  "id": "PRM-IR-001",
  "prompt": "بهترین آژانس دیجیتال مارکتینگ و سئو در ایران کدام است؟",
  "intent": "commercial",
  "source_type": "observed",
  "source_reference": "answerpath",
  "cluster": "general_recommendation",
  "language": "fa"
}
```

### 3. `observations.jsonl`
```json
{
  "run_id": "RUN-2026-0917-001",
  "prompt_id": "PRM-IR-001",
  "prompt_text": "بهترین آژانس دیجیتال مارکتینگ و سئو در ایران کدام است؟",
  "requested_provider": "gemini",
  "requested_model": "gemini-2.5-flash",
  "actual_provider": "gemini",
  "actual_model": "gemini-2.5-flash",
  "fallback_active": false,
  "execution_class": "native",
  "response_text": "در ایران آژانس‌های مختلفی در زمینه سئو و دیجیتال مارکتینگ فعالیت می‌کنند...",
  "mentioned_brands": ["Web24", "Novin"],
  "competitor_ranks": {"Web24": 1, "Novin": 2},
  "top1_brand": "Web24",
  "citations": ["https://web24.ir", "https://novin.com"],
  "status": "SUCCESS",
  "latency_ms": 842.5
}
```

### 4. `entities.json`
```json
[
  "Web24",
  "Novin",
  "Dimarketing",
  "Triboon",
  "DMN Agency",
  "Rayan",
  "Hamrah Marketing",
  "Inten"
]
```

---

## Verification & Integrity Check

Verify the entire release directory:
```bash
geo-scope benchmark verify --dataset benchmark/releases/geo-seo-digital-agency-iran-2026.1
```
Expected output:
```text
✓ Checksum Verification PASSED: 11 files verified intact in 'benchmark/releases/geo-seo-digital-agency-iran-2026.1'
```
