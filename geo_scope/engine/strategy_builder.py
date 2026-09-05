"""Evidence-aware follow-up planning; suggestions are not measured effect sizes."""


def generate_geo_playbook(analysis, delta_info=None):
    summary = analysis["summary"]
    topics = [
        (
            "Review source content",
            "بررسی محتوای منابع",
            "Check factual completeness and clear answers against the observed queries.",
            "کامل‌بودن اطلاعات و پاسخ روشن به پرسش‌های مشاهده‌شده را بررسی کنید.",
        ),
        (
            "Review cited communities",
            "بررسی انجمن‌های استنادشده",
            "Inspect observed citations before selecting relevant communities.",
            "پیش از انتخاب انجمن مرتبط، منابع واقعی پاسخ‌ها را بررسی کنید.",
        ),
        (
            "Review product information",
            "بررسی اطلاعات محصول",
            "Keep verified product facts and pricing consistent across relevant directories.",
            "اطلاعات تأییدشده محصول و قیمت را در دایرکتوری‌های مرتبط هماهنگ نگه دارید.",
        ),
        (
            "Check entity consistency",
            "بررسی یکپارچگی موجودیت",
            "Verify official identity links and structured data against public facts.",
            "پیوندهای هویت رسمی و داده ساختاریافته را با واقعیت‌های عمومی تطبیق دهید.",
        ),
        (
            "Run matched experiments",
            "اجرای آزمایش‌های همسان",
            "Repeat the saved prompt set and review variability; changes alone do not prove causality.",
            "پرسش‌های ذخیره‌شده را تکرار و نوسان را بررسی کنید؛ تغییر به‌تنهایی علت را اثبات نمی‌کند.",
        ),
    ]
    return {
        "target_brand": summary["target_brand"],
        "execution_mode": summary.get("execution_mode", "unknown"),
        "evidence_status": "research_suggestions_not_measured_effect_sizes",
        "current_sov": summary["overall_sov"],
        "current_top1_rate": summary["overall_top1_rate"],
        "feedback_loop": {
            "is_first_audit": True,
            "delta_sov_pct": 0,
            "delta_top1_pct": 0,
            "status_label": "Compare matched experiments; automated causal claims disabled",
        },
        "pillars": [
            {
                "pillar_id": i,
                "name_en": en,
                "name_fa": fa,
                "impact_score": "Unmeasured",
                "tactics": [{"title_en": en, "title_fa": fa, "desc_en": desc, "desc_fa": desc_fa}],
            }
            for i, (en, fa, desc, desc_fa) in enumerate(topics, 1)
        ],
    }
