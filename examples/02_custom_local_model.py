"""
Example 02: Adding a Custom Local Model (e.g. Ollama / DeepSeek / vLLM)
"""

import httpx
from geo_scope.engine.feature_extractor import parse_model_response

async def query_local_ollama(prompt: str, model_name: str = "deepseek-r1:14b") -> str:
    """
    Connects to local Ollama server running on http://localhost:11434
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(url, json=payload)
            return res.json().get("response", "")
    except Exception as e:
        return f"Error connecting to local Ollama: {e}"

if __name__ == "__main__":
    prompt_meta = {
        "id": "test_001",
        "query": "What is the best CRM software for startups in 2026?",
        "intent": "commercial_direct",
        "target_brand": "HubSpot",
        "expected_entities": ["HubSpot", "Salesforce", "Zoho CRM"]
    }
    
    mock_local_response = """
    Based on recent developer feedback, here are the top picks:
    1. **HubSpot**: Great free tier and intuitive interface.
    2. **Zoho CRM**: Highly customizable.
    
    Sources:
    - [Reddit discussion](https://reddit.com/r/sales/comments/crm)
    - [G2 CRM grid](https://g2.com/categories/crm)
    """
    
    parsed = parse_model_response(prompt_meta, "local_deepseek", mock_local_response)
    print("Parsed Local Model Output:")
    print(parsed)
