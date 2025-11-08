# Railway Deployment Instructions - Backend Only

## Chuẩn bị Deploy Backend trên Railway

### 1. Cấu hình Project để Deploy chỉ Backend

Railway sẽ deploy chỉ folder `backend` với cấu hình Docker:

**Files quan trọng:**

- `Dockerfile`: Container configuration
- `.dockerignore`: Ignore unnecessary files
- `railway.json`: Railway deployment config
- `requirements.txt`: Python dependencies

### 2. Cách Deploy

#### Option 1: Deploy từ GitHub (Recommended)

1. Push code lên GitHub repository
2. Trên Railway dashboard:
   - Tạo new project
   - Connect GitHub repository
   - Chọn **root directory** là `backend/`
   - Railway sẽ tự động detect Dockerfile

#### Option 2: Deploy từ CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to backend folder
cd backend

# Initialize and deploy
railway project:init
railway up
```

### 3. Environment Variables cần set trên Railway

```
# API Keys
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key

# Qdrant Configuration
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=netflix_collection

# App Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_secret_key
```

### 4. Dockerfile Highlights

- **Base Image**: `python:3.11-slim` (tối ưu size)
- **Security**: Non-root user execution
- **Performance**: Multi-stage caching với requirements.txt
- **Health Check**: Built-in health monitoring
- **Port**: Expose 8000 (Railway auto-assigns $PORT)

### 5. Railway Project Structure

```
Railway Project (chỉ backend)
├── Dockerfile              # Container config
├── .dockerignore           # Ignore files
├── railway.json           # Railway settings
├── requirements.txt       # Dependencies
├── main.py               # FastAPI app
├── config.py             # Configuration
├── routers/              # API routes
├── services/             # Business logic
└── tests/                # Test files
```

### 6. Deploy Commands

```bash
# Deploy manually from backend folder
cd backend
railway up

# Check logs
railway logs

# Check status
railway status

# Open in browser
railway open
```

### 7. Monitoring & Troubleshooting

- **Health Check**: `/health` endpoint
- **Logs**: `railway logs --follow`
- **Metrics**: Railway dashboard
- **Environment**: Check environment variables

### 8. CI/CD với GitHub Actions (Optional)

Railway tự động deploy khi push code lên GitHub branch đã connect.

**Auto-deploy triggers:**

- Push to main/master branch
- Pull request merge
- Manual trigger từ Railway dashboard

### Notes:

- Frontend sẽ không được deploy cùng
- Mọi API endpoints sẽ có Railway domain
- CORS cần configure cho frontend domain
- Database connections qua environment variables
