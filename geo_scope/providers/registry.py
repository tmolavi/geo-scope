"""
Provider Registry for GEO-Scope
Allows dynamic discovery, registration, selection, availability checking, and cost estimation of AI models.
"""

from typing import Dict, Any, List, Optional
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.public_research_provider import PublicResearchProvider
from geo_scope.providers.keyless_wrapper_provider import KeylessWrapperProvider
from geo_scope.providers.openrouter_provider import OpenRouterProvider
from geo_scope.providers.openai_provider import OpenAIProvider
from geo_scope.providers.perplexity_provider import PerplexityProvider
from geo_scope.providers.gemini_provider import GeminiProvider
from geo_scope.providers.claude_provider import ClaudeProvider
from geo_scope.providers.ollama_provider import OllamaProvider


class ProviderRegistry:
    ALIASES = {
        "openai": "openai_completion",
        "chatgpt_search": "openai_completion",
        "chatgpt": "openai_completion",
        "perplexity": "perplexity_sonar",
        "sonar": "perplexity_sonar",
        "gemini": "gemini_grounding",
        "google": "gemini_grounding",
        "claude": "claude_completion",
        "anthropic": "claude_completion",
        "claude_3_7": "claude_completion",
        "ollama": "ollama_local",
        "openrouter": "openrouter_free",
        "public": "mlvoca_public",
        "keyless": "keyless_local",
    }

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
        self.register(KeylessWrapperProvider())

    def register(self, provider: BaseProvider):
        """
        Registers a new AI model provider.
        """
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[BaseProvider]:
        """
        Retrieves a provider by its unique identifier or alias.
        """
        norm = name.strip().lower()
        canonical_name = self.ALIASES.get(norm, norm)
        return self._providers.get(canonical_name)

    def resolve(self, name: str) -> BaseProvider:
        """
        Retrieves a provider or raises a clear ValueError if unknown.
        """
        p = self.get(name)
        if p is None:
            available = sorted(list(self._providers.keys()) + list(self.ALIASES.keys()))
            raise ValueError(f"Unknown provider: {name!r}. Available providers/aliases: {', '.join(available)}")
        return p

    def list_all(self) -> List[Dict[str, Any]]:
        """
        Returns metadata for all registered providers.
        """
        return [p.get_metadata() for p in self._providers.values()]

    def check_availability(self) -> List[Dict[str, Any]]:
        """
        Returns structured diagnostic information for each provider without exposing secrets.
        """
        rows = []
        ordered_keys = [
            ("OpenAI", "openai_completion", "parametric (direct completion)"),
            ("Perplexity", "perplexity_sonar", "search-grounded"),
            ("Gemini", "gemini_grounding", "search-grounded"),
            ("Anthropic", "claude_completion", "parametric (direct completion)"),
            ("Ollama Local", "ollama_local", "local parametric (direct completion)"),
            ("OpenRouter", "openrouter_free", "parametric (free tier)"),
            ("Keyless Wrapper", "keyless_local", "unverified wrapper"),
            ("Public Research", "mlvoca_public", "public endpoint"),
        ]

        for display, provider_id, grounding in ordered_keys:
            p = self._providers.get(provider_id)
            is_avail = p.is_available() if p else False
            rows.append({
                "provider": display,
                "id": provider_id,
                "configured": "yes" if is_avail else "no",
                "mode_support": "live",
                "grounding": grounding,
            })

        # Simulation baseline is always available in simulation mode
        rows.append({
            "provider": "Simulation",
            "id": "simulation",
            "configured": "yes",
            "mode_support": "simulation",
            "grounding": "synthetic baseline",
        })

        return rows

    def format_availability_table(self) -> str:
        """
        Formats provider availability as an aligned human-readable CLI table.
        """
        data = self.check_availability()
        lines = [
            f"{'Provider':<16} {'Configured':<12} {'Mode support':<14} {'Grounding'}",
            f"{'-'*16} {'-'*12} {'-'*14} {'-'*30}",
        ]
        for row in data:
            lines.append(
                f"{row['provider']:<16} {row['configured']:<12} {row['mode_support']:<14} {row['grounding']}"
            )
        return "\n".join(lines)

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
