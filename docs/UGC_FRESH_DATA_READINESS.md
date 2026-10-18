# UGC Fresh Data Readiness Audit Specification

**Version:** 1.0.0  
**Effective Date:** October 2026  
**Module:** `geo_scope.audit.ugc_readiness`  
**Reference:** [Google UGC Fresh Data Program Documentation](https://developers.google.com/search/docs/appearance/ugc-fresh-data-program)  
**Status:** Optional Standalone Audit Module  

---

## 1. Overview and Purpose

Google's **UGC Fresh Data Program** allows community platforms, forums, and creator networks to submit structured, fresh user-generated content feeds to Google via automated feeds or real-time APIs.

This module provides a technical and structural readiness audit for publishers, forums, community hubs, and media portals seeking to determine whether their platform architecture is eligible and technically prepared for Google's program.

### Scope & Invariant
- **This module is strictly an audit tool.** It does not turn GEO-Scope into a content submission platform or proxy.
- **This audit does NOT guarantee acceptance into Google's program or indexation in Google Search.**
- **This module is optional and does not directly alter or distort core MAVI empirical scores.**

---

## 2. Comprehensive Audit Checklist (14 Criteria)

The audit evaluates platforms against 14 essential technical and editorial criteria:

### Category A: URL Permanence & Public Accessibility
1. **Public Stable URL:** Each piece of UGC (post, thread, comment, review) must resolve to a permanent, canonical, publicly accessible URL.
2. **Permanent Storage:** Content must not reside exclusively in ephemeral feeds, temporary stories, or disappearing streams.
3. **No Forced Login or Paywall:** Content must be directly visible to anonymous visitors and crawlers without requiring account creation, login, or paywall bypass.
4. **Crawlability & Robots Integrity:** `robots.txt`, HTTP headers (`X-Robots-Tag`), and firewall rules must permit Googlebot full access without cloaking.

### Category B: Creator Identity & Attribution
5. **Public Creator Profile:** The author/creator must possess a dedicated public profile or identifier page on the platform.
6. **Visible Attribution:** Creator name/handle and profile link must be clearly rendered in the visible on-page UI.

### Category C: Structured Data & Schema.org Compliance
7. **Schema.org Vocabulary:** Must implement valid JSON-LD schemas: `SocialMediaPosting`, `DiscussionForumPosting`, `Comment`, or `Review`.
8. **Valid Interaction Statistics:** Must declare valid `interactionStatistic` objects (`LikeAction`, `CommentAction`, `ShareAction`, `ViewAction`).
9. **Visible Text Parity:** Structured data payload must strictly match the visible rendered textual content (no hidden or deceptive schema).
10. **Timestamp Precision:** Must provide ISO 8601 timestamps for `datePublished` and `dateModified`.

### Category D: Content Moderation & Platform Trust
11. **Abuse & Violation Reporting:** Platform must provide a visible, functional mechanism for users to report policy violations or copyright infringement.
12. **Public Moderation Guidelines:** Platform must publish transparent Community Guidelines and Content Moderation policies.
13. **Real-Time / Fresh Engagement Counters:** System must be capable of reflecting updated engagement counters within reasonable sync cycles.

### Category E: Technical Ingestion Capability
14. **OAuth 2.0 & Feed Validation:** Technical team must possess the capability to generate validated JSON-LD payloads and support OAuth 2.0 machine-to-machine authentication.

---

## 3. Output Schema & Scoring Model

The audit engine returns a structured result:

```json
{
  "ugc_fresh_data_readiness": {
    "status": "eligible_candidate",
    "score": 88,
    "max_score": 100,
    "evaluated_at": "2026-10-12T14:30:00Z",
    "checks": [
      {
        "id": "public_stable_url",
        "category": "accessibility",
        "passed": true,
        "weight": 8,
        "detail": "Every tested UGC item resolves to a permanent canonical URL."
      },
      {
        "id": "schema_jsonld",
        "category": "structured_data",
        "passed": true,
        "weight": 10,
        "detail": "Valid DiscussionForumPosting JSON-LD found with author and interactionStatistic."
      }
    ],
    "blocking_issues": [],
    "recommended_actions": [
      "Add explicit dateModified field to JSON-LD when edits occur.",
      "Publish dedicated moderation policy page in footer."
    ],
    "disclaimer": "This audit does not guarantee acceptance into Google's program or appearance in Search."
  }
}
```

### 3.1 Status Determination
- **`eligible_candidate`** (Score $\ge 80$ with 0 blocking issues): Meets baseline prerequisites; ready for formal program application review.
- **`needs_work`** (Score $< 80$ or $\ge 1$ blocking issues): Identified structural or crawlability deficiencies that must be remediated.
- **`not_applicable`**: Target domain is not a UGC, community, or forum platform.

---

*UGC Fresh Data Readiness Audit Specification v1.0.*
