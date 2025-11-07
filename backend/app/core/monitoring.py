"""
Application monitoring and observability utilities.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor application performance metrics.
    """
    
    def __init__(self):
        self.metrics: Dict[str, list] = {
            'request_duration': [],
            'db_query_duration': [],
            'api_calls': [],
            'errors': [],
        }
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record API request metrics."""
        self.metrics['request_duration'].append({
            'endpoint': endpoint,
            'duration': duration,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Log slow requests
        if duration > 1.0:  # More than 1 second
            logger.warning(
                f"Slow request detected: {endpoint} took {duration:.2f}s"
            )
    
    def record_db_query(self, query: str, duration: float):
        """Record database query metrics."""
        self.metrics['db_query_duration'].append({
            'query': query[:100],  # Truncate long queries
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Log slow queries
        if duration > 0.5:  # More than 500ms
            logger.warning(
                f"Slow query detected: {query[:100]} took {duration:.2f}s"
            )
    
    def record_error(self, error_type: str, message: str, context: Optional[Dict] = None):
        """Record application errors."""
        self.metrics['errors'].append({
            'type': error_type,
            'message': message,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        logger.error(f"Error recorded: {error_type} - {message}", extra=context)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        return {
            'total_requests': len(self.metrics['request_duration']),
            'total_db_queries': len(self.metrics['db_query_duration']),
            'total_errors': len(self.metrics['errors']),
            'avg_request_duration': self._calculate_average('request_duration', 'duration'),
            'avg_db_query_duration': self._calculate_average('db_query_duration', 'duration'),
        }
    
    def _calculate_average(self, metric_key: str, field: str) -> float:
        """Calculate average for a metric field."""
        values = [m[field] for m in self.metrics[metric_key] if field in m]
        return sum(values) / len(values) if values else 0.0
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        for key in self.metrics:
            self.metrics[key].clear()


# Global monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(func):
    """
    Decorator to monitor function performance.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed in {duration:.3f}s"
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            performance_monitor.record_error(
                error_type=type(e).__name__,
                message=str(e),
                context={'function': func.__name__, 'duration': duration}
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed in {duration:.3f}s"
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            performance_monitor.record_error(
                error_type=type(e).__name__,
                message=str(e),
                context={'function': func.__name__, 'duration': duration}
            )
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


@contextmanager
def monitor_db_query(query: str):
    """
    Context manager to monitor database query performance.
    
    Usage:
        with monitor_db_query("SELECT * FROM patients"):
            # Execute query
            pass
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        performance_monitor.record_db_query(query, duration)


class HealthCheck:
    """
    Application health check utilities.
    """
    
    @staticmethod
    def check_database(db_session) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Simple query to test connection
            db_session.execute("SELECT 1")
            return {
                'status': 'healthy',
                'message': 'Database connection OK',
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
            }
    
    @staticmethod
    def check_disk_space() -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            free_percent = (free / total) * 100
            
            if free_percent < 10:
                status = 'unhealthy'
                message = f'Low disk space: {free_percent:.1f}% free'
            elif free_percent < 20:
                status = 'degraded'
                message = f'Disk space warning: {free_percent:.1f}% free'
            else:
                status = 'healthy'
                message = f'Disk space OK: {free_percent:.1f}% free'
            
            return {
                'status': status,
                'message': message,
                'free_gb': free // (2**30),
                'total_gb': total // (2**30),
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Could not check disk space: {str(e)}',
            }
    
    @staticmethod
    def check_memory() -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = 'unhealthy'
                message = f'High memory usage: {memory.percent:.1f}%'
            elif memory.percent > 80:
                status = 'degraded'
                message = f'Memory usage warning: {memory.percent:.1f}%'
            else:
                status = 'healthy'
                message = f'Memory usage OK: {memory.percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'used_percent': memory.percent,
                'available_gb': memory.available // (2**30),
            }
        except ImportError:
            return {
                'status': 'unknown',
                'message': 'psutil not installed',
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Could not check memory: {str(e)}',
            }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information."""
        try:
            import platform
            import psutil
            
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
            }
        except Exception as e:
            return {
                'error': f'Could not get system info: {str(e)}',
            }

