# Setup Guide

This guide will walk you through setting up UniMate from scratch.

## Prerequisites Checklist

- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed
- [ ] MongoDB Atlas account (or local MongoDB)
- [ ] Gemini API key from Google
- [ ] Git installed

## Step-by-Step Setup

### 1. Environment Setup

#### Install Node.js
- Download from https://nodejs.org/
- Verify: `node --version` (should be 20.x or higher)

#### Install Python
- Download from https://www.python.org/
- Verify: `python --version` (should be 3.11 or higher)
- Ensure pip is installed: `pip --version`

### 2. MongoDB Setup

#### Option A: MongoDB Atlas (Recommended)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a new cluster (free tier)
4. Create database user
5. Whitelist IP: `0.0.0.0/0` (for development)
6. Get connection string
7. Update `apps/api/.env` and `apps/ai/.env` with connection string

#### Option B: Local MongoDB
1. Install MongoDB locally
2. Start MongoDB service
3. Use connection string: `mongodb://localhost:27017/unimate`

### 3. Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy key to `apps/ai/.env`

### 4. Project Setup

```bash
# Clone or navigate to project
cd unimate

# Frontend dependencies
cd apps/web
npm install

# Backend dependencies
cd ../api
npm install

# AI service dependencies
cd ../ai
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Environment Variables

Copy example files and fill in values:

```bash
# Backend
cd apps/api
cp .env.example .env
# Edit .env with your values

# AI Service
cd ../ai
cp .env.example .env
# Edit .env with your values

# Frontend
cd ../web
cp .env.example .env
# Edit .env with your values
```

### 6. Generate JWT Secrets

```bash
# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Use output for `JWT_SECRET` and generate another for `JWT_REFRESH_SECRET`.

### 7. Create Admin User

After starting the backend, create an admin user:

```javascript
// scripts/createAdmin.js
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
require('dotenv').config({ path: './apps/api/.env' });

const User = require('./apps/api/src/models/User');

async function createAdmin() {
  await mongoose.connect(process.env.MONGODB_URI);
  const hashedPassword = await bcrypt.hash('admin123', 10);
  await User.create({
    email: 'admin@unimate.lk',
    passwordHash: hashedPassword,
    role: 'admin'
  });
  console.log('Admin created!');
  process.exit();
}

createAdmin();
```

### 8. Start Services

**Terminal 1 - AI Service:**
```bash
cd apps/ai
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Backend API:**
```bash
cd apps/api
npm run dev
```

**Terminal 3 - Frontend:**
```bash
cd apps/web
npm run dev
```

### 9. Verify Setup

1. Open http://localhost:5173
2. Register a new account
3. Try sending a message
4. Check backend logs for errors
5. Check AI service logs for errors

## Troubleshooting

### MongoDB Connection Error
- Verify connection string
- Check IP whitelist in Atlas
- Ensure MongoDB service is running (if local)

### Gemini API Error
- Verify API key is correct
- Check API quota/limits
- Ensure internet connection

### Port Already in Use
- Change PORT in .env files
- Kill process using port: `lsof -ti:5000 | xargs kill` (Mac/Linux)

### Module Not Found
- Reinstall dependencies
- Check Node/Python versions
- Clear node_modules and reinstall

## Next Steps

After setup is complete, proceed with:
1. Document ingestion (Step 5)
2. Z-score data seeding (Step 6)
3. Testing all features
4. Deployment preparation

