# 🤖 AI Knowledge Assistant

RAG (Retrieval-Augmented Generation) tabanlı bilgi asistanı. Dökümanlarınızı yükleyin, sorularınızı sorun.

## Özellikler

- 📄 **Döküman İşleme**: TXT, PDF, MD dosyalarını destekler
- 🔍 **Hibrit Arama**: Vektör araması + BM25 keyword araması (RRF ile birleştirilmiş)
- 💬 **Sohbet Hafızası**: Son 5 konuşmayı hatırlar
- 🌐 **REST API**: FastAPI ile Swagger UI desteği
- 📊 **Değerlendirme**: Otomatik keyword ve kaynak doğruluk testi

## Kurulum

```bash
# Repo'yu klonla
git clone <repo-url>
cd ai_knowledge_asistant

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ollama'yı kur ve modeli indir
brew install ollama
ollama serve  # ayrı terminal
ollama pull llama3
```

## Yapılandırma

`.env.example` dosyasını `.env` olarak kopyalayıp düzenleyin:

```bash
cp .env.example .env
```

## Kullanım

### CLI (Komut Satırı)

```bash
python main.py
```

### API Sunucusu

```bash
python run.py
# veya
uvicorn app.api.routes:app --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoint'leri

| Endpoint | Metot | Açıklama |
|-----------|-------|----------|
| `/ask` | POST | Tek soru sor (hafızasız) |
| `/chat` | POST | Sohbet et (hafızalı) |
| `/upload` | POST | Döküman yükle (.txt, .pdf, .md) |
| `/documents` | GET | Yüklü dökümanları listele |

## Proje Yapısı

```
ai_knowledge_asistant/
├── app/
│   ├── api/
│   │   ├── models.py        # Pydantic request/response modelleri
│   │   └── routes.py        # API endpoint'leri
│   ├── core/
│   │   ├── config.py        # Merkezi ayarlar
│   │   └── rag.py           # RAG motoru (hibrit arama + RRF)
│   └── services/
│       ├── assistant.py     # Konuşma hafızalı asistan
│       ├── evaluation.py    # Otomatik değerlendirme
│       └── ingest.py        # Döküman işleme ve yükleme
├── data/
│   └── docs/                # Dökümanlar
├── tests/
│   └── test_rag.py          # Testler
├── main.py                  # CLI giriş noktası
├── run.py                   # API giriş noktası
├── requirements.txt         # Python bağımlılıkları
└── .env                     # Ortam değişkenleri
```

## Lisans

MIT
