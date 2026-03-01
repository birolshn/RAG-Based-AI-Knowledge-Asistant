from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import logging

from app.core.config import (
    DB_DIR, LLM_MODEL, EMBEDDING_MODEL, GOOGLE_API_KEY,
    SIMILARITY_TOP_K, BM25_TOP_K, LOG_FILE
)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Embedding (her zaman aynı)
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# LLM modelleri (lazy init)
_llm_cache = {}


def get_llm(model="llama3"):
    """Model adına göre LLM döndür (cache'li)"""
    if model not in _llm_cache:
        if model == "gemini":
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY .env dosyasında tanımlı değil!")
            _llm_cache[model] = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GOOGLE_API_KEY,
            )
        else:
            _llm_cache[model] = ChatOllama(model=LLM_MODEL)
    return _llm_cache[model]


def get_db():
    """Her çağrıda taze DB bağlantısı aç"""
    return Chroma(persist_directory=str(DB_DIR), embedding_function=embedding)


def reciprocal_rank_fusion(result_list, k=60):
    """Birden fazla retriever sonucunu birleştir (RRF algoritması)"""
    fused_scores = {}
    for results in result_list:
        for rank, doc in enumerate(results):
            key = doc.page_content
            if key not in fused_scores:
                fused_scores[key] = {"doc": doc, "score": 0}
            fused_scores[key]["score"] += 1 / (rank + k)

    sorted_docs = sorted(
        fused_scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    return [item["doc"] for item in sorted_docs]


def check_relevance(question, context, llm):
    """Getirilen bilgilerin soru ile ilgili olup olmadığını kontrol et"""
    prompt = f"""Aşağıdaki bilgiler soruyu cevaplamak için yeterli mi?

    Bilgiler: {context}
    Soru: {question}

    Sadece 'EVET' veya 'HAYIR' cevabı ver."""
    response = llm.invoke(prompt)
    return "EVET" in response.content.upper()


def ask(question, category=None, model="llama3"):
    """RAG tabanlı soru cevaplama"""
    logging.info(f"SORU: {question} | MODEL: {model}")

    llm = get_llm(model)
    db = get_db()

    filter_dict = None
    if category:
        filter_dict = {"category": category}

    vector_docs = db.similarity_search(question, k=SIMILARITY_TOP_K, filter=filter_dict)

    all_docs = db.get()
    bm25_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(all_docs["documents"], all_docs["metadatas"])
    ]

    # BM25 için en az 1 doküman gerekli
    if bm25_docs:
        bm25 = BM25Retriever.from_documents(bm25_docs)
        bm25.k = BM25_TOP_K
        keyword_docs = bm25.invoke(question)
        docs = reciprocal_rank_fusion([vector_docs, keyword_docs])
    else:
        docs = vector_docs

    if not docs:
        return "Veritabanında henüz döküman yok. Lütfen önce döküman yükleyin.", []

    context = ""
    sources = []

    for doc in docs:
        context += doc.page_content + "\n"
        sources.append(doc.metadata.get("source", "bilinmiyor"))

    # Relevance check (sadece llama3 ile, hız için)
    if model == "llama3":
        if not check_relevance(question, context, llm):
            logging.info("UYARI: Getirilen bilgiler yetersiz bulundu.")

    from langchain_core.messages import SystemMessage, HumanMessage

    unique_sources = list(set(sources))
    source_list = ", ".join(unique_sources)

    system_prompt = """Sen Türkçe konuşan bir bilgi asistanısın. HER ZAMAN TÜRKÇE cevap ver.
Verilen bilgileri kullanarak soruya kapsamlı bir şekilde cevap ver.
Cevabının sonunda kullandığın kaynakları "Kaynaklar: dosya1.txt, dosya2.txt" şeklinde belirt.
Kısa ve net cevaplar ver."""

    human_prompt = f"""Bilgiler (Kaynak dosyalar: {source_list}):
{context}

Soru: {question}

Türkçe Cevap:"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    response = llm.invoke(messages)

    logging.info(f"MODEL: {model} | KAYNAKLAR: {sources}")
    logging.info(f"CEVAP UZUNLUĞU: {len(response.content)} karakter")

    return response.content, sources

