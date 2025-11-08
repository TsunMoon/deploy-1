# Railway Deployment Checklist

Use this checklist to ensure a smooth deployment to Railway.

## Pre-Deployment Checklist

### ✅ Configuration Files
- [ ] `Procfile` exists in backend directory
- [ ] `railway.json` exists in backend directory
- [ ] `nixpacks.toml` exists in backend directory
- [ ] `runtime.txt` exists in backend directory
- [ ] `.railwayignore` exists in backend directory
- [ ] `.env.railway.template` exists with all variables

### ✅ Code Preparation
- [ ] `main.py` uses `os.getenv("PORT", 8000)` for port
- [ ] CORS includes Railway domains (`*.railway.app`)
- [ ] All imports are in `requirements.txt`
- [ ] Health check endpoint `/health` works locally
- [ ] `.env` file is in `.gitignore`

### ✅ Git Repository
- [ ] All changes committed to git
- [ ] Repository pushed to GitHub
- [ ] Branch is up to date with remote

## Railway Setup Checklist

### ✅ Project Creation
- [ ] Railway account created at https://railway.app
- [ ] New project created
- [ ] Connected to GitHub repository
- [ ] **Root directory set to `backend`** ⚠️ CRITICAL

### ✅ Environment Variables
Add these in Railway Dashboard → Variables:

- [ ] `AZURE_OPENAI_ENDPOINT`
- [ ] `AZURE_OPENAI_API_KEY`
- [ ] `AZURE_DEPLOYMENT_NAME`
- [ ] `AZURE_EMBEDDING_ENDPOINT`
- [ ] `AZURE_EMBEDDING_API_KEY`
- [ ] `AZURE_EMBEDDING_DEPLOYMENT`
- [ ] `QDRANT_API_KEY`
- [ ] `QDRANT_URL`
- [ ] `QDRANT_COLLECTION_NAME`

**Note:** Railway automatically provides `PORT` variable - don't add it manually!

### ✅ Deployment
- [ ] Railway build completed successfully
- [ ] Deployment status shows "Active"
- [ ] Logs show no critical errors
- [ ] Railway provided a public URL

## Post-Deployment Checklist

### ✅ Testing
- [ ] Health endpoint works: `https://your-app.up.railway.app/health`
- [ ] API docs accessible: `https://your-app.up.railway.app/docs`
- [ ] Root endpoint works: `https://your-app.up.railway.app/`
- [ ] Test recommendation endpoint with sample query
- [ ] Check response times are acceptable

### ✅ Frontend Integration
- [ ] Updated frontend environment variables with Railway URL
- [ ] Frontend can connect to Railway backend
- [ ] CORS is working (no CORS errors in browser)
- [ ] All API calls working from frontend

### ✅ Monitoring
- [ ] Check Railway logs for any errors
- [ ] Monitor resource usage (CPU, Memory)
- [ ] Set up alerts (if on Pro plan)
- [ ] Bookmark Railway dashboard URL

## Optional Enhancements

### 🎯 Custom Domain (Optional)
- [ ] Custom domain purchased
- [ ] Domain added in Railway → Settings → Domains
- [ ] DNS CNAME record configured
- [ ] SSL certificate provisioned (automatic)
- [ ] Domain is accessible

### 🔒 Security (Recommended)
- [ ] API keys rotated and secured
- [ ] CORS origins restricted to specific domains
- [ ] Rate limiting implemented (if needed)
- [ ] Logging configured for security events

### 📊 Production Optimization (Optional)
- [ ] Consider adding Redis for caching
- [ ] Set up database backup strategy
- [ ] Configure auto-scaling rules
- [ ] Set up monitoring and alerting
- [ ] Document API endpoints for team

## Troubleshooting Steps

If deployment fails, check:

- [ ] Railway logs for error messages
- [ ] Root directory is set to `backend`
- [ ] All environment variables are set correctly
- [ ] Python version matches `runtime.txt`
- [ ] All dependencies in `requirements.txt` are valid
- [ ] No hardcoded ports in code
- [ ] CORS configuration includes Railway domains

## Success Criteria

✅ All these should be true:

1. Health endpoint returns `{"status": "healthy"}`
2. API documentation loads at `/docs`
3. No errors in Railway logs
4. Frontend successfully calls backend
5. Response times < 2 seconds
6. Memory usage stable
7. No CORS errors

## Need Help?

- 📖 Read: `RAILWAY_SETUP.md` (Quick reference)
- 📚 Read: `RAILWAY_DEPLOY.md` (Full guide)
- 🎯 Use: `./deploy-railway.sh` (Interactive helper)
- 🌐 Visit: https://docs.railway.app
- 💬 Join: Railway Discord community

---

## Quick Commands

### Check deployment status:
```bash
railway status
```

### View logs:
```bash
railway logs
```

### Open dashboard:
```bash
railway open
```

### Deploy manually:
```bash
railway up
```

---

**Last Updated:** November 8, 2025
**Configuration Version:** 1.0.0
