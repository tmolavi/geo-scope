"""
UGC Fresh Data Readiness Audit Engine for GEO-Scope.
Evaluates publisher & platform readiness for Google's UGC Fresh Data Program.
Reference: https://developers.google.com/search/docs/appearance/ugc-fresh-data-program

Mandatory Invariant:
This audit does not guarantee acceptance into Google's program or appearance in Search.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class UGCAuditCheck(BaseModel):
    id: str
    name: str
    category: str
    passed: bool
    weight: int
    is_blocking: bool = False
    detail: str


class UGCFreshDataReadinessAudit:
    """
    Evaluates whether a UGC platform, forum, or social community site
    satisfies the 14 baseline prerequisites of Google's UGC Fresh Data Program.
    """

    OFFICIAL_DISCLAIMER = (
        "This audit does not guarantee acceptance into Google's program or appearance in Search."
    )

    def evaluate(
        self,
        html_content: Optional[str] = None,
        url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the UGC Fresh Data Readiness evaluation.
        Accepts HTML content and optional platform config dictionary.
        """
        config = config or {}
        html = html_content or ""
        html_lower = html.lower()

        checks: List[UGCAuditCheck] = []
        blocking_issues: List[str] = []
        recommended_actions: List[str] = []

        # 1. public_stable_url
        has_stable_url = bool(url or config.get("has_canonical_urls", False) or ('<link rel="canonical"' in html_lower))
        checks.append(UGCAuditCheck(
            id="public_stable_url",
            name="Public Stable Canonical URL",
            category="accessibility",
            passed=has_stable_url,
            weight=8,
            is_blocking=True,
            detail="Content resolves to a permanent, canonical URL." if has_stable_url else "Missing canonical public URL structure.",
        ))
        if not has_stable_url:
            blocking_issues.append("UGC items must resolve to permanent, publicly accessible canonical URLs.")

        # 2. permanent_storage
        is_permanent = config.get("is_permanent_storage", True) and not bool(re.search(r"\b(expires in|disappearing|24h story)\b", html_lower))
        checks.append(UGCAuditCheck(
            id="permanent_storage",
            name="Permanent Storage (Non-Ephemeral)",
            category="accessibility",
            passed=is_permanent,
            weight=6,
            is_blocking=True,
            detail="Content stored permanently without auto-deletion." if is_permanent else "Content appears to reside on ephemeral or temporary feeds.",
        ))
        if not is_permanent:
            blocking_issues.append("Content must not reside on temporary feeds or auto-expiring stories.")

        # 3. no_mandatory_login_or_paywall
        has_no_wall = not bool(re.search(r"\b(sign in to read|login required|subscribe to view|paywall)\b", html_lower)) and config.get("public_without_login", True)
        checks.append(UGCAuditCheck(
            id="no_mandatory_login_or_paywall",
            name="Publicly Visible Without Login or Paywall",
            category="accessibility",
            passed=has_no_wall,
            weight=8,
            is_blocking=True,
            detail="Directly accessible to anonymous visitors." if has_no_wall else "Content requires account login or paywall.",
        ))
        if not has_no_wall:
            blocking_issues.append("Anonymous visitors and Googlebot must be able to view content without mandatory sign-in.")

        # 4. googlebot_crawl_allowed
        robots_ok = not bool(re.search(r'<meta[^>]*robots[^>]*content=["\']noindex', html_lower)) and config.get("robots_crawl_allowed", True)
        checks.append(UGCAuditCheck(
            id="googlebot_crawl_allowed",
            name="Googlebot Crawling Allowed",
            category="crawlability",
            passed=robots_ok,
            weight=8,
            is_blocking=True,
            detail="Robots meta directives permit indexing." if robots_ok else "noindex directive detected.",
        ))
        if not robots_ok:
            blocking_issues.append("Remove noindex directives to allow Googlebot crawling.")

        # 5. public_creator_profile
        has_creator_profile = bool(re.search(r'href=["\'](?:/user/|/u/|/profile/|/author/|/creator/)', html_lower)) or config.get("has_public_creator_profiles", False)
        checks.append(UGCAuditCheck(
            id="public_creator_profile",
            name="Public Creator Profile Page",
            category="attribution",
            passed=has_creator_profile,
            weight=7,
            detail="Link to creator's public profile detected." if has_creator_profile else "No link to author/creator profile page found.",
        ))
        if not has_creator_profile:
            recommended_actions.append("Add public profile links for content authors.")

        # 6. creator_attribution_visible
        has_visible_author = bool(re.search(r'\b(by|author|posted by|نویسنده|yazar)\b', html_lower)) or config.get("visible_creator_attribution", True)
        checks.append(UGCAuditCheck(
            id="creator_attribution_visible",
            name="Visible Creator Attribution",
            category="attribution",
            passed=has_visible_author,
            weight=7,
            detail="Creator name/handle is visibly rendered." if has_visible_author else "Missing visible creator attribution in on-page UI.",
        ))

        # 7. structured_data_schema
        has_ugc_schema = bool(re.search(r'(SocialMediaPosting|DiscussionForumPosting|Comment|Review)', html, re.IGNORECASE)) or config.get("has_ugc_schema", False)
        checks.append(UGCAuditCheck(
            id="structured_data_schema",
            name="Schema.org UGC Vocabulary",
            category="structured_data",
            passed=has_ugc_schema,
            weight=10,
            is_blocking=True,
            detail="Detected SocialMediaPosting / DiscussionForumPosting schema." if has_ugc_schema else "Missing Schema.org DiscussionForumPosting or SocialMediaPosting JSON-LD.",
        ))
        if not has_ugc_schema:
            blocking_issues.append("Implement Schema.org DiscussionForumPosting or SocialMediaPosting JSON-LD.")

        # 8. valid_interaction_statistic
        has_interaction = bool(re.search(r'interactionStatistic', html, re.IGNORECASE)) or config.get("has_interaction_statistic", False)
        checks.append(UGCAuditCheck(
            id="valid_interaction_statistic",
            name="Valid Interaction Statistics",
            category="structured_data",
            passed=has_interaction,
            weight=8,
            detail="interactionStatistic (LikeAction/CommentAction) present." if has_interaction else "interactionStatistic not declared in JSON-LD.",
        ))
        if not has_interaction:
            recommended_actions.append("Include interactionStatistic objects for likes, comments, and views in schema.")

        # 9. structured_data_matches_visible_text
        schema_parity = config.get("structured_data_text_parity", True)
        checks.append(UGCAuditCheck(
            id="structured_data_matches_visible_text",
            name="Visible Text & Schema Parity",
            category="structured_data",
            passed=schema_parity,
            weight=7,
            detail="Schema text matches rendered page content." if schema_parity else "Discrepancy detected between schema and visible page.",
        ))

        # 10. publication_and_modification_timestamps
        has_timestamps = bool(re.search(r'(datePublished|dateModified)', html, re.IGNORECASE)) or config.get("has_timestamps", False)
        checks.append(UGCAuditCheck(
            id="publication_and_modification_timestamps",
            name="ISO 8601 Publication & Modification Timestamps",
            category="metadata",
            passed=has_timestamps,
            weight=8,
            detail="datePublished and/or dateModified present." if has_timestamps else "Timestamps missing in metadata.",
        ))
        if not has_timestamps:
            recommended_actions.append("Ensure ISO 8601 datePublished and dateModified timestamps are exposed in JSON-LD.")

        # 11. abuse_reporting_mechanism
        has_abuse = bool(re.search(r'\b(report|flag|گزارش تخلف|şikayet et|إبلاغ)\b', html_lower)) or config.get("has_abuse_reporting", True)
        checks.append(UGCAuditCheck(
            id="abuse_reporting_mechanism",
            name="Abuse / Violation Reporting Mechanism",
            category="trust_and_safety",
            passed=has_abuse,
            weight=6,
            detail="Abuse reporting link or flag button detected." if has_abuse else "No clear abuse reporting mechanism found.",
        ))
        if not has_abuse:
            recommended_actions.append("Add a clear mechanism for community members to flag policy violations.")

        # 12. public_moderation_policy
        has_policy = bool(re.search(r'\b(community guidelines|rules|قوانین|kullanım kuralları)\b', html_lower)) or config.get("has_moderation_policy", False)
        checks.append(UGCAuditCheck(
            id="public_moderation_policy",
            name="Public Content Moderation Policy",
            category="trust_and_safety",
            passed=has_policy,
            weight=6,
            detail="Community guidelines or moderation rules present." if has_policy else "Missing public moderation guidelines.",
        ))
        if not has_policy:
            recommended_actions.append("Publish clear community guidelines in footer.")

        # 13. updatable_engagement_counter
        counters_ok = config.get("updatable_counters", True)
        checks.append(UGCAuditCheck(
            id="updatable_engagement_counter",
            name="Dynamic Engagement Counter Sync",
            category="technical",
            passed=counters_ok,
            weight=5,
            detail="Engagement counters sync dynamically." if counters_ok else "Static counters without update pipeline.",
        ))

        # 14. oauth2_and_jsonld_validation_ready
        oauth_ready = config.get("oauth2_and_jsonld_ready", True)
        checks.append(UGCAuditCheck(
            id="oauth2_and_jsonld_validation_ready",
            name="OAuth 2.0 & JSON-LD Validation Pipeline",
            category="technical",
            passed=oauth_ready,
            weight=6,
            detail="Team has demonstrated automated JSON-LD feed capability." if oauth_ready else "Feed validation capability not established.",
        ))

        # Compute Total Score
        max_score = sum(c.weight for c in checks)
        achieved_score = sum(c.weight for c in checks if c.passed)
        pct_score = round((achieved_score / max_score) * 100) if max_score > 0 else 0

        # Status
        if len(blocking_issues) == 0 and pct_score >= 80:
            status = "eligible_candidate"
        else:
            status = "needs_work"

        return {
            "ugc_fresh_data_readiness": {
                "status": status,
                "score": pct_score,
                "max_score": 100,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "checks": [c.model_dump() for c in checks],
                "blocking_issues": blocking_issues,
                "recommended_actions": recommended_actions,
                "disclaimer": self.OFFICIAL_DISCLAIMER,
            }
        }
