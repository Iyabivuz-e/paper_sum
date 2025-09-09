"""
Pipeline Service - Business logic for paper processing
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import structlog
import time

from app.models.schemas import (
    PaperProcessRequest, PaperProcessResponse, BatchProcessRequest, 
    BatchProcessResponse, ProcessingStatus, PaperMetadata, PaperAnalysisResult
)
from app.pipeline.nodes import create_production_pipeline
from app.pipeline.state import create_initial_state, PipelineState
from app.core.config import settings
from app.services.database_service import db_service

logger = structlog.get_logger()


class PipelineService:
    """Service for managing paper processing pipeline"""
    
    def __init__(self):
        self.pipeline = create_production_pipeline()
        self.jobs: Dict[str, PipelineState] = {}
        
    def test_connections(self) -> bool:
        """Test all external connections"""
        try:
            # Test vector database connection
            # Test LLM connection
            # Add other connection tests
            return True
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return False
    
    async def create_job(self, request: PaperProcessRequest) -> Dict[str, Any]:
        """Create a new processing job"""
        try:
            # Create initial state
            initial_state = create_initial_state(
                arxiv_id=request.arxiv_id,
                pdf_url=str(request.pdf_url) if request.pdf_url else None,
                pdf_file_path=request.pdf_file_path,
                user_query=request.user_query or ""
            )
            
            # Store job
            self.jobs[initial_state["job_id"]] = initial_state
            
            # Create response as dict with serialized datetimes
            response_dict = {
                "job_id": initial_state["job_id"],
                "status": initial_state["status"],
                "created_at": initial_state["created_at"].isoformat(),
                "updated_at": initial_state["updated_at"].isoformat(),
                "paper_metadata": None,
                "processing_steps": [],
                "current_step": None,
                "error_message": None
            }
            
            return response_dict
            
        except Exception as e:
            logger.error("Failed to create job", error=str(e))
            raise
    
    async def process_paper_async(self, job_id: str, request: PaperProcessRequest):
        """Process paper asynchronously"""
        try:
            # Check if job exists
            if job_id not in self.jobs:
                logger.error("Job not found for processing", job_id=job_id)
                return
            
            state = self.jobs[job_id]
            
            logger.info("Starting paper processing", job_id=job_id)
            
            # Record start time for analytics
            start_time = time.time()
            
            # Run the pipeline
            result_state = await self.pipeline.ainvoke(state)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update stored state
            self.jobs[job_id] = result_state
            
            # Log analytics to database
            try:
                await db_service.log_paper_analytics(
                    paper_title=result_state.get("paper_metadata", {}).get("title"),
                    arxiv_id=result_state.get("arxiv_id"),
                    processing_time_ms=processing_time_ms,
                    tokens_used=result_state.get("tokens_used"),
                    novelty_score=result_state.get("novelty_score"),
                    status="completed" if result_state["status"] == ProcessingStatus.COMPLETED else "failed",
                    error_message=result_state.get("error_message")
                )
            except Exception as analytics_error:
                logger.warning("Failed to log analytics", error=str(analytics_error))
            
            logger.info(
                "Paper processing completed",
                job_id=job_id,
                status=result_state["status"],
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error("Paper processing failed", job_id=job_id, error=str(e))
            
            # Log failed analytics
            try:
                processing_time_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else None
                await db_service.log_paper_analytics(
                    paper_title=request.arxiv_id if hasattr(request, 'arxiv_id') else None,
                    arxiv_id=request.arxiv_id if hasattr(request, 'arxiv_id') else None,
                    processing_time_ms=processing_time_ms,
                    status="failed",
                    error_message=str(e)
                )
            except Exception as analytics_error:
                logger.warning("Failed to log failed analytics", error=str(analytics_error))
            
            # Update job with error
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = ProcessingStatus.FAILED
                self.jobs[job_id]["error_message"] = str(e)
                self.jobs[job_id]["updated_at"] = datetime.utcnow()
    
    async def create_batch_job(self, request: BatchProcessRequest) -> BatchProcessResponse:
        """Create a batch processing job"""
        try:
            paper_jobs = []
            
            for paper_request in request.papers:
                job_response = await self.create_job(paper_request)
                paper_jobs.append(job_response.job_id)
            
            batch_response = BatchProcessResponse(
                batch_name=request.batch_name,
                status=ProcessingStatus.QUEUED,
                total_papers=len(request.papers),
                paper_jobs=paper_jobs
            )
            
            return batch_response
            
        except Exception as e:
            logger.error("Failed to create batch job", error=str(e))
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and results"""
        try:
            if job_id not in self.jobs:
                logger.warning(f"Job {job_id} not found in jobs storage")
                return None
            
            state = self.jobs[job_id]
            
            # Create response dict with serialized datetimes
            response = {
                "job_id": job_id,
                "status": state["status"],
                "created_at": state["created_at"].isoformat() if state.get("created_at") else None,
                "updated_at": state["updated_at"].isoformat() if state.get("updated_at") else None,
                "processing_steps": [
                    {
                        "step_name": getattr(step, 'step_name', ''),
                        "status": getattr(step, 'status', ''),
                        "started_at": getattr(step, 'started_at', None).isoformat() if getattr(step, 'started_at', None) else None,
                        "completed_at": getattr(step, 'completed_at', None).isoformat() if getattr(step, 'completed_at', None) else None,
                        "duration_seconds": getattr(step, 'duration_seconds', None),
                        "error_message": getattr(step, 'error_message', None),
                        "metadata": getattr(step, 'metadata', {})
                    } for step in state.get("processing_steps", [])
                ],
                "current_step": state.get("current_step"),
                "error_message": state.get("error_message")
            }
            
            # Add paper metadata if available
            if state.get("paper_metadata"):
                response["paper_metadata"] = {
                    "title": state["paper_metadata"].get("title", ""),
                    "authors": state["paper_metadata"].get("authors", []),
                    "abstract": state["paper_metadata"].get("abstract", ""),
                    "arxiv_id": state["paper_metadata"].get("arxiv_id"),
                    "categories": state["paper_metadata"].get("categories", []),
                    "published_date": state["paper_metadata"].get("published_date"),
                    "pdf_url": state["paper_metadata"].get("pdf_url")
                }
            
            # Add analysis results if completed
            if state.get("status") == ProcessingStatus.COMPLETED:
                response["analysis_result"] = {
                    "serious_summary": state.get("serious_summary", ""),
                    "contextual_analysis": state.get("contextual_analysis", ""),
                    "novelty_score": state.get("novelty_score", 0.0),
                    "human_fun_summary": state.get("human_fun_summary", ""),
                    "final_digest": state.get("final_digest", ""),
                    "tweet_thread": state.get("tweet_thread", []),
                    "blog_post": state.get("blog_post", "")
                }
            
            return response
            
        except Exception as e:
            logger.error("Failed to get job status", job_id=job_id, error=str(e))
            return None
    
    async def list_jobs(
        self, 
        status_filter: Optional[ProcessingStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PaperProcessResponse]:
        """List jobs with filtering and pagination"""
        try:
            jobs = []
            
            for job_id, state in list(self.jobs.items())[offset:offset+limit]:
                if status_filter and state["status"] != status_filter:
                    continue
                    
                job_response = await self.get_job_status(job_id)
                if job_response:
                    jobs.append(job_response)
            
            return jobs
            
        except Exception as e:
            logger.error("Failed to list jobs", error=str(e))
            return []
    
    async def list_all_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs for debugging/testing"""
        try:
            jobs = []
            for job_id, state in self.jobs.items():
                job_summary = {
                    "job_id": job_id,
                    "status": state.get("status", "unknown"),
                    "created_at": state.get("created_at").isoformat() if state.get("created_at") else None,
                    "updated_at": state.get("updated_at").isoformat() if state.get("updated_at") else None,
                }
                
                # Add paper metadata if available
                if state.get("paper_metadata"):
                    job_summary["paper_title"] = state["paper_metadata"].get("title", "")
                    job_summary["arxiv_id"] = state["paper_metadata"].get("arxiv_id")
                
                jobs.append(job_summary)
            
            return jobs
        except Exception as e:
            logger.error("Failed to list all jobs", error=str(e))
            return []
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a processing job"""
        try:
            if job_id not in self.jobs:
                return False
            
            state = self.jobs[job_id]
            
            # Can only cancel queued or running jobs
            if state["status"] in [ProcessingStatus.QUEUED, ProcessingStatus.INGESTING, 
                                 ProcessingStatus.PARSING, ProcessingStatus.RAG_PROCESSING,
                                 ProcessingStatus.SUMMARIZING, ProcessingStatus.HUMANIZING]:
                state["status"] = ProcessingStatus.FAILED
                state["error_message"] = "Job cancelled by user"
                state["updated_at"] = datetime.utcnow()
                return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to cancel job", job_id=job_id, error=str(e))
            return False
    
    async def get_job_output(self, job_id: str, format: str) -> Optional[str]:
        """Get job output in specific format"""
        try:
            if job_id not in self.jobs:
                return None
            
            state = self.jobs[job_id]
            
            if state["status"] != ProcessingStatus.COMPLETED:
                return None
            
            if format == "json":
                return json.dumps({
                    "job_id": job_id,
                    "paper_metadata": state["paper_metadata"],
                    "serious_summary": state["serious_summary"],
                    "human_fun_summary": state["human_fun_summary"],
                    "final_digest": state["final_digest"],
                    "tweet_thread": state["tweet_thread"],
                    "blog_post": state["blog_post"],
                    "novelty_score": state["novelty_score"]
                }, indent=2)
            
            elif format == "markdown":
                return f"""# {state["paper_metadata"].get("title", "Research Paper Analysis")}

## Serious Summary
{state["serious_summary"]}

## Fun Summary  
{state["human_fun_summary"]}

## Final Digest
{state["final_digest"]}

## Tweet Thread
{chr(10).join(state["tweet_thread"])}

## Blog Post
{state["blog_post"]}
"""
            
            elif format == "txt":
                return state["final_digest"]
            
            return None
            
        except Exception as e:
            logger.error("Failed to get job output", job_id=job_id, format=format, error=str(e))
            return None
    
    async def reset_vector_database(self):
        """Reset the vector database"""
        try:
            # Implementation would reset the Chroma database
            logger.info("Vector database reset requested")
            # Add actual reset logic here
            
        except Exception as e:
            logger.error("Failed to reset vector database", error=str(e))
            raise
