from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import os

from app.api.models import (
    QuestionRequest, AnswerResponse, ChatResponse,
    UploadResponse, DocumentListResponse
)
from app.core.config import DOCS_DIR, ALLOWED_EXTENSIONS, BASE_DIR
from app.core.rag import ask
from app.services.assistant import RAGAssistant
from app.services.ingest import ingest

STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="AI Knowledge Assistant",
    description="RAG tabanlı bilgi asistanı API'si",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konuşma hafızalı asistan
assistant = RAGAssistant()


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(req: QuestionRequest):
    """Soru sor ve cevap al"""
    try:
        answer, sources = ask(req.question, req.category, model=req.model)
        return AnswerResponse(answer=answer, sources=sources, model=req.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Soru cevaplanırken hata oluştu: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: QuestionRequest):
    """Konuşma hafızalı sohbet"""
    try:
        answer = assistant.ask(req.question, model=req.model)
        return ChatResponse(answer=answer, model=req.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sohbet sırasında hata oluştu: {str(e)}")


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Yeni döküman yükle"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya türü: {ext}. Desteklenen: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        path = DOCS_DIR / file.filename
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        ingest()
        return UploadResponse(message=f"{file.filename} başarıyla yüklendi.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya yüklenirken hata oluştu: {str(e)}")


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """Yüklü dökümanları listele"""
    try:
        docs = os.listdir(DOCS_DIR)
        docs = [d for d in docs if not d.startswith(".")]
        return DocumentListResponse(documents=docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dökümanlar listelenirken hata oluştu: {str(e)}")


# ============ FRONTEND ============
@app.get("/")
async def serve_frontend():
    """Ana sayfayı serve et"""
    return FileResponse(str(STATIC_DIR / "index.html"))


# Static dosyaları serve et (CSS, JS) — en sonda olmalı
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

