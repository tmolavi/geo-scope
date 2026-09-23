<div align="center">

# ⟠ GEO-Scope

### Empirik Süni İntellekt Cavab Görünmə Ölçmə Çərçivəsi (AI Answer Visibility)

**Generativ süni intellekt sistemlərində obyektlərin (Entity) qeyd olunması, tövsiyə edilməsi, istinad verilməsi və mənsubiyyətini empirik olaraq ölçən və sübut zəncirini qoruyan açıq mənbəli çərçivə.**

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)
[![فارسی](https://img.shields.io/badge/فارسی-README.fa.md-green)](README.fa.md)
[![Türkçe](https://img.shields.io/badge/T%C3%BCrk%C3%A7e-README.tr.md-red)](README.tr.md)
[![Azərbaycan](https://img.shields.io/badge/Az%C9%99rbaycan-README.az.md-orange)](#)
[![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README.ar.md-teal)](README.ar.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research Paper Outline](https://img.shields.io/badge/Research-Paper%20Outline-purple)](docs/RESEARCH_PAPER_OUTLINE.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[Giriş](#1-giriş) • [Ölçülən Sahələr](#2-geo-scope-nəyi-ölçür) • [Qeyri-empirik Sahələr](#3-geo-scope-nəyi-ölçmür) • [Memarlıq](#4-sistem-memarlığı) • [İcra Rejimləri](#5-icra-rejimləri-execution-modes) • [Təkrar İstehsal](#6-təkrar-istehsal-və-yoxlama) • [Tez Başlama](#7-quraşdırma-və-istifadə)

</div>

---

## 1. Giriş

Generativ süni intellekt sistemləri və internet axtarışı ilə dəstəklənən cavab mühərrikləri (Search Answer Engines) məlumat əldə etmək üçün əsas kəşf qatına çevrilməkdədir.

**GEO-Scope**, süni intellekt modellərinin sualları necə cavablandırdığını sübuta əsaslanan və müstəqil şəkildə yoxlanıla bilən metodologiya ilə ölçmək üçün hazırlanmış açıq mənbəli ölçmə çərçivəsidir. Təsdiqlənməmiş reytinq alqoritmləri iddia etmək əvəzinə, sənədləşdirilmiş və neytral sorğu dəstləri altındakı müşahidə olunan model nəticələrini qeyd edir və təhlil edir.

---

## 2. GEO-Scope Nəyi Ölçür?

GEO-Scope görünmənin dörd müstəqil ölçüsünü bir-birindən dəqiq ayırır:

1. **Obyektin Qeyd Olunması (Mention - `mentioned`)**: Hədəf obyekt (brend, şəxs, texnologiya, təşkilat) cavabda qeyd edilibmi? (Omonim filtrləmə və çoxdilli normalizasiya daxil olmaqla).
2. **Açıq Tövsiyə (Recommendation - `recommended`)**: Model obyekti açıq şəkildə tövsiyə olunan və ya ən yaxşı seçim kimi təqdim etdimi? (`mentioned != recommended`).
3. **Domen İstinadı (Citation - `cited`)**: Model cavabında hədəf obyektə aid veb sayt linki və ya mənbə URL-i yer aldımı?
4. **Mətn Mənsubiyyəti (Attribution - `attributed`)**: Hər hansı bir məlumat və ya fakt mətndə birbaşa hədəf obyektə aid edildimi? (URL linki olmasa belə).
5. **Sıra Pozisiyası (Rank - `rank`)**: Yalnız cavabda nömrələnmiş sıra siyahısı olduqda ədədi sıra kimi çıxarılır (ümumi məlumat sorğularında `null` təyin edilir).

---

## 3. GEO-Scope Nəyi Ölçmür?

Elmi sərhədləri qorumaq məqsədilə:
- ❌ Modellərin daxili reytinq alqoritmləri və ya gizli çəkiləri tərs mühəndisliklə araşdırılmır.
- ❌ Modellərin gizli təlim məlumatları təhlil edilmir; yalnız müşahidə edilə bilən API çıxışları ölçülür.
- ❌ Səbəb-nəticə reytinq amilləri (Causal Ranking Factors) iddia edilmir.
- ❌ Simulyasiya məlumatları ilə canlı ölçmə məlumatları heç vaxt qarışdırılmır.

---

## 4. Sistem Memarlığı

```text
Təchizatçı Qatı (Provider Layer: Answer Engine / LLM)
        ↓
Ölçmə Mühərriki (Measurement Engine)
        ↓
Xam Cavabların Saxlanması (Raw Response Storage: raw_responses.jsonl)
        ↓
Müşahidə Analizatoru (Observation Parser)
        ↓
Metriklərin Hesablanması (Metrics Calculation)
        ↓
Sübut Paketləri və Hesabatlar (Reports + Replay Bundle)
```

---

## 5. İcra Rejimləri (Execution Modes)

- **`demo` (Simulyasiya)**: İnkişaf, test və CI yoxlaması üçün yerəl sintetik məlumat rejimi. Rəsmi bençmarklara daxil edilmir.
- **`measure` (Canlı Ölçmə)**: Həqiqi API-lar üzərində işləyən və xəta zamanı saxta məlumat əvəzləməsi etməyən (**Zero Silent Fallback**) canlı ölçmə rejimi.
- **`replay` (Oflayn Təkrar İstehsal)**: Saxlanılan `raw_responses.jsonl` faylından şəbəkə çağırışı etmədən metrikləri yenidən hesablayan audit rejimi.

---

## 6. Təkrar İstehsal və Yoxlama

`benchmark/releases/` altındakı bütün məlumat dəstləri `checksums.sha256` kriptoqrafik xülasələri ilə qorunur:

```bash
# Məlumat dəstinin bütövlüyünü yoxlamaq
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# Oflayn təkrar istehsal (Replay)
geo-scope replay --bundle benchmark/releases/global-ai-answers-2026.2 --out-dir output/replay_az
```

---

## 7. Quraşdırma və İstifadə

```bash
# Repozitoriyanı klonlayın
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Paketi inkişaf rejimində quraşdırın
pip install -e .

# Simulyasiya demosunu başladın
geo-scope demo

# Golden Parser testini başladın
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

---

## Müəllif və Lisenziya

Müəllif: **[Taqi Molavi](https://molavi.pro)** — [MIT License](LICENSE) altında lisenziyalaşdırılmışdır.
