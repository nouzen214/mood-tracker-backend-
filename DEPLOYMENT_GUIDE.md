# 🚀 Backend Server Deployment Guide

This guide will help you deploy your Mood Tracker backend server to **Render.com** (FREE!).

## 📋 What You Need

1. GitHub account (free)
2. Render.com account (free)
3. Your `serviceAccountKey.json` file
4. Your Gemini API key

---

## Step 1: Prepare Files

### 1.1 Copy serviceAccountKey.json

```cmd
copy C:\Users\Nouzen\Desktop\poject\serviceAccountKey.json C:\Users\Nouzen\Desktop\poject\backend\serviceAccountKey.json
```

### 1.2 Create .gitignore

Create `backend/.gitignore`:
```
__pycache__/
*.pyc
.env
serviceAccountKey.json
*.log
```

---

## Step 2: Push to GitHub

### 2.1 Initialize Git (if not already done)

```cmd
cd C:\Users\Nouzen\Desktop\poject\backend
git init
git add .
git commit -m "Initial backend server"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com/new
2. Name: `mood-tracker-backend`
3. Make it **Private** (important for security!)
4. Click "Create repository"

### 2.3 Push Code

```cmd
git remote add origin https://github.com/YOUR_USERNAME/mood-tracker-backend.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy to Render

### 3.1 Sign Up

1. Go to https://render.com/
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 3.2 Create Web Service

1. Click "New +" → "Web Service"
2. Connect your `mood-tracker-backend` repository
3. Configure:
   - **Name**: `mood-tracker-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app`
   - **Plan**: `Free`

### 3.3 Add Environment Variables

In Render dashboard, go to "Environment" tab and add:

```
GEMINI_API_KEY = AIzaSyDiSKNlLqxAqNBqEJmWCMQcDHdWxvOSB4E
```

### 3.4 Upload serviceAccountKey.json

**Option A: Using Render Secret Files (Recommended)**
1. In Render dashboard → "Environment" → "Secret Files"
2. Add file: `serviceAccountKey.json`
3. Paste the contents of your serviceAccountKey.json

**Option B: Base64 Encode (Alternative)**
```cmd
# In PowerShell
$content = Get-Content serviceAccountKey.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$encoded = [Convert]::ToBase64String($bytes)
Write-Output $encoded
```
Then add as environment variable: `FIREBASE_CREDENTIALS_BASE64`

### 3.5 Deploy!

Click "Create Web Service" and wait 5-10 minutes for deployment.

Your API will be live at: `https://mood-tracker-api.onrender.com`

---

## Step 4: Test Your API

### Test Health Endpoint

Open in browser:
```
https://mood-tracker-api.onrender.com/api/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T..."
}
```

### Test with Postman or curl

```bash
curl -X POST https://mood-tracker-api.onrender.com/api/ai_chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "test123"}'
```

---

## Step 5: Update Android App

Now update your Android app to use this backend URL instead of direct Firebase/Gemini calls.

Replace all Firebase/Gemini code with HTTP requests to:
```
https://mood-tracker-api.onrender.com/api/...
```

---

## 🔒 Security Notes

1. **Never commit serviceAccountKey.json to public repos**
2. **Keep your GitHub repo Private**
3. **Use environment variables for all secrets**
4. **Enable HTTPS only** (Render does this automatically)

---

## 📊 Monitoring

- **Logs**: Render dashboard → "Logs" tab
- **Metrics**: Render dashboard → "Metrics" tab
- **Free tier limits**: 750 hours/month (enough for testing)

---

## 🆙 Upgrading

Free tier limitations:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds

To upgrade to paid ($7/month):
- Always-on server
- No spin-down delays
- Better performance

---

## 🐛 Troubleshooting

### Server won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure serviceAccountKey.json is uploaded

### API returns errors
- Check Firebase database URL is correct
- Verify Gemini API key is valid
- Check logs for detailed error messages

### Slow responses
- Free tier spins down - first request is slow
- Consider upgrading to paid tier
- Or use a keep-alive service

---

## ✅ Next Steps

1. Deploy backend to Render
2. Test all API endpoints
3. Modify Android app to use backend
4. Rebuild APK
5. Test on Android phone

**Your app will now work fully on Android!** 🎉
