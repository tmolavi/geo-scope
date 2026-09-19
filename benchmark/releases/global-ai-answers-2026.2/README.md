# Global AI Answers Benchmark 2026.2 (`global-ai-answers-2026.2`)

## Overview
This package is the full-scale empirical benchmark dataset observing generative engine visibility and recommendation patterns across 500 culturally localized prompts in 50 countries, 22+ languages, and 9 core human concern categories.

- **Status**: Published Global Research Release
- **Execution Mode**: `live` (Via Hamzad AI Gateway)
- **Prompts**: 500 (60% observed user questions, 40% research templates)
- **Countries**: 50 (MENA, North America, Europe, Asia Pacific, Latin America, Sub-Saharan Africa)
- **Languages**: 22+ native languages
- **Entities Tracked**: 73 Multi-Type Entities
- **Categories**: 9 Core Life, Career, Technology, and Cultural Concerns

## Verification & Reproduction
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2
```
