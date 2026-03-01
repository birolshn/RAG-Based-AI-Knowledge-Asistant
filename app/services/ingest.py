import os
import shutil
import threading
import time

# Eşzamanlı ingest çağrılarını engelle
_ingest_lock = threading.Lock()
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import (
    DOCS_DIR, DB_DIR, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP
)


def get_loader(path):
    """Dosya uzantısına göre uygun loader döndür"""
    if path.endswith(".txt"):
        return TextLoader(path, encoding="utf-8")
    elif path.endswith(".pdf"):
        return PyPDFLoader(path)
    elif path.endswith(".md"):
        return UnstructuredMarkdownLoader(path)
    else:
        return None


def get_category(filename):
    """Dosya adına göre kategori belirle"""
    name = filename.lower()
    if "ai" in name:
        return "AI"
    elif "ml" in name or "machine" in name:
        return "ML"
    elif "python" in name:
        return "Python"
    else:
        return "Other"


def ingest():
    """Tüm dökümanları işle ve vektör veritabanına yükle"""
    # Eşzamanlı çağrıları engelle (dosya yükleme sırasında çakışma önlenir)
    if not _ingest_lock.acquire(timeout=1):
        print("⏳ Başka bir ingest işlemi devam ediyor, bekleniyor...")
        _ingest_lock.acquire()

    try:
        all_docs = []

        for file in os.listdir(DOCS_DIR):
            path = os.path.join(DOCS_DIR, file)

            if file.startswith("."):
                continue

            try:
                loader = get_loader(path)
                if loader is None:
                    print(f"⚠️  {file} desteklenmiyor, atlanıyor.")
                    continue

                documents = loader.load()

                category = get_category(file)
                for doc in documents:
                    doc.metadata["source"] = file
                    doc.metadata["category"] = category

                all_docs.extend(documents)
                print(f"✅ {file} yüklendi. (Kategori: {category})")
            except Exception as e:
                print(f"❌ {file} yüklenemedi. Hata: {e}")

        if not all_docs:
            print("Yüklenecek döküman bulunamadı.")
            return

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " "]
        )

        chunks = splitter.split_documents(all_docs)
        print(f"📄 Toplam chunk sayısı: {len(chunks)}")

        db_path = str(DB_DIR)
        os.makedirs(db_path, exist_ok=True)

        embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # Mevcut koleksiyonu ChromaDB API ile sil (dosya sistemi dokunulmaz)
        try:
            existing_db = Chroma(persist_directory=db_path, embedding_function=embedding)
            existing_db.delete_collection()
            print("🗑️  Eski koleksiyon silindi.")
        except Exception:
            pass  # İlk çalıştırmada koleksiyon yoktur

        try:
            Chroma.from_documents(
                chunks,
                embedding,
                persist_directory=db_path
            )
            print("✅ Tüm dökümanlar başarıyla işlendi.")
        except Exception as e:
            print(f"❌ Veritabanı oluşturma hatası: {e}")
            raise
    finally:
        _ingest_lock.release()

