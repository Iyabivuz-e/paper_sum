"""
Database service for analytics and feedback using Prisma
"""

from prisma import Prisma
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog

logger = structlog.get_logger()

class DatabaseService:
    """Service for database operations with Prisma"""
    
    def __init__(self):
        self.prisma = Prisma()
        self._connected = False
    
    async def connect(self):
        """Connect to database"""
        if not self._connected:
            await self.prisma.connect()
            self._connected = True
            logger.info("Database connected successfully")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._connected:
            await self.prisma.disconnect()
            self._connected = False
            logger.info("Database disconnected")
    
    async def ensure_connected(self):
        """Ensure database connection is active"""
        if not self._connected:
            await self.connect()
    
    async def submit_feedback(
        self,
        rating: str,
        comment: Optional[str] = None,
        paper_title: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit user feedback to database"""
        try:
            await self.ensure_connected()
            
            feedback = await self.prisma.paperfeedback.create(
                data={
                    'rating': rating,
                    'comment': comment,
                    'paperTitle': paper_title,
                    'arxivId': arxiv_id,
                    'sessionId': session_id,
                    'userAgent': user_agent,
                    'ipAddress': ip_address,
                }
            )
            
            logger.info(
                "Feedback submitted",
                feedback_id=feedback.id,
                rating=rating,
                paper_title=paper_title
            )
            
            return {
                "id": feedback.id,
                "rating": feedback.rating,
                "created_at": feedback.createdAt.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to submit feedback", error=str(e))
            raise
    
    async def log_paper_analytics(
        self,
        paper_title: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        novelty_score: Optional[float] = None,
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log paper analysis metrics"""
        try:
            await self.ensure_connected()
            
            analytics = await self.prisma.paperanalytics.create(
                data={
                    'paperTitle': paper_title,
                    'arxivId': arxiv_id,
                    'processingTimeMs': processing_time_ms,
                    'tokensUsed': tokens_used,
                    'noveltyScore': novelty_score,
                    'sessionId': session_id,
                    'userAgent': user_agent,
                    'ipAddress': ip_address,
                    'status': status,
                    'errorMessage': error_message,
                }
            )
            
            logger.info(
                "Analytics logged",
                analytics_id=analytics.id,
                paper_title=paper_title,
                status=status
            )
            
            return {
                "id": analytics.id,
                "status": analytics.status,
                "created_at": analytics.createdAt.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to log analytics", error=str(e))
            raise
    
    async def track_user_session(
        self,
        session_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        papers_analyzed_increment: int = 0,
        feedback_given_increment: int = 0
    ) -> Dict[str, Any]:
        """Track or update user session"""
        try:
            await self.ensure_connected()
            
            # Try to find existing session
            existing_session = await self.prisma.usersession.find_unique(
                where={'sessionId': session_id}
            )
            
            if existing_session:
                # Update existing session
                session = await self.prisma.usersession.update(
                    where={'sessionId': session_id},
                    data={
                        'papersAnalyzed': existing_session.papersAnalyzed + papers_analyzed_increment,
                        'feedbackGiven': existing_session.feedbackGiven + feedback_given_increment,
                        'lastActivity': datetime.utcnow(),
                    }
                )
            else:
                # Create new session
                session = await self.prisma.usersession.create(
                    data={
                        'sessionId': session_id,
                        'userAgent': user_agent,
                        'ipAddress': ip_address,
                        'papersAnalyzed': papers_analyzed_increment,
                        'feedbackGiven': feedback_given_increment,
                    }
                )
            
            logger.info(
                "Session tracked",
                session_id=session_id,
                papers_analyzed=session.papersAnalyzed,
                feedback_given=session.feedbackGiven
            )
            
            return {
                "session_id": session.sessionId,
                "papers_analyzed": session.papersAnalyzed,
                "feedback_given": session.feedbackGiven,
                "first_visit": session.firstVisit.isoformat(),
                "last_activity": session.lastActivity.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to track session", error=str(e))
            raise
    
    async def get_feedback_analytics(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get feedback analytics for dashboard"""
        try:
            await self.ensure_connected()
            
            # Calculate date threshold
            from datetime import timedelta
            threshold_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get feedback counts
            total_feedback = await self.prisma.paperfeedback.count(
                where={'createdAt': {'gte': threshold_date}}
            )
            
            positive_feedback = await self.prisma.paperfeedback.count(
                where={
                    'rating': 'positive',
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            negative_feedback = await self.prisma.paperfeedback.count(
                where={
                    'rating': 'negative',
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            # Get recent feedback with comments
            recent_feedback = await self.prisma.paperfeedback.find_many(
                where={
                    'comment': {'not': None},
                    'createdAt': {'gte': threshold_date}
                },
                order={'createdAt': 'desc'},
                take=10
            )
            
            satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
            
            return {
                "total_feedback": total_feedback,
                "positive_feedback": positive_feedback,
                "negative_feedback": negative_feedback,
                "satisfaction_rate": round(satisfaction_rate, 2),
                "recent_comments": [
                    {
                        "rating": fb.rating,
                        "comment": fb.comment,
                        "paper_title": fb.paperTitle,
                        "created_at": fb.createdAt.isoformat()
                    }
                    for fb in recent_feedback
                ],
                "period_days": days_back
            }
            
        except Exception as e:
            logger.error("Failed to get feedback analytics", error=str(e))
            raise
    
    async def get_usage_analytics(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get usage analytics for dashboard"""
        try:
            await self.ensure_connected()
            
            from datetime import timedelta
            threshold_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get paper analysis counts
            total_analyses = await self.prisma.paperanalytics.count(
                where={'createdAt': {'gte': threshold_date}}
            )
            
            successful_analyses = await self.prisma.paperanalytics.count(
                where={
                    'status': 'completed',
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            failed_analyses = await self.prisma.paperanalytics.count(
                where={
                    'status': 'failed',
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            # Get average processing time
            analytics_with_processing_time = await self.prisma.paperanalytics.find_many(
                where={
                    'status': 'completed',
                    'processingTimeMs': {'not': None},
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            avg_processing_time_ms = None
            if analytics_with_processing_time:
                total_time = sum(a.processingTimeMs for a in analytics_with_processing_time if a.processingTimeMs)
                avg_processing_time_ms = total_time / len(analytics_with_processing_time)
            
            # Get average novelty score
            analytics_with_novelty = await self.prisma.paperanalytics.find_many(
                where={
                    'status': 'completed',
                    'noveltyScore': {'not': None},
                    'createdAt': {'gte': threshold_date}
                }
            )
            
            avg_novelty_score_val = None
            if analytics_with_novelty:
                total_novelty = sum(a.noveltyScore for a in analytics_with_novelty if a.noveltyScore)
                avg_novelty_score_val = total_novelty / len(analytics_with_novelty)
            
            success_rate = (successful_analyses / total_analyses * 100) if total_analyses > 0 else 0
            
            return {
                "total_analyses": total_analyses,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": round(success_rate, 2),
                "avg_processing_time_ms": round(avg_processing_time_ms, 2) if avg_processing_time_ms else 0,
                "avg_novelty_score": round(avg_novelty_score_val, 3) if avg_novelty_score_val else 0,
                "period_days": days_back
            }
            
        except Exception as e:
            logger.error("Failed to get usage analytics", error=str(e))
            raise

# Global database service instance
db_service = DatabaseService()
