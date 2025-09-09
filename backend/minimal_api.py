"""
Minimal API to prevent 404 loops from frontend analytics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Minimal Paper API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check
@app.get("/")
async def root():
    return {"message": "Minimal Paper API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Analytics endpoints (minimal implementation)
class AnalyticsEvent(BaseModel):
    event_type: str
    action: str
    category: str
    label: Optional[str] = None
    value: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    page_path: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    screen_resolution: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/analytics/track")
async def track_analytics(event: AnalyticsEvent):
    """Accept analytics events and just log them (no storage)"""
    print(f"Analytics event: {event.action} - {event.category}")
    return {"status": "received", "event_id": "mock_id"}

@app.get("/analytics/dashboard")
async def analytics_dashboard():
    """Mock analytics dashboard"""
    return {
        "total_events": 0,
        "unique_users": 0,
        "page_views": 0,
        "top_pages": []
    }

# Basic paper endpoints (mock responses)
@app.post("/summarize")
async def summarize_paper():
    """Mock summarization endpoint"""
    return {
        "success": False,
        "message": "Paper summarization not available in minimal mode"
    }

@app.get("/papers")
async def list_papers():
    """Mock papers list"""
    return {"papers": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
