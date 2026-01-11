"""
Document Ingestion Script
Processes PDF files from docs/ folder and stores them in the vector database
"""
import os
import sys
import logging
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.config.db import MongoDBConnection
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def find_pdf_files(docs_dir: str) -> List[str]:
    """
    Find all PDF files in the docs directory
    
    Args:
        docs_dir: Path to docs directory
        
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        logger.warning(f"Docs directory not found: {docs_dir}")
        return pdf_files
    
    # Find all PDF files recursively
    for pdf_file in docs_path.rglob("*.pdf"):
        pdf_files.append(str(pdf_file))
    
    logger.info(f"Found {len(pdf_files)} PDF files in {docs_dir}")
    return pdf_files


def ingest_document(file_path: str, processor: DocumentProcessor, 
                    embedding_service: EmbeddingService, 
                    vector_store: VectorStore) -> bool:
    """
    Process and ingest a single PDF document
    
    Args:
        file_path: Path to PDF file
        processor: Document processor instance
        embedding_service: Embedding service instance
        vector_store: Vector store instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing: {file_path}")
        
        # Process PDF into chunks
        chunks = processor.process_pdf(file_path)
        
        if not chunks:
            logger.warning(f"No chunks extracted from {file_path}")
            return False
        
        logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
        
        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = embedding_service.batch_embed(texts, batch_size=32)
        
        if len(embeddings) != len(chunks):
            logger.error(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
            return False
        
        # Store in vector database
        stored_count = vector_store.store_documents(chunks, embeddings)
        
        if stored_count > 0:
            logger.info(f"✅ Successfully stored {stored_count} chunks from {file_path}")
            return True
        else:
            logger.warning(f"No chunks stored from {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error ingesting {file_path}: {e}", exc_info=True)
        return False


def main():
    """Main ingestion function"""
    logger.info("=" * 60)
    logger.info("Document Ingestion Script")
    logger.info("=" * 60)
    
    # Check MongoDB connection
    db = MongoDBConnection.connect()
    if db is None:
        logger.error("❌ MongoDB connection failed. Please check MONGODB_URI in .env")
        sys.exit(1)
    
    logger.info("✅ MongoDB connected")
    
    # Initialize services
    try:
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedding_service = EmbeddingService()
        vector_store = VectorStore(collection_name="documents")
        logger.info("✅ Services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        sys.exit(1)
    
    # Find docs directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"
    
    # Allow custom docs directory via environment variable
    custom_docs_dir = os.getenv("DOCS_DIR")
    if custom_docs_dir:
        docs_dir = Path(custom_docs_dir)
    
    if not docs_dir.exists():
        logger.warning(f"Docs directory not found: {docs_dir}")
        logger.info("Creating docs directory...")
        docs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Please add PDF files to: {docs_dir}")
        sys.exit(0)
    
    # Find all PDF files
    pdf_files = find_pdf_files(str(docs_dir))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {docs_dir}")
        logger.info(f"Please add PDF files to: {docs_dir}")
        sys.exit(0)
    
    # Process each PDF
    logger.info(f"\nProcessing {len(pdf_files)} PDF file(s)...")
    logger.info("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for pdf_file in pdf_files:
        if ingest_document(pdf_file, processor, embedding_service, vector_store):
            success_count += 1
        else:
            fail_count += 1
        logger.info("-" * 60)
    
    # Update index
    logger.info("Updating vector index...")
    vector_store.update_index()
    
    # Get collection stats
    stats = vector_store.get_collection_stats()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Ingestion Summary")
    logger.info("=" * 60)
    logger.info(f"Total PDFs processed: {len(pdf_files)}")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")
    logger.info(f"📊 Total documents in vector store: {stats.get('document_count', 0)}")
    logger.info(f"📐 Embedding dimension: {stats.get('embedding_dimension', 'N/A')}")
    logger.info("=" * 60)
    
    if success_count > 0:
        logger.info("✅ Document ingestion completed successfully!")
    else:
        logger.warning("⚠️ No documents were successfully ingested")


if __name__ == "__main__":
    main()

