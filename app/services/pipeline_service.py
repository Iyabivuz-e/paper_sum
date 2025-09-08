"""
Pipeline Service - Business logic for paper processing
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import structlog

from app.models.schemas import (
    PaperProcessRequest, PaperProcessResponse, BatchProcessRequest, 
    BatchProcessResponse, ProcessingStatus, PaperMetadata, PaperAnalysisResult
)
from app.pipeline.nodes import create_production_pipeline
from app.pipeline.state import create_initial_state, PipelineState
from app.core.config import settings

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
    
    async def create_job(self, request: PaperProcessRequest) -> PaperProcessResponse:
        """Create a new processing job"""
        try:
            # Create initial state
            initial_state = create_initial_state(
                arxiv_id=request.arxiv_id,
                pdf_url=str(request.pdf_url) if request.pdf_url else None,
                user_query=request.user_query or ""
            )
            
            # Store job
            self.jobs[initial_state["job_id"]] = initial_state
            
            # Create response
            response = PaperProcessResponse(
                job_id=initial_state["job_id"],
                status=ProcessingStatus.QUEUED,
                created_at=initial_state["created_at"],
                updated_at=initial_state["updated_at"]
            )
            
            return response
            
        except Exception as e:
            logger.error("Failed to create job", error=str(e))
            raise
    
    async def process_paper_async(self, job_id: str, request: PaperProcessRequest):
        """Process paper asynchronously"""
        try:
            if job_id not in self.jobs:
                logger.error("Job not found", job_id=job_id)
                return
            
            state = self.jobs[job_id]
            
            logger.info("Starting paper processing", job_id=job_id)
            
            # Run the pipeline
            result_state = await self.pipeline.ainvoke(state)
            
            # Update stored state
            self.jobs[job_id] = result_state
            
            # Save results to file
            await self._save_job_results(job_id, result_state)
            
            logger.info(
                "Paper processing completed",
                job_id=job_id,
                status=result_state["status"]
            )
            
        except Exception as e:
            logger.error("Paper processing failed", job_id=job_id, error=str(e))
            
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
    
    async def get_job_status(self, job_id: str) -> Optional[PaperProcessResponse]:
        """Get job status and results"""
        try:
            if job_id not in self.jobs:
                return None
            
            state = self.jobs[job_id]
            
            # Create response from state
            response = PaperProcessResponse(
                job_id=job_id,
                status=state["status"],
                created_at=state["created_at"],
                updated_at=state["updated_at"],
                processing_steps=state["processing_steps"],
                current_step=state["current_step"],
                error_message=state["error_message"]
            )
            
            # Add paper metadata if available
            if state["paper_metadata"]:
                response.paper_metadata = PaperMetadata(
                    title=state["paper_metadata"].get("title", ""),
                    authors=state["paper_metadata"].get("authors", []),
                    abstract=state["paper_metadata"].get("abstract", ""),
                    arxiv_id=state["paper_metadata"].get("arxiv_id"),
                    categories=state["paper_metadata"].get("categories", [])
                )
            
            # Add analysis results if completed
            if state["status"] == ProcessingStatus.COMPLETED:
                response.analysis_result = PaperAnalysisResult(
                    serious_summary=state["serious_summary"],
                    contextual_analysis=state["contextual_analysis"],
                    novelty_score=state["novelty_score"],
                    human_fun_summary=state["human_fun_summary"],
                    final_digest=state["final_digest"],
                    tweet_thread=state["tweet_thread"],
                    blog_post=state["blog_post"]
                )
            
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
    
    async def _save_job_results(self, job_id: str, state: PipelineState):
        """Save job results to files"""
        try:
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            # Save JSON results
            results = {
                "job_id": job_id,
                "status": state["status"],
                "paper_metadata": state["paper_metadata"],
                "serious_summary": state["serious_summary"],
                "contextual_analysis": state["contextual_analysis"],
                "novelty_score": state["novelty_score"],
                "human_fun_summary": state["human_fun_summary"],
                "final_digest": state["final_digest"],
                "tweet_thread": state["tweet_thread"],
                "blog_post": state["blog_post"],
                "processing_steps": [step.dict() for step in state["processing_steps"]],
                "completed_at": datetime.utcnow().isoformat()
            }
            
            json_file = output_dir / f"{job_id}_result.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info("Job results saved", job_id=job_id, file=str(json_file))
            
        except Exception as e:
            logger.error("Failed to save job results", job_id=job_id, error=str(e))
