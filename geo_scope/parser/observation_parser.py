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
from geo_scope.entities.registry import normalize_text, extract_domain_hostname


# Regex patterns for intent classification
INFORMATIONAL_PATTERNS = [
    # English
    r"\bwho is\b", r"\bwhat is\b", r"\bdefine\b", r"\bexplain\b", r"\bhistory of\b",
    r"\bbiography\b", r"\bhow does\b", r"\bhow to\b", r"\bbackground of\b", r"\bwho founded\b",
    r"\boverview of\b", r"\bwhere is\b", r"\bwhen is\b", r"\bguide\b", r"\btutorial\b",
    # Persian
    r"\bکیست\b", r"\bچیست\b", r"\bتوضیح دهید\b", r"\bدرباره\b", r"\bمعرفی\b", r"\bبیوگرافی\b",
    r"\bتاریخچه\b", r"\bچگونه کار میکند\b", r"\bچگونه\b", r"\bنحوه\b", r"\bروش\b", r"\bراهنمای\b",
    r"\bموسس\b", r"\bبنیانگذار\b", r"\bزندگینامه\b", r"\bکجاست\b", r"\bقیمت\b",
    # Arabic
    r"\bمن هو\b", r"\bما هو\b", r"\bما هي\b", r"\bعرف\b", r"\bاشرح\b", r"\bتاريخ\b",
    r"\bسيرة\b", r"\bكيف يعمل\b", r"\bكيفية\b", r"\bمؤسس\b", r"\bنبذة عن\b", r"\bمتى\b",
    r"\bأين\b", r"\bدليل\b",
    # Turkish
    r"\bkimdir\b", r"\bnedir\b", r"\bne zaman kuruldu\b", r"\bhakkında\b", r"\bnasıl çalışır\b",
    r"\bnasıl\b", r"\bnerede\b", r"\brehberi\b", r"\btarihçesi\b", r"\bkurucusu kim\b",
    # Chinese
    r"是谁", r"是什么", r"介绍", r"历史", r"如何运作", r"如何", r"怎么", r"创始人", r"简介", r"简史", r"指南", r"在哪里",
]

RECOMMENDATION_PATTERNS = [
    # English
    r"\bbest\b", r"\btop\b", r"\brecommend\b", r"\branked\b", r"\bcomparison\b",
    r"\bwhich is better\b", r"\bagencies in\b", r"\bcompanies in\b", r"\bproviders in\b",
    r"\balternatives to\b", r"\bsuggest\b",
    # Persian
    r"\bبهترین\b", r"\bبرترین\b", r"\bپیشنهاد\b", r"\bمعرفی کنید\b", r"\bکدام بهتر است\b",
    r"\bمقایسه\b", r"\bشرکت های برتر\b", r"\bآژانس های برتر\b", r"\bلیست شرکت ها\b",
    # Arabic
    r"\bأفضل\b", r"\bافضل\b", r"\bأحسن\b", r"\bترشيح\b", r"\bمقارنة\b",
    r"\bأيهما أفضل\b", r"\bأبرز الشركات\b", r"\bأهم\b",
    # Turkish
    r"\ben iyi\b", r"\ben popüler\b", r"\bkarşılaştırma\b", r"\bhangisi daha iyi\b",
    r"\btavsiye\b", r"\bönerilen\b",
    # Chinese
    r"最好的", r"最佳", r"推荐", r"哪个好", r"对比", r"排名", r"排行榜", r"优秀",
]

