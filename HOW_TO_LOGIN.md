# How to Login to UniMate

## 🚀 Quick Start Guide

### Step 1: Start All Services

**Terminal 1 - Backend API:**
```powershell
cd apps/api
npm run dev
```
Wait for: `Server running on port 5000`

**Terminal 2 - AI Service:**
```powershell
cd apps/ai
uvicorn main:app --reload --port 8000
```
Wait for: `Application startup complete`

**Terminal 3 - Frontend:**
```powershell
cd apps/web
npm run dev
```
Wait for: `Local: http://localhost:5173`

---

### Step 2: Access Login Page

Open your browser and go to:
```
http://localhost:5173
```

You will be automatically redirected to the login page at:
```
http://localhost:5173/login
```

---

### Step 3: Register (First Time Only)

If you don't have an account yet:

1. **Click "Register"** at the bottom of the login form
2. **Enter your email** (e.g., `student@example.com`)
3. **Enter a password** that meets these requirements:
   - At least 8 characters
   - At least one uppercase letter (A-Z)
   - At least one lowercase letter (a-z)
   - At least one number (0-9)

**Example passwords:**
- ✅ `Student123` (valid)
- ✅ `MyPass123` (valid)
- ❌ `password` (no uppercase/number)
- ❌ `PASS123` (no lowercase)

4. **Click "Register"**
5. You will be automatically logged in and redirected to the chat page

---

### Step 4: Login (If You Have an Account)

1. **Enter your email** (the one you registered with)
2. **Enter your password**
3. **Click "Login"**
4. You will be redirected to the chat page at `/chat`

---

## 📝 Login Page Features

The login page supports:
- ✅ **Email/Password authentication**
- ✅ **Automatic registration** (toggle between Login/Register)
- ✅ **Error messages** for invalid credentials
- ✅ **Password validation** feedback
- ✅ **Auto-redirect** to chat after successful login

---

## 🔐 Password Requirements

Your password must have:
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter (A-Z)
- ✅ At least 1 lowercase letter (a-z)
- ✅ At least 1 number (0-9)

**Valid Examples:**
- `Student123`
- `MyPass2024`
- `UniMate123`

**Invalid Examples:**
- `password` (no uppercase/number)
- `PASSWORD` (no lowercase/number)
- `12345678` (no letters)
- `short` (too short)

---

## 🆘 Troubleshooting

### "Invalid email or password"
- Check that you're using the correct email
- Make sure your password is correct
- Try registering a new account if you forgot your password

### "User with this email already exists"
- This email is already registered
- Click "Login" instead of "Register"
- Or use a different email address

### "Password must be at least 8 characters..."
- Your password doesn't meet the requirements
- Make sure it has uppercase, lowercase, and a number

### Can't access login page
- Make sure frontend is running: `cd apps/web && npm run dev`
- Check that it's running on `http://localhost:5173`
- Check browser console for errors

### Login works but chat doesn't load
- Make sure backend API is running: `cd apps/api && npm run dev`
- Make sure AI service is running: `cd apps/ai && uvicorn main:app --reload --port 8000`
- Check browser console for API errors

---

## 🎯 After Login

Once logged in, you will:
1. Be redirected to `/chat`
2. See the chat interface
3. Be able to ask questions to UniMate AI
4. Have your conversations saved
5. See your profile in the navbar

---

## 💡 Tips

- **Remember your email** - This is your login username
- **Use a strong password** - Keep it secure
- **Stay logged in** - Your session lasts 7 days
- **Logout** - Click the logout button in the navbar when done

---

## 🔄 Switching Between Login/Register

The login page has a toggle at the bottom:
- Click **"Register"** to create a new account
- Click **"Login"** to sign in with existing account

---

*Need help? Check the server logs for detailed error messages.*

