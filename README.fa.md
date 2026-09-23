<div align="center">

# ⟠ GEO-Scope

### فریم‌ورک متن‌باز سنجش تجربی هویدایی پاسخ‌ها در هوش مصنوعی (AI Answer Visibility)

**یک فریم‌ورک استاندارد و متن‌باز برای سنجش تجربی و ثبت شواهد قابل بازرسی پیرامون نحوه نمایش، پیشنهاد، استناد و ارجاع موجودیت‌ها در مدل‌های هوش مصنوعی مولد.**

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)
[![فارسی](https://img.shields.io/badge/فارسی-README.fa.md-green)](#)
[![Türkçe](https://img.shields.io/badge/T%C3%BCrk%C3%A7e-README.tr.md-red)](README.tr.md)
[![Azərbaycan](https://img.shields.io/badge/Az%C9%99rbaycan-README.az.md-orange)](README.az.md)
[![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README.ar.md-teal)](README.ar.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research Paper Outline](https://img.shields.io/badge/Research-Paper%20Outline-purple)](docs/RESEARCH_PAPER_OUTLINE.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[معرفی](#۱-معرفی) • [موارد قابل سنجش](#۲-چه-مواردی-توسط-geo-scope-سنجیده-میشود) • [مرزهای اپیستمیک](#۳-چه-مواردی-توسط-geo-scope-سنجیده-نمیشود) • [معماری](#۴-معماری-سیستم) • [حالت‌های اجرا](#۵-حالتهای-اجرا-execution-modes) • [بازتولیدپذیری](#۶-بازتولیدپذیری-و-اعتبارسنجی) • [راهنمای سریع](#۷-نصب-و-راهاندازی-سریع)

</div>

---

## ۱. معرفی

سیستم‌های هوش مصنوعی مولد و موتورهای پاسخ‌دهی متصل به وب (Answer Engines) به سرعت در حال تبدیل شدن به لایه اصلی اکتشاف اطلاعات برای کاربران هستند.

**GEO-Scope** یک فریم‌ورک پژوهشی و مهندسی مبتنی بر شواهد است که با هدف اندازه‌گیری تجربی، تفکیک ابعاد هویدایی (Visibility)، و نگهداری ردپای شواهد کامل پاسخ‌های ارائه‌شده توسط مدل‌های زبانی طراحی شده است. این ابزار بدون ادعاهای غیرعلمی و بدون فرض‌های غیرقابل اثبات، رفتار خروجی مدل‌ها را در برابر مجموعه‌پرامپت‌های خنثی ثبت و تحلیل می‌کند.

---

## ۲. چه مواردی توسط GEO-Scope سنجیده می‌شود؟

GEO-Scope تفکیک ساختاریافته‌ای میان ۴ بعد هویدایی برقرار می‌کند:

۱. **نمایش موجودیت (Mention - `mentioned`)**: آیا موجودیت، برند، فرد یا فناوری مورد نظر در پاسخ هوش مصنوعی ظاهر شده است؟ (با در نظر گرفتن نگارش چندزبانه، نیم‌فاصله‌ها و تفکیک همنام‌ها).
۲. **پیشنهاد صریح (Recommendation - `recommended`)**: آیا مدل به شکل صریح موجودیت را به عنوان گزینه برتر یا راهکار پیشنهادی توصیه کرده است؟ (`mentioned != recommended`).
۳. **استناد دامنه (Citation - `cited`)**: آیا لینک، URL یا منبع دامنه‌ای متعلق به موجودیت در پاسخ مدل درج شده است؟
۴. **ارجاع متنی (Attribution - `attributed`)**: آیا گزاره، آمار یا ادعایی در متن صریحاً به موجودیت ارجاع داده شده است؟ (حتی اگر لینک مستقیم وجود نداشته باشد).
۵. **رتبه عددی (Rank - `rank`)**: رتبه استخراج‌شده صرفاً در مواردی که یک لیست مرتب پاسخ داده شده است (در سوالات عمومی و بدون رتبه‌بندی، مقدار `null` درج می‌شود).

---

## ۳. چه مواردی توسط GEO-Scope سنجیده نمی‌شود؟

به منظور حفظ دقت علمی:
- ❌ الگوریتم‌های رتبه‌بندی درونی یا وزن‌های مخفی مدل‌ها مهندسی معکوس نمی‌شوند.
- ❌ داده‌های آموزش خصوصی مدل‌ها ارزیابی نمی‌شوند؛ سنجش صرفاً روی خروجی‌های قابل مشاهده صورت می‌گیرد.
- ❌ ادعای کشف فاکتورهای علیتی (Causal Ranking Factors) مطرح نمی‌شود.
- ❌ شبیه‌سازی با داده‌های زنده یکسان در نظر گرفته نمی‌شود.

---

## ۴. معماری سیستم

```text
لایه‌ تأمین‌کنندگان (Provider Layer)
        ↓
موتور سنجش (Measurement Engine)
        ↓
ذخیره‌سازی پاسخ‌های خام (Raw Response Storage)
        ↓
پارسِر مشاهدات (Observation Parser)
        ↓
محاسبه سنجه‌ها (Metrics Calculation)
        ↓
بسته‌های شواهد و گزارش‌ها (Reports + Replay Bundle)
```

---

## ۵. حالت‌های اجرا (Execution Modes)

- **`demo` (شبیه‌سازی)**: داده‌های ساختگی محلی صرفاً برای تست اولیه، توسعه و CI. این داده‌ها وارد بنچمارک‌های رسمی نمی‌شوند.
- **`measure` (سنجش زنده)**: اجرای زنده پرامپت‌ها روی APIهای واقعی با سیاست **عدم جایگزینی خودکار شبیه‌سازی در صورت خطا (Zero Silent Fallback)**.
- **`replay` (بازپخش آفلاین)**: اجرای محاسبات و پارس مجدد مستقیماً از روی فایل `raw_responses.jsonl` بدون نیاز به دسترسی اینترنت یا هزینه API.

---

## ۶. بازتولیدپذیری و اعتبارسنجی

تمامی بنچمارک‌های منتشرشده در پوشه `benchmark/releases/` با هش‌های رمزنگاری شده `checksums.sha256` تضمین شده‌اند:

```bash
# اعتبارسنجی یکپارچگی فایل‌های بنچمارک
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# بازپخش و محاسبه مجدد سنجه‌ها به صورت آفلاین
geo-scope replay --bundle benchmark/releases/global-ai-answers-2026.2 --out-dir output/replay_fa
```

---

## ۷. نصب و راه‌اندازی سریع

```bash
# کلون کردن مخزن
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# نصب بسته به صورت قابل ویرایش
pip install -e .

# اجرای تست دمو
geo-scope demo

# ارزیابی پارسر روی Golden Dataset
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

---

## ارجاع و حق امتیاز

توسعه‌داده‌شده توسط **[تقی مولوی](https://molavi.pro)** — تحت مجوز [MIT License](LICENSE).
