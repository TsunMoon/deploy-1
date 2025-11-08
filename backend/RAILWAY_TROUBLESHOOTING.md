# Railway Configuration Guide - UPDATED FOR ERROR FIX

## ⚠️ Railway Build Error Fix

If you see: `⚠ Script start.sh not found` or `✖ Railpack could not determine how to build the app`

### Solution 1: Use start.sh (Recommended)

Railway will now use the `start.sh` file that was created. No additional configuration needed.

Just push to GitHub:
```bash
git add start.sh
git commit -m "Add start.sh for Railway"
git push
```

### Solution 2: Simplified Configuration

If start.sh doesn't work, try these steps in Railway Dashboard:

1. **Go to Settings → Deploy**
2. **Set Custom Start Command:**
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Build Command (optional):**
   ```
   pip install -r requirements.txt
   ```

### Solution 3: Use Railway Service Configuration

In Railway Dashboard → Settings:

- **Builder:** Nixpacks
- **Root Directory:** `backend`
- **Custom Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Build Command:** `pip install -r requirements.txt`

### Solution 4: Minimal Configuration

If all else fails, try this minimal setup:

1. **Remove** `railway.json` temporarily
2. **Keep only:**
   - `Procfile`
   - `requirements.txt`
   - `runtime.txt`

Then Railway will auto-detect Python and use Procfile.

## Verification Steps

After deploying, check:

1. **Build Logs** - Should show:
   ```
   ✓ Installing dependencies from requirements.txt
   ✓ Build completed successfully
   ```

2. **Deploy Logs** - Should show:
   ```
   ✓ Starting uvicorn...
   ✓ Application startup complete
   ```

3. **Test endpoints:**
   ```bash
   curl https://your-app.railway.app/health
   ```

## Common Issues & Fixes

### Issue: "Could not determine how to build"
**Fix:** Ensure `requirements.txt` exists in backend directory

### Issue: "start.sh: No such file or directory"
**Fix:** Run `chmod +x start.sh` before pushing

### Issue: "Module 'main' not found"
**Fix:** Verify `main.py` exists in the same directory as start.sh

### Issue: "Port binding failed"
**Fix:** Ensure code uses `$PORT` environment variable:
```python
port = int(os.getenv("PORT", 8000))
```

## Current File Structure

Your backend should have:
```
backend/
├── main.py                 ✅ Main application
├── requirements.txt        ✅ Dependencies
├── runtime.txt            ✅ Python version
├── Procfile               ✅ Start command (fallback)
├── start.sh               ✅ NEW - Railway start script
├── nixpacks.toml          ✅ Build configuration
├── railway.json           ✅ Railway config
└── .railwayignore         ✅ Exclude files
```

## Push Changes

```bash
cd backend
git add .
git commit -m "Fix Railway deployment - add start.sh"
git push origin main
```

Railway will automatically redeploy with the new configuration.

## Still Having Issues?

Try these debugging steps:

1. **Check Railway Logs:**
   ```bash
   railway logs
   ```

2. **Verify Root Directory:**
   - Railway Settings → Root Directory = `backend`

3. **Verify Environment Variables:**
   ```bash
   railway variables
   ```

4. **Test Locally:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Contact Railway Support:**
   - Railway Discord: https://discord.gg/railway
   - Include build logs in your question

## Alternative: Railway CLI Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd backend
railway link

# Deploy
railway up
```

---

**Updated:** November 8, 2025
**Issue:** start.sh not found
**Status:** FIXED ✅
