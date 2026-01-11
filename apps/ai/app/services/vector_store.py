"""
Vector Store Service
MongoDB Vector Search integration for storing and retrieving document embeddings
"""
import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, OperationFailure

from app.config.db import MongoDBConnection

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for RAG system using MongoDB
    Stores document chunks with embeddings and enables vector search
    """
    
    def __init__(self, collection_name: str = "documents"):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of MongoDB collection to store documents
        """
        self.collection_name = collection_name
        self.db = None
        self.collection = None
        self.embedding_dimension = None  # Will be set when first document is stored
        
        # Connect to MongoDB
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and get collection"""
        try:
            self.db = MongoDBConnection.get_db()
            if self.db is None:
                logger.warning("MongoDB not connected. Vector store operations will fail.")
                return
            
            self.collection = self.db[self.collection_name]
            logger.info(f"Vector store connected to collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}", exc_info=True)
            self.db = None
            self.collection = None
    
    def _ensure_index(self, embedding_dimension: int):
        """
        Ensure vector search index exists on the collection
        
        Args:
            embedding_dimension: Dimension of embedding vectors
        """
        if self.db is None:
            logger.warning("Cannot create index: MongoDB not connected")
            return
        
        try:
            # Check if index already exists
            indexes = self.collection.list_indexes()
            index_names = [idx['name'] for idx in indexes]
            
            if 'vector_index' in index_names:
                logger.info("Vector index already exists")
                return
            
            # Create vector search index
            # Note: MongoDB Atlas Vector Search requires specific index configuration
            # For local MongoDB, we'll use a workaround with cosine similarity calculation
            
            # Create a regular index on embedding field for faster queries
            self.collection.create_index([("embedding", 1)])
            logger.info("Created index on embedding field")
            
            # For MongoDB Atlas, you would create a vector search index like this:
            # {
            #   "name": "vector_index",
            #   "type": "vectorSearch",
            #   "definition": {
            #     "fields": [{
            #       "type": "vector",
            #       "path": "embedding",
            #       "numDimensions": embedding_dimension,
            #       "similarity": "cosine"
            #     }]
            #   }
            # }
            
            self.embedding_dimension = embedding_dimension
            
        except Exception as e:
            logger.warning(f"Could not create vector index: {e}")
            logger.info("Will use cosine similarity calculation instead")
    
    def store_documents(self, chunks: List[Dict[str, Any]], embeddings: List[np.ndarray]) -> int:
        """
        Store document chunks with their embeddings in MongoDB
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of numpy arrays (embeddings for each chunk)
            
        Returns:
            Number of documents stored
        """
        if self.collection is None:
            raise RuntimeError("MongoDB not connected. Cannot store documents.")
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        try:
            # Set embedding dimension from first embedding
            if self.embedding_dimension is None and len(embeddings) > 0:
                self.embedding_dimension = len(embeddings[0])
                self._ensure_index(self.embedding_dimension)
            
            # Prepare documents for insertion
            documents = []
            for chunk, embedding in zip(chunks, embeddings):
                # Convert numpy array to list for MongoDB storage
                embedding_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                
                # Validate embedding dimension
                if len(embedding_list) != self.embedding_dimension:
                    logger.warning(
                        f"Embedding dimension mismatch: expected {self.embedding_dimension}, "
                        f"got {len(embedding_list)}. Skipping chunk."
                    )
                    continue
                
                doc = {
                    "text": chunk.get("text", ""),
                    "embedding": embedding_list,
                    "source": chunk.get("source", "unknown"),
                    "page": chunk.get("page"),
                    "metadata": chunk.get("metadata", {}),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "char_count": chunk.get("char_count", 0)
                }
                documents.append(doc)
            
            if not documents:
                logger.warning("No valid documents to store")
                return 0
            
            # Insert documents in batches to avoid timeout
            batch_size = 100  # Insert 100 documents at a time
            stored_count = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                try:
                    result = self.collection.insert_many(batch, ordered=False)  # ordered=False for better performance
                    stored_count += len(result.inserted_ids)
                    logger.debug(f"Stored batch {i//batch_size + 1}: {len(result.inserted_ids)} documents")
                except Exception as e:
                    logger.warning(f"Error inserting batch {i//batch_size + 1}: {e}")
                    # Continue with next batch even if one fails
                    continue
            
            logger.info(f"Stored {stored_count} document chunks in vector store (out of {len(documents)} total)")
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}", exc_info=True)
            raise
    
    def search_similar(self, query_embedding: np.ndarray, limit: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            min_score: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of similar documents with scores
        """
        if self.collection is None:
            raise RuntimeError("MongoDB not connected. Cannot search documents.")
        
        try:
            # Convert query embedding to list
            query_vector = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # For MongoDB Atlas Vector Search, you would use:
            # pipeline = [
            #     {
            #         "$vectorSearch": {
            #             "index": "vector_index",
            #             "path": "embedding",
            #             "queryVector": query_vector,
            #             "numCandidates": limit * 10,
            #             "limit": limit
            #         }
            #     }
            # ]
            # results = list(self.collection.aggregate(pipeline))
            
            # For local MongoDB, calculate cosine similarity manually
            # Get all documents (or a large sample for efficiency)
            # Use batch_size to avoid loading too many at once
            all_docs = list(self.collection.find(
                {}, 
                {"embedding": 1, "text": 1, "source": 1, "page": 1, "metadata": 1}
            ).batch_size(100))
            
            if not all_docs:
                logger.info("No documents in vector store")
                return []
            
            # Calculate cosine similarity for each document
            similarities = []
            query_norm = np.linalg.norm(query_vector)
            
            for doc in all_docs:
                doc_embedding = doc.get("embedding")
                if not doc_embedding or len(doc_embedding) != len(query_vector):
                    continue
                
                # Calculate cosine similarity
                dot_product = np.dot(query_vector, doc_embedding)
                doc_norm = np.linalg.norm(doc_embedding)
                
                if doc_norm == 0:
                    continue
                
                similarity = dot_product / (query_norm * doc_norm)
                
                if similarity >= min_score:
                    similarities.append({
                        "text": doc.get("text", ""),
                        "source": doc.get("source", "unknown"),
                        "page": doc.get("page"),
                        "metadata": doc.get("metadata", {}),
                        "score": float(similarity)
                    })
            
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top results
            results = similarities[:limit]
            
            logger.info(f"Found {len(results)} similar documents (min_score={min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}", exc_info=True)
            return []
    
    def update_index(self):
        """
        Refresh/update the vector search index
        This is useful after bulk document insertions
        """
        if self.collection is None:
            logger.warning("Cannot update index: MongoDB not connected")
            return
        
        try:
            # Rebuild index if needed
            if self.embedding_dimension:
                self._ensure_index(self.embedding_dimension)
            
            logger.info("Vector index updated")
            
        except Exception as e:
            logger.error(f"Error updating index: {e}", exc_info=True)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection
        
        Returns:
            Dictionary with collection statistics
        """
        if self.collection is None:
            return {"error": "MongoDB not connected"}
        
        try:
            count = self.collection.count_documents({})
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_dimension": self.embedding_dimension
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}", exc_info=True)
            return {"error": str(e)}

