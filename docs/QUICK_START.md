# Quick Start Guide

Get UniMate running in 5 minutes!

## Prerequisites

- Node.js 20+
- Python 3.11+
- MongoDB Atlas account
- Gemini API key

## Setup Steps

### 1. Install Dependencies

```bash
# Frontend
cd apps/web && npm install

# Backend
cd ../api && npm install

# AI Service
cd ../ai
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` files in each app directory:

**apps/api/.env:**
```env
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=generate_random_32_char_string
JWT_REFRESH_SECRET=generate_random_32_char_string
PORT=5000
AI_SERVICE_URL=http://localhost:8000
```

**apps/ai/.env:**
```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_connection_string
```

**apps/web/.env:**
```env
VITE_API_URL=http://localhost:5000
```

### 3. Start Services

Open 3 terminals:

**Terminal 1 - AI Service:**
```bash
cd apps/ai
venv\Scripts\activate  # or source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Backend:**
```bash
cd apps/api
npm run dev
```

**Terminal 3 - Frontend:**
```bash
cd apps/web
npm run dev
```

### 4. Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- AI Service: http://localhost:8000

### 5. Test

1. Open http://localhost:5173
2. Register a new account
3. Login
4. Send a test message

## Troubleshooting

**Port already in use?**
- Change PORT in .env files

**MongoDB connection error?**
- Verify connection string
- Check IP whitelist in Atlas

**Gemini API error?**
- Verify API key
- Check quota limits

**Module not found?**
- Reinstall dependencies
- Check Node/Python versions

## Next Steps

1. Ingest documents (UGC handbooks)
2. Seed Z-score data
3. Test all features
4. Deploy to production

For detailed setup, see [SETUP.md](./SETUP.md)

