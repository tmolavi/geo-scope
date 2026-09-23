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
[![Research Paper Outline](https://img.shields.io/badge/Research-Paper%20Outline-purple)](docs/RESEARCH_PAPER_OUTLINE.md)
[![Golden Parser](https://img.shields.io/badge/Golden%20Parser-v1%20Verified-blueviolet)](benchmark/golden_sets/v1/)

[Giriş](#1-giriş) • [Ölçülen Boyutlar](#2-geo-scope-neyi-ölçer) • [Kapsam Dışı Alanlar](#3-geo-scope-neyi-ölçmez) • [Mimari](#4-sistem-mimarisi) • [Çalıştırma Modları](#5-çalıştırma-modları-execution-modes) • [Tekrarlanabilirlik](#6-tekrarlanabilirlik-ve-doğrulama) • [Hızlı Başlangıç](#7-kurulum-ve-kullanım)

</div>

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

## 6. Tekrarlanabilirlik ve Doğrulama

`benchmark/releases/` altındaki tüm veri setleri `checksums.sha256` kriptografik özetleriyle korunur:

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
