# Postman Method Fix - Register Endpoint

## 🔍 The Problem

You're getting:
```json
{
    "success": false,
    "message": "Route not found",
    "path": "/auth/register",
    "method": "GET"
}
```

**The issue:** You're using `GET` method, but `/auth/register` requires `POST` method!

## ✅ Solution

### Step 1: Change Method to POST
1. In Postman, look at the method dropdown (left of URL bar)
2. It probably says `GET` - **change it to `POST`**

### Step 2: Set the URL
```
http://localhost:5000/auth/register
```

### Step 3: Set Headers
Click on **Headers** tab and add:
```
Content-Type: application/json
```

### Step 4: Set Body
1. Click on **Body** tab
2. Select **raw**
3. Select **JSON** from dropdown
4. Paste this:
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```

### Step 5: Send Request
Click **Send**

---

## ✅ Complete Request Setup

**Method:** `POST` (NOT GET!)  
**URL:** `http://localhost:5000/auth/register`  
**Headers:**
```
Content-Type: application/json
```
**Body (raw JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```

---

## 📋 All Endpoints with Correct Methods

### GET Endpoints (No Body Needed)
1. **Health Check**
   - Method: `GET`
   - URL: `http://localhost:5000/health`
   - No headers, no body

2. **API Status**
   - Method: `GET`
   - URL: `http://localhost:5000/`
   - No headers, no body

3. **Get Current User**
   - Method: `GET`
   - URL: `http://localhost:5000/auth/me`
   - Headers: `Authorization: Bearer YOUR_TOKEN`

4. **Get Chat History**
   - Method: `GET`
   - URL: `http://localhost:5000/chat/history`
   - Headers: `Authorization: Bearer YOUR_TOKEN`

### POST Endpoints (Need Body)
1. **Register**
   - Method: `POST` ✅
   - URL: `http://localhost:5000/auth/register`
   - Headers: `Content-Type: application/json`
   - Body: `{ "email": "...", "password": "..." }`

2. **Login**
   - Method: `POST` ✅
   - URL: `http://localhost:5000/auth/login`
   - Headers: `Content-Type: application/json`
   - Body: `{ "email": "...", "password": "..." }`

3. **Refresh Token**
   - Method: `POST` ✅
   - URL: `http://localhost:5000/auth/refresh`
   - Headers: `Content-Type: application/json`
   - Body: `{ "refreshToken": "..." }`

4. **Send Message**
   - Method: `POST` ✅
   - URL: `http://localhost:5000/chat/send`
   - Headers: 
     - `Authorization: Bearer YOUR_TOKEN`
     - `Content-Type: application/json`
   - Body: `{ "message": "Hello" }`

### DELETE Endpoints
1. **Delete Conversation**
   - Method: `DELETE`
   - URL: `http://localhost:5000/chat/history/CONVERSATION_ID`
   - Headers: `Authorization: Bearer YOUR_TOKEN`

---

## 🎯 Quick Reference

| Endpoint | Method | Needs Body? | Needs Auth? |
|----------|--------|-------------|-------------|
| `/health` | GET | No | No |
| `/auth/register` | **POST** | Yes | No |
| `/auth/login` | **POST** | Yes | No |
| `/auth/refresh` | **POST** | Yes | No |
| `/auth/me` | GET | No | Yes |
| `/chat/send` | **POST** | Yes | Yes |
| `/chat/history` | GET | No | Yes |
| `/chat/history/:id` | DELETE | No | Yes |

---

## 💡 Common Mistakes

1. ❌ Using GET for `/auth/register` → ✅ Use POST
2. ❌ Using GET for `/auth/login` → ✅ Use POST
3. ❌ Using GET for `/chat/send` → ✅ Use POST
4. ❌ Forgetting Content-Type header for POST → ✅ Add it
5. ❌ Forgetting Authorization header for protected routes → ✅ Add it

---

## ✅ Test Register Endpoint Correctly

1. **Method:** Select `POST` from dropdown
2. **URL:** `http://localhost:5000/auth/register`
3. **Headers Tab:**
   - Key: `Content-Type`
   - Value: `application/json`
4. **Body Tab:**
   - Select `raw`
   - Select `JSON` from dropdown
   - Paste:
   ```json
   {
     "email": "test@example.com",
     "password": "Test1234"
   }
   ```
5. **Click Send**

**Expected Response (201):**
```json
{
  "success": true,
  "message": "User created successfully",
  "token": "...",
  "refreshToken": "...",
  "user": {...}
}
```

---

**The key is: Change method from GET to POST!** 🚀

