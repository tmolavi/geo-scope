"""
Base Provider Interface for GEO-Scope
Defines the standard contract for all AI search and LLM engines.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseProvider(ABC):
    """
    Abstract base class for all AI/LLM search engine providers.
    """

    def __init__(self, name: str, display_name: str, bias_description: str = "", cost_per_1k: float = 0.0):
        self.name = name
        self.display_name = display_name
        self.bias_description = bias_description
        self.cost_per_1k = cost_per_1k

    @abstractmethod
    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        """
        Executes a prompt against the AI engine and returns the response string with citations.
        """
        pass

    def is_available(self) -> bool:
        """
        Returns True if the provider is configured (e.g., API key is present or is local/simulation).
        """
        return True

    def estimate_cost(self, prompt_count: int) -> float:
        """
        Returns the estimated API cost in USD for running N prompts.
        """
        return (prompt_count / 1000.0) * self.cost_per_1k

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns serializable provider metadata.
        """
        return {
            "id": self.name,
            "display_name": self.display_name,
            "bias_description": self.bias_description,
            "cost_per_1k_usd": self.cost_per_1k,
            "is_available": self.is_available()
        }
