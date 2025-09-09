# 🚀 LaughGraph API Tutorial

## Quick Start Guide

### 1. Start the Server
```bash
cd /home/dio/Public/learning/paper_sum
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the APIs

## 📍 Method 1: Interactive API Documentation (EASIEST!)
Open in your browser: **http://localhost:8000/docs**

This gives you a beautiful interactive interface where you can:
- See all available endpoints
- Test them directly in the browser
- See request/response examples
- No coding required!

## 📍 Method 2: Command Line Testing

### Health Check
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-08T11:32:06.764033Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### System Metrics
```bash
curl http://localhost:8000/metrics
```

### List Jobs
```bash
curl http://localhost:8000/jobs
```

### Process a Paper - SIMPLIFIED! 🎉
```bash
# SUPER SIMPLE - Just provide arXiv ID
curl -X POST "http://localhost:8000/process-paper" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2310.06825"}'

# With custom question
curl -X POST "http://localhost:8000/process-paper" \
  -H "Content-Type: application/json" \
  -d '{
    "arxiv_id": "2310.06825",
    "user_query": "What are the main contributions?"
  }'

# Using PDF URL instead
curl -X POST "http://localhost:8000/process-paper" \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://arxiv.org/pdf/2310.06825.pdf"}'
```

### Check Job Status
```bash
# Replace JOB_ID with the actual job ID from previous response
curl http://localhost:8000/job-status/JOB_ID
```

## 📍 Method 3: Python Script Testing

Run the tutorial script:
```bash
python api_tutorial.py
```

## 🎯 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check if API is running |
| GET | `/metrics` | System performance metrics |
| GET | `/jobs` | List all processing jobs |
| POST | `/process-paper` | 🔥 **SIMPLE**: Process paper (just arXiv ID or PDF URL!) |
| POST | `/papers/process` | **Advanced**: Full control with all options |
| GET | `/job-status/{job_id}` | Check status of a specific job |
| POST | `/process-batch` | Process multiple papers at once |

## 🔥 How the Paper Processing Works - NOW SIMPLIFIED!

### **Super Simple Approach** (Recommended)
1. **Submit Paper**: POST to `/process-paper` with just `{"arxiv_id": "2310.06825"}`
2. **Get Job ID**: API returns a job ID immediately  
3. **Monitor Progress**: Use `/job-status/{job_id}` to track progress
4. **Get Results**: When status is "completed", full results are in the response

### **What You Need to Provide**
- **Required**: Either `arxiv_id` OR `pdf_url` (just one!)
- **Optional**: `user_query` (what you want to know about the paper)
- **That's it!** Everything else uses smart defaults.

### **Example Requests**
```json
// Minimal - just the paper ID
{"arxiv_id": "2310.06825"}

// With a specific question
{
  "arxiv_id": "2310.06825", 
  "user_query": "What are the main technical innovations?"
}

// Using PDF URL instead
{"pdf_url": "https://arxiv.org/pdf/2310.06825.pdf"}
```

## 📱 What Happens During Processing

Your paper goes through this 7-step AI pipeline:

1. **Ingestion** - Downloads paper from arXiv
2. **Parsing** - Extracts text from PDF
3. **RAG Processing** - Creates searchable vector database
4. **Summarization** - AI creates intelligent summary
5. **Contextualization** - Adds relevant context
6. **Novelty Analysis** - Identifies unique contributions
7. **Fun Generation** - Creates engaging insights

## 🎮 Real-Time Testing Tips

1. **Start Simple**: Always test `/health` first
2. **Use the Docs**: The `/docs` page is your best friend
3. **Check Logs**: Watch the terminal where the server runs
4. **Monitor Progress**: Use job status to see real-time updates
5. **Try Different Papers**: Use different arXiv IDs

## 🔧 Example arXiv IDs to Try

- `2310.06825` - AI/ML paper
- `2301.07041` - Language models
- `2208.11970` - Computer vision
- `2104.09864` - Research methodology

## 🚨 Troubleshooting

### Server Won't Start
```bash
# Kill any existing processes
pkill -f uvicorn
# Try different port
uv run uvicorn app.main:app --reload --port 8001
```

### API Not Responding
- Check if server is running: `curl http://localhost:8000/health`
- Check the terminal for error messages
- Make sure all environment variables are set in `.env`

### Processing Fails
- Check your OpenAI API key in `.env`
- Make sure you have internet connection
- Try a different arXiv ID

## 🎉 Success Indicators

✅ **Health endpoint returns 200**
✅ **Interactive docs load at `/docs`**
✅ **Can submit papers and get job IDs**
✅ **Job status updates show progress**
✅ **Completed jobs have full results**

---

**🌟 Pro Tip**: The interactive docs at `/docs` are the fastest way to understand and test your APIs. Start there!
