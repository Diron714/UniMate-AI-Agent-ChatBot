# RAG (Retrieval Augmented Generation) System

This document describes the RAG system implementation for UniMate AI service.

## Overview

The RAG system enables the AI to search and retrieve relevant information from UGC documents and official university handbooks, providing accurate, source-cited responses to user queries.

## Architecture

```
User Query
    ↓
UGCSearchTool (app/tools/ugc_search_tool.py)
    ↓
EmbeddingService (app/services/embedding_service.py)
    ↓
VectorStore (app/services/vector_store.py)
    ↓
MongoDB (documents collection)
    ↓
Retrieved Chunks + Sources
    ↓
LLM Context (LangChain)
    ↓
Response with Citations
```

## Components

### 1. Document Processor (`app/services/document_processor.py`)

**Purpose:** Process PDF files and prepare them for embedding

**Features:**
- `read_pdf()`: Extract text from PDF files
- `chunk_text()`: Split text into chunks (500 chars, 50 char overlap)
- `clean_text()`: Remove extra whitespace and special characters
- `extract_metadata()`: Extract source, page number, date
- `process_pdf()`: Complete pipeline for PDF processing

**Usage:**
```python
from app.services.document_processor import DocumentProcessor

processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
chunks = processor.process_pdf("path/to/document.pdf")
```

### 2. Embedding Service (`app/services/embedding_service.py`)

**Purpose:** Generate vector embeddings for text chunks

**Features:**
- Uses `sentence-transformers` with `all-MiniLM-L6-v2` model (384 dimensions)
- `generate_embeddings()`: Convert text to vectors
- `batch_embed()`: Process multiple chunks efficiently
- `encode_query()`: Encode search queries

**Usage:**
```python
from app.services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()
embeddings = embedding_service.batch_embed(texts, batch_size=32)
query_embedding = embedding_service.encode_query("admission requirements")
```

### 3. Vector Store (`app/services/vector_store.py`)

**Purpose:** Store and retrieve document embeddings using MongoDB

**Features:**
- `store_documents()`: Save chunks with embeddings
- `search_similar()`: Find top 5 relevant chunks using cosine similarity
- `update_index()`: Refresh vector index
- `get_collection_stats()`: Get collection statistics

**MongoDB Schema:**
```javascript
{
  text: string,              // Chunk text
  embedding: array[384],     // Vector embedding
  source: string,            // Source document name
  page: number,              // Page number
  metadata: object,          // Additional metadata
  chunk_index: number,       // Chunk position in document
  char_count: number          // Character count
}
```

**Usage:**
```python
from app.services.vector_store import VectorStore

vector_store = VectorStore(collection_name="documents")
stored_count = vector_store.store_documents(chunks, embeddings)
results = vector_store.search_similar(query_embedding, limit=5)
```

### 4. UGC Search Tool (`app/tools/ugc_search_tool.py`)

**Purpose:** LangChain tool for searching UGC documents

**Features:**
- Automatically used by LLM when user asks about university information
- Returns top 5 relevant chunks with sources
- Formats response: "Based on [Source], [Answer]"
- Integrated with chat endpoint

**Usage:**
The tool is automatically available to the LLM. When a user asks:
- "What are the admission requirements for Engineering?"
- "Tell me about UGC policies"
- "What courses are available?"

The LLM will automatically call `ugc_search` tool to retrieve relevant information.

### 5. Ingestion Script (`scripts/ingest_documents.py`)

**Purpose:** Process PDF files and populate the vector database

**Features:**
- Reads PDFs from `docs/` folder
- Processes each PDF into chunks
- Generates embeddings
- Stores in MongoDB
- Logs progress

**Usage:**
```bash
cd apps/ai
python scripts/ingest_documents.py
```

**Environment Variables:**
- `DOCS_DIR`: Custom path to docs directory (optional, defaults to `apps/ai/docs/`)
- `MONGODB_URI`: MongoDB connection string (required)
- `MONGODB_DB_NAME`: Database name (default: "unimate")

## Setup Instructions

### 1. Install Dependencies

All required packages are already in `requirements.txt`:
- `sentence-transformers==2.2.2`
- `pypdf2==3.0.1`
- `pymongo==4.6.0`
- `numpy>=2.0.0`

Install with:
```bash
cd apps/ai
pip install -r requirements.txt
```

### 2. Prepare Documents

Create a `docs/` folder in `apps/ai/` and add PDF files:
```bash
mkdir -p apps/ai/docs
# Copy your PDF files to apps/ai/docs/
```

