# 🤖 AI Destekli Ticaret Zekası Platformu
## Prototip Proje - KOBİ'ler için Akıllı Ticaret Karar Destek Sistemi

### 🎯 Proje Özeti
Bu prototip, KOBİ'lerin uluslararası ticarette karar verme süreçlerini desteklemek için geliştirilmiş **AI destekli ticaret zekası platformu**dur. Platform, elektronik ürün kategorisi odaklı olarak Almanya (DE) ve Hollanda (NL) pazarlarına yönelik optimize edilmiştir.

### ✨ Temel Özellikler
- 🔍 **Akıllı Risk Analizi**: ML tabanlı gümrük riski tahmini
- 📈 **Dinamik Pazar Analizi**: Talep tahmini ve pazar kümeleri
- 🚛 **Lojistik Optimizasyonu**: Profesyonel maliyet ve rota analizi
- 📋 **Entegre Raporlama**: AI destekli yönetici raporları

### 🚀 Hızlı Başlangıç

#### 1) Ortam Kurulumu
```bash
# Python 3.10+ gerekli
pip install -r requirements.txt
```

#### 2) Veri Üretimi (Opsiyonel)
```bash
# Sentetik veri oluştur
python -m app.generate_data
```

#### 3) Uygulamayı Çalıştır
```bash
# Ana uygulama
streamlit run streamlit_app.py
```

### 📊 Modüller

#### 🔍 Modül 1: Akıllı Risk Analizi
- Random Forest ML modeli ile risk sınıflandırması
- Türkçe ürün kategorileri (Elektronik, Telefon, Bilgisayar, vb.)
- Gelişmiş risk faktörleri (mevsimsel, rota, ürün bazlı)
- Gerçek zamanlı risk skorlaması

#### 📈 Modül 2: Dinamik Pazar Analizi
- Prophet/naive forecast ile zaman serisi tahmini
- K-means kümeleme ile pazar segmentasyonu
- COVID etkisi simülasyonu (2020-2021)
- Gerçekçi trend ve mevsimsellik analizi

#### 🚛 Modül 3: Gelişmiş Lojistik Optimizasyonu
- Toplam iniş maliyeti hesaplama (CIF, sigorta, gümrük, KDV)
- Monte Carlo ETA simülasyonu
- Servis düzeyi olasılık hesaplamaları
- Ürün bazlı gümrük vergisi oranları

#### 📋 Modül 4: Akıllı Yönetici Raporu
- Diğer modüllerden veri entegrasyonu
- Çoklu analiz türleri (Risk, Pazar, Maliyet)
- Stratejik öneriler
- Maliyet projeksiyonları

### 🏗️ Proje Yapısı
```
AI Destekli Ticaret Zekası Platformu/
├── streamlit_app.py              # Ana giriş noktası
├── app/
│   ├── modules/                  # Streamlit modülleri
│   │   ├── risk.py              # Risk analizi
│   │   ├── market.py            # Pazar analizi
│   │   ├── logistics.py         # Lojistik optimizasyonu
│   │   └── summary.py           # Yönetici raporu
│   ├── domain.py                # Veri modelleri
│   ├── services.py              # İş mantığı
│   ├── utils.py                 # Yardımcı fonksiyonlar
│   └── generate_data.py         # Veri üretimi
├── data/                        # Veri dosyaları
└── requirements.txt
```

### 📈 Teknik Özellikler
- **ML/AI**: scikit-learn, pandas, numpy
- **Frontend**: Streamlit (Python)
- **Veri**: CSV, JSON
- **Deploy**: Streamlit Cloud
- **Performans**: <2s yanıt süresi

### 🌐 Streamlit Cloud Deploy
1. Repo'yu GitHub'a push edin
2. Streamlit Cloud'da "New app" → repo'yu seçin
3. Entry point: `streamlit_app.py`
4. Python: 3.10+, Gereksinimler: `requirements.txt`

### 📊 Veri Yönetimi
- **Sentetik Veri**: Gerçekçi ticaret verileri
- **Türkçe Ürünler**: 10 farklı elektronik ürün
- **Zaman Serisi**: 36 aylık geçmiş veri
- **Risk Verileri**: 2000+ kayıt ile ML eğitimi

### 🎯 Hedef Kitle
- KOBİ'ler (Küçük ve Orta Büyüklükteki İşletmeler)
- İhracat/ithalat firmaları
- Lojistik şirketleri
- Ticaret danışmanları

### 🔧 Geliştirme
```bash
# Geliştirme ortamı
git clone [repository-url]
cd AI-Destekli-Ticaret-Zekasi-Platformu
pip install -r requirements.txt
streamlit run streamlit_app.py
```

*Bu prototip, AI destekli ticaret zekası alanında önemli bir adımı temsil etmektedir. Platform, KOBİ'lerin uluslararası ticarette karar verme süreçlerini destekleyerek risk yönetimini iyileştirir, pazar fırsatlarını tespit eder ve lojistik maliyetlerini optimize eder.*
