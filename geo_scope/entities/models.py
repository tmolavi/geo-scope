"""
Entity Data Models for GEO-Scope.
Supports multi-lingual brand aliases, associated people (founders/executives),
official domains, related domains, parent-child brand hierarchy,
and negative disambiguation patterns (do_not_confuse, excluded_aliases).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EntityAlias(BaseModel):
    """Structured alias entry with declared language and match type."""
    value: str
    language: Optional[str] = None
    match_type: str = "exact"  # "exact" | "case_insensitive" | "normalized_exact" | "probable"


class Entity(BaseModel):
    """
    Structured entity representation for AI visibility tracking.
    Enforces strict distinction between organization names and associated people,
    and supports parent-child brand hierarchy.
    """
    id: str = Field(..., description="Unique entity identifier (e.g. 'inten', 'hubspot')")
    entity_type: str = Field(default="organization", description="Entity category: company, people, country, product, website, organization")
    canonical_name: Optional[str] = Field(default=None, description="Canonical display name")
    parent_entity_id: Optional[str] = Field(default=None, description="Optional parent conglomerate / parent brand identifier")
    names: List[str] = Field(default_factory=list, description="Primary brand names and aliases in all languages (e.g. ['Inten', 'اینتن', 'InTen'])")
    aliases: List[Any] = Field(default_factory=list, description="Extended alias objects with language and match_type metadata")
    excluded_aliases: List[str] = Field(default_factory=list, description="Explicit lexical collisions that must not trigger matches")
    people: List[str] = Field(default_factory=list, description="Key individuals / executives (e.g. ['Taghi Molavi', 'تقی مولوی']). Person mentions are tracked separately.")
    domains: List[str] = Field(default_factory=list, description="Primary official domains (e.g. ['inten.asia'])")
    related_domains: List[str] = Field(default_factory=list, description="Associated or personal portfolio domains (e.g. ['molavi.pro'])")
    do_not_confuse: List[str] = Field(default_factory=list, description="Negative keywords / homonyms that must NOT trigger brand mention (e.g. ['بازار مولوی', 'فرش مولوی', 'مولوی رومی'])")
    same_as: List[str] = Field(default_factory=list, description="External identity URIs (e.g. Wikidata, Wikipedia, Crunchbase)")
    normalization_version: str = Field(default="1.0", description="Normalization specification version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary additional metadata (industry, founded_year, etc.)")

    def all_names(self) -> List[str]:
        """Returns consolidated list of all primary and alias names."""
        result = list(self.names)
        if self.canonical_name and self.canonical_name not in result:
            result.insert(0, self.canonical_name)
        for al in self.aliases:
            if isinstance(al, dict) and "value" in al:
                val = al["value"]
                if val and val not in result:
                    result.append(val)
            elif isinstance(al, str) and al not in result:
                result.append(al)
        return result

    def all_domains(self) -> List[str]:
        """Returns all domains associated with the entity."""
        return list(dict.fromkeys(self.domains + self.related_domains))

    def has_name(self, candidate: str) -> bool:
        """Case-insensitive and whitespace-stripped check for brand names."""
        c = candidate.strip().lower()
        return any(c == n.strip().lower() for n in self.all_names())

    def has_person(self, candidate: str) -> bool:
        """Case-insensitive and whitespace-stripped check for associated people."""
        c = candidate.strip().lower()
        return any(c == p.strip().lower() for p in self.people)
