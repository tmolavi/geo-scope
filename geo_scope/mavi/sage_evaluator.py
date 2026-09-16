"""
SAGE Audit Engine for MAVI Layers L1, L2, L3, L4.
Extracts measured technical, semantic, entity, and citation signals from webpage HTML and metadata.
Zero external dependencies (uses standard library html.parser).
"""

import json
import re
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional, Tuple

from geo_scope.mavi.models import LayerResult, LayerProvenance


class SAGEHTMLParser(HTMLParser):
    """
    Lightweight, fast standard library HTML parser extracting DOM structures for SAGE audits.
    """

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_tags: List[Dict[str, str]] = []
        self.link_tags: List[Dict[str, str]] = []
        self.script_json_ld: List[str] = []
        self.headings: List[Tuple[str, str]] = []  # (tag, text)
        self.paragraphs: List[str] = []
        self.tables: List[List[List[str]]] = []  # list of tables, each table is list of rows
        self.has_main = False
        self.has_article = False
        self.text_chunks: List[str] = []

        # Internal state
        self._current_tag = None
        self._current_text = []
        self._in_script_json_ld = False
        self._in_table = False
        self._current_row = []
        self._current_cell = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): (v or "") for k, v in attrs}

        self._current_tag = tag_lower
        if tag_lower in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "title", "script", "td", "th"):
            self._current_text = []

        if tag_lower == "main":
            self.has_main = True
        elif tag_lower == "article":
            self.has_article = True
        elif tag_lower == "meta":
            self.meta_tags.append(attr_dict)
        elif tag_lower == "link":
            self.link_tags.append(attr_dict)
        elif tag_lower == "script" and attr_dict.get("type", "").lower() == "application/ld+json":
            self._in_script_json_ld = True
        elif tag_lower == "table":
            self._in_table = True
            self.tables.append([])
        elif tag_lower == "tr" and self._in_table:
            self._current_row = []
        elif tag_lower in ("td", "th") and self._in_table:
            self._current_cell = []

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        accumulated = "".join(self._current_text).strip()

        if tag_lower == "title":
            self.title = accumulated
        elif tag_lower in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if accumulated:
                self.headings.append((tag_lower, accumulated))
        elif tag_lower == "p":
            if accumulated:
                self.paragraphs.append(accumulated)
        elif tag_lower == "script" and self._in_script_json_ld:
            if accumulated:
                self.script_json_ld.append(accumulated)
            self._in_script_json_ld = False
        elif tag_lower in ("td", "th") and self._in_table:
            cell_text = "".join(self._current_cell).strip()
            self._current_row.append(cell_text)
            self._current_cell = []
        elif tag_lower == "tr" and self._in_table:
            if self.tables:
                self.tables[-1].append(self._current_row)
            self._current_row = []
        elif tag_lower == "table":
            self._in_table = False

        self._current_tag = None
        self._current_text = []

    def handle_data(self, data: str):
        if not data:
            return
        if self._in_script_json_ld:
            self._current_text.append(data)
        else:
            self._current_text.append(data)
            self.text_chunks.append(data)
            if self._in_table:
                self._current_cell.append(data)

    def get_full_text(self) -> str:
        return " ".join(" ".join(self.text_chunks).split())


