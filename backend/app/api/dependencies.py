"""
API Dependencies for FastAPI
"""

from fastapi import HTTPException, Request
import redis
import time
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()


# Redis client for caching and rate limiting
redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for caching and rate limiting (optional)"""
    global redis_client
    
    if not redis_client:
        try:
            redis_client = redis.from_url(settings.redis_url)
            redis_client.ping()  # Test connection
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning("Redis connection failed", error=str(e))
            return None  # Return None instead of failing
    
    return redis_client


# Rate limiting
async def rate_limit_check(request: Request):
    """Rate limiting check"""
    client_ip = request.client.host if request.client else "unknown"
    redis_conn = get_redis_client()
    
    if not redis_conn:
        return  # Skip rate limiting if Redis not available
    
    try:
        # Rate limiting key
        key = f"rate_limit:{client_ip}"
        current_time = int(time.time())
        window = settings.rate_limit_window
        
        # Sliding window rate limiting
        pipe = redis_conn.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window)
        
        results = pipe.execute()
        request_count = results[1]
        
        if request_count >= settings.rate_limit_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per {window} seconds."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Rate limiting error", error=str(e))
        # Continue without rate limiting on error
