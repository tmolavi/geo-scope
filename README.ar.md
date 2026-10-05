<div align="center">

# ⟠ GEO-Scope

### إطار عمل مفتوح المصدر للقياس التجريبي لظهور الإجابات في الذكاء الاصطناعي (AI Answer Visibility)

**إطار عمل تجريبي ومفتوح المصدر لقياس وحفظ أدلة ظهور الكيانات (Entity)، والتوصية بها، والاستشهاد بمصادرها، ونسب المعلومات إليها عبر أنظمة الذكاء الاصطناعي التوليدي.**

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)
[![فارسی](https://img.shields.io/badge/فارسی-README.fa.md-green)](README.fa.md)
[![Türkçe](https://img.shields.io/badge/T%C3%BCrk%C3%A7e-README.tr.md-red)](README.tr.md)
[![Azərbaycan](https://img.shields.io/badge/Az%C9%99rbaycan-README.az.md-orange)](README.az.md)
[![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README.ar.md-teal)](#)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research Paper](https://img.shields.io/badge/Research-Paper-purple)](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[المقدمة](#١-المقدمة) • [ما يقيسه الإطار](#٢-ما-يقيسه-geo-scope) • [ما لا يقيسه الإطار](#٣-ما-لا-يقيسه-geo-scope) • [البنية الهندسية](#٤-البنية-الهندسية-للنظام) • [أنماط التشغيل](#٥-أنماط-التشغيل-execution-modes) • [إعادة الإنتاج](#٦-إعادة-الإنتاج-والتدقيق) • [دليل البدء السريع](#٧-التثبيت-والاستخدام)

</div>

---

## ١. المقدمة

أصبحت أنظمة الذكاء الاصطناعي التوليدي ومحركات الإجابة المدعومة بالبحث على الويب (Search Answer Engines) طبقة الاستكشاف الأساسية للوصول إلى المعلومات والخدمات.

**GEO-Scope** هو إطار عمل هندسي وبحثي مبني على الأدلة لقياس مخرجات نماذج الذكاء الاصطناعي تجريبياً وحفظ سلسلة الأدلة الكاملة للتحقق منها بشكل مستقل. بدلاً من افتراض خوارزميات ترتيب غير مثبتة، يقوم الإطار بتسجيل وتحليل مخرجات النماذج القابلة للملاحظة تحت مجموعات مطالبات (prompts) محايدة وموثقة.

---

## ٢. ما يقيسه GEO-Scope؟

يميز GEO-Scope بدقة بين أربعة أبعاد مستقلة للظهور:

١. **ذكر الكيان (Mention - `mentioned`)**: هل ظهر الكيان المستهدف (علامة تجارية، شخص، تقنية، مؤسسة) في إجابة النموذج؟ (مع معالجة الأسماء المترادفة والتطبيع اللغوي وتصفية الكلمات المتجانسة).
٢. **التوصية الصريحة (Recommendation - `recommended`)**: هل أوصى النموذج صراحةً بالكيان كخيار مفضل أو حل مقترح؟ (`mentioned != recommended`).
٣. **الاستشهاد بالنطاق (Citation - `cited`)**: هل تضمنت الإجابة رابطاً لموقع الكيان أو مصدراً لنطاقه؟
٤. **نسب المعلومات (Attribution - `attributed`)**: هل تم نسب حقيقة أو إحصائية أو ادعاء نصياً إلى الكيان المستهدف؟ (حتى وإن لم يتوفر رابط URL نشط).
٥. **الترتيب العددي (Rank - `rank`)**: يُستخرج فقط عند وجود قائمة مرتبة في الإجابة (في الأسئلة العامة غير المرتبة يتم تعيين القيمة `null`).

---

## ٣. ما لا يقيسه GEO-Scope؟

للحفاظ على الدقة والنزاهة العلمية:
- ❌ لا يدعي الإطار الهندسة العكسية لخوارزميات الترتيب الداخلية أو الأوزان المخفية للنماذج.
- ❌ لا يفحص بيانات التدريب الخاصة غير المعلنة؛ القياس يعتمد فقط على مخرجات واجهات البرمجة (APIs) القابلة للملاحظة.
- ❌ لا يدعي اكتشاف عوامل ترتيب سببية (Causal Ranking Factors).
- ❌ لا يتم خلط بيانات المحاكاة الافتراضية مع بيانات القياس الحية أبداً.

---

## ٤. البنية الهندسية للنظام

```text
طبقة المزودين (Provider Layer: Answer Engine / LLM)
        ↓
محرك القياس (Measurement Engine)
        ↓
تخزين الإجابات الخام (Raw Response Storage: raw_responses.jsonl)
        ↓
محلل المشاهدات (Observation Parser)
        ↓
حساب المقاييس (Metrics Calculation)
        ↓
حزم الأدلة والتقارير (Reports + Replay Bundle)
```

---

## ٥. أنماط التشغيل (Execution Modes)

- **`demo` (المحاكاة)**: نمط بيانات محلية وهمية مخصص للتطوير واختبارات التكامل (CI). لا يتم إدراج هذه البيانات في حزم القياس المرجعية الرسمية.
- **`measure` (القياس المباشر)**: تشغيل مباشر على واجهات البرمجة الحقيقية مع تطبيق سياسة **منع الاستبدال التلقائي للبيانات الوهمية عند الخطأ (Zero Silent Fallback)**.
- **`replay` (إعادة التشغيل دون اتصال)**: إعادة حساب وتدقيق المقاييس مباشرة من ملف `raw_responses.jsonl` دون الحاجة للاتصال بالإنترنت أو تكبد تكاليف واجهات البرمجة.

---

## ٦. إعادة الإنتاج والتدقيق

جميع مجموعات البيانات المنشورة في `benchmark/releases/` محمية بملفات الهاش المشفرة `checksums.sha256`:

```bash
# التحقق من سلامة ملفات حزمة القياس
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# إعادة حساب المقاييس محلياً دون اتصال
geo-scope replay --bundle benchmark/releases/global-ai-answers-2026.2 --out-dir output/replay_ar
```

---

## ٧. التثبيت والاستخدام

```bash
# استنساخ المستودع
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# تثبيت الحزمة
pip install -e .

# تشغيل العرض التجريبي للمحاكاة
geo-scope demo

# تقييم المحلل باستخدام Golden Dataset
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

---

## الاقتباس والترخيص

تم التطوير بواسطة **[تقي مولوي (Taqi Molavi)](https://molavi.pro)** — مرخص بموجب [MIT License](LICENSE).
