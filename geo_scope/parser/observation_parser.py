"""
Observation Parser for GEO-Scope.
Evaluates AI/LLM responses against entity definitions with strict intent recognition,
person-vs-organization disambiguation, negative phrase filtering, explicit recommendation
evidence verification, and confidence gating.
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

# Explicit linguistic recommendation / endorsement patterns
EXPLICIT_RECOMMENDATION_PATTERNS_EN = [
    r"\brecommend(?:ed|s|ing)?\b",
    r"\bsuggest(?:ed|s|ing)?\b",
    r"\btop choice\b",
    r"\btop pick\b",
    r"\bbest option\b",
    r"\bbest choice\b",
    r"\bideal choice\b",
    r"\bhighly rated\b",
    r"\bgreat choice\b",
    r"\bstandout\b",
    r"\bleading choice\b",
    r"\bwe recommend\b",
    r"\bi recommend\b",
    r"\bour recommendation\b",
    r"\bshould consider\b",
    r"\bworth considering\b",
    r"\bstrongly suggest\b",
]

EXPLICIT_RECOMMENDATION_PATTERNS_FA = [
    r"پیشنهاد\s+(?:می‌کنم|می‌کنیم|می‌شود|ما)",
    r"توصیه\s+(?:می‌کنم|می‌کنیم|می‌شود|ما)",
    r"بهترین\s+(?:گزینه|انتخاب|پیشنهاد|راهکار)",
    r"گزینه\s+(?:برتر|اول|مناسب|ایده‌آل|پیشنهادی)",
    r"انتخاب\s+(?:اول|برتر|عالی)",
    r"شرکت\s+(?:برتر|پیشنهادی|منتخب)",
    r"آژانس\s+(?:برتر|پیشنهادی|منتخب)",
    r"از\s+بهترین\s+گزینه‌ها",
]

LIST_ITEM_RECOMMENDATION_HEADER_PATTERNS = [
    r"recommended\s+(?:solutions|options|companies|tools|providers|platforms|services)",
    r"top\s+(?:recommendations|picks|options|choices|providers|companies|tools)",
    r"best\s+(?:options|tools|companies|agencies|solutions|platforms|choices)",
    r"گزینه‌های\s+پیشنهادی",
    r"شرکت‌های\s+پیشنهادی",
    r"برترین\s+گزینه‌ها",
    r"پیشنهادهای\s+برتر",
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
    Strictly adheres to:
    1. mentioned != recommended (recommendation requires explicit linguistic endorsement).
    2. Strict ranking contract: rank_position is assigned ONLY from recognized ordered list syntax,
       never inferred from arbitrary paragraph order.
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
        Strictly distinguishes brand mentions from associated people, homonyms, and recommendations.
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

        # 7. Strict Recommendation and Rank Extraction
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
            # Entity was mentioned. Evaluate strictly if explicit recommendation endorsement exists.
            rank, is_top1, is_explicit_rec, rec_conf = self._extract_rank_and_recommendation(text, entity)
            
            # Strict Rule: mentioned != recommended
            # recommended is True ONLY if there is explicit endorsement or an ordered recommendation list item
            recommended = is_explicit_rec
            top1 = is_top1
            
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
        if recommended:
            evidence.append("Explicit recommendation evidence confirmed")

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

    def _extract_rank_and_recommendation(
        self,
        text: str,
        entity: Entity,
    ) -> Tuple[Optional[int], bool, bool, float]:
        """
        Strict Ranking & Recommendation Extraction.
        Contract:
        1. rank / rank_position is assigned ONLY from recognized ordered recommendation list syntax.
           Paragraph order is NEVER converted to rank.
        2. recommended is True ONLY if explicit linguistic endorsement is present or if the entity
           is placed in an ordered recommendation/ranking list.
        Returns: (rank, is_top1, is_recommended, confidence)
        """
        lines = text.split("\n")
        
        # Regex matching numbered list items (e.g. "1. ", "1- ", "#1 ", "۱. ", "۱- ")
        numbered_item_regex = re.compile(r"^\s*(?:([0-9]+|[۰-۹]+)|\#\s*([0-9]+))[\.\-\:\)]\s*(.*)$")
        
        numbered_list_items: List[Tuple[int, str]] = []
        for line in lines:
            line_str = line.strip()
            m = numbered_item_regex.match(line_str)
            if m:
                num_str = m.group(1) or m.group(2)
                persian_digits = {"۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"}
                for p_digit, e_digit in persian_digits.items():
                    num_str = num_str.replace(p_digit, e_digit)
                try:
                    num_val = int(num_str)
                except ValueError:
                    num_val = len(numbered_list_items) + 1
                numbered_list_items.append((num_val, line_str))

        # Check if entity appears in a recognized numbered ranking list
        rank: Optional[int] = None
        is_top1 = False
        in_numbered_list = False

        if numbered_list_items:
            for item_num, item_text in numbered_list_items:
                item_norm = normalize_text(item_text).lower()
                if any(normalize_text(n).lower() in item_norm for n in entity.names):
                    rank = item_num
                    is_top1 = (rank == 1)
                    in_numbered_list = True
                    break

        # Check explicit linguistic recommendation endorsement in text
        text_lower = text.lower()
        has_linguistic_rec = False
        
        for pat in EXPLICIT_RECOMMENDATION_PATTERNS_EN:
            if re.search(pat, text_lower, re.IGNORECASE):
                for sentence in re.split(r"[\.\!\?\n]", text_lower):
                    if re.search(pat, sentence, re.IGNORECASE) and any(normalize_text(n).lower() in sentence for n in entity.names):
                        has_linguistic_rec = True
                        break
            if has_linguistic_rec:
                break

        if not has_linguistic_rec:
            for pat in EXPLICIT_RECOMMENDATION_PATTERNS_FA:
                if re.search(pat, text_lower, re.IGNORECASE):
                    for sentence in re.split(r"[\.\!\?\n]", text_lower):
                        if re.search(pat, sentence, re.IGNORECASE) and any(normalize_text(n).lower() in sentence for n in entity.names):
                            has_linguistic_rec = True
                            break
                if has_linguistic_rec:
                    break

        # If in a numbered list with recommendation header
        has_rec_header = any(re.search(pat, text_lower, re.IGNORECASE) for pat in LIST_ITEM_RECOMMENDATION_HEADER_PATTERNS)

        is_recommended = in_numbered_list or has_linguistic_rec or (has_rec_header and in_numbered_list)

        # Confidence calculation
        if in_numbered_list:
            confidence = 0.95
        elif has_linguistic_rec:
            confidence = 0.90
        else:
            confidence = 0.80

        return rank, is_top1, is_recommended, confidence
