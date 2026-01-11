"""
Document Processor Service
Handles PDF reading, text chunking, cleaning, and metadata extraction
"""
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available. PDF processing will not work.")

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents for RAG system:
    - Reads PDF files
    - Chunks text into manageable pieces
    - Cleans text
    - Extracts metadata
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks in characters (default: 500)
            chunk_overlap: Overlap between chunks in characters (default: 50)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if not PYPDF2_AVAILABLE:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    def read_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with text, metadata, and page information
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            reader = PdfReader(file_path)
            full_text = ""
            pages_data = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                full_text += page_text + "\n"
                pages_data.append({
                    "page": page_num,
                    "text": page_text,
                    "char_count": len(page_text)
                })
            
            # Extract metadata
            metadata = self.extract_metadata(file_path, reader)
            
            return {
                "text": full_text,
                "pages": pages_data,
                "total_pages": len(reader.pages),
                "metadata": metadata,
                "source": os.path.basename(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}", exc_info=True)
            raise
    
    def chunk_text(self, text: str, source: str = "", page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            source: Source document name
            page: Page number (optional)
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Clean text first
        cleaned_text = self.clean_text(text)
        
        chunks = []
        start = 0
        text_length = len(cleaned_text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk
            chunk_text = cleaned_text[start:end]
            
            # Find a good break point (sentence or word boundary)
            if end < text_length:
                # Try to break at sentence end
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size * 0.5:  # Only break if we're past 50% of chunk size
                    chunk_text = chunk_text[:break_point + 1]
                    end = start + break_point + 1
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "source": source,
                    "page": page,
                    "chunk_index": len(chunks),
                    "char_count": len(chunk_text)
                })
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= text_length:
                break
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special control characters but keep newlines for structure
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def extract_metadata(self, file_path: str, pdf_reader: Optional[Any] = None) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            file_path: Path to PDF file
            pdf_reader: PyPDF2 PdfReader object (optional)
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "source": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "processed_date": datetime.now().isoformat(),
            "file_type": "pdf"
        }
        
        # Extract PDF metadata if reader is provided
        if pdf_reader and hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
            pdf_meta = pdf_reader.metadata
            
            if pdf_meta.get('/Title'):
                metadata["title"] = str(pdf_meta.get('/Title'))
            if pdf_meta.get('/Author'):
                metadata["author"] = str(pdf_meta.get('/Author'))
            if pdf_meta.get('/Subject'):
                metadata["subject"] = str(pdf_meta.get('/Subject'))
            if pdf_meta.get('/CreationDate'):
                metadata["creation_date"] = str(pdf_meta.get('/CreationDate'))
        
        return metadata
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Complete PDF processing pipeline:
        1. Read PDF
        2. Extract text
        3. Chunk text
        4. Add metadata
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of processed chunks ready for embedding
        """
        # Read PDF
        pdf_data = self.read_pdf(file_path)
        source = pdf_data["source"]
        metadata = pdf_data["metadata"]
        
        # Process each page separately for better context
        all_chunks = []
        
        for page_data in pdf_data["pages"]:
            page_text = page_data["text"]
            page_num = page_data["page"]
            
            # Chunk the page text
            page_chunks = self.chunk_text(page_text, source=source, page=page_num)
            
            # Add full metadata to each chunk
            for chunk in page_chunks:
                chunk["metadata"] = {
                    **metadata,
                    "page": page_num,
                    "chunk_index": chunk["chunk_index"]
                }
            
            all_chunks.extend(page_chunks)
        
        logger.info(f"Processed {file_path}: {len(all_chunks)} chunks from {pdf_data['total_pages']} pages")
        
        return all_chunks

