# Railway Deployment - Quick Reference

## 🎯 Configuration Complete!

Your backend is now configured for Railway deployment with the following files:

### Configuration Files Created:
- ✅ `Procfile` - Startup command
- ✅ `railway.json` - Railway configuration
- ✅ `nixpacks.toml` - Build settings
- ✅ `runtime.txt` - Python version (3.11.9)
- ✅ `.railwayignore` - Files to exclude
- ✅ `.env.railway.template` - Environment variables template
- ✅ `deploy-railway.sh` - Deployment helper script
- ✅ `RAILWAY_DEPLOY.md` - Full deployment guide

### Code Updates:
- ✅ `main.py` - Updated to use Railway's PORT environment variable
- ✅ CORS configured for Railway and Vercel domains

---

## 🚀 Quick Deploy (3 Steps)

### Step 1: Push to GitHub
```bash
cd backend
git add .
git commit -m "Add Railway configuration"
git push origin main
```

### Step 2: Deploy on Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. **Important:** Set Root Directory to `backend`

### Step 3: Add Environment Variables
Copy from `.env.railway.template` to Railway Dashboard → Variables:

```env
AZURE_OPENAI_ENDPOINT=https://aiportalapi.stu-platform.live/use
AZURE_OPENAI_API_KEY=sk-2iSwylXiz7Fu67m-5pnJTA
AZURE_DEPLOYMENT_NAME=Gemini-2.5-Flash
AZURE_EMBEDDING_ENDPOINT=https://aiportalapi.stu-platform.live/jpe
AZURE_EMBEDDING_API_KEY=sk-GVqe4XKV0jlett_3b9mIdw
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3xqHOd49L1tN2yzGCLyuo6O4j1FoBzp6dvYzKDKdTig
QDRANT_URL=https://cb76d45d-8aa2-44aa-9fad-8c7921e271b5.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_COLLECTION_NAME=netflix_movies_tv_shows
```

---

## 🔍 Test Deployment

After deployment, Railway will give you a URL like: `https://your-app.up.railway.app`

Test these endpoints:
```bash
# Health check
curl https://your-app.up.railway.app/health

# API docs
open https://your-app.up.railway.app/docs

# Root endpoint
curl https://your-app.up.railway.app/
```

---

## 📱 Update Frontend

Update your frontend to use the Railway URL:

**For React/Vite:**
```env
# In frontend/.env
VITE_API_URL=https://your-app.up.railway.app
```

**For Next.js:**
```env
# In frontend/.env
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

---

## 🛠️ Using the Deployment Script

Run the helper script for guided deployment:

```bash
cd backend
./deploy-railway.sh
```

This script will:
- ✅ Check all configuration files
- ✅ Verify git status
- ✅ Help commit and push changes
- ✅ Show next steps

---

## 📚 Documentation

- **Full Guide:** See `RAILWAY_DEPLOY.md` for detailed instructions
- **Environment Variables:** See `.env.railway.template`
- **Railway Docs:** https://docs.railway.app
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/

---

## ⚠️ Important Notes

1. **Never commit `.env`** - It's already in `.gitignore`
2. **Set all environment variables in Railway Dashboard**
3. **Railway automatically provides `PORT` variable**
4. **Root directory MUST be set to `backend`**
5. **Health check endpoint: `/health`**

---

## 💰 Pricing

- **Free Tier:** $5 of usage per month
- **Hobby:** $5/month + usage
- **Pro:** $20/month + usage

Enough for development and small production apps!

---

## 🆘 Troubleshooting

### Build Fails
```bash
# Check Railway logs
railway logs

# Verify requirements.txt
pip freeze > requirements.txt
```

### App Won't Start
```bash
# Verify environment variables
railway variables

# Check health endpoint
curl https://your-app.up.railway.app/health
```

### Need Help?
- Check `RAILWAY_DEPLOY.md` for detailed troubleshooting
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

---

## ✅ Ready to Deploy!

Everything is configured and ready. Follow the 3 steps above to deploy! 🚀

For questions or issues, check the full deployment guide in `RAILWAY_DEPLOY.md`.
