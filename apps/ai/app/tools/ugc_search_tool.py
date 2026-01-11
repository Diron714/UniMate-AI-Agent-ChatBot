"""
UGC Search Tool
RAG search in UGC documents using vector search
"""
from typing import Dict, Any, List, Optional
from app.tools.base_tool import BaseTool
from app.services.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)

class UGCSearchTool(BaseTool):
    """
    Tool for searching UGC documents using vector search (RAG)
    """
    
    def __init__(self):
        super().__init__(
            name="ugc_search",
            description="Search UGC handbooks and official university documents for verified information. Use this when the user asks about admission requirements, courses, policies, or any official university information. Returns relevant document chunks with sources."
        )
        
        # Initialize vector store and embedding service
        self.vector_store = None
        self.embedding_service = None
        
        try:
            self.vector_store = VectorStore(collection_name="documents")
            self.embedding_service = EmbeddingService()
            logger.info("UGC Search Tool: Vector store and embedding service initialized")
        except Exception as e:
            logger.error(f"UGC Search Tool: Failed to initialize services: {e}")
            logger.warning("UGC Search Tool will not be available")
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant UGC documents"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str = "", limit: int = 5) -> Dict[str, Any]:
        """
        Search UGC documents using vector search (RAG)
        
        Args:
            query: Search query
            limit: Maximum number of results (default: 5)
        
        Returns:
            Dict with search results, sources, and formatted answer
        """
        if not query:
            return {
                "success": False,
                "results": [],
                "sources": [],
                "message": "No search query provided"
            }
        
        if not self.vector_store or not self.embedding_service:
            logger.warning("UGC Search Tool: Vector store or embedding service not available")
            return {
                "success": False,
                "results": [],
                "sources": [],
                "message": "Search service is currently unavailable. Please ensure MongoDB is connected and embeddings are initialized."
            }
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_service.encode_query(query)
            
            # Search for similar documents
            similar_docs = self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=limit,
                min_score=0.3  # Minimum similarity threshold
            )
            
            if not similar_docs:
                return {
                    "success": False,
                    "results": [],
                    "sources": [],
                    "message": "No relevant documents found. The information may not be available in UGC documents."
                }
            
            # Format results
            formatted_results = []
            sources = []
            
            for doc in similar_docs:
                formatted_results.append({
                    "text": doc.get("text", ""),
                    "source": doc.get("source", "UGC Handbook"),
                    "page": doc.get("page"),
                    "score": doc.get("score", 0.0),
                    "metadata": doc.get("metadata", {})
                })
                
                # Collect unique sources
                source_name = doc.get("source", "UGC Handbook")
                if source_name not in sources:
                    sources.append(source_name)
            
            # Format response with sources
            # Combine top results into a context string
            context_parts = []
            for i, result in enumerate(formatted_results[:3], 1):  # Top 3 for context
                source = result.get("source", "UGC Handbook")
                page = result.get("page", "")
                page_info = f" (page {page})" if page else ""
                context_parts.append(
                    f"[Source: {source}{page_info}]\n{result.get('text', '')}"
                )
            
            context = "\n\n---\n\n".join(context_parts)
            
            return {
                "success": True,
                "results": formatted_results,
                "sources": sources,
                "context": context,
                "message": f"Found {len(formatted_results)} relevant document chunks",
                "formatted_answer": f"Based on {', '.join(sources)}, here is the relevant information:\n\n{context}"
            }
                
        except Exception as e:
            logger.error(f"UGC Search Tool error: {e}", exc_info=True)
            return {
                "success": False,
                "results": [],
                "sources": [],
                "message": f"Search error: {str(e)}"
            }

