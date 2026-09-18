# Global AI Answers Benchmark 2026.2 Pilot (`global-ai-answers-2026.2-pilot`)

## Overview
This package is a controlled, live pilot execution validating the complete 7-stage GEO-Scope measurement pipeline across 100 culturally localized prompts in 10 countries, 8 languages, and 5 core human concern categories.

- **Status**: Pilot Benchmark (Peer-Review Ready)
- **Execution Mode**: `live` (Via Hamzad AI Gateway)
- **Prompts**: 100 (60% observed user questions, 40% research templates)
- **Countries**: 10 (Iran, Turkey, Germany, United Kingdom, United States, India, Japan, Saudi Arabia, Brazil, Nigeria)
- **Languages**: 8 (`fa`, `tr`, `de`, `en`, `hi`, `ja`, `ar`, `pt`)
- **Entities Tracked**: 30 Multi-Type Entities

## Cryptographic Verification
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2-pilot
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```
