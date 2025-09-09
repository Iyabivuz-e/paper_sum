from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.analytics import AnalyticsEvent, UserSession

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/track")
async def track_event(
    event_data: Dict,
    db: Session = Depends(get_db)
):
    """Track analytics events from frontend"""
    try:
        # Create analytics event record
        analytics_event = AnalyticsEvent(
            event_type=event_data.get("event_type"),
            event_action=event_data.get("action"),
            event_category=event_data.get("category"),
            event_label=event_data.get("label"),
            event_value=event_data.get("value"),
            user_id=event_data.get("user_id"),
            session_id=event_data.get("session_id"),
            page_path=event_data.get("page_path"),
            user_agent=event_data.get("user_agent"),
            ip_address=event_data.get("ip_address"),
            referrer=event_data.get("referrer"),
            timestamp=datetime.utcnow(),
            event_data=json.dumps(event_data.get("metadata", {}))
        )
        
        db.add(analytics_event)
        db.commit()
        
        return {"status": "success", "message": "Event tracked"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get real analytics data for dashboard"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get real data from database
        events = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.timestamp >= start_date,
            AnalyticsEvent.timestamp <= end_date
        ).all()
        
        # Process real analytics data
        analytics_data = {
            "dailyUsers": get_daily_users(events),
            "totalSessions": get_total_sessions(events),
            "averageSessionTime": get_average_session_time(events),
            "topCountries": get_top_countries(events),
            "deviceTypes": get_device_types(events),
            "popularPages": get_popular_pages(events),
            "conversionRate": get_conversion_rate(events),
            "errorRate": get_error_rate(events),
            "averageLoadTime": get_average_load_time(events),
            "paperUploads": get_paper_uploads(events),
            "coffeeClicks": get_coffee_clicks(events),
            "feedbackData": get_feedback_data(events),
            "realTimeUsers": get_real_time_users(db),
            "hourlyData": get_hourly_data(events),
            "conversionFunnel": get_conversion_funnel(events)
        }
        
        return analytics_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

def get_daily_users(events: List[AnalyticsEvent]) -> int:
    """Count unique users in the time period"""
    unique_users = set()
    for event in events:
        if event.user_id:
            unique_users.add(event.user_id)
        elif event.session_id:
            unique_users.add(event.session_id)
    return len(unique_users)

def get_total_sessions(events: List[AnalyticsEvent]) -> int:
    """Count total sessions"""
    unique_sessions = set()
    for event in events:
        if event.session_id:
            unique_sessions.add(event.session_id)
    return len(unique_sessions)

def get_average_session_time(events: List[AnalyticsEvent]) -> str:
    """Calculate average session duration"""
    session_times = {}
    
    for event in events:
        if event.session_id:
            if event.session_id not in session_times:
                session_times[event.session_id] = {"start": event.timestamp, "end": event.timestamp}
            else:
                if event.timestamp < session_times[event.session_id]["start"]:
                    session_times[event.session_id]["start"] = event.timestamp
                if event.timestamp > session_times[event.session_id]["end"]:
                    session_times[event.session_id]["end"] = event.timestamp
    
    total_duration = 0
    session_count = 0
    
    for session_data in session_times.values():
        duration = (session_data["end"] - session_data["start"]).total_seconds()
        if duration > 0:  # Only count sessions with actual duration
            total_duration += duration
            session_count += 1
    
    if session_count > 0:
        avg_seconds = total_duration / session_count
        minutes = int(avg_seconds // 60)
        seconds = int(avg_seconds % 60)
        return f"{minutes}m {seconds}s"
    
    return "0m 0s"

def get_top_countries(events: List[AnalyticsEvent]) -> List[Dict]:
    """Get top countries from IP geolocation"""
    # This would require IP geolocation service
    # For now, return sample data based on actual events
    countries = {}
    for event in events:
        # You'd use a GeoIP service here to get country from IP
        # For demo, we'll extract from event_data if available
        if event.event_data:
            try:
                event_metadata = json.loads(event.event_data)
                country = event_metadata.get("country", "Unknown")
                countries[country] = countries.get(country, 0) + 1
            except:
                countries["Unknown"] = countries.get("Unknown", 0) + 1
    
    # Convert to list format
    return [{"country": k, "users": v} for k, v in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]]

