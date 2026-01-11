# UniMate AI Agent

**National AI-Powered University Companion for Sri Lanka**

UniMate is a premium, production-ready AI agent system designed to support Sri Lankan students throughout their university journey—from A/L results to graduation. It combines verified knowledge, advanced reasoning, and ethical governance to provide accurate, contextual, and equitable university guidance.

## 🎯 Project Overview

UniMate is not just a chatbot—it's a multi-agent, reasoning-driven, policy-aware AI platform that:

- Provides verified answers from UGC handbooks and university documents
- Predicts course eligibility based on Z-scores
- Offers university-specific guidance (hostels, attendance, exams)
- Remembers user context and personalizes responses
- Ensures safety and ethical AI usage

## 🏗️ Architecture

```
unimate/
├── apps/
│   ├── web/              # React + Vite + Tailwind frontend
│   ├── api/              # Node.js + Express backend (API Gateway)
│   └── ai/               # FastAPI + LangChain AI agent
├── packages/
│   └── prompts/          # Centralized prompt templates
└── docs/                 # Documentation
```

### Tech Stack

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- Zustand (state management)
- React Query (data fetching)
- React Router (routing)

**Backend (API Gateway):**
- Node.js + Express
- MongoDB (Mongoose)
- JWT Authentication
- Rate Limiting
- CORS

**AI Service:**
- FastAPI
- LangChain
- Google Gemini 2.5 Flash
- MongoDB Vector Search (RAG)
- Sentence Transformers

## 🚀 Quick Start

### Prerequisites

- Node.js 20+ 
- Python 3.11+
- MongoDB Atlas account (or local MongoDB)
- Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd unimate
   ```

2. **Setup Frontend**
   ```bash
   cd apps/web
   npm install
   ```

3. **Setup Backend**
   ```bash
   cd apps/api
   npm install
   ```

4. **Setup AI Service**
   ```bash
   cd apps/ai
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Environment Variables

**apps/api/.env:**
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/unimate
JWT_SECRET=your_super_secret_jwt_key_min_32_chars
JWT_REFRESH_SECRET=your_refresh_secret_key_min_32_chars
NODE_ENV=development
PORT=5000
AI_SERVICE_URL=http://localhost:8000
```

**apps/ai/.env:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=same_as_above
REDIS_URL=redis://localhost:6379  # Optional
ENVIRONMENT=development
```

**apps/web/.env:**
```env
VITE_API_URL=http://localhost:5000
```

### Running the Application

1. **Start AI Service** (Terminal 1)
   ```bash
   cd apps/ai
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn main:app --reload --port 8000
   ```

2. **Start Backend API** (Terminal 2)
   ```bash
   cd apps/api
   npm run dev
   ```

3. **Start Frontend** (Terminal 3)
   ```bash
   cd apps/web
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - AI Service: http://localhost:8000

## 📁 Project Structure

### Frontend (apps/web)
```
src/
├── components/      # Reusable UI components
├── pages/          # Page components
├── store/          # Zustand state management
├── utils/          # Utility functions
└── config/         # Configuration files
```

### Backend (apps/api)
```
src/
├── routes/         # API routes
├── controllers/   # Request handlers
├── models/         # MongoDB models
├── middleware/    # Auth, rate limiting, etc.
├── config/         # Database, etc.
└── utils/          # Validation, helpers
```

### AI Service (apps/ai)
```
app/
├── routes/         # FastAPI endpoints
├── tools/          # AI agent tools
├── services/       # Gemini, RAG, etc.
├── models/         # Data models
└── utils/          # Helper functions
```

## 🔑 Key Features

### 1. Conversational AI Interface
- Natural language interaction
- Multi-language support (Sinhala, Tamil, English)
- Context-aware responses

### 2. Z-Score Course Prediction
- Analyzes historical cut-off data
- Categorizes courses: Safe, Probable, Reach
- Provides explanations

### 3. RAG (Retrieval Augmented Generation)
- Answers grounded in verified documents
- Source citations
- No hallucinations

### 4. University Context Switching
- Remembers user's university
- Provides university-specific answers
- Personalizes responses

### 5. Admin Panel
- Document upload
- Cut-off management
- Conversation logs
- System settings

### 6. Safety & Guardrails
- Prompt injection detection
- Sensitive topic filtering
- Human escalation paths
- Audit logging

## 🧪 Testing

### API Testing
```bash
# Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Send chat message (with JWT token)
curl -X POST http://localhost:5000/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message":"Hello UniMate","context":{}}'
```

## 📚 Documentation

- [API Documentation](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Contributing](./docs/CONTRIBUTING.md)

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting
- Input validation
- CORS configuration
- Environment variable security

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd apps/web
npm run build
vercel deploy
```

### Backend (Render)
- Connect GitHub repository
- Set build command: `cd apps/api && npm install`
- Set start command: `cd apps/api && node server.js`

### AI Service (Railway)
- Connect GitHub repository
- Set start command: `cd apps/ai && uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- UGC (University Grants Commission) of Sri Lanka
- All participating universities
- Open source community

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for Sri Lankan students**

