# 🚁 Drone Filo Optimizasyonu Projesi

Bu proje, enerji limitleri ve uçuşa yasak bölgeler (No-Fly Zones) gibi dinamik kısıtlar altında drone'ların en verimli şekilde teslimat yapmasını sağlayan bir rota optimizasyon sistemidir.

## 🔧 Geliştirme Ortamı

- Python 3.10+
- Kullanılan kütüphaneler:
  - `numpy`
  - `networkx`
  - `matplotlib`
  - `folium`
  - `shapely`

Kurulum:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📦 Proje Yapısı

```
drone-fleet/
│
├── main.py                # Ana çalışma dosyası
├── models.py              # Veri sınıfları: Drone, Delivery, NoFlyZone
├── data_generator.py      # Rastgele veri üretici
├── graph_utils.py         # Graf ve mesafe/maliyet hesaplamaları
├── planner_astar.py       # A* rota planlayıcısı
├── optimizer_ga.py        # Genetik algoritma ile çoklu optimizasyon
├── visualize_map.py       # Harita üzerinde rotaların görselleştirilmesi
├── requirements.txt       # Bağımlılıklar
└── drone_routes.html      # Çıktı haritası (otomatik oluşur)
```

## ✨ Özellikler

- [x] **A\*** algoritması ile en kısa yol bulma  
- [x] **Genetik Algoritma** ile drone başına optimum teslimat dağılımı  
- [x] **No-Fly Zone** kesişim kontrolü ve cezalandırma  
- [x] Batarya kapasitesi ve zaman penceresi kısıtları  
- [x] Gerçek harita üzerinde **interaktif rota görselleştirme** (`folium`)  
- [x] Rastgele drone, teslimat ve NFZ üretimi  
- [x] Harici veri seti ihtiyacı olmadan test edilebilir yapı

## 🗺️ Harita Görselleştirmesi

- `main.py` çalıştırıldığında `drone_routes.html` dosyası oluşur.
- Bu dosya tarayıcıda açıldığında:
  - 📦 Teslimat noktaları
  - 🚁 Drone başlangıç/dönüş noktaları
  - 🟥 No-Fly Zone’lar
  - 📈 Drone rotaları
  görsel olarak izlenebilir.

## 🧪 Test Senaryoları

- **Senaryo 1**: 5 drone, 25 teslimat, 3 NFZ (aktif)
- GA algoritması 150 jenerasyon boyunca toplam maliyeti minimize eder.
- No-Fly Zone ihlalleri `5000` puan ceza ile hesaplanır.

## 📊 Çıktı Örneği

```
✅ GA Sonuç: Toplam skor = 45442.8

🚁 Drone 0 teslimatlar: [2, 7, 21, 17, 18]
   maliyet=3090.7  batarya=1379/8320

🚁 Drone 4 teslimatlar: [13, 16, 10, 20, 6]
   maliyet=19233.8  batarya=1748/11398
```

## 📘 Kullanım

```bash
python main.py
```
