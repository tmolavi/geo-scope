"""
Entity Data Models for GEO-Scope.
Supports multi-lingual brand aliases, associated people (founders/executives),
official domains, related domains, and negative disambiguation patterns (do_not_confuse).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """
    Structured entity representation for AI visibility tracking.
    Enforces strict distinction between organization names and associated people.
    """
    id: str = Field(..., description="Unique entity identifier (e.g. 'inten', 'hubspot')")
    entity_type: str = Field(default="organization", description="Entity category: company, people, country, product, website, organization")
    names: List[str] = Field(default_factory=list, description="Primary brand names and aliases in all languages (e.g. ['Inten', 'اینتن', 'InTen'])")
    people: List[str] = Field(default_factory=list, description="Key individuals / executives (e.g. ['Taghi Molavi', 'تقی مولوی']). Person mentions are tracked separately.")
    domains: List[str] = Field(default_factory=list, description="Primary official domains (e.g. ['inten.asia'])")
    related_domains: List[str] = Field(default_factory=list, description="Associated or personal portfolio domains (e.g. ['molavi.pro'])")
    do_not_confuse: List[str] = Field(default_factory=list, description="Negative keywords / homonyms that must NOT trigger brand mention (e.g. ['بازار مولوی', 'فرش مولوی', 'مولوی رومی'])")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary additional metadata (industry, founded_year, etc.)")

    def all_domains(self) -> List[str]:
        """Returns all domains associated with the entity."""
        return list(set(self.domains + self.related_domains))

    def has_name(self, candidate: str) -> bool:
        """Case-insensitive and whitespace-stripped check for brand names."""
        c = candidate.strip().lower()
        return any(c == n.strip().lower() for n in self.names)

    def has_person(self, candidate: str) -> bool:
        """Case-insensitive and whitespace-stripped check for associated people."""
        c = candidate.strip().lower()
        return any(c == p.strip().lower() for p in self.people)
