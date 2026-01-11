# UniMate Project Structure

Complete directory structure and file organization.

## Root Structure

```
unimate/
├── apps/
│   ├── web/              # React Frontend
│   ├── api/              # Node.js Backend
│   └── ai/               # FastAPI AI Service
├── packages/
│   └── prompts/          # Prompt Templates
├── docs/                 # Documentation
├── .gitignore
└── README.md
```

## Frontend (apps/web)

```
web/
├── src/
│   ├── components/       # UI Components
│   │   ├── Navbar.jsx
│   │   ├── ChatBox.jsx
│   │   └── MessageBubble.jsx
│   ├── pages/            # Page Components
│   │   ├── ChatPage.jsx
│   │   └── LoginPage.jsx
│   ├── store/            # Zustand Stores
│   │   ├── chatStore.js
│   │   └── authStore.js
│   ├── utils/            # Utilities
│   │   └── api.js
│   ├── config/           # Configuration
│   │   └── api.js
│   ├── App.jsx           # Main App Component
│   ├── main.jsx          # Entry Point
│   └── index.css         # Global Styles
├── index.html            # HTML Entry
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Backend API (apps/api)

```
api/
├── src/
│   ├── routes/           # API Routes
│   │   ├── authRoutes.js
│   │   ├── chatRoutes.js
│   │   └── adminRoutes.js
│   ├── controllers/      # Request Handlers
│   │   ├── authController.js
│   │   └── chatController.js
│   ├── models/           # MongoDB Models
│   │   ├── User.js
│   │   └── Conversation.js
│   ├── middleware/       # Express Middleware
│   │   ├── authMiddleware.js
│   │   └── rateLimiter.js
│   ├── config/           # Configuration
│   │   └── db.js
│   └── utils/            # Utilities
│       └── validation.js
├── server.js             # Entry Point
└── package.json
```

## AI Service (apps/ai)

```
ai/
├── app/
│   ├── routes/           # FastAPI Routes
│   │   ├── chat.py
│   │   ├── zscore.py
│   │   └── university.py
│   ├── services/         # Business Logic
│   │   └── gemini_service.py
│   ├── tools/            # AI Agent Tools
│   │   └── base_tool.py
│   ├── models/           # Data Models
│   └── utils/            # Utilities
├── main.py               # Entry Point
└── requirements.txt
```

## Packages

```
packages/
└── prompts/
    └── system_prompt.txt  # System prompts for AI
```

## Documentation

```
docs/
├── SETUP.md              # Setup instructions
└── PROJECT_STRUCTURE.md  # This file
```

## Environment Files (Create Manually)

```
apps/api/.env            # Backend environment variables
apps/ai/.env             # AI service environment variables
apps/web/.env            # Frontend environment variables
```

## Key Files

### Configuration Files
- `package.json` (web, api) - Node.js dependencies
- `requirements.txt` (ai) - Python dependencies
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind CSS configuration

### Entry Points
- `apps/web/src/main.jsx` - React entry
- `apps/api/server.js` - Express server
- `apps/ai/main.py` - FastAPI app

### Core Logic
- Authentication: `apps/api/src/controllers/authController.js`
- Chat: `apps/api/src/controllers/chatController.js`
- AI Service: `apps/ai/app/routes/chat.py`
- Gemini Integration: `apps/ai/app/services/gemini_service.py`

## File Naming Conventions

- **Components**: PascalCase (e.g., `ChatBox.jsx`)
- **Utilities**: camelCase (e.g., `api.js`)
- **Routes**: camelCase with "Routes" suffix (e.g., `authRoutes.js`)
- **Controllers**: camelCase with "Controller" suffix (e.g., `authController.js`)
- **Models**: PascalCase (e.g., `User.js`)
- **Python**: snake_case (e.g., `gemini_service.py`)

## Next Steps

1. Create `.env` files from examples
2. Install dependencies
3. Setup MongoDB
4. Configure API keys
5. Start development servers

