# GEO-Scope Bölgesel Ticari Yapay Zeka Görünürlük Karşılaştırması (2026.1)
### İran (`fa-IR`) ve Türkiye (`tr-TR`) Ticari Arama Pazarları

**Tanımlayıcı:** `regional-commercial-intent-2026.1`  
**Uygulama Durumu:** `COMPLETE` (144 / 144 Ampirik Gözlem Tamamlandı, 0 Hata, 2.291 Kaynak Gösterimi)  
**Çalıştırma Modu:** `empirical` (%100 Canlı Arama Destekli Motorlar, Sıfır Sentetik Veri)  
**Metodolojik İlham:** [Peak Ace AI Visibility LLM Benchmark 2026](https://peakace.agency/en/latest/ai-visibility-llm-benchmark-2026/)  

---

<div align="center">

### 🌐 Karşılaştırma Dokümantasyonunu 5 Dilde Okuyun
[**English**](README.md) • [**فارسی**](README.fa.md) • [**Türkçe**](README.tr.md) • [**Azərbaycan**](README.az.md) • [**العربية**](README.ar.md)

### 📊 Detaylı Sonuç ve Rapor Dosyaları
[**Results (EN)**](results.md) • [**نتایج کامل (FA)**](results.fa.md) • [**Tam Sonuçlar (TR)**](results.tr.md) • [**Tam Nəticələr (AZ)**](results.az.md) • [**النتائج الكاملة (AR)**](results.ar.md)

[⬅ GEO-Scope Ana Sayfasına Dön](../../README.tr.md)

</div>

---

> [!IMPORTANT]
> ### 🏆 Bölgesel Aramada Bu Ölçek ve Derinlikte İLK KEZ Yayımlandı
> Bu çalışma, **İran** ve **Türkiye** dijital arama ekosistemlerinde üretken yapay zeka modellerinin ticari marka görünürlüğünü (AI Visibility), doğrudan tavsiye oranlarını ve web kaynak bağlantılarını değerlendiren **ilk bağımsız ve kapsamlı ampirik karşılaştırmadır**.
> Tüm 144 gözlem, **%100 canlı web aramasıyla güçlendirilmiş (Search Grounding)**, **sentetik veri uydurmasından tamamen arındırılmış** ve **kriptografik olarak doğrulanabilir (SHA-256)** biçimde kaydedilmiştir.

---

## 1. Yönetici Özeti ve Temel Göstergeler

| Parametre | Ölçülen Değer | Doğrulama Notu |
| :--- | :--- | :--- |
| **Canlı Yanıt Sayısı** | **144 / 144** (%100,0) | 24 tarafsız alıcı sorgusu $\times$ 3 yapay zeka motoru $\times$ 2 tekrar |
| **Varlık Düzeyinde Gözlem** | **1.584 gözlem** | 11 hedef dijital ajans tüm yanıtlarda bağımsız incelendi |
| **Gerçek Kaynak Gösterimi (Citation)** | **2.291 doğrulanmış URL** | Sıfır sahte/ölü bağlantı; %100 gerçek zamanlı web kaynakları |
| **Sağlayıcı Hata Oranı** | **%0,0 (0 hata)** | Tüm arama motorlarında kesintisiz ve tam tamamlama |
| **Manuel Denetim (QA) Doğruluğu** | **%100,0** | 20 rastgele katmanlı örnekte (10 IR, 10 TR) tam eşleşme |
| **Toplam Çalıştırma Maliyeti** | **$2,16 USD** | Belirlenen 10 dolarlık pilot bütçe sınırının oldukça altında |
| **Kriptografik Bütünlük** | **SHA-256 Onaylı** | Tüm kanıt dosyaları [`checksums.sha256`](checksums.sha256) dosyasında kayıtlı |

---

## 2. Pazar Bazlı Marka Görünürlüğü ve Ses Payı (Share of Voice)

### 2.1 Türkiye (`tr-TR`) Ticari Arama Pazarı
72 tamamlanan yanıtta ($12 \text{ sorgu} \times 3 \text{ motor} \times 2 \text{ tekrar}$) 6 önde gelen Türk dijital ajansının değerlendirmesi:

| Sıra | Ajans / Marka | Anılma | Anılma Oranı (%) | %95 Wilson GA | Doğrudan Tavsiye | Kaynak Gösterimi | 1. Sıra | Ses Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Zeo Agency** (`zeo`) | 18 | %25,00 | [%16,44, %36,09] | 1 | 0 | 0 | **%47,37** |
| 🥈 | **Webtures** (`webtures`) | 17 | %23,61 | [%15,30, %34,60] | 1 | 6 | 1 | **%44,74** |
| 🥉 | **Roas Digital** (`roas`) | 3 | %4,17 | [%1,43, %11,55] | 0 | 0 | 0 | **%7,89** |
| 4 | **SEM Danışmanlık** (`semtr`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |
| 5 | **Stradiji** (`stradiji`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |
| 6 | **B2Press** (`b2press`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |

*Varlık Belirsizliğini Giderme (Entity Disambiguation) Notu: Stradiji ticari marka bağlamında sıfır yanıtta anılmıştır. Genel Türkçe "strateji" sözcüğüyle oluşan 60 hatalı eşleşme (false-positive), GEO-Scope'un bağlam duyarlı filtreleme algoritması tarafından başarıyla elenmiştir.*

---

### 2.2 İran (`fa-IR`) Ticari Arama Pazarı
72 tamamlanan yanıtta ($12 \text{ sorgu} \times 3 \text{ motor} \times 2 \text{ tekrar}$) 5 önde gelen İran ajansının değerlendirmesi:

| Sıra | Ajans / Marka | Anılma | Anılma Oranı (%) | %95 Wilson GA | Doğrudan Tavsiye | Kaynak Gösterimi | 1. Sıra | Ses Payı (SOV) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Novin** (`novin`) | 12 | %16,67 | [%9,80, %26,91] | 2 | 0 | 1 | **%36,36** |
| 🥈 | **Web24** (`web24`) | 11 | %15,28 | [%8,75, %25,32] | 1 | 0 | 1 | **%33,33** |
| 🥉 | **Triboon** (`triboon`) | 7 | %9,72 | [%4,79, %18,74] | 0 | 7 | 0 | **%21,21** |
| 4 | **Inten** (`inten`) | 3 | %4,17 | [%1,43, %11,55] | 0 | 1 | 0 | **%9,09** |
| 5 | **Dimarketing** (`dimarketing`) | 0 | %0,00 | [%0,00, %5,07] | 0 | 0 | 0 | **%0,00** |

---

## 3. Yapay Zeka Motorlarının Kaynak Gösterme Performansı

| Yapay Zeka Motoru | Temel Model | Yanıtlar | Toplam Kaynak | Sorgu Başına Kaynak | Ort. Yanıt Süresi | Hata Oranı |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Perplexity Sonar** | `sonar-pro` | 48 | **1.003** | **20,90** | 7,94 sn | %0,0 |
| **Google Gemini Grounding** | `gemini-2.5-flash` | 48 | **944** | **19,67** | 17,85 sn | %0,0 |
| **ChatGPT Search** | `gpt-4o` (Web Araması) | 48 | **344** | **7,17** | 10,42 sn | %0,0 |

- **Kaynak Yoğunluğu**: Perplexity ve Gemini, ChatGPT Search'e kıyasla soru başına yaklaşık 3 kat daha fazla kaynak web bağlantısı sunmaktadır.
- **Hız ve Derinlik**: Perplexity Sonar 7,94 saniye ile en hızlı yanıtı üretirken, Gemini çok aşamalı arama adımları nedeniyle daha yüksek gecikme süresine sahiptir.

---

## 4. En Çok Kaynak Gösterilen Alan Adları

Yapay zeka modelleri ajansların kendi ana sayfalarına nadiren bağlantı vermektedir. Bunun yerine bağımsız dizinler, sektörel bloglar ve dijital PR platformları yoğun şekilde kaynak gösterilmektedir:

| Sıra | Türkiye (`tr-TR`) En Çok Kaynak | Sayı | Kategori | İran (`fa-IR`) En Çok Kaynak | Sayı | Kategori |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| 1 | `agencies.semrush.com` | 22 | Ajans Rehberi | `iranweblife.com` | 21 | Ajans ve SEO Blogu |
| 2 | `edvido.com` | 16 | Ajans Eşleştirme Portalı | `miladjalayi.com` | 14 | Teknik SEO Uzman Blogu |
| 3 | `pr.net.tr` | 16 | Dijital PR Dağıtımı | `frac.tl` | 14 | Dijital PR Endüstri Kaynağı |
| 4 | `prix-studio.com` | 14 | Pazarlama İncelemeleri | `demandsage.com` | 12 | Teknoloji ve Analiz Portalı |
| 5 | `ranktracker.com` | 13 | Global SEO Araç Rehberi | `triboon.net` | 12 | Dijital PR ve Medya |
| 6 | `onuruzunonline.com` | 12 | Bağımsız SEO Uzmanı | `virgool.io` | 11 | Kullanıcı İçerik Platformu |
| 7 | `habergazetesi.com.tr` | 12 | Ulusal Haber Portalı | `setare.com` | 11 | İnceleme ve Genel Medya |

---

## 5. Kullanıcı Niyeti (Intent) Kırılımı

24 sorgu, 4 temel ticari niyet grubuna eşit olarak dağıtılmıştır:

| Ticari Niyet Grubu | Toplam Kaynak | Kaynak / Sorgu | Marka Anılması | Açık Tavsiye | Stratejik Çıkarım |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **En İyi / Tavsiye** | 622 | **17,28** | **31** | **5** | Markaların anılmasını ve doğrudan önerilmesini tetikleyen ana kategori. |
| **Karşılaştırma** | 584 | **16,22** | **22** | **0** | Çoklu ajans listeleri oluşturulur ancak tek bir kazanan seçilmez. |
| **Fiyat / Ajans Seçimi** | 542 | **15,06** | **14** | **0** | Modeller fiyat kriter rehberlerine ve ajans rehberlerine yönelir. |
| **Kriter / Rehber** | 543 | **15,08** | **6** | **0** | Ajans adlarından ziyade teknik standartlar ve metodolojiler sunulur. |

---

## 6. Dosya Yapısı ve Kanıt Arşivi

```
benchmarks/regional-commercial-intent-2026.1/
├── README.md               # İngilizce Dokümantasyon
├── README.fa.md            # Farsça Dokümantasyon
├── README.tr.md            # Türkçe Dokümantasyon (Bu dosya)
├── README.az.md            # Azerbaycan Türkçesi Dokümantasyon
├── README.ar.md            # Arapça Dokümantasyon
├── results.md              # Kapsamlı Ampirik Sonuç Raporu (İngilizce)
├── results.fa.md           # Farsça Sonuç Raporu
├── results.tr.md           # Kapsamlı Ampirik Sonuç Raporu (Türkçe)
├── results.az.md           # Azerbaycanca Sonuç Raporu
├── results.ar.md           # Arapça Sonuç Raporu
├── manifest.json           # v0.3 şemasına uygun metaveri (COMPLETE)
├── run-config.json         # Yürütme parametreleri ve maliyet ($2,16 USD)
├── prompts.jsonl           # 24 tarafsız marka bağımsız soru
├── entities.json           # Hedef ajans profilleri (5 IR, 6 TR)
├── metrics.json            # %95 Wilson aralıklı hesaplanmış metrikler
├── raw_responses.jsonl     # 144 değiştirilmemiş canlı model yanıtı
├── observations.jsonl      # 1.584 puanlanmış varlık gözlemi
├── errors.jsonl            # Hata kayıtları (0 hata)
├── methodology.md          # Bilimsel metodoloji ve Peak Ace kıyaslaması
├── limitations.md          # Sınırlar ve epistemik kapsam
└── checksums.sha256        # Kriptografik SHA-256 doğrulama imzaları
```

---

## 7. Çevrimdışı Tekrarlanabilirlik

Metrikleri API maliyeti olmadan çevrimdışı yeniden doğrulamak için:

```bash
# Kanıt dosyalarının bütünlüğünü test edin
sha256sum -c benchmarks/regional-commercial-intent-2026.1/checksums.sha256

# Ham yanıtlardan metrikleri yeniden hesaplayın
geo-scope replay \
  --archive benchmarks/regional-commercial-intent-2026.1/raw_responses.jsonl \
  --entities benchmarks/regional-commercial-intent-2026.1/entities.json \
  --out-dir /tmp/replay-verification
```

---

## 8. Akademik ve Sektörel Atıf

```bibtex
@misc{geoscope_regional_benchmark_2026,
  author = {Molavi, Taqi and GEO-Scope Contributors},
  title = {GEO-Scope Regional Commercial AI Visibility Benchmark 2026.1: An Empirical Evaluation of AI Answer Engines in Iran and Türkiye},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/tmolavi/geo-scope/tree/main/benchmarks/regional-commercial-intent-2026.1}}
}
```
