# Frontend Production Deployment - Branch Strategy

This branch (`frontend-production`) is specifically configured for frontend deployment to Vercel.

## Production Configuration

### Backend URL
- Production Backend: `https://research-paper-summary-backend.onrender.com`
- Configured in `vercel.json` for automatic deployment

### CORS Configuration
The backend has been updated to allow the following origins:
- `https://paper-sum.vercel.app` (main production)
- `https://paper-sum-*.vercel.app` (preview deployments)
- `https://*.vercel.app` (all Vercel domains)

### Environment Variables for Vercel

Set these in your Vercel project dashboard:

```bash
NEXT_PUBLIC_BACKEND_URL=https://research-paper-summary-backend.onrender.com
NEXT_PUBLIC_GA_MEASUREMENT_ID=your-ga-id
NEXT_PUBLIC_ANALYTICS_ENABLED=true
NEXT_PUBLIC_APP_NAME=Paper Summarizer
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Deployment Steps

1. **Push to this branch:**
   ```bash
   git push origin frontend-production
   ```

2. **Connect Vercel to this branch:**
   - Go to Vercel Dashboard
   - Import project from GitHub
   - Select this repository
   - Choose `frontend-production` branch
   - Set root directory to `frontend/`

3. **Configure Vercel:**
   - Framework: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

### Branch Strategy

- `master` branch: Full-stack development and backend deployment
- `frontend-production` branch: Frontend-only production deployment
- This separation prevents frontend deployments from triggering backend rebuilds

### Testing Production Build

Before deploying, test locally:
```bash
cd frontend
NEXT_PUBLIC_BACKEND_URL=https://research-paper-summary-backend.onrender.com npm run build
npm start
```

### Monitoring

After deployment, verify:
- [ ] Frontend loads correctly
- [ ] API calls reach the backend successfully
- [ ] CORS is working (no blocked requests)
- [ ] Analytics are functioning
- [ ] All pages render properly
