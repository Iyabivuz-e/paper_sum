# 🚀 Cloud Deployment Guide

## Overview
- **Frontend**: Vercel (Next.js optimized)
- **Backend**: Render (Python FastAPI)

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Your Backend
1. Ensure your backend code is pushed to GitHub/GitLab
2. Your `Dockerfile` and `render.yaml` are already configured

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `paper-summarizer-backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `master` or `main`
   - **Root Directory**: `backend`

### Step 3: Environment Variables
Add these in Render dashboard:
```bash
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url (optional)
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

### Step 4: Add Database (Optional)
- Add PostgreSQL add-on in Render
- Or use NeonDB (external)
- Update `DATABASE_URL` accordingly

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Your Frontend
1. Your `vercel.json` is already configured
2. Update the backend URL in `.env.production`

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "Add New..." → "Project"
3. Import your repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Environment Variables
Add in Vercel dashboard:
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_ANALYTICS_ENABLED=true
NEXT_PUBLIC_SITE_URL=https://your-app.vercel.app
```

### Step 4: Update CORS
After frontend deployment, update backend CORS:
```bash
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

---

## 🔄 Post-Deployment

### 1. Test the Connection
- Frontend should connect to backend
- Upload a test paper
- Verify all features work

### 2. Update URLs
- Replace placeholder URLs with actual deployment URLs
- Test CORS configuration

### 3. Monitor
- Check Render logs for backend issues
- Check Vercel function logs for frontend issues

---

## 💰 Costs

### Render (Backend)
- **Starter Plan**: $7/month
- **Free Tier**: Available (sleeps after 15min inactivity)

### Vercel (Frontend)
- **Hobby Plan**: Free
- **Pro Plan**: $20/month (if needed)

---

## 🛠️ Troubleshooting

### Common Issues:
1. **CORS Errors**: Update CORS_ORIGINS in backend
2. **API Connection**: Check NEXT_PUBLIC_API_URL
3. **Build Failures**: Check dependencies and Node.js version
4. **Database Issues**: Verify DATABASE_URL connection

### Logs:
- **Render**: Dashboard → Your Service → Logs
- **Vercel**: Dashboard → Your Project → Functions

---

## 🚀 Quick Commands

### Backend (Render)
```bash
# Local test with production settings
docker build -t paper-backend .
docker run -p 8000:8000 paper-backend
```

### Frontend (Vercel)
```bash
# Local production build
npm run build
npm start
```

## 📱 Mobile Optimization
Both platforms handle mobile optimization automatically:
- Vercel: Edge CDN + automatic compression
- Render: Auto-scaling containers

Your app will be fast and responsive on all devices! 🌟
