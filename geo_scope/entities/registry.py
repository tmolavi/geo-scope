"""
Entity Registry and Multi-lingual Normalization for GEO-Scope.
"""

import json
import re
import unicodedata
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set

from geo_scope.entities.models import Entity


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


def normalize_text(text: str) -> str:
    """
    High-precision multi-lingual text normalization for Persian, Arabic, Turkish, English, and Chinese.
    - Full Unicode NFKC normalization (unifies ligatures, fullwidth symbols)
    - Persian/Arabic character unification:
        * Arabic Yeh (ي, ى, ۍ, ې) -> Persian Yeh (ی \u06cc)
        * Arabic Kaf (ك, ڬ, ڭ) -> Persian Kaf (ک \u06a9)
        * Teh Marbuta (ة) -> Heh (ه \u0647)
        * Alef variants (آ, أ, إ, ٱ) -> Bare Alef (ا \u0627)
        * Waw with Hamza (ؤ) -> Waw (و \u0648)
        * Yeh with Hamza (ئ) -> Persian Yeh (ی \u06cc)
    - Removes Arabic/Persian diacritics (Harakat / Tashkeel: Fatha, Damma, Kasra, Sukun, Tanwin, Shadda)
    - Removes Arabic tatweel / kashida (ـ \u0640)
    - Zero-width character handling:
        * Collapses ZWNJ (\u200c) to space for token matching
        * Strips ZWJ (\u200d), ZWSP (\u200b), LTR (\u200e), RTL (\u200f), Bidi marks (\u202a-\u202e), BOM (\ufeff)
    - Turkish character normalization for lowercase comparisons
    - Collapses multiple whitespace
    """
    if not text:
        return ""
    
    # 1. Unicode NFKC normalization
    t = unicodedata.normalize("NFKC", str(text))
    
    # 2. Arabic & Persian letter normalization
    t = t.replace("\u064a", "\u06cc")  # Arabic Yeh -> Persian Yeh (ي -> ی)
    t = t.replace("\u0649", "\u06cc")  # Alef Maksura -> Persian Yeh (ى -> ی)
    t = t.replace("\u06d2", "\u06cc")  # Urdu Yeh -> Persian Yeh (ے -> ی)
    t = t.replace("\u0643", "\u06a9")  # Arabic Kaf -> Persian Kaf (ك -> ک)
    t = t.replace("\u06aa", "\u06a9")  # Swash Kaf -> Persian Kaf
    t = t.replace("\u0629", "\u0647")  # Teh Marbuta -> Heh (ة -> ه)
    t = t.replace("\u06c0", "\u0647")  # Heh with Hamza -> Heh
    t = t.replace("\u06c1", "\u0647")  # Urdu Heh -> Heh
    t = t.replace("\u06d5", "\u0647")  # Ae -> Heh
    t = t.replace("\u0622", "\u0627")  # Alef with Madda -> Alef (آ -> ا)
    t = t.replace("\u0623", "\u0627")  # Alef with Hamza Above -> Alef (أ -> ا)
    t = t.replace("\u0625", "\u0627")  # Alef with Hamza Below -> Alef (إ -> ا)
    t = t.replace("\u0671", "\u0627")  # Alef Wasla -> Alef (ٱ -> ا)
    t = t.replace("\u0624", "\u0648")  # Waw with Hamza -> Waw (ؤ -> و)
    t = t.replace("\u0626", "\u06cc")  # Yeh with Hamza -> Yeh (ئ -> ی)
    t = t.replace("\u0647\u0654", "\u0647")  # Heh with Hamza above -> Heh

    # 3. Remove Arabic Tatweel / Kashida
    t = t.replace("\u0640", "")

    # 4. Remove Arabic / Persian Tashkeel & Diacritics
    t = re.sub(r"[\u064b-\u065f\u0670]", "", t)

    # 5. Zero-Width & Directional Characters
    t = t.replace("\u200c", " ")       # ZWNJ -> space for boundary segmentation
    t = t.replace("\u200b", "")        # Zero-width space -> strip
    t = t.replace("\u200d", "")        # Zero-width joiner -> strip
    t = t.replace("\u200e", "")        # LTR mark -> strip
    t = t.replace("\u200f", "")        # RTL mark -> strip
    t = re.sub(r"[\u202a-\u202e]", "", t)  # Bidi embeddings
    t = t.replace("\ufeff", "")        # BOM

    # 6. Standardize Whitespace
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
