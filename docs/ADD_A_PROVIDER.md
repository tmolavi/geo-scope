# 🤖 How to Add an AI / Search Provider to GEO-Scope

GEO-Scope features a modular, pluggable **Provider Architecture** located in `geo_scope/providers/`.

Contributors can add support for new AI models (e.g. Grok 3, DeepSeek Web, Brave Search LLM, Copilot, Cohere) in just **3 simple steps**.

---

## Step 1: Subclass `BaseProvider`

Create a new file in `geo_scope/providers/your_provider.py`:

```python
import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class YourCustomProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "custom-search-model"):
        super().__init__(
            name="your_custom_provider",
            display_name=f"Custom AI Engine ({model})",
            bias_description="Description of retrieval index & grounding bias",
            cost_per_1k=5.00  # Estimated cost in USD per 1,000 queries
        )
        self.api_key = api_key or os.getenv("CUSTOM_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        """Returns True if the provider is ready to execute calls."""
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        """
        Calls the external API and returns the synthesized text response with Markdown citations.
        """
        query_text = prompt_item.get("query", "")

        # Example API call
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.yourprovider.com/v1/chat",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "prompt": query_text,
                    "search_web": True
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["text_output"]
```

---

## Step 2: Register in `ProviderRegistry`

Open `geo_scope/providers/registry.py` and register your provider:

```python
from geo_scope.providers.your_provider import YourCustomProvider

# Inside ProviderRegistry._register_default_providers():
self.register(YourCustomProvider())
```

---

## Step 3: Add Unit Tests

Add a test in `tests/test_providers.py`:

```python
from geo_scope.providers.registry import registry

def test_custom_provider_registered():
    provider = registry.get("your_custom_provider")
    assert provider is not None
    assert provider.name == "your_custom_provider"
```

Submit a Pull Request using the **New AI Provider** PR template!
