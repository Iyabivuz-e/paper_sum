from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from core.database import Base
from datetime import datetime

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # page_view, user_action, api_call, etc.
    event_action = Column(String(100), nullable=False)  # paper_upload, coffee_click, etc.
    event_category = Column(String(50), nullable=False)  # engagement, conversion, error, etc.
    event_label = Column(String(200))  # additional context
    event_value = Column(Float)  # numeric value (time, size, rating, etc.)
    
    # User identification
    user_id = Column(String(100))  # anonymous user ID
    session_id = Column(String(100), nullable=False)  # session identifier
    
    # Page context
    page_path = Column(String(500))  # current page URL
    page_title = Column(String(200))  # page title
    referrer = Column(String(500))  # referring page
    
    # Device/Browser info
    user_agent = Column(Text)  # full user agent string
    ip_address = Column(String(45))  # IP address (IPv4/IPv6)
    screen_resolution = Column(String(20))  # screen dimensions
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional data (JSON string)
    event_data = Column(Text)  # JSON string for extra data

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100))  # anonymous user ID
    
    # Session timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Session context
    landing_page = Column(String(500))  # first page visited
    exit_page = Column(String(500))  # last page visited
    page_views = Column(Integer, default=0)
    
    # Device info
    device_type = Column(String(20))  # desktop, mobile, tablet
    browser = Column(String(50))
    os = Column(String(50))
    country = Column(String(2))  # ISO country code
    city = Column(String(100))
    
    # Conversion tracking
    converted = Column(Boolean, default=False)  # completed main action
    conversion_value = Column(Float)  # value of conversion

class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # User metrics
    unique_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    
    # Engagement metrics
    page_views = Column(Integer, default=0)
    average_session_duration = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    
    # Conversion metrics
    paper_uploads = Column(Integer, default=0)
    successful_summaries = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Revenue metrics
    coffee_clicks = Column(Integer, default=0)
    donations_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Performance metrics
    average_load_time = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)

class PopularContent(Base):
    __tablename__ = "popular_content"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Content identification
    page_path = Column(String(500), nullable=False)
    page_title = Column(String(200))
    content_type = Column(String(50))  # page, paper, result, etc.
    
    # Metrics
    views = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    average_time_on_page = Column(Float, default=0.0)
    exit_rate = Column(Float, default=0.0)
    
    # Social/sharing
    shares = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
