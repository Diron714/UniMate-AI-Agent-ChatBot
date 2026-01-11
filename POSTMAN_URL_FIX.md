# Fix Postman URL Issue - Step by Step

## 🔍 The Problem

You're getting 404 errors because your Postman URL contains hidden newline characters (`%0A` or `%0D`).

## ✅ Solution - Fix Your Postman Request

### Step 1: Delete the Entire URL
1. In Postman, click on the URL field
2. Select all (Ctrl+A or Cmd+A)
3. Delete everything

### Step 2: Type the URL Fresh
**DO NOT copy-paste!** Type it manually:

```
http://localhost:5000/health
```

### Step 3: Verify the URL
- Make sure there are NO spaces before or after
- Make sure there are NO newlines
- The URL should be exactly: `http://localhost:5000/health`

### Step 4: Set Method
- Make sure Method is: `GET`

### Step 5: Send Request
Click Send

---

## ✅ Correct URLs for All Endpoints

### Health Check
```
GET http://localhost:5000/health
```
(No headers needed)

### API Status
```
GET http://localhost:5000/
```
(No headers needed)

### Register
```
POST http://localhost:5000/auth/register
Headers: Content-Type: application/json
Body: { "email": "test@example.com", "password": "Test1234" }
```

### Login
```
POST http://localhost:5000/auth/login
Headers: Content-Type: application/json
Body: { "email": "test@example.com", "password": "Test1234" }
```

### Get Me
```
GET http://localhost:5000/auth/me
Headers: Authorization: Bearer YOUR_TOKEN
```

### Send Message
```
POST http://localhost:5000/chat/send
Headers: 
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
Body: { "message": "Hello UniMate" }
```

### Get History
```
GET http://localhost:5000/chat/history
Headers: Authorization: Bearer YOUR_TOKEN
```

---

## 🎯 Quick Test

1. **Open Postman**
2. **Create New Request**
3. **Method:** GET
4. **URL:** Type manually `http://localhost:5000/health`
5. **Click Send**

Expected Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "..."
}
```

---

## 💡 Pro Tips

1. **Never copy-paste URLs** - Always type them manually in Postman
2. **Use Environment Variables:**
   - Create variable: `base_url` = `http://localhost:5000`
   - Use: `{{base_url}}/health`
3. **Check for invisible characters:**
   - After typing URL, select all and check if there's any extra selection
4. **Use Postman's URL bar:**
   - Don't use the address bar from browser
   - Type directly in Postman's URL field

---

## 🔧 Alternative: Use curl

If Postman keeps having issues, test with curl:

```bash
# Health check
curl http://localhost:5000/health

# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

---

## ✅ Verification

After fixing, you should get:

**GET /health:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-08T..."
}
```

**POST /auth/register:**
```json
{
  "success": true,
  "message": "User created successfully",
  "token": "...",
  "user": {...}
}
```

If you still get 404, the server might not be running. Check:
```bash
cd apps/api
npm run dev
```

