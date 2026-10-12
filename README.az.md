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
[![Research Paper](https://img.shields.io/badge/Research-Paper-purple)](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[🏆 Mühüm Bençmark (İran və Türkiyə)](#-mühüm-bençmark-kommersiya-süni-i̇ntellekt-görünməsi--i̇ran-və-türkiyə-20261) • [Giriş](#1-giriş) • [Ölçülən Sahələr](#2-geo-scope-nəyi-ölçür) • [Qeyri-empirik Sahələr](#3-geo-scope-nəyi-ölçmür) • [Memarlıq](#4-sistem-memarlığı) • [İcra Rejimləri](#5-icra-rejimləri-execution-modes) • [Təkrar İstehsal](#6-təkrar-istehsal-və-yoxlama) • [Tez Başlama](#7-quraşdırma-və-istifadə)

</div>

---

## 🏆 Mühüm Bençmark: Kommersiya Süni İntellekt Görünməsi — İran və Türkiyə (2026.1)

> [!IMPORTANT]
> ### 🚀 Regional Axtarışda Bu Miqyas və Dəqiqlikdə İLK DƏFƏ Dərc Olunub
> Bu tədqiqat, **İran (`fa-IR`)** və **Türkiyə (`tr-TR`)** rəqəmsal axtarış bazarlarında generativ süni intellekt cavab sistemlərində kommersiya brend görünməsini (Commercial AI Visibility), birbaşa tövsiyə dərəcələrini və internet istinadlarını qiymətləndirən **ilk müstəqil və hərtərəfli empirik bençmarkdır**.
> Bütün 144 müşahidə, **100% canlı internet axtarışı ilə dəstəklənən (Search Grounding)**, **süni verilənlərdən tamamilə uzaq** və **kriptoqrafik olaraq yoxlanıla bilən (SHA-256)** şəkildə qeydə alınmışdır.

<div align="center">

**[Bençmark Verilənlərini İncələyin](benchmarks/regional-commercial-intent-2026.1/)** • **[Tam Nəticələr Hesabatı (Azərbaycan)](benchmarks/regional-commercial-intent-2026.1/results.az.md)** • **[Full Results (English)](benchmarks/regional-commercial-intent-2026.1/results.md)** • **[نتایج کامل (فارسی)](benchmarks/regional-commercial-intent-2026.1/results.fa.md)** • **[Sonuç Raporu (Türkçe)](benchmarks/regional-commercial-intent-2026.1/results.tr.md)** • **[النتائج الكاملة (العربية)](benchmarks/regional-commercial-intent-2026.1/results.ar.md)**

</div>

### Əsas Göstəricilər Xülasəsi

| Göstərici | Ölçülən Qiymət | Empirik Doğrulama Qeydi |
| :--- | :--- | :--- |
| **Canlı Cavablar** | **144 / 144** (100.0%) | 24 neytral alıcı sorğusu $\times$ 3 süni intellekt mühərriki $\times$ 2 təkrar |
| **Obyekt Müşahidələri** | **1.584 müşahidə** | 11 hədəf agentlik kontekst üzrə incələndi |
| **Təsdiqlənmiş İstinadlar** | **2.291 URL** | Sıfır halüsinasiya; 100% real vaxt internet mənbələri |
| **Xəta Dərəcəsi** | **0.0% (0 xəta)** | Bütün mühərriklərdə tam və kəsintisiz icra |
| **Ümumi Xərc** | **$2.16 USD** | 10 dollarlıq pilot büdcə limitindən xeyli aşağı |
| **Qiymətləndirilən Mühərriklər** | **ChatGPT Search, Gemini Grounding, Perplexity Sonar** | Axtarış modelləri: `gpt-4o`, `gemini-2.5-flash`, `sonar-pro` |

### Bazar Sıralamaları və Səs Payı (Share of Voice)

#### 🇹🇷 Türkiyə (`tr-TR`) Kommersiya Bazarı — 72 Tamamlanmış Cavab
| Sıra | Agentlik / Brend | Qeyd Olunma | Qeyd Nisbəti (%) | 95% Vilson İnt. | Tövsiyə | İstinad | 1-ci Yer | Səs Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Zeo Agency** (`zeo`) | 18 | 25.00% | [16.44%, 36.09%] | 1 | 0 | 0 | **47.37%** |
| 🥈 | **Webtures** (`webtures`) | 17 | 23.61% | [15.30%, 34.60%] | 1 | 6 | 1 | **44.74%** |
| 🥉 | **Roas Digital** (`roas`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 0 | 0 | **7.89%** |
| 4 | **SEM Danışmanlık** (`semtr`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 5 | **Stradiji** (`stradiji`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |
| 6 | **B2Press** (`b2press`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

*Obyekt Dəqiqləşdirməsi Qeydi: Stradiji markası 0 kommersiya cavabında qeyd edilmişdir; ümumi türk sözü olan "strateji" ilə yaranan 60 yanlış uyğunluq GEO-Scope-un kontekst filtrləmə sistemi tərəfindən uğurla kənarlaşdırılmışdır.*

#### 🇮🇷 İran (`fa-IR`) Kommersiya Bazarı — 72 Tamamlanmış Cavab
| Sıra | Agentlik / Brend | Qeyd Olunma | Qeyd Nisbəti (%) | 95% Vilson İnt. | Tövsiyə | İstinad | 1-ci Yer | Səs Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Novin** (`novin`) | 12 | 16.67% | [9.80%, 26.91%] | 2 | 0 | 1 | **36.36%** |
| 🥈 | **Web24** (`web24`) | 11 | 15.28% | [8.75%, 25.32%] | 1 | 0 | 1 | **33.33%** |
| 🥉 | **Triboon** (`triboon`) | 7 | 9.72% | [4.79%, 18.74%] | 0 | 7 | 0 | **21.21%** |
| 4 | **Inten** (`inten`) | 3 | 4.17% | [1.43%, 11.55%] | 0 | 1 | 0 | **9.09%** |
| 5 | **Dimarketing** (`dimarketing`) | 0 | 0.00% | [0.00%, 5.07%] | 0 | 0 | 0 | **0.00%** |

### Axtarış Mühərriklərinin İstinad Sıxlığı
- **Perplexity Sonar (`sonar-pro`)**: **1.003 istinad** (**20.90** istinad/sorğu, 7.94 san ortalama müddət)
- **Google Gemini Grounding (`gemini-2.5-flash`)**: **944 istinad** (**19.67** istinad/sorğu, 17.85 san ortalama müddət)
- **ChatGPT Search (`gpt-4o`)**: **344 istinad** (**7.17** istinad/sorğu, 10.42 san ortalama müddət)

### Ən Çox İstinad Edilən Mənbələr
- **Türkiyə**: Agentlik kataloqları və müqayisə platformaları (`agencies.semrush.com` #1 22 istinad, `edvido.com` #2 16 istinad, `pr.net.tr` #3 16 istinad).
- **İran**: İxtisaslaşmış agentlik keysləri və mütəxəssis bloqları (`iranweblife.com` #1 21 istinad, `miladjalayi.com` #2 14 istinad, `triboon.net` #5 12 istinad).

🔗 **[5 Dildə Tam Metodologiya və Bençmark Hesabatını Oxuyun](benchmarks/regional-commercial-intent-2026.1/README.az.md)**

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
