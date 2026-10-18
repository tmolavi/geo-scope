"""
Entity Registry and Multi-lingual Normalization for GEO-Scope.
Integrates MultilingualNormalizer, parent-child brand hierarchies,
and robust domain extraction.
"""

import json
import re
import unicodedata
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set

from geo_scope.entities.models import Entity
from geo_scope.entities.normalizer import MultilingualNormalizer, EntityMatchResult


def extract_domain_hostname(url: str) -> str:
    """
    Extracts the clean, normalized domain hostname from a URL, citation string, or domain name.
    Strips protocol, www, port, paths, parameters, and trailing slashes.
    Example: 'https://www.inten.asia/services/?q=seo' -> 'inten.asia'
    """
    if not url:
        return ""
    u = str(url).strip().lower()
    if "://" not in u:
        u = "http://" + u
    try:
        parsed = urlparse(u)
        host = parsed.netloc or parsed.path
        # Remove port if present
        host = host.split(":")[0]
        # Strip www. prefix
        if host.startswith("www."):
            host = host[4:]
        # Remove any stray path or query remnants
        host = host.split("/")[0].strip()
        return host
    except Exception:
        # Fallback regex extraction
        m = re.search(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.\-]+)", url)
        return m.group(1).lower().rstrip("/") if m else url.lower().strip()


def normalize_text(text: str, language: Optional[str] = None) -> str:
    """
    High-precision multi-lingual text normalization for Persian, Arabic, Turkish, Azerbaijani, and English.
    Preserves exact backward compatibility with legacy signature, returning the normalized text string.
    """
    normalized, _ = MultilingualNormalizer.normalize(text, language=language)
    return normalized


class EntityRegistry:
    """
    Repository of tracked entities, aliases, key people, parent brands,
    and negative disambiguation rules.
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

    def get_children(self, parent_entity_id: str) -> List[Entity]:
        """Returns child entities belonging to the given parent entity ID."""
        return [e for e in self._entities.values() if e.parent_entity_id == parent_entity_id]

    def get_parents(self) -> List[Entity]:
        """Returns entities that act as parents or have no parent_entity_id."""
        return [e for e in self._entities.values() if not e.parent_entity_id]

    def find_matches(self, text: str, language: Optional[str] = None) -> List[EntityMatchResult]:
        """
        Scans text against all registered entities using the MultilingualNormalizer.
        """
        all_results: List[EntityMatchResult] = []
        for entity in self._entities.values():
            matches = MultilingualNormalizer.match_entity(
                text=text,
                entity_id=entity.id,
                names=entity.all_names(),
                do_not_confuse=entity.do_not_confuse,
                excluded_aliases=entity.excluded_aliases,
                language=language,
            )
            all_results.extend(matches)
        return all_results

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
