"""
Observation Parser for GEO-Scope.
Evaluates AI/LLM responses against entity definitions with strict intent recognition,
person-vs-organization disambiguation, negative phrase filtering, and confidence gating.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from geo_scope.entities.models import Entity
from geo_scope.entities.registry import normalize_text


# Regex patterns for intent classification
INFORMATIONAL_PATTERNS = [
    r"\bwho is\b",
    r"\bwhat is\b",
    r"\bdefine\b",
    r"\bexplain\b",
    r"\bhistory of\b",
    r"\bbiography\b",
    r"\bکیست\b",
    r"\bچیست\b",
    r"\bتوضیح دهید\b",
    r"\bدرباره\b",
    r"\bمعرفی\b",
    r"\bبیوگرافی\b",
    r"\bتاریخچه\b",
    r"\bچگونه کار میکند\b",
]

RECOMMENDATION_PATTERNS = [
    r"\bbest\b",
    r"\btop\b",
    r"\brecommend\b",
    r"\branked\b",
    r"\bcomparison\b",
    r"\bwhich is better\b",
    r"\bagencies in\b",
    r"\bcompanies in\b",
    r"\bproviders in\b",
    r"\bبهترین\b",
    r"\bبرترین\b",
    r"\bپیشنهاد\b",
    r"\bمعرفی کنید\b",
    r"\bکدام بهتر است\b",
    r"\bمقایسه\b",
    r"\bشرکت های برتر\b",
    r"\bآژانس های برتر\b",
    r"\bلیست شرکت ها\b",
]


class ObservationParsedResult(BaseModel):
    """
    Standard observation record independently exposing all entity detection flags.
    """
    entity_id: str
    entity: str = ""
    entity_type: str = "organization"
    mentioned: bool = False
    person_mentioned: bool = False
    recommended: bool = False
    top1: bool = False
    rank: Optional[int] = None
    rank_position: Optional[int] = None
    cited: bool = False
    citation_found: bool = False
    source_domain: Optional[str] = None
    attributed: bool = False
    context: Optional[str] = None
    confused_with: List[str] = Field(default_factory=list)
    wrong_entity: bool = False
    parser_confidence: float = 1.0
    confidence: float = 1.0
    scoring_status: str = "scored"  # "scored" | "unscored"
    intent_type: str = "recommendation"  # "recommendation" | "informational" | "navigational" | "general"
    evidence_snippets: List[str] = Field(default_factory=list)


def classify_query_intent(query: str) -> str:
    """
    Classifies prompt query into recommendation, informational, or general intent.
    """
    if not query:
        return "general"
    
    q_norm = normalize_text(query).lower()
    
    # Check informational patterns
    for pat in INFORMATIONAL_PATTERNS:
        if re.search(pat, q_norm, re.IGNORECASE):
            return "informational"

    # Check recommendation patterns
    for pat in RECOMMENDATION_PATTERNS:
        if re.search(pat, q_norm, re.IGNORECASE):
            return "recommendation"

    return "general"


class ObservationParser:
    """
    Entity-aware observation parser for AI search engine and LLM responses.
    """

    def __init__(self, confidence_threshold: float = 0.70):
        self.confidence_threshold = confidence_threshold

    def parse(
        self,
        text: str,
        entity: Entity,
        *,
        query: str = "",
        citations: Optional[List[str]] = None,
        query_intent: Optional[str] = None,
    ) -> ObservationParsedResult:
        """
        Parses a response text for a specific entity.
        Strictly distinguishes brand mentions from associated people and homonyms.
        """
        citations = citations or []
        norm_text = normalize_text(text)
        norm_text_lower = norm_text.lower()
        
        # 1. Determine Intent
        intent = query_intent or classify_query_intent(query)
        
        # 2. Check Negative Homonyms / Do-Not-Confuse
        confused_terms = []
        for dnc in entity.do_not_confuse:
            dnc_norm = normalize_text(dnc).lower()
            if dnc_norm and dnc_norm in norm_text_lower:
                confused_terms.append(dnc)
                
        # 3. Check Brand Mention (Names and Domains)
        brand_matched = False
        matched_brand_names = []
        
        # Mask out confused terms to verify brand names exist independently of homonyms
        search_text = norm_text_lower
        if confused_terms:
            for ct in confused_terms:
                ct_norm = normalize_text(ct).lower()
                if ct_norm:
                    search_text = search_text.replace(ct_norm, " ")

        # Name matching with boundary checks
        for name in entity.names:
            name_norm = normalize_text(name).lower()
            if not name_norm:
                continue
            # Use regex word boundary for english/alphanumeric or exact substring with space boundaries
            pattern = r"(?<!\w)" + re.escape(name_norm) + r"(?!\w)"
            if re.search(pattern, search_text, re.IGNORECASE):
                brand_matched = True
                matched_brand_names.append(name)
                
        # Domain matching in text
        for dom in entity.domains:
            dom_clean = dom.lower().replace("https://", "").replace("http://", "").rstrip("/")
            if dom_clean in search_text:
                brand_matched = True
                matched_brand_names.append(dom)

        # 4. Check Person Mention (Strictly Separate from Brand Mention)
        person_matched = False
        matched_people = []
        for person in entity.people:
            person_norm = normalize_text(person).lower()
            if not person_norm:
                continue
            pattern = r"(?<!\w)" + re.escape(person_norm) + r"(?!\w)"
            if re.search(pattern, norm_text_lower, re.IGNORECASE):
                person_matched = True
                matched_people.append(person)

        # 5. Evaluate Wrong Entity & Disambiguation
        wrong_entity = False
        if confused_terms and not brand_matched:
            wrong_entity = True

        # If only person matched and brand did not match, brand is NOT mentioned
        # Person mention is flagged independently
        mentioned = brand_matched and not wrong_entity

        # 6. Check Citations & Attribution
        cited = False
        all_entity_domains = [d.lower().replace("https://", "").replace("http://", "").rstrip("/") for d in entity.all_domains()]
        
        for cit in citations:
            cit_lower = str(cit).lower()
            if any(dom in cit_lower for dom in all_entity_domains if dom):
                cited = True
                break

        # Attribution check (explicit credit phrases in text or citation match)
        attributed = cited
        if not attributed and mentioned:
            attribution_patterns = [
                r"بر اساس\s+.*" + re.escape(entity.names[0].lower()) if entity.names else "",
                r"طبق گزارش\s+.*" + re.escape(entity.names[0].lower()) if entity.names else "",
                r"according to\s+.*" + re.escape(entity.names[0].lower()) if entity.names else "",
                r"source:\s*.*" + re.escape(entity.names[0].lower()) if entity.names else "",
            ]
            for pat in attribution_patterns:
                if pat and re.search(pat, norm_text_lower, re.IGNORECASE):
                    attributed = True
                    break

        # 7. Recommendation and Rank Extraction
        recommended = False
        top1 = False
        rank: Optional[int] = None
        parser_conf = 1.0

        if intent == "informational":
            # Informational entity queries ("Who is...", "What is...") must NOT produce recommendation rankings
            scoring_status = "unscored"
            recommended = False
            top1 = False
            rank = None
            parser_conf = 0.95
        elif not mentioned:
            scoring_status = "scored"
            recommended = False
            top1 = False
            rank = None
            parser_conf = 1.0 if not confused_terms else 0.85
        else:
            # Entity was mentioned in a recommendation or general context
            # Detect list ranking and position
            rank, is_top1, rec_conf = self._extract_rank_and_recommendation(norm_text, entity)
            if rank is not None:
                recommended = True
                top1 = is_top1
            else:
                # Mentioned but not in a structured ranking list
                recommended = True
                top1 = False
            
            parser_conf = rec_conf
            if parser_conf < self.confidence_threshold:
                scoring_status = "unscored"
            else:
                scoring_status = "scored"

        # Evidence snippets
        evidence = []
        if matched_brand_names:
            evidence.append(f"Matched brand names: {matched_brand_names}")
        if matched_people:
            evidence.append(f"Matched associated people: {matched_people}")
        if confused_terms:
            evidence.append(f"Matched negative homonyms: {confused_terms}")

        e_display = entity.names[0] if entity.names else entity.id
        e_type = getattr(entity, "entity_type", "organization")
        matched_domain = entity.domains[0] if entity.domains else ""

        return ObservationParsedResult(
            entity_id=entity.id,
            entity=e_display,
            entity_type=e_type,
            mentioned=mentioned,
            person_mentioned=person_matched,
            recommended=recommended,
            top1=top1,
            rank=rank,
            rank_position=rank,
            cited=cited,
            citation_found=cited,
            source_domain=matched_domain if cited else None,
            attributed=attributed,
            context=query if query else intent,
            confused_with=confused_terms,
            wrong_entity=wrong_entity,
            parser_confidence=round(parser_conf, 3),
            confidence=round(parser_conf, 3),
            scoring_status=scoring_status,
            intent_type=intent,
            evidence_snippets=evidence,
        )

    def _extract_rank_and_recommendation(self, text: str, entity: Entity) -> Tuple[Optional[int], bool, float]:
        """
        Extracts rank position (1-based) if the response is formatted as a numbered or bulleted recommendation list.
        Returns: (rank, is_top1, confidence)
        """
        lines = text.split("\n")
        list_items = []
        
        # Regex matching numbered list items (e.g. "1. ", "1- ", "#1 ", "۱. ", "۱- ")
        item_regex = re.compile(r"^\s*(?:[0-9]+|[۰-۹]+|\*|\-|\#\s*[0-9]+)[\.\-\:\)]\s*(.*)$")
        
        for line in lines:
            m = item_regex.match(line.strip())
            if m:
                list_items.append(line.strip())

        if not list_items:
            # Check paragraph order
            # If entity is in the very first paragraph, it might be top recommendation
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for idx, p in enumerate(paragraphs):
                p_norm = p.lower()
                if any(normalize_text(n).lower() in p_norm for n in entity.names):
                    rank = idx + 1
                    is_top1 = (rank == 1)
                    return rank, is_top1, 0.75
            return None, False, 0.70

        # Find position in numbered list
        for idx, item in enumerate(list_items):
            item_norm = normalize_text(item).lower()
            if any(normalize_text(n).lower() in item_norm for n in entity.names):
                rank = idx + 1
                is_top1 = (rank == 1)
                return rank, is_top1, 0.95

        return None, False, 0.75
