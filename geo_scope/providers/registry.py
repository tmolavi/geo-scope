"""
Provider Registry for GEO-Scope
Allows dynamic discovery, registration, selection, and cost estimation of AI models.
"""

from typing import Dict, Any, List, Optional
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.public_research_provider import PublicResearchProvider
from geo_scope.providers.openrouter_provider import OpenRouterProvider
from geo_scope.providers.openai_provider import OpenAIProvider
from geo_scope.providers.perplexity_provider import PerplexityProvider
from geo_scope.providers.gemini_provider import GeminiProvider
from geo_scope.providers.claude_provider import ClaudeProvider
from geo_scope.providers.ollama_provider import OllamaProvider


class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        # Live providers (activated if API keys present)
        self.register(OpenAIProvider())
        self.register(PerplexityProvider())
        self.register(GeminiProvider())
        self.register(ClaudeProvider())
        self.register(OllamaProvider())
        self.register(OpenRouterProvider())
        self.register(PublicResearchProvider())

    def register(self, provider: BaseProvider):
        """
        Registers a new AI model provider.
        """
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[BaseProvider]:
        """
        Retrieves a provider by its unique identifier.
        """
        aliases = {"chatgpt_search": "openai_completion", "claude_3_7": "claude_completion"}
        return self._providers.get(aliases.get(name, name))

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Returns metadata for all registered providers.
        """
        return [p.get_metadata() for p in self._providers.values()]

    def estimate_total_cost(self, provider_names: List[str], prompt_count: int) -> float:
        """
        Calculates the aggregate estimated API cost for a benchmark run.
        """
        total = 0.0
        for name in provider_names:
            p = self.get(name)
            if p:
                total += p.estimate_cost(prompt_count)
        return round(total, 2)


# Global singleton
registry = ProviderRegistry()
