# RAG System Setup Instructions

## Quick Start

### 1. Install Dependencies

All required packages are in `requirements.txt`. Install them:

```bash
cd apps/ai
.\venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac

pip install -r requirements.txt
```

**Required packages:**
- `sentence-transformers==2.2.2` - For embeddings
- `pypdf2==3.0.1` - For PDF processing
- `pymongo==4.6.0` - For MongoDB (already installed)
- `numpy>=2.0.0` - For vector operations (already installed)

### 2. Prepare Documents

Create a `docs/` folder and add your PDF files:

```bash
cd apps/ai
mkdir docs
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

### 5. Test

The RAG system is automatically integrated. Start the FastAPI server and test:

```bash
cd apps/ai
uvicorn main:app --reload --port 8000
```

Then send a query that would trigger the UGC search tool:

```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the admission requirements for Engineering?",
    "context": {},
    "userId": "test123",
    "sessionId": "test001"
  }'
```

## Verification

After installation, verify everything works:

```bash
# Test imports
python -c "from app.services.document_processor import DocumentProcessor; print('✅ DocumentProcessor OK')"
python -c "from app.services.embedding_service import EmbeddingService; print('✅ EmbeddingService OK')"
python -c "from app.services.vector_store import VectorStore; print('✅ VectorStore OK')"
python -c "from app.tools.ugc_search_tool import UGCSearchTool; print('✅ UGCSearchTool OK')"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pymongo'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### "sentence-transformers not available"
**Solution:** `pip install sentence-transformers`

### "PyPDF2 not available"
**Solution:** `pip install PyPDF2`

### "MongoDB connection failed"
**Solution:** 
- Check MongoDB is running: `mongosh` or check service status
- Verify `MONGODB_URI` in `.env` file

### "No PDF files found"
**Solution:** 
- Create `apps/ai/docs/` folder
- Add PDF files to the folder
- Or set custom path: `export DOCS_DIR=/path/to/docs`

---

**Status:** ✅ All code implemented, ready for dependency installation and document ingestion.

