"""
Mock API for Frontend Testing
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio

app = FastAPI(title="AI Paper Explainer API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
jobs: Dict[str, Dict[str, Any]] = {}

# Request/response models
class SummarizeRequest(BaseModel):
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None

class SummarizeResponse(BaseModel):
    job_id: str
    status: str

async def mock_processing(job_id: str, arxiv_id: str):
    """Simulate paper processing"""
    await asyncio.sleep(10)  # Simulate processing time
    
    # Mock results based on the new format
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "analysis_result": {
            "serious_summary": f"This paper (ArXiv: {arxiv_id}) introduces a novel approach to transformer architectures that significantly improves computational efficiency. The authors propose a sparse attention mechanism that reduces complexity from O(n²) to O(n log n) while maintaining comparable performance across multiple NLP benchmarks. Key innovations include dynamic attention patterns and adaptive computation allocation.",
            "novelty_score": 0.72
        },
        "human_fun_summary": """1. **Sparse Attention Magic**

**Serious:** The paper introduces sparse attention patterns that only focus on the most relevant tokens, reducing computational overhead.

**Fun:** Think of it like a speed-reader who's learned to skip boring parts and only read the juicy bits - same understanding, way faster!

**Friend's Take:** Basically these researchers said "what if we made AI less of a perfectionist?" and somehow it worked better! 😂

2. **Dynamic Resource Allocation**

**Serious:** The model dynamically allocates computational resources based on input complexity and attention requirements.

**Fun:** It's like having a smart assistant who knows when to put in full effort vs when to coast - working smarter, not harder!

**Friend's Take:** Your AI just learned to be efficiently lazy, and honestly, that's a mood 😴✨""",
        "paper_metadata": {
            "title": f"Efficient Transformer Architecture via Sparse Attention (ArXiv: {arxiv_id})",
            "authors": ["Dr. Smart Researcher", "Prof. AI Expert"],
            "arxiv_id": arxiv_id
        }
    }

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_paper(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks
):
    """Submit a paper for processing"""
    if not request.arxiv_id:
        raise HTTPException(status_code=400, detail="ArXiv ID is required")
    
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    # Start background processing
    background_tasks.add_task(mock_processing, job_id, request.arxiv_id)
    
    return SummarizeResponse(job_id=job_id, status="processing")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
