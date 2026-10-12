<div align="center">

# ⟠ GEO-Scope

### Ampirik Yapay Zeka Cevap Görünürlüğü Ölçüm Çerçevesi (AI Answer Visibility)

**Üretken yapay zeka sistemlerinde varlıkların (Entity) anılma, tavsiye edilme, kaynak gösterilme ve atıf alma durumlarını ampirik olarak ölçen ve kanıt zincirini koruyan açık kaynaklı çerçeve.**

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)
[![فارسی](https://img.shields.io/badge/فارسی-README.fa.md-green)](README.fa.md)
[![Türkçe](https://img.shields.io/badge/T%C3%BCrk%C3%A7e-README.tr.md-red)](#)
[![Azərbaycan](https://img.shields.io/badge/Az%C9%99rbaycan-README.az.md-orange)](README.az.md)
[![العربية](https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README.ar.md-teal)](README.ar.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Research Paper](https://img.shields.io/badge/Research-Paper-purple)](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[🏆 Dönüm Noktası Karşılaştırma (İran ve Türkiye)](#-dönüm-noktası-karşılaştırma-ticari-yapay-zeka-görünürlüğü--i̇ran-ve-türkiye-20261) • [Giriş](#1-giriş) • [Ölçülen Boyutlar](#2-geo-scope-neyi-ölçer) • [Kapsam Dışı Alanlar](#3-geo-scope-neyi-ölçmez) • [Mimari](#4-sistem-mimarisi) • [Çalıştırma Modları](#5-çalıştırma-modları-execution-modes) • [Tekrarlanabilirlik](#6-tekrarlanabilirlik-ve-doğrulama) • [Hızlı Başlangıç](#7-kurulum-ve-kullanım)

</div>

---

## 🏆 Dönüm Noktası Karşılaştırma: Ticari Yapay Zeka Görünürlüğü — İran ve Türkiye (2026.1)

> [!IMPORTANT]
> ### 🚀 Bölgesel Aramada Bu Ölçek ve Ampirik Derinlikte İLK KEZ Yayımlandı
> Bu çalışma, **İran (`fa-IR`)** ve **Türkiye (`tr-TR`)** dijital arama pazarlarında üretken yapay zeka cevap motorlarında ticari marka görünürlüğünü (Commercial AI Visibility), doğrudan önerilme oranlarını ve web kaynak bağlantılarını değerlendiren **ilk bağımsız ve kapsamlı ampirik karşılaştırmadır**.
> Tüm 144 gözlem, **%100 canlı web aramasıyla güçlendirilmiş (Search Grounding)**, **sentetik veri uydurmasından tamamen arındırılmış** ve **kriptografik olarak doğrulanabilir (SHA-256)** biçimde kaydedilmiştir.

<div align="center">

**[Karşılaştırma Veri Setini İnceleyin](benchmarks/regional-commercial-intent-2026.1/)** • **[Tam Sonuç Raporu (Türkçe)](benchmarks/regional-commercial-intent-2026.1/results.tr.md)** • **[Full Results (English)](benchmarks/regional-commercial-intent-2026.1/results.md)** • **[نتایج کامل (فارسی)](benchmarks/regional-commercial-intent-2026.1/results.fa.md)** • **[Nəticələr (Azərbaycan)](benchmarks/regional-commercial-intent-2026.1/results.az.md)** • **[النتائج الكاملة (العربية)](benchmarks/regional-commercial-intent-2026.1/results.ar.md)**

</div>

### Temel Göstergeler Özeti

| Gösterge | Ölçülen Değer | Ampirik Doğrulama Notu |
| :--- | :--- | :--- |
| **Canlı Yanıtlar** | **144 / 144** (%100,0) | 24 tarafsız alıcı sorgusu $\times$ 3 yapay zeka motoru $\times$ 2 tekrar |
| **Varlık Gözlemleri** | **1.584 gözlem** | 11 hedef ajans bağlam duyarlı incelendi |
| **Doğrulanmış Kaynaklar** | **2.291 URL** | Sıfır halüsinasyon; %100 gerçek zamanlı web bağlantıları |
| **Hata Oranı** | **%0,0 (0 hata)** | Tüm motorlarda kesintisiz ve hatasız tamamlama |
| **Toplam Maliyet** | **$2,16 USD** | 10 dolarlık pilot bütçe sınırının oldukça altında |
| **Değerlendirilen Motorlar** | **ChatGPT Search, Gemini Grounding, Perplexity Sonar** | Arama tabanlı modeller: `gpt-4o`, `gemini-2.5-flash`, `sonar-pro` |

### Pazar Sıralamaları ve Ses Payı (Share of Voice)

#### 🇹🇷 Türkiye (`tr-TR`) Ticari Pazarı — 72 Tamamlanan Yanıt
| Sıra | Ajans / Marka | Anılma | Anılma Oranı (%) | %95 Wilson GA | Tavsiye | Kaynak | 1. Sıra | Ses Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Zeo Agency** (`zeo`) | 18 | %25,00 | [%16,44, %36,09] | 1 | 0 | 0 | **%47,37** |
| 🥈 | **Webtures** (`webtures`) | 17 | %23,61 | [%15,30, %34,60] | 1 | 6 | 1 | **%44,74** |
| 🥉 | **Roas Digital** (`roas`) | 3 | %4,17 | [%1,43, %11,55] | 0 | 0 | 0 | **%7,89** |
| 4 | **SEM Danışmanlık** (`semtr`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |
| 5 | **Stradiji** (`stradiji`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |
| 6 | **B2Press** (`b2press`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |

*Varlık Belirsizliği Giderme Notu: Stradiji markası 0 ticari yanıtta yer almıştır; genel Türkçe "strateji" sözcüğüyle oluşan 60 hatalı eşleşme GEO-Scope'un varlık filtreleme motoru tarafından başarıyla elenmiştir.*

#### 🇮🇷 İran (`fa-IR`) Ticari Pazarı — 72 Tamamlanan Yanıt
| Sıra | Ajans / Marka | Anılma | Anılma Oranı (%) | %95 Wilson GA | Tavsiye | Kaynak | 1. Sıra | Ses Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Novin** (`novin`) | 12 | %16,67 | [%9,80, %26,91] | 2 | 0 | 1 | **%36,36** |
| 🥈 | **Web24** (`web24`) | 11 | %15,28 | [%8,75, %25,32] | 1 | 0 | 1 | **%33,33** |
| 🥉 | **Triboon** (`triboon`) | 7 | %9,72 | [%4,79, %18,74] | 0 | 7 | 0 | **%21,21** |
| 4 | **Inten** (`inten`) | 3 | %4,17 | [%1,43, %11,55] | 0 | 1 | 0 | **%9,09** |
| 5 | **Dimarketing** (`dimarketing`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |

### Arama Motorlarının Kaynak Gösterme Performansı
- **Perplexity Sonar (`sonar-pro`)**: **1.003 kaynak bağlantısı** (**20,90** kaynak/sorgu, 7,94 sn ortalama süre)
- **Google Gemini Grounding (`gemini-2.5-flash`)**: **944 kaynak bağlantısı** (**19,67** kaynak/sorgu, 17,85 sn ortalama süre)
- **ChatGPT Search (`gpt-4o`)**: **344 kaynak bağlantısı** (**7,17** kaynak/sorgu, 10,42 sn ortalama süre)

### En Çok Kaynak Gösterilen Alan Adları
- **Türkiye**: Ajans rehberleri ve dizinler ağırlıklı (`agencies.semrush.com` #1 22 kaynak, `edvido.com` #2 16 kaynak, `pr.net.tr` #3 16 kaynak).
- **İran**: Sektörel vaka analizleri ve uzman blogları ağırlıklı (`iranweblife.com` #1 21 kaynak, `miladjalayi.com` #2 14 kaynak, `triboon.net` #5 12 kaynak).

🔗 **[5 Dilde Tam Metodoloji ve Karşılaştırma Raporunu Okuyun](benchmarks/regional-commercial-intent-2026.1/README.tr.md)**

---

## 1. Giriş

Üretken yapay zeka sistemleri ve web aramasıyla güçlendirilmiş cevap motorları (Search Answer Engines), bilgiye ve ürünlere ulaşmada birincil keşif katmanı haline gelmektedir.

**GEO-Scope**, üretken yapay zeka modellerinin soruları nasıl yanıtladığını kanıta dayalı ve bağımsız olarak doğrulanabilir bir metodolojiyle ölçmek için tasarlanmış açık kaynaklı bir ölçüm çerçevesidir. Spekülatif sıralama algoritmaları iddia etmek yerine, belgelenmiş ve tarafsız istem (prompt) setleri altındaki gözlemlenebilir model çıktılarını kaydeder ve analiz eder.

---

## 2. GEO-Scope Neyi Ölçer?

GEO-Scope, dört bağımsız görünürlük boyutunu birbirinden kesin olarak ayırır:

1. **Varlık Anılması (Mention - `mentioned`)**: Hedef varlık (marka, kişi, teknoloji, kurum) model yanıtında yer aldı mı? (Eş sesli kelime filtreleme ve çok dilli normalizasyon dahil).
2. **Açık Tavsiye (Recommendation - `recommended`)**: Model, varlığı açıkça tavsiye edilen veya öne çıkan bir seçenek olarak sundu mu? (`mentioned != recommended`).
3. **Alan Adı / Bağlantı Kaynak Gösterimi (Citation - `cited`)**: Model yanıtında hedef varlığa ait web sitesi bağlantısı veya kaynak URL yer aldı mı?
4. **Metinsel Atıf (Attribution - `attributed`)**: Bir bilgi, veri veya açıklama metin içinde hedef varlığa atfedildi mi? (URL bağlantısı olmasa dahi).
5. **Sıralama Pozisyonu (Rank - `rank`)**: Yalnızca model yanıtında sıralı bir liste bulunduğunda sayısal sıra olarak çıkarılır (bilgilendirici sorularda `null` atanır).

---

## 3. GEO-Scope Neyi Ölçmez?

Bilimsel sınırları korumak adına:
- ❌ Tescilli model sıralama algoritmaları veya gizli ağırlıklar tersine mühendislikle çözülmeye çalışılmaz.
- ❌ Modellerin gizli eğitim verileri analiz edilmez; yalnızca gözlemlenebilir API çıktıları ölçülür.
- ❌ Nedensel sıralama faktörleri (Causal Ranking Factors) iddiasında bulunulmaz.
- ❌ Simülasyon verileri ile canlı ölçüm verileri asla birbirine karıştırılmaz.

---

## 4. Sistem Mimarisi

```text
Sağlayıcı Katmanı (Provider Layer: Answer Engine / LLM)
        ↓
Ölçüm Motoru (Measurement Engine)
        ↓
Ham Yanıt Depolama (Raw Response Storage: raw_responses.jsonl)
        ↓
Gözlem Ayrıştırıcı (Observation Parser)
        ↓
Metrik Hesaplama (Metrics Calculation)
        ↓
Kanıt Paketleri ve Raporlar (Reports + Replay Bundle)
```

---

## 5. Çalıştırma Modları (Execution Modes)

- **`demo` (Simülasyon)**: Geliştirme, birim testi ve CI doğrulaması için yerel sentetik veri modu. Resmi kıyaslamalara (benchmark) dahil edilmez.
- **`measure` (Canlı Ölçüm)**: Gerçek API'lar üzerinde çalışan ve hata anında sahte veri ikamesi yapmayan (**Zero Silent Fallback**) canlı ölçüm modu.
- **`replay` (Çevrimdışı Tekrar Oynatma)**: Preserved `raw_responses.jsonl` dosyasından ağ çağrısı yapmadan metrikleri deterministik olarak yeniden hesaplayan denetim modu.

---

## 6. Yayımlanan Karşılaştırma Paketleri (Benchmarks) ve Tekrarlanabilirlik

GEO-Scope, hakemli denetime hazır ve `checksums.sha256` ile kriptografik olarak doğrulanmış bağımsız veri setleri yayımlar:

| Karşılaştırma Paketi (Benchmark) | Çalışma Türü | Sorgu / Gözlem Sayısı | Temel Bulgu | Dokümantasyon ve Sonuçlar |
|:---|:---|:---|:---|:---|
| 🏆 [`regional-commercial-intent-2026.1`](benchmarks/regional-commercial-intent-2026.1/) | İran ve Türkiye Bölgesel Ticari Benchmark (İlk Kez Bu Ölçekte) | 24 sorgu / 1.584 gözlem (2.291 kaynak) | Canlı arama motoru ölçümü; Zeo %47,4 ses payı (TR), Novin %36,4 ses payı (IR) | [Tam Sonuçlar (TR)](benchmarks/regional-commercial-intent-2026.1/results.tr.md) · [Results (EN)](benchmarks/regional-commercial-intent-2026.1/results.md) |
| [`global-ai-answers-2026.2`](benchmark/releases/global-ai-answers-2026.2/) | Küresel Çok Modelli Benchmark | 500 sorgu (50 ülke) / 45.698 gözlem | Çok modelli marka anılma ve kaynak dağılımı | [Makale Taslağı](docs/research/global-ai-answers-2026.2/global-ai-answers-paper.md) |
| [`geo-seo-digital-agency-iran-2026.1`](benchmarks/geo-seo-digital-agency-iran-2026.1/) | İran Dijital Ajans Benchmark | 30 ticari sorgu / 120 çıktı | Dijital ajansların AI görünürlük oranları | [Ajans Raporu](benchmarks/geo-seo-digital-agency-iran-2026.1/report.md) |
| [`query-fanout-brand-introduction`](benchmarks/query-fanout-brand-introduction/) | Arama Dağılımı Mekanizma Testi | 50 oturum / 300 marka gözlemi | İç arama sorgularında geçen markalar nihai yanıtta **5,01 kat** daha fazla yer aldı | [Yöntem ve Kanıtlar](benchmarks/query-fanout-brand-introduction/README.md) |

### Veri Seti Bütünlüğünü Doğrulama ve Çevrimdışı Çalıştırma

`benchmark/releases/` ve `benchmarks/` altındaki tüm veri setleri `checksums.sha256` kriptografik özetleriyle korunur:

```bash
# Veri seti bütünlüğünü doğrulama
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2

# Çevrimdışı tekrar oynatma (Replay)
geo-scope replay --bundle benchmark/releases/global-ai-answers-2026.2 --out-dir output/replay_tr
```

---

## 7. Kurulum ve Kullanım

```bash
# Depoyu klonlayın
git clone https://github.com/tmolavi/geo-scope.git
cd geo-scope

# Paketi geliştirme modunda kurun
pip install -e .

# Simülasyon demosunu çalıştırın
geo-scope demo

# Golden Parser testini çalıştırın
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```

---

## Atıf ve Lisans

Geliştirici: **[Taqi Molavi](https://molavi.pro)** — [MIT License](LICENSE) altında lisanslanmıştır.
