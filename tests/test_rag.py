"""
AI Knowledge Assistant — Temel Testler
"""


def test_config_imports():
    """Config dosyası doğru yükleniyor mu?"""
    from app.core.config import (
        DOCS_DIR, DB_DIR, LLM_MODEL,
        EMBEDDING_MODEL, CHUNK_SIZE
    )
    assert DOCS_DIR is not None
    assert DB_DIR is not None
    assert LLM_MODEL == "llama3"
    assert EMBEDDING_MODEL == "all-MiniLM-L6-v2"
    assert CHUNK_SIZE == 500


def test_models():
    """Pydantic modelleri doğru çalışıyor mu?"""
    from app.api.models import QuestionRequest, AnswerResponse

    req = QuestionRequest(question="NLP nedir?")
    assert req.question == "NLP nedir?"
    assert req.category is None

    req_with_cat = QuestionRequest(question="Test?", category="AI")
    assert req_with_cat.category == "AI"

    resp = AnswerResponse(answer="Cevap", sources=["ai.txt"])
    assert resp.answer == "Cevap"
    assert len(resp.sources) == 1


def test_ingest_get_category():
    """Kategori belirleme doğru çalışıyor mu?"""
    from app.services.ingest import get_category

    assert get_category("ai.txt") == "AI"
    assert get_category("ml.txt") == "ML"
    assert get_category("python.txt") == "Python"
    assert get_category("random.txt") == "Other"
    assert get_category("machine_learning.txt") == "ML"


def test_ingest_get_loader():
    """Loader seçimi doğru çalışıyor mu?"""
    from app.services.ingest import get_loader

    assert get_loader("test.txt") is not None
    assert get_loader("test.pdf") is not None
    assert get_loader("test.md") is not None
    assert get_loader("test.xlsx") is None
