"""
Pipeline State Management for LangGraph
"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import ProcessingStatus, ProcessingStep


class PipelineState(TypedDict):
    """State passed between pipeline nodes"""
    
    # Job Management
    job_id: str
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    
    # Input Parameters
    arxiv_id: Optional[str]
    pdf_url: Optional[str]
    user_query: str
    
    # Paper Data
    paper_metadata: Dict[str, Any]
    pdf_path: Optional[str]
    paper_content: str
    
    # Processing Data
    text_chunks: List[str]
    chunk_ids: List[str]
    retrieved_context: List[str]
    
    # Analysis Results
    serious_summary: str
    contextual_analysis: str
    novelty_score: float
    novelty_analysis: str
    human_fun_summary: str
    
    # Output
    final_digest: str
    tweet_thread: List[str]
    blog_post: str
    
    # Processing Metadata
    processing_steps: List[ProcessingStep]
    current_step: Optional[str]
    error_message: Optional[str]
    
    # Performance Metrics
    tokens_used: Optional[int]
    processing_time_seconds: Optional[float]


def create_initial_state(
    arxiv_id: Optional[str] = None,
    pdf_url: Optional[str] = None,
    user_query: str = "",
    job_id: Optional[str] = None
) -> PipelineState:
    """Create initial pipeline state"""
    
    if not job_id:
        job_id = str(uuid.uuid4())
    
    now = datetime.utcnow()
    
    return PipelineState(
        # Job Management
        job_id=job_id,
        status=ProcessingStatus.QUEUED,
        created_at=now,
        updated_at=now,
        
        # Input Parameters
        arxiv_id=arxiv_id,
        pdf_url=pdf_url,
        user_query=user_query,
        
        # Paper Data
        paper_metadata={},
        pdf_path=None,
        paper_content="",
        
        # Processing Data
        text_chunks=[],
        chunk_ids=[],
        retrieved_context=[],
        
        # Analysis Results
        serious_summary="",
        contextual_analysis="",
        novelty_score=0.0,
        novelty_analysis="",
        human_fun_summary="",
        
        # Output
        final_digest="",
        tweet_thread=[],
        blog_post="",
        
        # Processing Metadata
        processing_steps=[],
        current_step=None,
        error_message=None,
        
        # Performance Metrics
        tokens_used=None,
        processing_time_seconds=None
    )
