# Render Deployment Checklist

## Pre-Deployment Tests ✅
- [x] Docker build successful
- [x] Health endpoint working (200 OK)
- [x] Analytics endpoints working
- [x] PostgreSQL connection working
- [x] Port 8001 properly configured
- [x] FastAPI docs accessible

## Render Deployment Steps

### 1. Environment Variables to Set on Render:
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://username:password@host:port (optional)
```

### 2. Database Setup:
- [ ] Create PostgreSQL database on Render or external provider
- [ ] Update DATABASE_URL with production credentials
- [ ] Run Prisma migrations: `prisma migrate deploy`

### 3. Deployment Configuration:
- [ ] Repository connected to Render
- [ ] Build uses `Dockerfile.api`
- [ ] Port set to 8001
- [ ] Health check endpoint: `/health`

### 4. Post-Deployment Verification:
- [ ] Health endpoint responds 200 OK
- [ ] Analytics endpoints working
- [ ] CORS configured for frontend domain
- [ ] All environment variables properly set

## Expected Render Service URL:
`https://paper-summarizer-backend-[random].onrender.com`

## Frontend Environment Variable Update:
Update Vercel with: `NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.onrender.com`

## Troubleshooting:
- If 400 errors: Check environment variables
- If database errors: Verify DATABASE_URL and run migrations
- If port errors: Ensure PORT=8001 in environment
- If psycopg2 errors: Dockerfile.api includes proper PostgreSQL dependencies
