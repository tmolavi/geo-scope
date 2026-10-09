"""
Query Fan-Out Brand Introduction Evaluation & Classification Module.
Tests the hypothesis:
BRANDS INTRODUCED BY THE ENGINE'S OWN SEARCH/FAN-OUT QUERIES
MAY BE MUCH MORE LIKELY TO APPEAR IN THE FINAL ANSWER.

Adheres strictly to the frozen definitions:
- USER_NAMED: Brand present in user prompt.
- ENGINE_QUERY_INTRODUCED: Brand absent from user prompt AND explicitly present in observable engine-generated search queries.
- RETRIEVED_ONLY: Brand absent from user prompt AND absent from observable queries BUT present in retrieved result/page metadata.
- NOT_RETRIEVED: Brand absent from prompt, queries, and retrieved metadata.
"""

from enum import Enum
import re
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field


class BrandSourceClass(str, Enum):
    USER_NAMED = "USER_NAMED"
    ENGINE_QUERY_INTRODUCED = "ENGINE_QUERY_INTRODUCED"
    RETRIEVED_ONLY = "RETRIEVED_ONLY"
    NOT_RETRIEVED = "NOT_RETRIEVED"


class BrandObservation(BaseModel):
    conversation_id: str
    prompt_id: str
    engine: str
    model: str
    brand: str
    brand_source_class: BrandSourceClass
    generated_query_reference: Optional[str] = None
    retrieval_reference: Optional[str] = None
    final_answer_mentioned: bool = False
    final_answer_cited: bool = False
    raw_evidence_reference: str = ""


class FanoutMetrics(BaseModel):
    total_conversations: int = 0
    total_brand_observations: int = 0
    engine_introduced_count: int = 0
    retrieved_only_count: int = 0
    user_named_count: int = 0
    not_retrieved_count: int = 0
    
    engine_introduced_mentioned_count: int = 0
    retrieved_only_mentioned_count: int = 0
    
    engine_introduced_cited_count: int = 0
    retrieved_only_cited_count: int = 0

    engine_introduced_mention_rate: Optional[float] = None
    retrieved_only_mention_rate: Optional[float] = None
    mention_rate_ratio: Optional[float] = None
    
    engine_introduced_citation_rate: Optional[float] = None
    retrieved_only_citation_rate: Optional[float] = None
    
    manual_validation_accuracy: Optional[float] = None
    result_classification: str = "INSUFFICIENT_OBSERVABILITY"


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip().lower()


def text_contains_brand(text: str, brand_name: str, aliases: Optional[List[str]] = None, domains: Optional[List[str]] = None) -> bool:
    """
    Checks if a text contains a brand name, any of its aliases, or its domains.
    Uses strict token/word boundary matching to avoid accidental substring hits.
    """
    norm_text = _normalize_text(text)
    if not norm_text:
        return False

    candidates = [brand_name] + (aliases or [])
    for cand in candidates:
        if not cand:
            continue
        c_norm = _normalize_text(cand)
        # Use regex word boundaries
        pattern = r"(?<!\w)" + re.escape(c_norm) + r"(?!\w)"
        if re.search(pattern, norm_text, re.IGNORECASE):
            return True

    # Check domains
    for dom in (domains or []):
        if not dom:
            continue
        d_clean = dom.lower().replace("https://", "").replace("http://", "").rstrip("/")
        if d_clean and d_clean in norm_text:
            return True

    return False


def citations_contain_brand(citations: List[str], domains: Optional[List[str]] = None, brand_name: Optional[str] = None) -> bool:
    """
    Checks if any citation URL references the brand's official or related domains.
    """
    if not citations or not domains:
        return False

    doms_clean = [
        d.lower().replace("https://", "").replace("http://", "").rstrip("/")
        for d in domains if d
    ]
    for cit in citations:
        cit_lower = cit.lower()
        for d in doms_clean:
            if d in cit_lower:
                return True
    return False


def classify_brand(
    brand_name: str,
    user_prompt: str,
    generated_queries: List[str],
    retrieved_metadata: List[Dict[str, Any]],
    aliases: Optional[List[str]] = None,
    domains: Optional[List[str]] = None,
) -> Tuple[BrandSourceClass, Optional[str], Optional[str]]:
    """
    Classifies a brand into USER_NAMED, ENGINE_QUERY_INTRODUCED, RETRIEVED_ONLY, or NOT_RETRIEVED.
    Returns: (BrandSourceClass, generated_query_reference, retrieval_reference)
    """
    # 1. Check USER_NAMED
    if text_contains_brand(user_prompt, brand_name, aliases, domains):
        return BrandSourceClass.USER_NAMED, None, None

    # 2. Check ENGINE_QUERY_INTRODUCED
    matching_query = None
    for idx, q in enumerate(generated_queries):
        if text_contains_brand(q, brand_name, aliases, domains):
            matching_query = f"query_{idx + 1}: {q}"
            break

    if matching_query is not None:
        return BrandSourceClass.ENGINE_QUERY_INTRODUCED, matching_query, None

    # 3. Check RETRIEVED_ONLY
    matching_retrieval = None
    for idx, item in enumerate(retrieved_metadata):
        # Check title, snippet, and url
        item_text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}"
        if text_contains_brand(item_text, brand_name, aliases, domains):
            matching_retrieval = f"doc_{idx + 1}: {item.get('url', item.get('title', ''))}"
            break

    if matching_retrieval is not None:
        return BrandSourceClass.RETRIEVED_ONLY, None, matching_retrieval

    # 4. NOT_RETRIEVED
    return BrandSourceClass.NOT_RETRIEVED, None, None


