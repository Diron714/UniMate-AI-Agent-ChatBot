# Postman Testing Guide - UniMate API

**Base URL:** `http://localhost:5000`

---

## 🔐 Authentication Endpoints

### 1. Register User
**Method:** `POST`  
**URL:** `http://localhost:5000/auth/register`  
**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```

**Expected Response (201):**
```json
{
  "success": true,
  "message": "User created successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "test@example.com",
    "role": "student",
    "preferences": {
      "language": "en",
      "university": "",
      "course": ""
    }
  }
}
```

**Error Responses:**
- `400`: Invalid email or password format
- `409`: User already exists
- `429`: Too many requests (rate limited)

---

### 2. Login User
**Method:** `POST`  
**URL:** `http://localhost:5000/auth/login`  
**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "test@example.com",
    "role": "student",
    "preferences": {
      "language": "en",
      "university": "",
      "course": ""
    }
  }
}
```

**Error Responses:**
- `400`: Email and password required
- `401`: Invalid credentials
- `429`: Too many requests (rate limited)

---

### 3. Refresh Token
**Method:** `POST`  
**URL:** `http://localhost:5000/auth/refresh`  
**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400`: Refresh token required
- `401`: Invalid or expired refresh token

---

### 4. Get Current User
**Method:** `GET`  
**URL:** `http://localhost:5000/auth/me`  
**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Expected Response (200):**
```json
{
  "success": true,
  "user": {
    "email": "test@example.com",
    "role": "student",
    "preferences": {
      "language": "en",
      "university": "",
      "course": ""
    },
    "createdAt": "2025-01-08T...",
    "updatedAt": "2025-01-08T..."
  }
}
```

**Error Responses:**
- `401`: No token provided or invalid token

---

## 💬 Chat Endpoints

### 5. Send Message
**Method:** `POST`  
**URL:** `http://localhost:5000/chat/send`  
**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "message": "What are the admission requirements for University of Colombo?",
  "context": {
    "university": "University of Colombo",
    "stage": "pre-application",
    "preferences": {}
  }
}
```

**Minimal Body (context optional):**
```json
{
  "message": "Hello UniMate"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "AI response here...",
  "sources": ["UGC Handbook 2023", "University Website"],
  "context": {
    "university": "University of Colombo",
    "stage": "pre-application",
    "preferences": {}
  }
}
```

**Error Responses:**
- `400`: Message is required
- `401`: Not authenticated
- `429`: Too many requests (30 per minute)
- `503`: AI service unavailable
- `504`: AI service timeout

---

### 6. Get Chat History
**Method:** `GET`  
**URL:** `http://localhost:5000/chat/history`  
**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters (optional):**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 50)

**Example URLs:**
- `http://localhost:5000/chat/history`
- `http://localhost:5000/chat/history?page=1&limit=10`

**Expected Response (200):**
```json
{
  "success": true,
  "conversations": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "messages": [
        {
          "role": "user",
          "content": "Hello",
          "timestamp": "2025-01-08T10:00:00.000Z",
          "sources": []
        },
        {
          "role": "assistant",
          "content": "Hello! How can I help you?",
          "timestamp": "2025-01-08T10:00:05.000Z",
          "sources": []
        }
      ],
      "context": {
        "university": "",
        "stage": "",
        "preferences": {}
      },
      "createdAt": "2025-01-08T10:00:00.000Z",
      "updatedAt": "2025-01-08T10:00:05.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1,
    "hasMore": false
  }
}
```

**Error Responses:**
- `401`: Not authenticated
- `500`: Server error

---

### 7. Delete Conversation
**Method:** `DELETE`  
**URL:** `http://localhost:5000/chat/history/:id`  
**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Example URL:**
```
http://localhost:5000/chat/history/65a1b2c3d4e5f6g7h8i9j0k1
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

**Error Responses:**
- `400`: Invalid conversation ID
- `401`: Not authenticated
- `404`: Conversation not found or not owned by user
- `500`: Server error

---

## 🏥 Health Check Endpoints

### 8. API Status
**Method:** `GET`  
**URL:** `http://localhost:5000/`  
**Headers:** None

**Expected Response (200):**
```json
{
  "message": "UniMate API Server",
  "status": "running",
  "version": "1.0.0",
  "timestamp": "2025-01-08T12:00:00.000Z"
}
```

---

