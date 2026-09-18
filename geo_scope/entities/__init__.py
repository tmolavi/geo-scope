"""
Entity registration, disambiguation models, and text normalization for GEO-Scope.
"""

from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry, normalize_text

__all__ = ["Entity", "EntityRegistry", "normalize_text"]
