# Services package
from app.services.memory_service import MemoryService
from app.services.context_service import ContextService

__all__ = ["MemoryService", "ContextService"]
# Import RAG services (always available)
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

# Import AI services (may require API keys)
try:
    from app.services.gemini_service import get_gemini_model, generate_response
    from app.services.langchain_service import LangChainService
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False
    get_gemini_model = None
    generate_response = None
    LangChainService = None

__all__ = [
    "DocumentProcessor",
    "EmbeddingService",
    "VectorStore",
    "MemoryService",
    "ContextService",
    "get_gemini_model",
    "generate_response",
    "LangChainService",
    "GEMINI_AVAILABLE",
]
