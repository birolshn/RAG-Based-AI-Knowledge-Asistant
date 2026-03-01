# 🤖 AI Knowledge Assistant

This project implements a sophisticated Retrieval-Augmented Generation pipeline that bridges the gap between static document storage and interactive AI. By leveraging Hybrid Search—combining the semantic depth of Vector Search with the keyword precision of BM25—and merging results through Reciprocal Rank Fusion (RRF), the assistant ensures high-accuracy retrieval. Built with FastAPI for high-performance serving and Ollama for local inference, it offers a secure, private, and scalable solution for document interrogation without relying on external cloud APIs.

## Features

- 📄 **Document Processing**: Supports TXT, PDF, MD files
- 🔍 **Hybrid Search**: Vector search + BM25 keyword search (combined with RRF)
- 💬 **Chat Memory**: Remembers the last 5 conversations
- 🌐 **REST API**: Swagger UI support with FastAPI
- 📊 **Evaluation**: Automatic keyword and source accuracy testing

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd ai_knowledge_asistant

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama and pull the model
brew install ollama
ollama serve  # in a separate terminal
ollama pull llama3```

## Configuration

```bash
cp .env.example .env
```

## Usage

### CLI (Commend Line)

```bash
python main.py
```

### API 

```bash
python run.py
# veya
uvicorn app.api.routes:app --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

| Endpoint | Method | Explenation |
|-----------|-------|----------|
| `/ask` | POST | Single Question |
| `/chat` | POST | Chat |
| `/upload` | POST | Upload File (.txt, .pdf, .md) |
| `/documents` | GET | List Uploaded File |

## Project Structure

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

