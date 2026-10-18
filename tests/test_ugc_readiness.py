"""
Unit tests for UGC Fresh Data Readiness Audit (geo_scope/audit/ugc_readiness.py).
Validates:
  - 14 audit criteria evaluation
  - Detection of blocking issues vs non-blocking recommendations
  - Status classification (eligible_candidate vs needs_work)
  - Official Google disclaimer preservation
"""

import pytest
from geo_scope.audit.ugc_readiness import UGCFreshDataReadinessAudit


SAMPLE_ELIGIBLE_FORUM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Best SEO Practices for Modern Web Apps - Developer Forum</title>
    <link rel="canonical" href="https://forum.example.com/threads/seo-practices-2026">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "DiscussionForumPosting",
        "headline": "Best SEO Practices for Modern Web Apps",
        "datePublished": "2026-10-10T12:00:00Z",
        "dateModified": "2026-10-11T09:30:00Z",
        "author": {
            "@type": "Person",
            "name": "Alex Dev",
            "url": "https://forum.example.com/user/alex-dev"
        },
        "interactionStatistic": [
            {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/LikeAction",
                "userInteractionCount": 142
            },
            {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/CommentAction",
                "userInteractionCount": 38
            }
        ]
    }
    </script>
</head>
<body>
    <header>
        <a href="/guidelines">Community Guidelines & Rules</a>
        <a href="/report-abuse">Report Policy Violation</a>
    </header>
    <main>
        <h1>Best SEO Practices for Modern Web Apps</h1>
        <div class="byline">Posted by <a href="/user/alex-dev">Alex Dev</a></div>
        <p>In this discussion, let's explore AI visibility and server-side rendering...</p>
    </main>
</body>
</html>
"""

SAMPLE_BLOCKED_UGC_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="robots" content="noindex, nofollow">
</head>
<body>
    <p>Sign in to read this post. Login required.</p>
</body>
</html>
"""


def test_ugc_readiness_eligible_candidate():
    audit = UGCFreshDataReadinessAudit()
    res = audit.evaluate(
        html_content=SAMPLE_ELIGIBLE_FORUM_HTML,
        url="https://forum.example.com/threads/seo-practices-2026",
        config={
            "has_canonical_urls": True,
            "is_permanent_storage": True,
            "public_without_login": True,
            "robots_crawl_allowed": True,
            "has_public_creator_profiles": True,
            "visible_creator_attribution": True,
            "has_ugc_schema": True,
            "has_interaction_statistic": True,
            "structured_data_text_parity": True,
            "has_timestamps": True,
            "has_abuse_reporting": True,
            "has_moderation_policy": True,
            "updatable_counters": True,
            "oauth2_and_jsonld_ready": True,
        }
    )

    data = res["ugc_fresh_data_readiness"]
    assert data["status"] == "eligible_candidate"
    assert data["score"] >= 80
    assert len(data["blocking_issues"]) == 0
    assert data["disclaimer"] == UGCFreshDataReadinessAudit.OFFICIAL_DISCLAIMER


def test_ugc_readiness_needs_work_with_blocking_issues():
    audit = UGCFreshDataReadinessAudit()
    res = audit.evaluate(
        html_content=SAMPLE_BLOCKED_UGC_HTML,
        url=None,
        config={"public_without_login": False}
    )

    data = res["ugc_fresh_data_readiness"]
    assert data["status"] == "needs_work"
    assert data["score"] < 80
    assert len(data["blocking_issues"]) > 0
    # Must contain blocking issue about login or noindex
    assert any("login" in issue.lower() or "noindex" in issue.lower() or "schema" in issue.lower() for issue in data["blocking_issues"])
    assert data["disclaimer"] == UGCFreshDataReadinessAudit.OFFICIAL_DISCLAIMER
