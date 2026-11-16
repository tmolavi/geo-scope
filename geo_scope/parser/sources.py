"""
Source and Domain Categorization Subsystem for GEO-Scope.
Classifies cited domains and URLs into deterministic provenance categories:
- Owned Domain (Brand assets)
- UGC & Community (Reddit, Quora, Forums, Discussion boards)
- Earned Media & Press (News organizations, independent journalism)
- Review Aggregators & Directories (G2, Trustpilot, Torob, Emalls)
- Official Documentation & Standards (Wikipedia, GitHub, RFCs, Government portals)
- General Web (Other blogs, informational sites)
"""

from enum import Enum
from typing import List, Optional, Sequence, Set
from urllib.parse import urlparse
from pydantic import BaseModel, Field


class SourceCategory(str, Enum):
    OWNED = "owned"
    UGC_COMMUNITY = "ugc_community"
    EARNED_MEDIA = "earned_media"
    AGGREGATOR_REVIEWS = "aggregator_reviews"
    OFFICIAL_DOCS = "official_docs"
    GENERAL_WEB = "general_web"


# Known UGC and Community Platforms (Global and Iranian)
KNOWN_UGC_DOMAINS: Set[str] = {
    "reddit.com",
    "quora.com",
    "medium.com",
    "stackoverflow.com",
    "superuser.com",
    "askubuntu.com",
    "stackexchange.com",
    "virgool.io",
    "virasty.com",
    "aparat.com",
    "youtube.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "threads.net",
    "telegram.org",
    "t.me",
    "eitaa.com",
    "bale.ai",
    "rubika.ir",
    "discussions.apple.com",
    "answers.microsoft.com",
    "community.cloudflare.com",
    "news.ycombinator.com",
    "lobste.rs",
    "dev.to",
    "hashnode.com",
}

# Known Review Aggregators and Directories
KNOWN_AGGREGATORS: Set[str] = {
    "g2.com",
    "capterra.com",
    "trustpilot.com",
    "gartner.com",
    "softwareadvice.com",
    "getapp.com",
    "producthunt.com",
    "torob.com",
    "emalls.ir",
    "digikala.com",
    "divar.ir",
    "bama.ir",
    "sheypoor.com",
    "tripadvisor.com",
    "yelp.com",
    "bbb.org",
    "glassdoor.com",
}

# Known Earned Media, News Outlets and Independent Publications
KNOWN_MEDIA: Set[str] = {
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "venturebeat.com",
    "bloomberg.com",
    "reuters.com",
    "forbes.com",
    "wsj.com",
    "nytimes.com",
    "bbc.com",
    "zoomit.ir",
    "digiato.com",
    "ivna.ir",
    "isna.ir",
    "irna.ir",
    "farsnews.ir",
    "tasnimnews.com",
    "mehrnews.com",
    "asriran.com",
    "tabnak.ir",
    "peivast.com",
    "itna.ir",
    "way2pay.ir",
    "sharghdaily.com",
    "donya-e-eqtesad.com",
}

# Known Official Documentation and Authority Repositories
KNOWN_OFFICIAL_DOCS: Set[str] = {
    "wikipedia.org",
    "wikidata.org",
    "w3.org",
    "schema.org",
    "github.com",
    "gitlab.com",
    "docs.python.org",
    "developer.mozilla.org",
    "go.dev",
    "rust-lang.org",
    "pypi.org",
    "npmjs.com",
    "arxiv.org",
    "biorxiv.org",
    "nih.gov",
    "ncbi.nlm.nih.gov",
}


class DomainSourceMeta(BaseModel):
    """
    Standard metadata record for a cited domain or URL.
    """
    raw_input: str
    clean_domain: str
    category: SourceCategory
    is_owned: bool = False
    is_ugc: bool = False
    is_earned_media: bool = False
    is_aggregator: bool = False
    is_official_doc: bool = False
    confidence: float = 1.0
    matched_rule: Optional[str] = None


class SourceClassifier:
    """
    Deterministically classifies domains and URLs into standard GEO source categories.
    """

    def __init__(self, owned_domains: Optional[Sequence[str]] = None):
        self.owned_domains: Set[str] = {
            self._clean_domain_str(d) for d in (owned_domains or []) if d
        }

    @staticmethod
    def _clean_domain_str(val: str) -> str:
        s = (val or "").strip().lower()
        if s.startswith("http://") or s.startswith("https://"):
            try:
                parsed = urlparse(s)
                s = parsed.netloc or parsed.path
            except Exception:
                pass
        s = s.split("/")[0].split(":")[0]
        if s.startswith("www."):
            s = s[4:]
        return s

    def _matches_domain_set(self, domain: str, domain_set: Set[str]) -> bool:
        if domain in domain_set:
            return True
        for root in domain_set:
            if domain.endswith("." + root):
                return True
        return False

    def classify_domain(self, domain_or_url: str) -> DomainSourceMeta:
        clean = self._clean_domain_str(domain_or_url)
        if not clean:
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain="",
                category=SourceCategory.GENERAL_WEB,
                confidence=0.0,
                matched_rule="empty_input",
            )

        # 1. Check Owned Domains
        if self._matches_domain_set(clean, self.owned_domains):
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain=clean,
                category=SourceCategory.OWNED,
                is_owned=True,
                confidence=1.0,
                matched_rule="owned_domain_match",
            )

        # 2. Check UGC & Community
        if self._matches_domain_set(clean, KNOWN_UGC_DOMAINS):
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain=clean,
                category=SourceCategory.UGC_COMMUNITY,
                is_ugc=True,
                confidence=0.95,
                matched_rule="known_ugc_catalog",
            )

        # 3. Check Aggregators & Reviews
        if self._matches_domain_set(clean, KNOWN_AGGREGATORS):
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain=clean,
                category=SourceCategory.AGGREGATOR_REVIEWS,
                is_aggregator=True,
                confidence=0.95,
                matched_rule="known_aggregator_catalog",
            )

        # 4. Check Earned Media & Press
        if self._matches_domain_set(clean, KNOWN_MEDIA):
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain=clean,
                category=SourceCategory.EARNED_MEDIA,
                is_earned_media=True,
                confidence=0.95,
                matched_rule="known_media_catalog",
            )

        # 5. Check Official Docs & Knowledge Bases
        if self._matches_domain_set(clean, KNOWN_OFFICIAL_DOCS):
            return DomainSourceMeta(
                raw_input=domain_or_url,
                clean_domain=clean,
                category=SourceCategory.OFFICIAL_DOCS,
                is_official_doc=True,
                confidence=0.95,
                matched_rule="known_official_docs_catalog",
            )

        # 6. Default General Web
        return DomainSourceMeta(
            raw_input=domain_or_url,
            clean_domain=clean,
            category=SourceCategory.GENERAL_WEB,
            confidence=0.70,
            matched_rule="general_web_fallback",
        )

    def classify_citations(
        self, citations: Sequence[str]
    ) -> List[DomainSourceMeta]:
        return [self.classify_domain(c) for c in citations if c]