### 9. Health Check
**Method:** `GET`  
**URL:** `http://localhost:5000/health`  
**Headers:** None

**Expected Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-08T12:00:00.000Z"
}
```

**If Database Disconnected:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2025-01-08T12:00:00.000Z"
}
```

---

## 📋 Postman Collection Setup

### Step 1: Create Environment Variables

In Postman, create an environment with these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:5000` | `http://localhost:5000` |
| `token` | (empty) | (will be set after login) |
| `refresh_token` | (empty) | (will be set after login) |
| `user_id` | (empty) | (will be set after login) |
| `conversation_id` | (empty) | (will be set after getting history) |

### Step 2: Setup Authorization

For protected endpoints, use:
- **Type:** Bearer Token
- **Token:** `{{token}}`

Or in Headers:
```
Authorization: Bearer {{token}}
```

### Step 3: Auto-Save Tokens (Optional)

Add this to the **Tests** tab of Login request:

```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("token", response.token);
    pm.environment.set("refresh_token", response.refreshToken);
    pm.environment.set("user_id", response.user._id);
}
```

---

## 🧪 Testing Workflow

### 1. Health Check First
```
GET http://localhost:5000/health
```
✅ Should return `"database": "connected"`

### 2. Register a New User
```
POST http://localhost:5000/auth/register
Body: { "email": "test@example.com", "password": "Test1234" }
```
✅ Save the `token` from response

### 3. Login (Alternative)
```
POST http://localhost:5000/auth/login
Body: { "email": "test@example.com", "password": "Test1234" }
```
✅ Save the `token` from response

### 4. Get Current User
```
GET http://localhost:5000/auth/me
Headers: Authorization: Bearer YOUR_TOKEN
```
✅ Should return user info

### 5. Send a Chat Message
```
POST http://localhost:5000/chat/send
Headers: Authorization: Bearer YOUR_TOKEN
Body: { "message": "Hello UniMate" }
```
✅ Should return AI response (if AI service is running)

### 6. Get Chat History
```
GET http://localhost:5000/chat/history
Headers: Authorization: Bearer YOUR_TOKEN
```
✅ Should return conversations

### 7. Delete Conversation
```
DELETE http://localhost:5000/chat/history/CONVERSATION_ID
Headers: Authorization: Bearer YOUR_TOKEN
```
✅ Should delete the conversation

---

## 🔍 Common Issues & Solutions

### Issue 1: "No token provided"
**Solution:** Make sure you're including the Authorization header:
```
Authorization: Bearer YOUR_TOKEN
```

### Issue 2: "Token expired"
**Solution:** Use the refresh token endpoint to get a new token:
```
POST /auth/refresh
Body: { "refreshToken": "YOUR_REFRESH_TOKEN" }
```

### Issue 3: "AI service unavailable"
**Solution:** Make sure the AI service is running on port 8000:
```bash
cd apps/ai
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

### Issue 4: "Too many requests"
**Solution:** Wait 1 minute. Rate limit is 30 requests per minute.

### Issue 5: "Database disconnected"
**Solution:** Check MongoDB connection in `.env` file and ensure MongoDB Atlas is accessible.

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created (registration) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (invalid/missing token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not Found |
| `409` | Conflict (duplicate entry) |
| `429` | Too Many Requests (rate limited) |
| `500` | Internal Server Error |
| `503` | Service Unavailable (AI service down) |
| `504` | Gateway Timeout (AI service timeout) |

---

## 🎯 Quick Test Checklist

- [ ] Health check works
- [ ] Register new user works
- [ ] Login works
- [ ] Get current user works
- [ ] Send message works (if AI service running)
- [ ] Get history works
- [ ] Delete conversation works
- [ ] Rate limiting works (try 31 requests in 1 minute)
- [ ] Token expiration handled
- [ ] Error responses are correct

---

## 📝 Example Postman Collection JSON

You can import this into Postman:

```json
{
  "info": {
    "name": "UniMate API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test1234\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/register",
          "host": ["{{base_url}}"],
          "path": ["auth", "register"]
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test1234\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/login",
          "host": ["{{base_url}}"],
          "path": ["auth", "login"]
        }
      }
    },
    {
      "name": "Send Message",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"Hello UniMate\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/chat/send",
          "host": ["{{base_url}}"],
          "path": ["chat", "send"]
        }
      }
    }
  ]
}
```

---

**Happy Testing! 🚀**