NAVIGATIONAL_PATTERNS = [
    # English
    r"\blogin\b", r"\bportal\b", r"\bofficial website\b", r"\bwebsite\b", r"\bsign in\b", r"\bdashboard\b",
    # Persian
    r"\bورود به\b", r"\bسایت رسمی\b", r"\bپورتال\b", r"\bداشبورد\b", r"\bپنل کاربری\b",
    # Arabic
    r"\bتسجيل الدخول\b", r"\bالموقع الرسمي\b", r"\bبوابة\b", r"\bرابط موقع\b",
    # Turkish
    r"\bgiriş\b", r"\bresmi web sitesi\b", r"\bpaneli\b",
    # Chinese
    r"登录", r"官网", r"官方网站", r"入口", r"主页",
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

EXPLICIT_RECOMMENDATION_PATTERNS_AR = [
    r"نوصي\s+بـ?",
    r"ننصح\s+بـ?",
    r"أفضل\s+خيار",
    r"افضل\s+خيار",
    r"الخيار\s+الأمثل",
    r"خيار\s+ممتاز",
    r"من\s+أبرز\s+الخيارات",
]

EXPLICIT_RECOMMENDATION_PATTERNS_TR = [
    r"tavsiye\s+edilir",
    r"tavsiye\s+ediyoruz",
    r"öneririz",
    r"en\s+iyi\s+seçenek",
    r"en\s+uygun\s+tercih",
    r"öne\s+çıkan\s+seçenek",
]

EXPLICIT_RECOMMENDATION_PATTERNS_ZH = [
    r"强烈推荐",
    r"首选",
    r"最佳选择",
    r"非常推荐",
    r"值得推荐",
    r"领先方案",
]

LIST_ITEM_RECOMMENDATION_HEADER_PATTERNS = [
    r"recommended\s+(?:solutions|options|companies|tools|providers|platforms|services)",
    r"top\s+(?:recommendations|picks|options|choices|providers|companies|tools)",
    r"best\s+(?:options|tools|companies|agencies|solutions|platforms|choices)",
    r"گزینه‌های\s+پیشنهادی",
    r"شرکت‌های\s+پیشنهادی",
    r"برترین\s+گزینه‌ها",
    r"پیشنهادهای\s+برتر",
    r"الخيارات\s+الموصى\s+بها",
    r"أفضل\s+الشركات",
    r"Önerilen\s+çözümler",
    r"En\s+iyi\s+seçenekler",
    r"推荐方案",
    r"最佳推荐",
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
    is_ambiguous: bool = False
    status: str = "scored"  # "scored" | "unscored" | "ambiguous"
    parser_confidence: float = 1.0
    confidence: float = 1.0
    scoring_status: str = "scored"  # "scored" | "unscored" | "ambiguous"
    intent_type: str = "recommendation"  # "recommendation" | "informational" | "navigational" | "general"
    evidence_snippets: List[str] = Field(default_factory=list)
    matched_text: Optional[str] = None
    normalized_text: Optional[str] = None
    source_span: Optional[Tuple[int, int]] = None


def classify_query_intent(query: str) -> str:
    """
    Classifies prompt query into recommendation, navigational, informational, or general intent.
    Recommendation queries take precedence when recommendation keywords (e.g. 'best', 'top', 'بهترین') are present.
    """
    if not query:
        return "general"
    
    q_norm = normalize_text(query).lower()
    
    # 1. Check recommendation patterns first
    for pat in RECOMMENDATION_PATTERNS:
        if re.search(pat, q_norm, re.IGNORECASE):
            return "recommendation"

    # 2. Check navigational patterns
    for pat in NAVIGATIONAL_PATTERNS:
        if re.search(pat, q_norm, re.IGNORECASE):
            return "navigational"

    # 3. Check informational patterns
    for pat in INFORMATIONAL_PATTERNS:
        if re.search(pat, q_norm, re.IGNORECASE):
            return "informational"

    return "general"


class ObservationParser:
    """
    Entity-aware observation parser for AI search engine and LLM responses.
    Strictly adheres to:
    1. mentioned != recommended (recommendation requires explicit linguistic endorsement).
    2. Strict ranking contract: rank_position is assigned ONLY from recognized ordered list syntax,
       never inferred from arbitrary paragraph order.
    3. Strict separation of cited (URL link presence) vs attributed (sourcing phrasing).
    4. Multi-lingual Unicode NFKC normalization, ZWNJ handling, and unspaced variant matching.
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
        matched_span = None
        matched_str = None
        
        # Mask out confused terms to verify brand names exist independently of homonyms
        search_text = norm_text_lower
        if confused_terms:
            for ct in confused_terms:
                ct_norm = normalize_text(ct).lower()
                if ct_norm:
                    search_text = search_text.replace(ct_norm, " ")

        # Build candidate aliases (both standard and continuous unspaced forms)
        all_name_candidates = []
        for n in entity.names:
            if n:
                all_name_candidates.append(n)
                n_continuous = re.sub(r"\s+", "", n)
                if n_continuous and n_continuous != n:
                    all_name_candidates.append(n_continuous)

        # Name matching with boundary checks & continuous token matching
        for name in all_name_candidates:
            name_norm = normalize_text(name).lower()
            if not name_norm:
                continue
            pattern = r"(?<!\w)" + re.escape(name_norm) + r"(?!\w)"
            m = re.search(pattern, search_text, re.IGNORECASE)
            if m:
                brand_matched = True
                matched_brand_names.append(name)
                if not matched_span:
                    matched_span = m.span()
                    matched_str = name
            else:
                # Check continuous unspaced match
                search_unspaced = re.sub(r"\s+", "", search_text)
                name_unspaced = re.sub(r"\s+", "", name_norm)
                if name_unspaced and name_unspaced in search_unspaced:
                    brand_matched = True
                    matched_brand_names.append(name)
                    if not matched_str:
                        matched_str = name
                
        # Domain matching in text
        for dom in entity.domains:
            dom_clean = dom.lower().replace("https://", "").replace("http://", "").rstrip("/")
            if dom_clean in search_text:
                brand_matched = True
                matched_brand_names.append(dom)
                if not matched_str:
                    matched_str = dom

        # 4. Check Person Mention (Separately Tracked with Unspaced Variants)
        person_matched = False
        matched_people = []
        all_people_candidates = []
        for p in entity.people:
            if p:
                all_people_candidates.append(p)
                p_continuous = re.sub(r"\s+", "", p)
                if p_continuous and p_continuous != p:
                    all_people_candidates.append(p_continuous)

        for person in all_people_candidates:
            person_norm = normalize_text(person).lower()
            if not person_norm:
                continue
            pattern = r"(?<!\w)" + re.escape(person_norm) + r"(?!\w)"
            if re.search(pattern, norm_text_lower, re.IGNORECASE):
                person_matched = True
                matched_people.append(person)
            else:
                norm_unspaced = re.sub(r"\s+", "", norm_text_lower)
                p_unspaced = re.sub(r"\s+", "", person_norm)
                if p_unspaced and p_unspaced in norm_unspaced:
                    person_matched = True
                    matched_people.append(person)

        # 5. Evaluate Wrong Entity & Disambiguation
        wrong_entity = False
        is_ambiguous = False
        
        if confused_terms and not brand_matched:
            wrong_entity = True
        elif confused_terms and brand_matched:
            is_ambiguous = True

        mentioned = brand_matched and not wrong_entity

        # 6. Strictly Separate Citations & Attribution
        # Cited = URL or domain reference appeared
        cited = False
        all_entity_domains = [extract_domain_hostname(d) for d in entity.all_domains() if d]
        
        for cit in citations:
            cit_host = extract_domain_hostname(cit)
            if cit_host and any(dom == cit_host or cit_host.endswith("." + dom) or dom in cit_host for dom in all_entity_domains):
                cited = True
                break

        if not cited:
            for dom in all_entity_domains:
                if dom and (dom in norm_text_lower or dom in text.lower()):
                    cited = True
                    break

        # Attributed = Explicit attribution/sourcing phrasing connects information to entity
        attributed = False
        entity_name_patterns = [re.escape(normalize_text(n).lower()) for n in (entity.names + entity.domains + entity.people) if n]
        combined_names = "|".join(entity_name_patterns) if entity_name_patterns else ""
        
        if combined_names:
            attribution_patterns = [
                # Persian
                rf"(?:بر اساس|طبق گزارش|به نقل از|به گزارش|مطابق آمار|به گفته)\s+.*?(?:{combined_names})",
                # English
                rf"(?:according to|source:|data from|reported by|published by|based on research by|as stated by)\s+.*?(?:{combined_names})",
                # Arabic
                rf"(?:وفقا لـ?|وفقاً لـ?|حسب تقرير|المصدر:|استناداً إلى|استنادا الى|بناءً على|نقلاً عن)\s+.*?(?:{combined_names})",
                # Turkish
                rf"(?:{combined_names})\s+.*?(?:göre|raporuna göre|verilerine göre)",
                rf"kaynak:\s*.*?(?:{combined_names})",
                # Chinese
                rf"(?:根据|据|数据来自|来源：|报告显示)\s*.*?(?:{combined_names})",
            ]
            for pat in attribution_patterns:
                if re.search(pat, norm_text_lower, re.IGNORECASE):
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
        if cited:
            evidence.append("Citation link/domain confirmed")
        if attributed:
            evidence.append("Attribution sourcing confirmed")

        e_display = entity.names[0] if entity.names else entity.id
        e_type = getattr(entity, "entity_type", "organization")
        matched_domain = entity.domains[0] if entity.domains else ""

        final_status = "ambiguous" if is_ambiguous else scoring_status

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
            is_ambiguous=is_ambiguous,
            status=final_status,
            parser_confidence=round(parser_conf, 3),
            confidence=round(parser_conf, 3),
            scoring_status=scoring_status,
            intent_type=intent,
            evidence_snippets=evidence,
            matched_text=matched_str,
            normalized_text=norm_text,
            source_span=matched_span,
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
                if any(normalize_text(n).lower() in item_norm for n in entity.names if n):
                    rank = item_num
                    is_top1 = (rank == 1)
                    in_numbered_list = True
                    break

        # Check explicit linguistic recommendation endorsement in text across EN, FA, AR, TR, ZH
        text_lower = text.lower()
        has_linguistic_rec = False
        
        all_explicit_patterns = (
            EXPLICIT_RECOMMENDATION_PATTERNS_EN
            + EXPLICIT_RECOMMENDATION_PATTERNS_FA
            + EXPLICIT_RECOMMENDATION_PATTERNS_AR
            + EXPLICIT_RECOMMENDATION_PATTERNS_TR
            + EXPLICIT_RECOMMENDATION_PATTERNS_ZH
        )
        
        for pat in all_explicit_patterns:
            if re.search(pat, text_lower, re.IGNORECASE):
                for sentence in re.split(r"[\.\!\?\n]", text_lower):
                    if re.search(pat, sentence, re.IGNORECASE) and any(normalize_text(n).lower() in sentence for n in entity.names if n):
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
