"""
Pydantic Models for API Request/Response
"""

from pydantic import BaseModel, Field, HttpUrl, validator, ConfigDict
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
import uuid


class ProcessingStatus(str, Enum):
    """Processing status enumeration"""
    QUEUED = "queued"
    INGESTING = "ingesting"
    PARSING = "parsing"
    RAG_PROCESSING = "rag_processing"
    SUMMARIZING = "summarizing"
    CONTEXTUALIZING = "contextualizing"
    NOVELTY_ANALYSIS = "novelty_analysis"
    HUMANIZING = "humanizing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputFormat(str, Enum):
    """Output format options"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TWEET_THREAD = "tweet_thread"
    BLOG_POST = "blog_post"


# Request Models
class PaperProcessRequest(BaseModel):
    """Request to process a research paper - simplified and user-friendly"""
    
    # Primary input - user only needs to provide ONE of these
    arxiv_id: Optional[str] = Field(
        None, 
        description="ArXiv paper ID (e.g., '2310.06825')",
        example="2310.06825"
    )
    pdf_url: Optional[Union[HttpUrl, str]] = Field(
        None, 
        description="Direct PDF URL or file path",
        example="https://arxiv.org/pdf/2310.06825.pdf"
    )
    pdf_file_path: Optional[str] = Field(
        None,
        description="Local file path for uploaded PDFs"
    )
    
    # Optional customization
    user_query: Optional[str] = Field(
        default="Provide a comprehensive analysis of this research paper", 
        description="Optional: Specific question or focus area for the analysis",
        example="What are the main contributions and how does this advance the field?"
    )
    
    # Advanced options (with sensible defaults)
    output_formats: List[OutputFormat] = Field(
        default=[OutputFormat.JSON], 
        description="Optional: Desired output formats (defaults to JSON)"
    )
    priority: int = Field(
        default=5, 
        ge=1, 
        le=10, 
        description="Optional: Processing priority (1=highest, 10=lowest, default=5)"
    )
    
    @validator('pdf_url')
    def validate_input_source(cls, v, values):
        """Ensure at least one input source is provided"""
        if not v and not values.get('arxiv_id'):
            raise ValueError("Either arxiv_id or pdf_url must be provided")
        return v


class BatchProcessRequest(BaseModel):
    """Request to process multiple papers"""
    papers: List[PaperProcessRequest] = Field(..., min_items=1, max_items=10)
    batch_name: Optional[str] = Field(None, description="Name for this batch")


# Response Models
class PaperMetadata(BaseModel):
    """Paper metadata"""
    title: str
    authors: List[str]
    abstract: str
    published_date: Optional[datetime]
    arxiv_id: Optional[str]
    pdf_url: Optional[str]
    categories: List[str] = []
    doi: Optional[str] = None


class ProcessingStep(BaseModel):
    """Individual processing step result"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    step_name: str
    status: ProcessingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class PaperAnalysisResult(BaseModel):
    """Complete analysis result for a paper"""
    # Core Analysis
    serious_summary: str = Field(..., description="Technical, academic summary")
    contextual_analysis: str = Field(..., description="How paper fits in research landscape")
    novelty_score: float = Field(..., ge=0.0, le=1.0, description="Novelty rating (0-1)")
    human_fun_summary: str = Field(..., description="Accessible, humorous explanation")
    
    # Synthesis
    final_digest: str = Field(..., description="Blended serious + fun perspective")
    tweet_thread: List[str] = Field(default=[], description="Social media thread")
    blog_post: str = Field(..., description="Long-form blog format")
    
    # Technical Details
    key_contributions: List[str] = []
    methodology: str = ""
    results_summary: str = ""
    limitations: List[str] = []
    future_work: str = ""


class PaperProcessResponse(BaseModel):
    """Response for paper processing"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    # Request Info
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ProcessingStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Paper Info
    paper_metadata: Optional[PaperMetadata] = None
    
    # Processing Info
    processing_steps: List[ProcessingStep] = []
    current_step: Optional[str] = None
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    estimated_completion: Optional[datetime] = None
    
    # Results
    analysis_result: Optional[PaperAnalysisResult] = None
    output_files: Dict[str, str] = Field(default={}, description="Generated file paths")
    
    # Error Handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Metadata
    processing_time_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None


class BatchProcessResponse(BaseModel):
    """Response for batch processing"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    batch_name: Optional[str] = None
    status: ProcessingStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    total_papers: int
    completed_papers: int = 0
    failed_papers: int = 0
    
    paper_jobs: List[str] = Field(default=[], description="Individual job IDs")
    results: List[PaperProcessResponse] = []


# Status and Health Models
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    environment: str
    dependencies: Dict[str, str] = {}


class SystemMetrics(BaseModel):
    """System metrics"""
    active_jobs: int
    completed_jobs_today: int
    failed_jobs_today: int
    average_processing_time: float
    queue_length: int
    memory_usage_mb: float
    cpu_usage_percent: float


# Error Models
class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "validation_error"
    message: str
    field_errors: List[Dict[str, Any]] = []
