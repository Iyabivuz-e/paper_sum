# 🚀 Quick Deploy Commands

## 🔧 Backend (Render)
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for production deployment"
git push origin main

# 2. Render Setup
# - Go to render.com
# - New Web Service → Connect repo
# - Root directory: backend
# - Environment: Docker
```

**Environment Variables for Render:**
```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
```

## 🌐 Frontend (Vercel)
```bash
# 1. Same repo, different directory
# Vercel will auto-detect Next.js

# 2. Vercel Setup  
# - Go to vercel.com
# - Import project → Connect repo
# - Root directory: frontend
# - Framework: Next.js
```

**Environment Variables for Vercel:**
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

## 🔄 After Both Deploy
1. **Update CORS**: Add Vercel URL to backend CORS_ORIGINS
2. **Test Connection**: Upload a paper and verify it works
3. **Share**: Your app is live! 🎉

## 📱 Live URLs
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **API Health**: `https://your-backend.onrender.com/health`

**Total Time**: ~15-20 minutes for both deployments! ⚡
