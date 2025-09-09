"""
Production API for Frontend Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import tempfile
import os
import uuid

# Import the real pipeline service
from app.services.pipeline_service import PipelineService
from app.services.database_service import db_service
from app.models.schemas import PaperProcessRequest

app = FastAPI(title="AI Paper Explainer API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db_service.disconnect()

# Initialize the real pipeline service
pipeline_service = PipelineService()

# Simplified request/response models for frontend
class SummarizeRequest(BaseModel):
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None

class SummarizeResponse(BaseModel):
    job_id: str
    status: str

class FeedbackRequest(BaseModel):
    rating: str  # 'positive' or 'negative'
    comment: Optional[str] = None
    paper_info: dict
    timestamp: Optional[str] = None

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_paper_multipart(
    background_tasks: BackgroundTasks,
    arxiv_id: Optional[str] = Form(None),
    pdf_url: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None)
):
    """Submit a paper for processing (multipart/form-data for file uploads)"""
    try:
        # Validate that at least one input is provided
        if not arxiv_id and not pdf_url and not pdf_file:
            raise HTTPException(
                status_code=400, 
                detail="Must provide either arxiv_id, pdf_url, or pdf_file"
            )
        
        # Handle PDF file upload
        if pdf_file:
            if not pdf_file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="File must be a PDF"
                )
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await pdf_file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Convert to internal request format
            paper_request = PaperProcessRequest(
                pdf_file_path=temp_file_path  # Use the new field for file paths
            )
        else:
            # Convert to internal request format
            paper_request = PaperProcessRequest(
                arxiv_id=arxiv_id,
                pdf_url=pdf_url
            )
        
        # Create job using real pipeline
        job_response = await pipeline_service.create_job(paper_request)
        
        # Start background processing with real pipeline
        background_tasks.add_task(
            pipeline_service.process_paper_async,
            job_response["job_id"],
            paper_request
        )
        
        return SummarizeResponse(
            job_id=job_response["job_id"],
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.post("/api/summarize-json", response_model=SummarizeResponse)  
async def summarize_paper_json(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks
):
    """Submit a paper for processing (JSON for URL/ID inputs)"""
    try:
        # Convert to internal request format
        paper_request = PaperProcessRequest(
            arxiv_id=request.arxiv_id,
            pdf_url=request.pdf_url
        )
        
        # Create job using real pipeline
        job_response = await pipeline_service.create_job(paper_request)
        
        # Start background processing with real pipeline
        background_tasks.add_task(
            pipeline_service.process_paper_async,
            job_response["job_id"],
            paper_request
        )
        
        return SummarizeResponse(
            job_id=job_response["job_id"],
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results from real pipeline"""
    try:
        job_data = await pipeline_service.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/jobs/")
async def list_all_jobs():
    """List all jobs - for debugging/testing"""
    try:
        jobs = await pipeline_service.list_all_jobs()
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest, request: Request):
    """Submit user feedback about the analysis"""
    try:
        # Extract request metadata
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None
        
        # Generate session ID if not provided (you can enhance this with proper session management)
        session_id = request.headers.get("x-session-id") or str(uuid.uuid4())
        
        # Submit to database
        result = await db_service.submit_feedback(
            rating=feedback.rating,
            comment=feedback.comment,
            paper_title=feedback.paper_info.get("title"),
            arxiv_id=feedback.paper_info.get("arxivId"),
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Track session activity
        await db_service.track_user_session(
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address,
            feedback_given_increment=1
        )
        
        return {
            "status": "success", 
            "message": "Feedback received",
            "feedback_id": result["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.get("/api/analytics/feedback")
async def get_feedback_analytics(days: int = 30):
    """Get feedback analytics for dashboard"""
    try:
        analytics = await db_service.get_feedback_analytics(days_back=days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback analytics: {str(e)}")

@app.get("/api/analytics/usage")
async def get_usage_analytics(days: int = 30):
    """Get usage analytics for dashboard"""
    try:
        analytics = await db_service.get_usage_analytics(days_back=days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Paper Explainer API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
