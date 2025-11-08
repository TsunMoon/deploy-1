# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository with your code
- Environment variables ready

---

## 📋 Step 1: Prepare Your Project

The following files have been created for Railway:

✅ `Procfile` - Tells Railway how to start your app
✅ `railway.json` - Railway configuration
✅ `nixpacks.toml` - Build configuration
✅ `runtime.txt` - Python version specification
✅ `.railwayignore` - Files to exclude from deployment

---

## 🔧 Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd backend
   git add .
   git commit -m "Add Railway configuration"
   git push origin main
   ```

2. **Create a new project on Railway:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect it's a Python project

3. **Set Root Directory:**
   - Go to Settings → General
   - Set "Root Directory" to: `backend`
   - Save changes

### Option B: Deploy with Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up
```

---

## 🔐 Step 3: Configure Environment Variables

In Railway Dashboard → Variables, add these:

```env
# LLM Model
AZURE_OPENAI_ENDPOINT=https://aiportalapi.stu-platform.live/use
AZURE_OPENAI_API_KEY=sk-2iSwylXiz7Fu67m-5pnJTA
AZURE_DEPLOYMENT_NAME=Gemini-2.5-Flash

# Embedding Model
AZURE_EMBEDDING_ENDPOINT=https://aiportalapi.stu-platform.live/jpe
AZURE_EMBEDDING_API_KEY=sk-GVqe4XKV0jlett_3b9mIdw
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# QDRANT Configuration
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3xqHOd49L1tN2yzGCLyuo6O4j1FoBzp6dvYzKDKdTig
QDRANT_URL=https://cb76d45d-8aa2-44aa-9fad-8c7921e271b5.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_COLLECTION_NAME=netflix_movies_tv_shows

# Optional: CORS Origins (if you have specific domains)
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.railway.app
```

**⚠️ Important Notes:**
- Railway automatically provides `PORT` environment variable
- Don't hardcode the port in your application
- Variables are encrypted and secure on Railway

---

## ✅ Step 4: Verify Deployment

After deployment, Railway will provide a URL like: `https://your-app.up.railway.app`

### Test your endpoints:

```bash
# Health check
curl https://your-app.up.railway.app/health

# API documentation
open https://your-app.up.railway.app/docs

# Root endpoint
curl https://your-app.up.railway.app/
```

---

## 📊 Step 5: Monitor Your Application

### View Logs
```bash
# Using Railway CLI
railway logs

# Or in Railway Dashboard → Deployments → Logs
```

### Check Metrics
- CPU Usage
- Memory Usage
- Network Traffic
- Request Count

All available in Railway Dashboard → Metrics

---

## 🔄 Step 6: Update Your Frontend

Update your frontend API URL to point to Railway:

```javascript
// In your frontend .env or config
REACT_APP_API_URL=https://your-app.up.railway.app
VITE_API_URL=https://your-app.up.railway.app
```

---

## 🛠️ Troubleshooting

### Build Fails

**Issue:** Dependencies can't be installed
```bash
# Solution: Check requirements.txt versions
# Railway logs will show the exact error
```

**Issue:** Python version mismatch
```bash
# Solution: Update runtime.txt to match your local version
# Current: python-3.11.9
```

### Application Won't Start

**Issue:** Port binding error
```bash
# Solution: Ensure you're using $PORT from environment
# Already configured in main.py
```

**Issue:** Module not found
```bash
# Solution: Check that all imports are in requirements.txt
pip freeze > requirements.txt
```

### Memory Issues

**Issue:** Application crashes due to memory
```bash
# Solution: Upgrade Railway plan or optimize:
# 1. Reduce model sizes
# 2. Use lighter dependencies
# 3. Implement caching
```

### Database Connection Issues

**Issue:** Can't connect to Qdrant
```bash
# Solution: Verify environment variables:
railway variables

# Test connection locally with same credentials
```

---

## 🚀 Production Optimizations

### 1. Add a Custom Domain
```bash
# In Railway Dashboard → Settings → Domains
# Add your custom domain (e.g., api.yoursite.com)
# Configure DNS with provided CNAME record
```

### 2. Enable Automatic Deployments
Railway automatically deploys on:
- Push to `main` or `master` branch
- Pull request merges
- Manual trigger in dashboard

### 3. Set Up Health Checks
Railway will ping `/health` endpoint every 30 seconds to ensure service is running.

### 4. Implement Caching
```python
# Add Redis for caching (optional)
# Railway provides Redis service integration
```

### 5. Add Database Persistence (Optional)
```bash
# If you need persistent storage beyond memory:
# 1. Add PostgreSQL service in Railway
# 2. Link to your app
# 3. Update connection string in your code
```

---

## 💰 Pricing

**Free Tier:**
- $5 of usage credits per month
- Enough for development and testing
- Idle services are automatically paused

**Hobby Plan: $5/month**
- $5 of included usage
- No idle timeout
- Community support

**Pro Plan: $20/month**
- $20 of included usage
- Priority support
- Private networking
- More resources

---

## 📝 Environment Variable Management

### Using Railway CLI
```bash
# List all variables
railway variables

# Add a variable
railway variables set VARIABLE_NAME=value

# Delete a variable
railway variables delete VARIABLE_NAME
```

### Using Dashboard
1. Go to your project
2. Click "Variables" tab
3. Add/Edit/Delete variables
4. Changes trigger automatic redeployment

---

## 🔄 CI/CD Integration

### Automatic Deployments
Railway automatically deploys when:
- Code is pushed to connected branch
- Environment variables are changed
- Manual deployment is triggered

### Deployment Status
Check deployment status:
- Railway Dashboard → Deployments
- GitHub PR checks (if connected)
- Railway CLI: `railway status`

---

## 📱 Monitoring & Alerts

### Set Up Alerts (Pro Plan)
1. Go to Settings → Notifications
2. Configure alerts for:
   - Deployment failures
   - High resource usage
   - Application errors
   - Downtime

### Integration Options
- Slack notifications
- Email alerts
- Webhook integrations
- Discord notifications

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use Railway variables instead

2. **Rotate API keys regularly**
   - Update in Railway dashboard
   - No code changes needed

3. **Use HTTPS only**
   - Railway provides SSL by default
   - All traffic is encrypted

4. **Implement rate limiting**
   ```python
   from slowapi import Limiter
   # Add to your FastAPI app
   ```

5. **Monitor logs for suspicious activity**
   ```bash
   railway logs --follow
   ```

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/
- **Railway CLI Reference:** https://docs.railway.app/develop/cli
- **Support:** https://help.railway.app

---

## ✅ Deployment Checklist

- [ ] All configuration files created
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Root directory set to `backend`
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] Frontend updated with Railway URL
- [ ] Logs monitored for errors
- [ ] Custom domain configured (optional)

---

## 🎉 Success!

Your API should now be live at: `https://your-app.up.railway.app`

Test it:
```bash
curl https://your-app.up.railway.app/health
# Should return: {"status": "healthy", ...}
```

For support, check Railway logs or contact Railway support.

Happy deploying! 🚀