### 3. Configure MongoDB

Ensure MongoDB is running and configured in `.env`:
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=unimate
```

### 4. Ingest Documents

Run the ingestion script:
```bash
cd apps/ai
python scripts/ingest_documents.py
```

Expected output:
```
============================================================
Document Ingestion Script
============================================================
✅ MongoDB connected
✅ Services initialized
Found 5 PDF files in apps/ai/docs
Processing 5 PDF file(s)...
------------------------------------------------------------
Processing: apps/ai/docs/handbook.pdf
Extracted 45 chunks from apps/ai/docs/handbook.pdf
Generating embeddings for 45 chunks...
✅ Successfully stored 45 chunks from apps/ai/docs/handbook.pdf
------------------------------------------------------------
...
============================================================
Ingestion Summary
============================================================
Total PDFs processed: 5
✅ Successful: 5
❌ Failed: 0
📊 Total documents in vector store: 225
📐 Embedding dimension: 384
============================================================
✅ Document ingestion completed successfully!
```

### 5. Verify Integration

The RAG system is automatically integrated with the chat endpoint. Test it:

```bash
# Start FastAPI server
cd apps/ai
uvicorn main:app --reload --port 8000

# Test with a query
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the admission requirements for Engineering?",
    "context": {},
    "userId": "test123",
    "sessionId": "test001"
  }'
```

The AI will automatically use the `ugc_search` tool to retrieve relevant information and cite sources.

## How It Works

1. **User asks a question** about university information
2. **LLM decides** to use `ugc_search` tool (based on system prompt)
3. **UGCSearchTool** encodes the query into an embedding
4. **VectorStore** searches for similar document chunks using cosine similarity
5. **Top 5 chunks** are retrieved with sources
6. **Chunks are formatted** and added to LLM context
7. **LLM generates response** citing the sources
8. **User receives** accurate, source-cited answer

## MongoDB Vector Search

### Local MongoDB

The current implementation uses **cosine similarity calculation** for local MongoDB. This works well for small to medium document collections (< 10,000 chunks).

### MongoDB Atlas (Production)

For production with MongoDB Atlas, you can use **Atlas Vector Search** for better performance:

1. Create a vector search index in MongoDB Atlas:
```json
{
  "name": "vector_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [{
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }]
  }
}
```

2. Update `vector_store.py` to use `$vectorSearch` aggregation pipeline instead of manual cosine similarity.

## Troubleshooting

### "No relevant documents found"

- Ensure documents have been ingested: `python scripts/ingest_documents.py`
- Check MongoDB connection: Verify `MONGODB_URI` in `.env`
- Check collection: `db.documents.countDocuments({})` should return > 0

### "Embedding service not available"

- Install sentence-transformers: `pip install sentence-transformers`
- Check model download: First run will download the model (~80MB)

### "PDF processing failed"

- Install PyPDF2: `pip install PyPDF2`
- Check PDF file: Ensure it's not corrupted or password-protected

### Slow search performance

- For large collections (> 10,000 chunks), consider:
  - Using MongoDB Atlas Vector Search
  - Increasing `min_score` threshold to reduce results
  - Implementing caching for frequent queries

## Performance Considerations

- **Embedding Model**: `all-MiniLM-L6-v2` is fast (384 dims) but less accurate than larger models
- **Chunk Size**: 500 chars with 50 char overlap balances context and granularity
- **Search Limit**: Top 5 chunks provides good context without overwhelming the LLM
- **Batch Processing**: Embeddings are generated in batches of 32 for efficiency

## Future Enhancements

- [ ] Support for other document formats (DOCX, TXT, HTML)
- [ ] Multi-language embedding models
- [ ] Hybrid search (vector + keyword)
- [ ] Document versioning and updates
- [ ] Automatic re-indexing on document changes
- [ ] Query expansion and refinement
- [ ] Relevance feedback learning

## Files Structure

```
apps/ai/
├── app/
│   ├── services/
│   │   ├── document_processor.py    # PDF processing
│   │   ├── embedding_service.py      # Embedding generation
│   │   └── vector_store.py           # MongoDB vector storage
│   └── tools/
│       └── ugc_search_tool.py        # RAG search tool
├── scripts/
│   └── ingest_documents.py            # Document ingestion script
└── docs/                               # PDF documents folder
    ├── handbook.pdf
    ├── policies.pdf
    └── ...
```

---

**Last Updated:** $(date)  
**Status:** ✅ Fully Implemented and Integrated

