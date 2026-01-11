# Postman POST Method Not Working - Troubleshooting

## 🔍 The Issue

You're setting POST in Postman, but the server receives GET. This can happen due to several reasons.

## ✅ Solutions (Try in Order)

### Solution 1: Restart Your Server

The server might be running old code. Restart it:

1. **Stop the server:**
   - Press `Ctrl+C` in the terminal where server is running
   - Or close the terminal

2. **Start the server again:**
   ```bash
   cd apps/api
   npm run dev
   ```

3. **Wait for:**
   ```
   ✅ MongoDB Connected: ...
   🚀 Server running on port 5000
   ```

4. **Try the request again in Postman**

---

### Solution 2: Check Postman Method Dropdown

1. **Look at the method dropdown** (left of URL bar in Postman)
2. **Make sure it says `POST`** (not GET, not OPTIONS)
3. **If it's not POST:**
   - Click the dropdown
   - Select `POST`
   - Make sure it stays as POST

---

### Solution 3: Clear Postman Cache

1. **Close Postman completely**
2. **Reopen Postman**
3. **Create a NEW request** (don't use saved request)
4. **Set method to POST**
5. **Type URL:** `http://localhost:5000/auth/register`
6. **Add headers and body**
7. **Send**

---

### Solution 4: Check for Redirects

Sometimes Postman might be following redirects. Check:

1. **In Postman Settings:**
   - Click the gear icon (⚙️)
   - Go to **Settings**
   - Make sure **"Follow redirects"** is OFF
   - Or set to **"Follow original HTTP method"**

---

### Solution 5: Verify Request Details

Before sending, check:

1. **Method dropdown shows:** `POST`
2. **URL is:** `http://localhost:5000/auth/register` (no trailing spaces)
3. **Headers tab has:** `Content-Type: application/json`
4. **Body tab:**
   - Selected: `raw`
   - Dropdown shows: `JSON`
   - Body contains valid JSON

---

### Solution 6: Use Postman Console

1. **Open Postman Console:**
   - View → Show Postman Console
   - Or `Ctrl+Alt+C`

2. **Send your request**

3. **Check the console** - it shows the actual request being sent:
   ```
   POST http://localhost:5000/auth/register
   ```

4. **If it shows GET instead of POST**, there's a Postman issue

---

### Solution 7: Test with curl (Alternative)

If Postman keeps having issues, test with curl:

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

If curl works, the issue is with Postman configuration.

---

### Solution 8: Check Server Logs

Look at your server terminal. When you send the request, you should see:

```
2025-01-08T... - POST /auth/register
```

If it shows `GET /auth/register`, then Postman is sending GET despite being set to POST.

---

## 🎯 Step-by-Step Fresh Request

1. **Stop server** (Ctrl+C)

2. **Start server:**
   ```bash
   cd apps/api
   npm run dev
   ```

3. **In Postman:**
   - Create **NEW** request (don't duplicate)
   - Method: **POST** (verify dropdown)
   - URL: `http://localhost:5000/auth/register` (type manually)
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "email": "test@example.com",
       "password": "Test1234"
     }
     ```

4. **Send request**

5. **Check server terminal** - should show `POST /auth/register`

---

## 🔧 If Still Not Working

### Check Server is Running Correct Port

In server terminal, you should see:
```
🚀 Server running on port 5000
```

If it's a different port, use that port in Postman.

### Check for Multiple Servers

Make sure only ONE server instance is running:
```bash
# Windows PowerShell
Get-Process -Name node | Stop-Process
```

Then start server again.

### Verify Route is Registered

The server should log routes on startup. Check if you see auth routes being registered.

---

## ✅ Expected Behavior

When working correctly:

1. **Postman shows:** Method = POST
2. **Server terminal shows:** `POST /auth/register`
3. **Response:** 201 Created with user data

---

## 🆘 Last Resort: Manual Test

Create a simple test file:

**test-api.js:**
```javascript
import axios from 'axios'

async function test() {
  try {
    const response = await axios.post('http://localhost:5000/auth/register', {
      email: 'test@example.com',
      password: 'Test1234'
    })
    console.log('Success:', response.data)
  } catch (error) {
    console.error('Error:', error.response?.data || error.message)
  }
}

test()
```

Run:
```bash
node test-api.js
```

If this works, the issue is definitely with Postman.

---

**Most likely fix: Restart the server and create a fresh Postman request!** 🚀

