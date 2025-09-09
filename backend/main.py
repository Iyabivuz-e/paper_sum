"""
Simplified API for Frontend Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Import our existing pipeline service with fallback for Docker environment
try:
    # Try Docker-style imports first (when running from /app)
    from services.pipeline_service import PipelineService
    from services.database_service import DatabaseService
    from models.schemas import PaperProcessRequest
except ImportError:
    # Fallback to local development imports
    from app.services.pipeline_service import PipelineService
    from app.services.database_service import DatabaseService
    from app.models.schemas import PaperProcessRequest

app = FastAPI(title="AI Paper Explainer API", version="1.0.0")

# Enable CORS for frontend (development and production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "https://paper-sum.vercel.app",  # Production frontend
        "https://paper-sum-*.vercel.app",  # Vercel preview deployments
        "https://*.vercel.app"  # Allow all Vercel domains for flexibility
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pipeline_service = PipelineService()
db_service = DatabaseService()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup - non-blocking"""
    try:
        await db_service.connect()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("🚀 Server will continue without database - some features may be limited")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db_service.disconnect()

# Request/response models
class SummarizeRequest(BaseModel):
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None

class SummarizeResponse(BaseModel):
    job_id: str
    status: str

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_paper(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks
):
    """Submit a paper for processing"""
    try:
        # Convert to internal request format
        paper_request = PaperProcessRequest(
            arxiv_id=request.arxiv_id,
            pdf_url=request.pdf_url
        )
        
        # Create job
        job_response = await pipeline_service.create_job(paper_request)
        
        # Start background processing and analytics tracking
        background_tasks.add_task(
            process_paper_with_analytics,
            job_response["job_id"],
            paper_request
        )
        
        return SummarizeResponse(
            job_id=job_response["job_id"],
            status="processing"
        )
        
    except Exception as e:
        # Track failed request
        background_tasks.add_task(
            track_analytics_async,
            None,
            request.arxiv_id,
            None,
            None,
            None,
            "failed",
            str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")


async def process_paper_with_analytics(job_id: str, paper_request: PaperProcessRequest):
    """Process paper and track analytics"""
    start_time = datetime.now()
    
    try:
        # Process the paper
        await pipeline_service.process_paper_async(job_id, paper_request)
        
        # Get job results for analytics
        job_data = await pipeline_service.get_job_status(job_id)
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Track successful analytics
        await track_analytics_async(
            job_data.get('result', {}).get('title'),
            paper_request.arxiv_id,
            processing_time,
            job_data.get('result', {}).get('tokens_used'),
            job_data.get('result', {}).get('novelty_score'),
            "completed",
            None
        )
        
    except Exception as e:
        # Calculate processing time even for failures
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Track failed analytics
        await track_analytics_async(
            None,
            paper_request.arxiv_id,
            processing_time,
            None,
            None,
            "failed",
            str(e)
        )


async def track_analytics_async(
    paper_title: Optional[str],
    arxiv_id: Optional[str],
    processing_time_ms: Optional[int],
    tokens_used: Optional[int],
    novelty_score: Optional[float],
    status: str,
    error_message: Optional[str]
):
    """Track analytics asynchronously"""
    try:
        await db_service.log_paper_analytics(
            paper_title=paper_title,
            arxiv_id=arxiv_id,
            processing_time_ms=processing_time_ms,
            tokens_used=tokens_used,
            novelty_score=novelty_score,
            status=status,
            error_message=error_message
        )
    except Exception as e:
        print(f"Failed to track analytics: {e}")  # Log but don't fail the main process


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results"""
    try:
        job_data = await pipeline_service.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
async def root():
    """Root endpoint to verify server is running"""
    return {
        "message": "AI Paper Summarizer API is running!", 
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "summarize": "/api/summarize",
            "status": "/api/status/{job_id}"
        }
    }


@app.post("/analytics/track")
async def track_analytics(data: Dict[str, Any]):
    """Accept analytics data to prevent 404 errors"""
    # Just accept and ignore the data
    return {"status": "ok"}


@app.post("/api/feedback")
async def submit_feedback(data: Dict[str, Any]):
    """Accept and store feedback data"""
    try:
        await db_service.submit_feedback(
            rating=data.get('rating', 'positive'),
            comment=data.get('comment'),
            paper_title=data.get('paperTitle'),
            arxiv_id=data.get('arxivId'),
            session_id=data.get('sessionId'),
            user_agent=data.get('userAgent'),
            ip_address=data.get('ipAddress')
        )
        return {"status": "ok", "message": "Feedback stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store feedback: {str(e)}")


@app.get("/api/analytics/feedback")
async def get_feedback_analytics(days: int = 30):
    """Get real feedback analytics from database"""
    try:
        analytics_data = await db_service.get_feedback_analytics(days_back=days)
        return analytics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback analytics: {str(e)}")


@app.get("/api/analytics/usage")
async def get_usage_analytics(days: int = 30):
    """Get real usage analytics from database"""
    try:
        analytics_data = await db_service.get_usage_analytics(days_back=days)
        return analytics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8001))  
    uvicorn.run(app, host="0.0.0.0", port=port)
