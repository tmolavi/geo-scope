"""
Entity Registry and Multi-lingual Normalization for GEO-Scope.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from geo_scope.entities.models import Entity


def normalize_text(text: str) -> str:
    """
    Normalizes Persian, Arabic, and English text for robust entity matching.
    - Unifies Arabic Yeh (ي, ى) to Persian Yeh (ی)
    - Unifies Arabic Kaf (ك) to Persian Kaf (ک)
    - Replaces Zero-Width Non-Joiner (ZWNJ \u200c) with standard space or normalizes it
    - Removes Arabic tatweel / kashida (ـ)
    - Collapses multiple whitespace
    - Strips leading and trailing whitespace
    """
    if not text:
        return ""
    
    t = str(text)
    
    # Arabic to Persian character mapping
    t = t.replace("\u064a", "\u06cc")  # Arabic Yeh -> Persian Yeh
    t = t.replace("\u0649", "\u06cc")  # Alef Maksura -> Persian Yeh
    t = t.replace("\u0643", "\u06a9")  # Arabic Kaf -> Persian Kaf
    t = t.replace("\u0647\u0654", "\u0647")  # Heh with Hamza above -> Heh
    t = t.replace("\u0640", "")        # Tatweel (Kashida)
    
    # ZWNJ handling
    t = t.replace("\u200c", " ")       # Replace ZWNJ with space for token matching
    t = t.replace("\u200e", "")        # Left-to-right mark
    t = t.replace("\u200f", "")        # Right-to-left mark
    
    # Standardize whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


class EntityRegistry:
    """
    Repository of tracked entities, aliases, key people, and negative disambiguation rules.
    """

    def __init__(self, entities: Optional[List[Entity]] = None):
        self._entities: Dict[str, Entity] = {}
        if entities:
            for e in entities:
                self.register(e)

    def register(self, entity: Entity) -> None:
        """Registers an entity in the registry."""
        self._entities[entity.id] = entity

    def get(self, entity_id: str) -> Optional[Entity]:
        """Retrieves an entity by its ID."""
        return self._entities.get(entity_id)

    def all(self) -> List[Entity]:
        """Returns all registered entities."""
        return list(self._entities.values())

    def ids(self) -> List[str]:
        """Returns all entity IDs."""
        return list(self._entities.keys())

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self):
        return iter(self._entities.values())

    @classmethod
    def load_from_file(cls, filepath: Union[str, Path]) -> "EntityRegistry":
        """
        Loads an entity registry from a JSON file.
        Accepts either a JSON array of entities or an object with an 'entities' list.
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"Entity file not found: {path}")

        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict) and "entities" in raw:
            items = raw["entities"]
        else:
            raise ValueError(f"Invalid entity file format in {path}. Expected a list of entities or an object with 'entities'.")

        entities = [Entity.model_validate(item) for item in items]
        return cls(entities)

    @classmethod
    def load_from_dict_list(cls, data: List[Dict[str, Any]]) -> "EntityRegistry":
        """Loads an entity registry from a list of dictionaries."""
        entities = [Entity.model_validate(item) for item in data]
        return cls(entities)

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> "EntityRegistry":
        """Alias for load_from_file."""
        return cls.load_from_file(filepath)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "EntityRegistry":
        """Alias for load_from_dict_list."""
        return cls.load_from_dict_list(data)

    def export_to_file(self, filepath: Union[str, Path]) -> None:
        """Exports all registered entities to a JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.model_dump() for e in self.all()]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
