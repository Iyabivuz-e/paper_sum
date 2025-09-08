"""
FastAPI Application - Production-grade API for LaughGraph
"""

from app.pipeline.state import PipelineState
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
import time
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import redis
import json

from app.core.config import settings, get_settings
from app.models.schemas import (
    PaperProcessRequest, PaperProcessResponse, BatchProcessRequest, 
    BatchProcessResponse, HealthCheck, SystemMetrics, ErrorResponse,
    ProcessingStatus
)
from app.api.dependencies import get_redis_client, rate_limit_check
from app.services.pipeline_service import PipelineService
from app.services.monitoring import MetricsCollector
from app.utils import clean_response_for_json

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        min_level=20 if settings.log_level == "INFO" else 10  # Simple level mapping
    ),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production API for processing research papers with AI-powered analysis",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.debug else ["yourdomain.com", "*.yourdomain.com"]
)

# Global services
pipeline_service = PipelineService()
metrics_collector = MetricsCollector()

# In-memory job storage (in production, use Redis or database)
active_jobs: Dict[str, PipelineState] = {}


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
    )
    
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error("Unexpected error", error=str(exc), exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health and Monitoring Endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        pipeline_service.test_connections()
        
        return HealthCheck(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
            dependencies={
                "vector_db": "healthy",
                "llm_service": "healthy",
                "redis": "healthy" if settings.redis_url else "not_configured"
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get system metrics"""
    return await metrics_collector.get_system_metrics()


# Main API Endpoints

# Simple test endpoint to verify datetime serialization
@app.post("/test-simple")
async def test_simple():
    """Simple test endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/process-paper")
async def process_paper_simple(
    request: PaperProcessRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(rate_limit_check)
):
    """
    🚀 **SUPER SIMPLE**: Process a paper with minimal input!
    
    **Just provide ONE of these**:
    - **arxiv_id**: ArXiv paper ID (e.g., "2310.06825")  
    - **pdf_url**: Direct URL to PDF file
    
    **Optional**:
    - **user_query**: What you want to know about the paper
    
    **Example usage**:
    ```
    POST /process-paper
    {
        "arxiv_id": "2310.06825"
    }
    ```
    
    That's it! Everything else uses smart defaults.
    """
    try:
        # Validate input
        if not request.arxiv_id and not request.pdf_url:
            raise HTTPException(
                status_code=400, 
                detail="Please provide either 'arxiv_id' or 'pdf_url'"
            )
        
        # Create job
        job_response = await pipeline_service.create_job(request)
        
        # Store job for tracking (use the job_id from the dict)
        active_jobs[job_response["job_id"]] = job_response
        
        # Start background processing
        background_tasks.add_task(
            pipeline_service.process_paper_async,
            job_response["job_id"],
            request
        )
        
        logger.info(
            "Simple paper processing job created",
            job_id=job_response["job_id"],
            arxiv_id=request.arxiv_id,
            pdf_url=request.pdf_url
        )
        
        # Return the dict directly (already JSON serializable)
        return job_response
        
    except Exception as e:
        logger.error("Failed to create simple processing job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create processing job")


@app.post("/papers/process", response_model=PaperProcessResponse)
async def process_paper(
    request: PaperProcessRequest,
    background_tasks: BackgroundTasks,
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(rate_limit_check)
):
    """
    Process a single research paper - Simple and user-friendly!
    
    **Required** (provide ONE of these):
    - **arxiv_id**: ArXiv paper ID (e.g., "2310.06825") 
    - **pdf_url**: Direct URL to PDF file
    
    **Optional**:
    - **user_query**: Specific question or focus area (defaults to comprehensive analysis)
    - **output_formats**: Desired output formats (defaults to JSON)
    - **priority**: Processing priority 1-10 (defaults to 5)
    
    **Examples**:
    ```json
    {"arxiv_id": "2310.06825"}
    {"pdf_url": "https://arxiv.org/pdf/2310.06825.pdf"}
    {"arxiv_id": "2310.06825", "user_query": "What are the main contributions?"}
    ```
    """
    try:
        # Validate input
        if not request.arxiv_id and not request.pdf_url:
            raise HTTPException(
                status_code=400, 
                detail="Either arxiv_id or pdf_url must be provided"
            )
        
        # Create job
        job_response = await pipeline_service.create_job(request)
        
        # Store job for tracking
        active_jobs[job_response.job_id] = job_response
        
        # Start background processing
        background_tasks.add_task(
            pipeline_service.process_paper_async,
            job_response.job_id,
            request
        )
        
        logger.info(
            "Paper processing job created",
            job_id=job_response.job_id,
            arxiv_id=request.arxiv_id,
            pdf_url=request.pdf_url
        )
        
        return job_response
        
    except Exception as e:
        logger.error("Failed to create processing job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create processing job")


@app.post("/papers/batch", response_model=BatchProcessResponse)
async def process_batch(
    request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    _rate_limit = Depends(rate_limit_check)
):
    """
    Process multiple papers in batch
    
    - **papers**: List of paper processing requests (max 10)
    - **batch_name**: Optional name for the batch
    """
    try:
        if len(request.papers) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 papers per batch"
            )
        
        batch_response = await pipeline_service.create_batch_job(request)
        
        # Start background processing for each paper
        for paper_request in request.papers:
            background_tasks.add_task(
                pipeline_service.process_paper_async,
                paper_request.arxiv_id or str(paper_request.pdf_url),
                paper_request
            )
        
        logger.info(
            "Batch processing job created",
            batch_id=batch_response.batch_id,
            paper_count=len(request.papers)
        )
        
        return batch_response
        
    except Exception as e:
        logger.error("Failed to create batch job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create batch job")


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status and results of a processing job
    
    - **job_id**: The unique job identifier returned when submitting a paper
    """
    try:
        job = await pipeline_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Return the job directly (already serialized)
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/jobs", response_model=List[PaperProcessResponse])
async def list_jobs(
    status: Optional[ProcessingStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List processing jobs with optional filtering
    
    - **status**: Filter by processing status
    - **limit**: Maximum number of jobs to return (default: 50, max: 100)
    - **offset**: Number of jobs to skip (for pagination)
    """
    try:
        if limit > 100:
            limit = 100
            
        jobs = await pipeline_service.list_jobs(status, limit, offset)
        return jobs
        
    except Exception as e:
        logger.error("Failed to list jobs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list jobs")


@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a processing job
    
    - **job_id**: The unique job identifier
    """
    try:
        success = await pipeline_service.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
        
        return {"message": "Job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel job")


# File Download Endpoints
@app.get("/jobs/{job_id}/download/{format}")
async def download_result(job_id: str, format: str):
    """
    Download job results in specific format
    
    - **job_id**: The unique job identifier
    - **format**: Output format (json, markdown, html, txt)
    """
    try:
        file_content = await pipeline_service.get_job_output(job_id, format)
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download result", job_id=job_id, format=format, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to download result")


# Administrative Endpoints
@app.post("/admin/reset-vector-db")
async def reset_vector_database():
    """Reset the vector database (admin only)"""
    try:
        await pipeline_service.reset_vector_database()
        return {"message": "Vector database reset successfully"}
    except Exception as e:
        logger.error("Failed to reset vector database", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to reset vector database")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if not settings.debug else 1,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
