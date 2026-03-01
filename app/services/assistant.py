from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from collections import deque

from app.core.config import DB_DIR, EMBEDDING_MODEL, MEMORY_SIZE
from app.core.rag import get_llm


class RAGAssistant:
    """Konuşma hafızalı RAG asistanı"""

    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.history = deque(maxlen=MEMORY_SIZE)

    def _get_db(self):
        """Her çağrıda taze DB bağlantısı"""
        return Chroma(persist_directory=str(DB_DIR), embedding_function=self.embedding)

    def ask(self, question, model="llama3"):
        """Konuşma geçmişini dikkate alarak soru cevapla"""
        llm = get_llm(model)
        db = self._get_db()

        # Konuşma geçmişini metin olarak oluştur
        history_text = ""
        for entry in self.history:
            history_text += f"Kullanıcı: {entry['input']}\nAsistan: {entry['output']}\n"

        docs = db.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""Konuşma Geçmişi:
        {history_text}

        Bilgiler:
        {context}

        Soru:
        {question}

        Geçmişi ve Bilgileri dikkate alarak Türkçe cevap ver."""

        response = llm.invoke(prompt)

        # Hafızaya kaydet
        self.history.append({
            "input": question,
            "output": response.content
        })

        return response.content
