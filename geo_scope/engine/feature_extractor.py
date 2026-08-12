"""
Feature Extractor Module for GEO (Generative Engine Optimization)
Extracts brand mentions, rank positions, cited URLs, source classifications, and sentiment.
"""

import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple

# Domain classification rules
DOMAIN_CATEGORIES = {
    "ugc_forums": [
        "reddit.com", "quora.com", "news.ycombinator.com", "stackexchange.com", 
        "stackoverflow.com", "virgool.io", "forum.", "community."
    ],
    "review_aggregators": [
        "g2.com", "capterra.com", "trustpilot.com", "producthunt.com", 
        "softwareadvice.com", "gartner.com", "getapp.com", "trustradius.com"
    ],
    "tech_media_pr": [
        "techcrunch.com", "forbes.com", "theverge.com", "wired.com", "zdnet.com",
        "venturebeat.com", "digiato.com", "zoomit.ir", "peivast.com", "ictna.ir",
        "businessinsider.com", "bloomberg.com", "wsj.com"
    ],
    "knowledge_base_wiki": [
        "wikipedia.org", "wikidata.org", "britannica.com", "github.com",
        "docs.", "developer."
    ],
    "blogs_industry": [
        "medium.com", "substack.com", "hubspot.com/blog", "ahrefs.com/blog",
        "backlinko.com", "searchengineland.com", "neilpatel.com"
    ]
}


def extract_citations_and_domains(text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Extracts all markdown links, raw URLs, and classifies their domains.
    """
    # Regex to find markdown links [text](url) and bare URLs
    md_links = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', text)
    raw_urls = re.findall(r'(?<!\()(https?://[^\s\)\"\'<>]+)', text)
    
    extracted_urls = set()
    for _, url in md_links:
        extracted_urls.add(url.strip())
    for url in raw_urls:
        extracted_urls.add(url.strip())
        
    classified_sources = []
    for url in extracted_urls:
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
                
            # Classify category
            cat = "other_web"
            for category, pattern_list in DOMAIN_CATEGORIES.items():
                for pat in pattern_list:
                    if pat in netloc or pat in url.lower():
                        cat = category
                        break
                if cat != "other_web":
                    break
                    
            classified_sources.append({
                "url": url,
                "domain": netloc,
                "category": cat
            })
        except Exception:
            continue
            
    return list(extracted_urls), classified_sources


def detect_brand_positions(text: str, brands: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Detects presence, rank order (1st, 2nd, 3rd, etc.), and sentiment of each brand.
    """
    results = {}
    lines = text.split("\n")
    
    for brand in brands:
        # Check if brand appears in text (case insensitive, word boundary)
        pattern = re.compile(rf'\b{re.escape(brand)}\b', re.IGNORECASE)
        matches = list(pattern.finditer(text))
        
        is_mentioned = len(matches) > 0
        mention_count = len(matches)
        
        # Rank detection: check numbered lists (e.g. "1. HubSpot", "1- HubSpot", "### 1. HubSpot")
        rank_pos = None
        list_rank = 999
        
        for idx, line in enumerate(lines):
            # Check for list numbering like "1. Brand", "1- Brand", "۱. Brand"
            list_match = re.match(r'^(?:[#\*\-\s]*)([\d\u06f0-\u06f9]+)[\.\-\)]\s*(.*)', line.strip())
            if list_match:
                num_str = list_match.group(1)
                # convert Persian numbers if any
                num_str = num_str.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
                try:
                    num_val = int(num_str)
                    content_after = list_match.group(2)
                    if pattern.search(content_after):
                        list_rank = min(list_rank, num_val)
                except ValueError:
                    pass
            elif pattern.search(line) and list_rank == 999:
                # If first time seen in paragraph
                if rank_pos is None:
                    rank_pos = idx + 1
                    
        final_rank = list_rank if list_rank != 999 else (1 if (is_mentioned and matches[0].start() < 150) else (2 if is_mentioned else 0))
        
        # Sentiment heuristic around brand context
        sentiment = "neutral"
        if is_mentioned:
            context_window = ""
            for m in matches:
                start = max(0, m.start() - 100)
                end = min(len(text), m.end() + 100)
                context_window += " " + text[start:end]
            
            pos_words = ["best", "top", "leading", "excellent", "superior", "recommended", "قدرتمند", "بهترین", "برتر", "توصیه", "عالی", "محبوب"]
            neg_words = ["worst", "expensive", "slow", "poor", "complaint", "lacks", "ضعیف", "گران", "کند", "نقص", "مشکل", "پیچیده"]
            
            pos_count = sum(1 for w in pos_words if w in context_window.lower())
            neg_count = sum(1 for w in neg_words if w in context_window.lower())
            
            if pos_count > neg_count:
                sentiment = "positive"
            elif neg_count > pos_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
                
        results[brand] = {
            "mentioned": is_mentioned,
            "mention_count": mention_count,
            "rank": final_rank if is_mentioned else 0,
            "is_top_1": final_rank == 1 if is_mentioned else False,
            "sentiment": sentiment
        }
        
    return results


def analyze_content_structure(text: str) -> Dict[str, Any]:
    """
    Analyzes formatting signals (lists, tables, statistics, direct answers).
    """
    has_table = "|" in text and (("---" in text) or ("-|-" in text) or (text.count("|") >= 4))
    has_bullets = bool(re.search(r'^\s*[\*\-]\s+', text, re.MULTILINE))
    has_numbers = bool(re.search(r'^\s*\d+[\.\)]\s+', text, re.MULTILINE))
    has_statistics = bool(re.search(r'\d+%\s*|\$\d+|\b\d+\s*(?:کاربر|user|dollar|تومان)', text, re.IGNORECASE))
    word_count = len(text.split())
    
    return {
        "word_count": word_count,
        "has_table": has_table,
        "has_bullets": has_bullets or has_numbers,
        "has_statistics": has_statistics,
        "structured_score": (1 if has_table else 0) + (1 if (has_bullets or has_numbers) else 0) + (1 if has_statistics else 0)
    }


def parse_model_response(
    query_item: Dict[str, Any],
    model_name: str,
    response_text: str
) -> Dict[str, Any]:
    """
    Parses a single AI model response and extracts full GEO metrics.
    """
    urls, sources = extract_citations_and_domains(response_text)
    brands = query_item.get("expected_entities", [query_item.get("target_brand", "Brand")])
    brand_positions = detect_brand_positions(response_text, brands)
    structure = analyze_content_structure(response_text)
    
    target_brand = query_item.get("target_brand")
    target_stats = brand_positions.get(target_brand, {
        "mentioned": False,
        "mention_count": 0,
        "rank": 0,
        "is_top_1": False,
        "sentiment": "neutral"
    })
    
    return {
        "query_id": query_item.get("id"),
        "model": model_name,
        "intent": query_item.get("intent"),
        "language": query_item.get("language"),
        "target_brand": target_brand,
        "target_mentioned": target_stats["mentioned"],
        "target_rank": target_stats["rank"],
        "target_is_top_1": target_stats["is_top_1"],
        "target_sentiment": target_stats["sentiment"],
        "all_brands_stats": brand_positions,
        "citation_count": len(urls),
        "citations": sources,
        "content_structure": structure,
        "response_length": len(response_text)
    }
