"""Optional public research endpoint, enabled only for noncommercial evaluation."""

import os
from geo_scope.providers.ollama_provider import OllamaProvider


class PublicResearchProvider(OllamaProvider):
    def __init__(self):
        super().__init__()
        self.name = "mlvoca_public"
        self.display_name = "MLVoca public research (noncommercial only)"
        self.host = "https://mlvoca.com"
        self.model = "tinyllama"
        self.bias_description = "Public direct completion; no web search. Noncommercial use only."

    def is_available(self):
        return os.getenv("GEO_SCOPE_NONCOMMERCIAL") == "1"

    async def generate_response(self, prompt_item):
        if not self.is_available():
            raise ValueError(
                "MLVoca permits noncommercial use only. Read docs/FREE_ACCESS.md and set GEO_SCOPE_NONCOMMERCIAL=1 only when applicable."
            )
        return await super().generate_response(prompt_item)
