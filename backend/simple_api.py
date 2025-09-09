"""
Simplified API for Frontend Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Import our existing pipeline service
from app.services.pipeline_service import PipelineService
from app.models.schemas import PaperProcessRequest

app = FastAPI(title="AI Paper Explainer API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline service
pipeline_service = PipelineService()

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
        
        # Start background processing
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