def get_device_types(events: List[AnalyticsEvent]) -> List[Dict]:
    """Analyze device types from user agents"""
    devices = {"Desktop": 0, "Mobile": 0, "Tablet": 0}
    
    for event in events:
        if event.user_agent:
            user_agent = event.user_agent.lower()
            if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
                devices["Mobile"] += 1
            elif "tablet" in user_agent or "ipad" in user_agent:
                devices["Tablet"] += 1
            else:
                devices["Desktop"] += 1
    
    total = sum(devices.values())
    if total == 0:
        return [{"type": "Desktop", "percentage": 100}]
    
    return [{"type": k, "percentage": round((v / total) * 100, 1)} for k, v in devices.items()]

def get_popular_pages(events: List[AnalyticsEvent]) -> List[Dict]:
    """Get most visited pages"""
    pages = {}
    for event in events:
        if event.page_path and event.event_type == "page_view":
            pages[event.page_path] = pages.get(event.page_path, 0) + 1
    
    return [{"page": k, "views": v} for k, v in sorted(pages.items(), key=lambda x: x[1], reverse=True)[:10]]

def get_conversion_rate(events: List[AnalyticsEvent]) -> float:
    """Calculate upload to success conversion rate"""
    uploads = len([e for e in events if e.event_action == "paper_upload"])
    successes = len([e for e in events if e.event_action == "summary_generated"])
    
    if uploads == 0:
        return 0.0
    
    return round((successes / uploads) * 100, 1)

def get_error_rate(events: List[AnalyticsEvent]) -> float:
    """Calculate error rate"""
    total_requests = len([e for e in events if e.event_category in ["api_call", "paper_processing"]])
    errors = len([e for e in events if e.event_category == "error"])
    
    if total_requests == 0:
        return 0.0
    
    return round((errors / total_requests) * 100, 1)

def get_average_load_time(events: List[AnalyticsEvent]) -> float:
    """Calculate average page load time"""
    load_times = []
    for event in events:
        if event.event_action == "page_load" and event.event_value:
            load_times.append(event.event_value)
    
    if not load_times:
        return 0.0
    
    return round(sum(load_times) / len(load_times) / 1000, 1)  # Convert to seconds

def get_paper_uploads(events: List[AnalyticsEvent]) -> int:
    """Count paper uploads"""
    return len([e for e in events if e.event_action == "paper_upload"])

def get_coffee_clicks(events: List[AnalyticsEvent]) -> int:
    """Count coffee button clicks"""
    return len([e for e in events if e.event_action == "coffee_support"])

def get_feedback_data(events: List[AnalyticsEvent]) -> Dict:
    """Analyze feedback data"""
    feedback_events = [e for e in events if e.event_action == "feedback_submitted"]
    
    if not feedback_events:
        return {"average_rating": 0, "total_feedback": 0}
    
    ratings = [e.event_value for e in feedback_events if e.event_value]
    
    return {
        "average_rating": round(sum(ratings) / len(ratings), 1) if ratings else 0,
        "total_feedback": len(feedback_events)
    }

def get_real_time_users(db: Session) -> int:
    """Count users active in last 5 minutes"""
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    recent_events = db.query(AnalyticsEvent).filter(
        AnalyticsEvent.timestamp >= five_minutes_ago
    ).all()
    
    unique_users = set()
    for event in recent_events:
        if event.session_id:
            unique_users.add(event.session_id)
    
    return len(unique_users)

def get_hourly_data(events: List[AnalyticsEvent]) -> List[Dict]:
    """Get hourly activity data"""
    hourly_counts = {}
    
    for event in events:
        hour = event.timestamp.hour
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    return [{"hour": h, "count": hourly_counts.get(h, 0)} for h in range(24)]

def get_conversion_funnel(events: List[AnalyticsEvent]) -> Dict:
    """Track conversion funnel steps"""
    funnel_steps = {
        "visits": len([e for e in events if e.event_type == "page_view"]),
        "uploads": len([e for e in events if e.event_action == "paper_upload"]),
        "processing": len([e for e in events if e.event_action == "processing_started"]),
        "completed": len([e for e in events if e.event_action == "summary_generated"]),
        "downloaded": len([e for e in events if e.event_action == "content_download"])
    }
    
    return funnel_steps