def evaluate_brand_presence(
    brand_name: str,
    final_answer: str,
    citations: List[str],
    aliases: Optional[List[str]] = None,
    domains: Optional[List[str]] = None,
) -> Tuple[bool, bool]:
    """
    Evaluates whether the brand is mentioned in the final answer text
    and whether it is cited in the citations.
    Mention and citation MUST remain strictly separate.
    """
    mentioned = text_contains_brand(final_answer, brand_name, aliases, domains)
    cited = citations_contain_brand(citations, domains, brand_name)
    return mentioned, cited


def compute_fanout_metrics(
    observations: List[BrandObservation],
    manual_validation_accuracy: Optional[float] = None,
) -> FanoutMetrics:
    """
    Computes primary metrics across brand observations.
    Explicitly handles zero denominators without converting infinity into arbitrary numbers.
    """
    unique_convs = len(set(o.conversation_id for o in observations))
    
    engine_intro = [o for o in observations if o.brand_source_class == BrandSourceClass.ENGINE_QUERY_INTRODUCED]
    retrieved_only = [o for o in observations if o.brand_source_class == BrandSourceClass.RETRIEVED_ONLY]
    user_named = [o for o in observations if o.brand_source_class == BrandSourceClass.USER_NAMED]
    not_retrieved = [o for o in observations if o.brand_source_class == BrandSourceClass.NOT_RETRIEVED]

    ei_count = len(engine_intro)
    ro_count = len(retrieved_only)

    ei_mentioned = sum(1 for o in engine_intro if o.final_answer_mentioned)
    ro_mentioned = sum(1 for o in retrieved_only if o.final_answer_mentioned)

    ei_cited = sum(1 for o in engine_intro if o.final_answer_cited)
    ro_cited = sum(1 for o in retrieved_only if o.final_answer_cited)

    # Rates
    ei_mention_rate = (ei_mentioned / ei_count) if ei_count > 0 else None
    ro_mention_rate = (ro_mentioned / ro_count) if ro_count > 0 else None

    # Ratio
    if ei_mention_rate is not None and ro_mention_rate is not None and ro_mention_rate > 0:
        mention_rate_ratio = round(ei_mention_rate / ro_mention_rate, 4)
    elif ei_mention_rate is not None and ro_mention_rate == 0.0:
        mention_rate_ratio = None  # Explicit zero denominator; do NOT convert to arbitrary number
    else:
        mention_rate_ratio = None

    ei_citation_rate = (ei_cited / ei_count) if ei_count > 0 else None
    ro_citation_rate = (ro_cited / ro_count) if ro_count > 0 else None

    # Result Classification
    # Exactly one of: REPRODUCED_DIRECTIONALLY, LIMITED_EVIDENCE, NOT_REPRODUCED, INSUFFICIENT_OBSERVABILITY
    if ei_count < 10 or ro_count < 10:
        result_classification = "INSUFFICIENT_OBSERVABILITY"
    elif ei_mention_rate is not None and ro_mention_rate is not None:
        if ei_mention_rate > ro_mention_rate:
            if (ei_count + ro_count) >= 50:
                result_classification = "REPRODUCED_DIRECTIONALLY"
            else:
                result_classification = "LIMITED_EVIDENCE"
        else:
            result_classification = "NOT_REPRODUCED"
    else:
        result_classification = "INSUFFICIENT_OBSERVABILITY"

    return FanoutMetrics(
        total_conversations=unique_convs,
        total_brand_observations=len(observations),
        engine_introduced_count=ei_count,
        retrieved_only_count=ro_count,
        user_named_count=len(user_named),
        not_retrieved_count=len(not_retrieved),
        engine_introduced_mentioned_count=ei_mentioned,
        retrieved_only_mentioned_count=ro_mentioned,
        engine_introduced_cited_count=ei_cited,
        retrieved_only_cited_count=ro_cited,
        engine_introduced_mention_rate=round(ei_mention_rate, 4) if ei_mention_rate is not None else None,
        retrieved_only_mention_rate=round(ro_mention_rate, 4) if ro_mention_rate is not None else None,
        mention_rate_ratio=mention_rate_ratio,
        engine_introduced_citation_rate=round(ei_citation_rate, 4) if ei_citation_rate is not None else None,
        retrieved_only_citation_rate=round(ro_citation_rate, 4) if ro_citation_rate is not None else None,
        manual_validation_accuracy=manual_validation_accuracy,
        result_classification=result_classification,
    )
