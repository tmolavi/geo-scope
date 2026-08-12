# 🔌 Live API Integration Guide

GEO-Scope supports running benchmarks using **Live API Endpoints** (OpenAI, Perplexity, Google Gemini, Anthropic Claude) or using the built-in **High-Fidelity GEO Simulation Engine**.

---

## 1. Setting Up API Keys

Set your environment variables in your terminal or in a `.env` file:

```bash
# OpenAI (ChatGPT Search / GPT-4o)
export OPENAI_API_KEY="sk-proj-..."

# Perplexity AI (Sonar / Sonar Pro Search)
export PERPLEXITY_API_KEY="pplx-..."

# Google Gemini (Gemini 1.5 Pro / Gemini 2.0 with Search Grounding)
export GEMINI_API_KEY="AIzaSy..."

# Anthropic (Claude 3.5 / Claude 3.7 Sonnet)
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 2. Model Adapters Implementation

### A. Perplexity API (Sonar Pro Search)
```python
import httpx

async def query_perplexity_sonar(prompt: str, api_key: str) -> str:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "return_citations": True
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

### B. OpenAI GPT-4o with Search
```python
import httpx

async def query_chatgpt_search(prompt: str, api_key: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

### C. Google Gemini with Search Grounding
```python
import httpx

async def query_gemini_grounding(prompt: str, api_key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.2}
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
```

---

## 3. Rate Limiting & Cost Estimation

For a standard 1,000 prompt benchmark across 4 models (4,000 total inferences):

| Model | Cost per 1,000 queries (approx.) | Concurrency Limit |
| :--- | :--- | :--- |
| Perplexity Sonar Pro | ~$5.00 | 20 req/sec |
| OpenAI GPT-4o Search | ~$7.50 | 50 req/sec |
| Google Gemini 1.5 Pro | ~$3.50 | 30 req/sec |
| Claude 3.7 Sonnet | ~$8.00 | 20 req/sec |
| **Total Full Run** | **~$24.00** | **~3-5 minutes total execution** |
