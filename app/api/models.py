from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Soru sorma isteği"""
    question: str
    category: str | None = None
    model: str = "llama3"  # "llama3" veya "gemini"


class AnswerResponse(BaseModel):
    """Soru cevabı yanıtı"""
    answer: str
    sources: list[str] = []
    model: str = "llama3"


class ChatResponse(BaseModel):
    """Sohbet yanıtı"""
    answer: str
    model: str = "llama3"


class UploadResponse(BaseModel):
    """Dosya yükleme yanıtı"""
    message: str


class DocumentListResponse(BaseModel):
    """Döküman listesi yanıtı"""
    documents: list[str]
