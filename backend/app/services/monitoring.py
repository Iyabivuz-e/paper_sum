"""
Monitoring and Metrics Collection Service
"""

import psutil
from datetime import datetime, timedelta
from typing import Dict, Any
import structlog

from models.schemas import SystemMetrics

logger = structlog.get_logger()


class MetricsCollector:
    """Collect and provide system metrics"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.job_stats = {
            "total_completed": 0,
            "total_failed": 0,
            "completed_today": 0,
            "failed_today": 0,
            "processing_times": []
        }
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Application metrics
            today = datetime.utcnow().date()
            
            return SystemMetrics(
                active_jobs=0,  # Would be populated from actual job tracking
                completed_jobs_today=self.job_stats["completed_today"],
                failed_jobs_today=self.job_stats["failed_today"],
                average_processing_time=self._calculate_avg_processing_time(),
                queue_length=0,  # Would be populated from actual queue
                memory_usage_mb=memory.used / 1024 / 1024,
                cpu_usage_percent=cpu_percent
            )
            
        except Exception as e:
            logger.error("Failed to collect metrics", error=str(e))
            return SystemMetrics(
                active_jobs=0,
                completed_jobs_today=0,
                failed_jobs_today=0,
                average_processing_time=0.0,
                queue_length=0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0
            )
    
    def record_job_completion(self, processing_time: float, success: bool = True):
        """Record job completion for metrics"""
        try:
            if success:
                self.job_stats["total_completed"] += 1
                self.job_stats["completed_today"] += 1
            else:
                self.job_stats["total_failed"] += 1
                self.job_stats["failed_today"] += 1
            
            self.job_stats["processing_times"].append(processing_time)
            
            # Keep only last 100 processing times
            if len(self.job_stats["processing_times"]) > 100:
                self.job_stats["processing_times"] = self.job_stats["processing_times"][-100:]
                
        except Exception as e:
            logger.error("Failed to record job completion", error=str(e))
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        if not self.job_stats["processing_times"]:
            return 0.0
        
        return sum(self.job_stats["processing_times"]) / len(self.job_stats["processing_times"])