class SAGEEvaluator:
    """
    SAGE (Structured AI Grounding & Extractability) Evaluator.
    Computes deterministic, measured audit layers L1 through L4 from webpage HTML.
    """

    def __init__(
        self,
        html_content: str,
        url: Optional[str] = None,
        target_brand: Optional[str] = None,
        http_status: int = 200,
    ):
        self.html = html_content or ""
        self.url = url or ""
        self.target_brand = (target_brand or "").strip()
        self.http_status = http_status

        self.parser = SAGEHTMLParser()
        if self.html:
            try:
                self.parser.feed(self.html)
            except Exception:
                pass

    def evaluate_l1_technical_accessibility(self, weight: float = 0.15) -> LayerResult:
        """
        L1 Technical Accessibility
        Measures HTTP status, crawler access, meta robots, canonical, renderability, and indexability.
        """
        findings = []
        evidence_count = 0
        score_components = []

        # 1. HTTP Status (Weight 30%)
        evidence_count += 1
        if self.http_status == 200:
            score_components.append(100.0 * 0.30)
            findings.append("HTTP 200 OK: Content accessible to AI retrieval crawlers")
        elif 300 <= self.http_status < 400:
            score_components.append(70.0 * 0.30)
            findings.append(f"HTTP {self.http_status} Redirect: Crawler follows redirect chain")
        else:
            score_components.append(0.0 * 0.30)
            findings.append(f"HTTP {self.http_status} Error: Page inaccessible to crawlers")

        # 2. Meta Robots & AI Crawler Rules (Weight 25%)
        evidence_count += 1
        robots_content = ""
        for meta in self.parser.meta_tags:
            name = meta.get("name", "").lower()
            if name in ("robots", "googlebot", "bingbot", "gptbot", "claudebot", "perplexitybot"):
                robots_content += " " + meta.get("content", "").lower()

        is_blocked = "noindex" in robots_content or "none" in robots_content
        if is_blocked:
            score_components.append(0.0 * 0.25)
            findings.append("Meta robots blocks indexing (noindex/none detected)")
        else:
            score_components.append(100.0 * 0.25)
            findings.append("Meta robots allows indexing by search & AI engine crawlers")

        # 3. Canonical Tag (Weight 15%)
        evidence_count += 1
        canonical_href = ""
        for link in self.parser.link_tags:
            if "canonical" in link.get("rel", "").lower():
                canonical_href = link.get("href", "")
                break

        has_canonical = bool(canonical_href)
        if has_canonical:
            score_components.append(100.0 * 0.15)
            findings.append(f"Canonical URL defined: {canonical_href[:60]}")
        else:
            score_components.append(50.0 * 0.15)
            findings.append("No canonical tag found (may cause duplicate content splitting)")

        # 4. Renderability & Token-to-HTML Density (Weight 20%)
        evidence_count += 1
        full_text = self.parser.get_full_text()
        word_count = len(full_text.split())
        html_len = len(self.html)
        density_ratio = (word_count * 100) / max(html_len, 1) if html_len > 0 else 0.0

        render_score = min(100.0, (density_ratio / 8.0) * 100.0)
        score_components.append(render_score * 0.20)
        findings.append(f"Text-to-DOM ratio: {density_ratio:.1f}% ({word_count} words in {html_len} bytes)")

        # 5. HTTPS Protocol (Weight 10%)
        evidence_count += 1
        is_https = self.url.startswith("https://") if self.url else True
        if is_https:
            score_components.append(100.0 * 0.10)
        else:
            score_components.append(40.0 * 0.10)
            findings.append("Insecure HTTP protocol detected (HTTPS preferred)")

        total_score = round(sum(score_components), 1)

        return LayerResult(
            layer_id="L1",
            layer_name="Technical Accessibility",
            weight=weight,
            score=total_score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="1.0.0",
                evidence_count=evidence_count,
                url=self.url,
            ),
            details={
                "http_status": self.http_status,
                "robots_directive": robots_content.strip() or "index,follow (default)",
                "has_canonical": has_canonical,
                "word_count": word_count,
                "html_bytes": html_len,
                "text_to_html_ratio_pct": round(density_ratio, 2),
                "is_https": is_https,
            },
            findings=findings,
        )

    def evaluate_l2_semantic_extractability(self, weight: float = 0.20) -> LayerResult:
        """
        L2 Semantic Extractability
        Measures heading structure, chunk quality, BLUF / direct answers, and semantic density.
        """
        findings = []
        evidence_count = 0
        score_components = []

        # 1. Heading Hierarchy (Weight 30%)
        evidence_count += 1
        h1_list = [txt for tag, txt in self.parser.headings if tag == "h1"]
        h2_list = [txt for tag, txt in self.parser.headings if tag == "h2"]
        h3_list = [txt for tag, txt in self.parser.headings if tag == "h3"]

        heading_score = 0.0
        if len(h1_list) == 1:
            heading_score += 50.0
            findings.append("Single clean <h1> tag present")
        elif len(h1_list) > 1:
            heading_score += 30.0
            findings.append(f"Multiple <h1> tags ({len(h1_list)}) found (single H1 recommended)")
        else:
            findings.append("Missing <h1> main heading")

        if len(h2_list) >= 2:
            heading_score += 35.0
            findings.append(f"Good sub-section hierarchy with {len(h2_list)} <h2> sections")
        elif len(h2_list) == 1:
            heading_score += 20.0

        if len(h3_list) >= 1:
            heading_score += 15.0

        score_components.append(min(100.0, heading_score) * 0.30)

        # 2. RAG Chunk Quality & Self-Contained Passages (Weight 30%)
        evidence_count += 1
        paragraphs = [p for p in self.parser.paragraphs if len(p) > 20]
        self_contained_chunks = [p for p in paragraphs if 15 <= len(p.split()) <= 120]
        chunk_ratio = len(self_contained_chunks) / max(len(paragraphs), 1) if paragraphs else 0.0
        chunk_score = min(100.0, (chunk_ratio * 80.0) + (min(len(self_contained_chunks), 5) * 4.0))
        score_components.append(chunk_score * 0.30)
        findings.append(
            f"RAG Chunk Readiness: {len(self_contained_chunks)}/{len(paragraphs)} paragraphs are optimal self-contained units (15-120 words)"
        )

        # 3. BLUF / Direct Answer in Top Section (Weight 25%)
        evidence_count += 1
        top_paragraphs = " ".join(paragraphs[:3])[:600]
        has_definition = bool(
            re.search(
                r"\b(is a|is the|refers to|provides|enables|helps|features|designed for|است|عبارت است از|شامل)\b",
                top_paragraphs,
                re.I,
            )
        )
        bluf_score = 90.0 if has_definition and len(top_paragraphs.split()) >= 15 else 45.0
        score_components.append(bluf_score * 0.25)
        if has_definition:
            findings.append("BLUF (Bottom Line Up Front) direct answer pattern detected in opening section")
        else:
            findings.append("Opening section lacks immediate direct answer / definition pattern")

        # 4. Semantic Density & Information Richness (Weight 15%)
        evidence_count += 1
        full_text = self.parser.get_full_text()
        words = full_text.split()
        unique_words = len(set(w.lower() for w in words))
        lexical_diversity = (unique_words / max(len(words), 1)) if words else 0.0
        density_score = min(100.0, lexical_diversity * 200.0)
        score_components.append(density_score * 0.15)
        findings.append(f"Lexical diversity: {lexical_diversity:.2f} ({unique_words} unique terms)")

        total_score = round(sum(score_components), 1)

        return LayerResult(
            layer_id="L2",
            layer_name="Semantic Extractability",
            weight=weight,
            score=total_score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="1.0.0",
                evidence_count=evidence_count,
                url=self.url,
            ),
            details={
                "h1_count": len(h1_list),
                "h2_count": len(h2_list),
                "h3_count": len(h3_list),
                "total_headings": len(self.parser.headings),
                "total_paragraphs": len(paragraphs),
                "optimal_chunks_count": len(self_contained_chunks),
                "has_bluf_opening": has_definition,
                "lexical_diversity": round(lexical_diversity, 2),
            },
            findings=findings,
        )

    def evaluate_l3_entity_clarity(self, weight: float = 0.20) -> LayerResult:
        """
        L3 Entity Clarity
        Measures JSON-LD schemas, sameAs disambiguation, entity consistency, and author/org identification.
        """
        findings = []
        evidence_count = 0
        score_components = []

        # 1. JSON-LD Schema Markup (Weight 40%)
        evidence_count += 1
        schemas_found = []
        schema_types = []
        same_as_links = []

        for raw_json in self.parser.script_json_ld:
            try:
                data = json.loads(raw_json)
                if isinstance(data, dict):
                    schemas_found.append(data)
                    stype = data.get("@type", "")
                    if stype:
                        schema_types.append(stype if isinstance(stype, str) else str(stype))
                    if "sameAs" in data:
                        same_as = data["sameAs"]
                        same_as_links.extend(same_as if isinstance(same_as, list) else [same_as])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            schemas_found.append(item)
                            stype = item.get("@type", "")
                            if stype:
                                schema_types.append(stype if isinstance(stype, str) else str(stype))
                            if "sameAs" in item:
                                same_as = item["sameAs"]
                                same_as_links.extend(same_as if isinstance(same_as, list) else [same_as])
            except Exception:
                pass

        schema_score = 0.0
        if schemas_found:
            schema_score = min(100.0, 50.0 + (len(schemas_found) * 15.0) + (len(set(schema_types)) * 10.0))
            findings.append(f"Structured Data: {len(schemas_found)} JSON-LD schemas found ({', '.join(set(schema_types))})")
        else:
            findings.append("No JSON-LD structured data detected")
        score_components.append(schema_score * 0.40)

        # 2. Entity Disambiguation (sameAs links to Wikidata, Wikipedia, etc.) (Weight 25%)
        evidence_count += 1
        authority_domains = ["wikidata.org", "wikipedia.org", "crunchbase.com", "linkedin.com", "github.com", "x.com", "twitter.com"]
        authoritative_same_as = [
            link for link in same_as_links if any(dom in str(link).lower() for dom in authority_domains)
        ]

        same_as_score = 0.0
        if authoritative_same_as:
            same_as_score = min(100.0, len(authoritative_same_as) * 35.0)
            findings.append(
                f"Entity Grounding: {len(authoritative_same_as)} authoritative sameAs references ({', '.join(str(s)[:35] for s in authoritative_same_as[:2])})"
            )
        elif same_as_links:
            same_as_score = 50.0
            findings.append(f"sameAs links present ({len(same_as_links)} total)")
        else:
            findings.append("No sameAs entity disambiguation links found in schemas")
        score_components.append(same_as_score * 0.25)

        # 3. Entity Name Consistency Across DOM (Weight 20%)
        evidence_count += 1
        title_text = self.parser.title
        desc_text = next((m.get("content", "") for m in self.parser.meta_tags if m.get("name", "").lower() == "description"), "")
        h1_text = " ".join(txt for tag, txt in self.parser.headings if tag == "h1")

        entity_target = self.target_brand.lower() if self.target_brand else ""
        if entity_target:
            matches_title = entity_target in title_text.lower()
            matches_h1 = entity_target in h1_text.lower()
            matches_desc = entity_target in desc_text.lower()
            consistency_pts = (matches_title * 40.0) + (matches_h1 * 35.0) + (matches_desc * 25.0)
            findings.append(
                f"Brand '{self.target_brand}' consistency: in title: {matches_title}, in H1: {matches_h1}, in meta description: {matches_desc}"
            )
        else:
            consistency_pts = 75.0 if title_text and h1_text else 40.0

        score_components.append(consistency_pts * 0.20)

        # 4. Organization / Author Entity Attribution (Weight 15%)
        evidence_count += 1
        has_author_or_org = any(
            t in ["Organization", "Corporation", "Person", "Author", "Brand", "SoftwareApplication"]
            for t in schema_types
        )
        auth_score = 100.0 if has_author_or_org else (50.0 if len(schemas_found) > 0 else 0.0)
        score_components.append(auth_score * 0.15)
        if has_author_or_org:
            findings.append("Explicit Organization / Author entity model identified in schema")

        total_score = round(sum(score_components), 1)

        return LayerResult(
            layer_id="L3",
            layer_name="Entity Clarity",
            weight=weight,
            score=total_score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="1.0.0",
                evidence_count=evidence_count,
                url=self.url,
            ),
            details={
                "schemas_count": len(schemas_found),
                "schema_types": list(set(schema_types)),
                "same_as_count": len(same_as_links),
                "authoritative_same_as_count": len(authoritative_same_as),
                "has_author_or_org_schema": has_author_or_org,
                "title": title_text[:80],
            },
            findings=findings,
        )

    def evaluate_l4_citation_readiness(self, weight: float = 0.20) -> LayerResult:
        """
        L4 Retrieval / Citation Readiness
        Measures structured comparison tables, quantitative statistics, citation-ready quote passages, and content cleanliness.
        """
        findings = []
        evidence_count = 0
        score_components = []

        # 1. Structured Data Tables (Weight 30%)
        evidence_count += 1
        tables = self.parser.tables
        table_rows = sum(len(t) for t in tables)

        table_score = 0.0
        if len(tables) >= 2 or table_rows >= 4:
            table_score = 100.0
            findings.append(f"High table density: {len(tables)} HTML tables ({table_rows} total rows) providing high token-extraction readiness")
        elif len(tables) == 1:
            table_score = 70.0
            findings.append(f"Single comparison table found with {table_rows} rows")
        else:
            findings.append("No HTML structured comparison tables found")
        score_components.append(table_score * 0.30)

        # 2. Quantitative Claims & Numeric Proof Points (Weight 30%)
        evidence_count += 1
        full_text = self.parser.get_full_text()
        numeric_matches = re.findall(r"(\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?|\b\d{2,}\b|\b\d+\.\d+\b)", full_text)
        stat_count = len(numeric_matches)

        stat_score = min(100.0, stat_count * 10.0)
        score_components.append(stat_score * 0.30)
        findings.append(f"Quantitative Data Points: {stat_count} metrics/percentages/numbers found (AI search engines prioritize quantitative evidence)")

        # 3. Citation-Ready Quote Passages (Weight 25%)
        evidence_count += 1
        paragraphs = self.parser.paragraphs
        quote_ready = [
            p
            for p in paragraphs
            if 15 <= len(p.split()) <= 60
            and any(
                kw in p.lower()
                for kw in [
                    "according to",
                    "provides",
                    "features",
                    "results in",
                    "increases",
                    "reduces",
                    "benchmark",
                    "نشان می‌دهد",
                    "افزایش",
                    "کاهش",
                    "دارای",
                ]
            )
        ]
        citation_passage_score = min(100.0, len(quote_ready) * 25.0)
        score_components.append(citation_passage_score * 0.25)
        findings.append(f"Citation-Ready Passages: {len(quote_ready)} quotable, high-relevance declarative sentences identified")

        # 4. Content Container Cleanliness (Weight 15%)
        evidence_count += 1
        has_main_container = self.parser.has_main or self.parser.has_article
        container_score = 100.0 if has_main_container else 60.0
        score_components.append(container_score * 0.15)
        if has_main_container:
            findings.append("Semantic <main> or <article> container isolates primary content from navigation boilerplate")
        else:
            findings.append("No semantic <main> or <article> tag found (crawler must infer main content boundaries)")

        total_score = round(sum(score_components), 1)

        return LayerResult(
            layer_id="L4",
            layer_name="Citation Readiness",
            weight=weight,
            score=total_score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="1.0.0",
                evidence_count=evidence_count,
                url=self.url,
            ),
            details={
                "tables_count": len(tables),
                "total_table_rows": table_rows,
                "quantitative_stats_count": stat_count,
                "sample_metrics": numeric_matches[:5],
                "citation_ready_passages_count": len(quote_ready),
                "has_semantic_main_container": has_main_container,
            },
            findings=findings,
        )
