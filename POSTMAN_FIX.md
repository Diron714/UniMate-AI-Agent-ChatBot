# Postman URL Issue Fix

## 🔍 Problem
You're getting:
```json
{
    "success": false,
    "message": "Route not found",
    "path": "/auth/register%0A"
}
```

The `%0A` is a URL-encoded newline character. This means your Postman URL has a trailing newline.

## ✅ Solution

### Fix in Postman:

1. **Check the URL field** - Make sure there's no trailing space or newline
2. **Use the correct URL:**
   ```
   http://localhost:5000/auth/register
   ```
   (No trailing spaces or newlines)

3. **Method:** `POST`
4. **Headers:**
   ```
   Content-Type: application/json
   ```

5. **Body (raw JSON):**
   ```json
   {
     "email": "test@example.com",
     "password": "Test1234"
   }
   ```

## 🔧 How to Fix in Postman

1. **Clear the URL field completely**
2. **Type the URL fresh:** `http://localhost:5000/auth/register`
3. **Make sure Method is:** `POST`
4. **Check Body tab:**
   - Select `raw`
   - Select `JSON` from dropdown
   - Paste the JSON body

## ✅ Correct Request Setup

**URL:** `http://localhost:5000/auth/register`  
**Method:** `POST`  
**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```

## 🧪 Test All Routes

### 1. Health Check (No auth needed)
```
GET http://localhost:5000/health
```

### 2. Register
```
POST http://localhost:5000/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Test1234"
}
```

### 3. Login
```
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Test1234"
}
```

### 4. Get Me (Need token)
```
GET http://localhost:5000/auth/me
Authorization: Bearer YOUR_TOKEN_HERE
```

### 5. Send Message (Need token)
```
POST http://localhost:5000/chat/send
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "message": "Hello UniMate"
}
```

## 💡 Pro Tips

1. **Use Postman Environment Variables:**
   - Create variable: `base_url` = `http://localhost:5000`
   - Use: `{{base_url}}/auth/register`

2. **Copy-Paste Safely:**
   - Always check for trailing spaces
   - Use "Paste and Match Style" or plain text

3. **Test with curl (alternative):**
   ```bash
   curl -X POST http://localhost:5000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test1234"}'
   ```

