"""
Structured logging configuration for MediFlow Lite.

Provides:
- Request ID tracking
- Structured JSON logging
- Security event logging
- Audit trail logging
- Performance monitoring
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
from pathlib import Path

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'user_email'):
            log_data['user_email'] = record.user_email
        if hasattr(record, 'user_role'):
            log_data['user_role'] = record.user_role
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        if hasattr(record, 'event_type'):
            log_data['event_type'] = record.event_type
        if hasattr(record, 'resource_type'):
            log_data['resource_type'] = record.resource_type
        if hasattr(record, 'resource_id'):
            log_data['resource_id'] = record.resource_id
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add stack trace if present
        if record.stack_info:
            log_data['stack_trace'] = self.formatStack(record.stack_info)
        
        return json.dumps(log_data)


class SecurityLogger:
    """
    Specialized logger for security events.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('mediflow.security')
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ):
        """Log login attempt."""
        extra = {
            'event_type': 'login_attempt',
            'user_email': email,
            'ip_address': ip_address,
            'success': success,
        }
        if user_agent:
            extra['user_agent'] = user_agent
        if failure_reason:
            extra['failure_reason'] = failure_reason
        
        if success:
            self.logger.info(f"Successful login: {email}", extra=extra)
        else:
            self.logger.warning(f"Failed login attempt: {email}", extra=extra)
    
    def log_logout(self, user_id: int, email: str):
        """Log user logout."""
        self.logger.info(
            f"User logout: {email}",
            extra={
                'event_type': 'logout',
                'user_id': user_id,
                'user_email': email,
            }
        )
    
    def log_account_lockout(self, email: str, ip_address: str):
        """Log account lockout."""
        self.logger.warning(
            f"Account locked due to failed login attempts: {email}",
            extra={
                'event_type': 'account_lockout',
                'user_email': email,
                'ip_address': ip_address,
            }
        )
    
    def log_password_change(self, user_id: int, email: str):
        """Log password change."""
        self.logger.info(
            f"Password changed: {email}",
            extra={
                'event_type': 'password_change',
                'user_id': user_id,
                'user_email': email,
            }
        )
    
    def log_permission_denied(
        self,
        user_id: int,
        email: str,
        role: str,
        endpoint: str,
        required_permission: str
    ):
        """Log permission denied."""
        self.logger.warning(
            f"Permission denied: {email} tried to access {endpoint}",
            extra={
                'event_type': 'permission_denied',
                'user_id': user_id,
                'user_email': email,
                'user_role': role,
                'endpoint': endpoint,
                'required_permission': required_permission,
            }
        )
    
    def log_suspicious_activity(
        self,
        description: str,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log suspicious activity."""
        extra = {
            'event_type': 'suspicious_activity',
            'description': description,
        }
        if user_id:
            extra['user_id'] = user_id
        if email:
            extra['user_email'] = email
        if ip_address:
            extra['ip_address'] = ip_address
        if details:
            extra.update(details)
        
        self.logger.error(f"Suspicious activity: {description}", extra=extra)


class AuditLogger:
    """
    Specialized logger for audit trail.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('mediflow.audit')
    
    def log_create(
        self,
        user_id: int,
        user_email: str,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log resource creation."""
        extra = {
            'event_type': 'create',
            'user_id': user_id,
            'user_email': user_email,
            'resource_type': resource_type,
            'resource_id': str(resource_id),
            'action': 'CREATE',
        }
        if details:
            extra['details'] = details
        
        self.logger.info(
            f"Created {resource_type} #{resource_id} by {user_email}",
            extra=extra
        )
    
    def log_update(
        self,
        user_id: int,
        user_email: str,
        resource_type: str,
        resource_id: Any,
        changes: Optional[Dict[str, Any]] = None
    ):
        """Log resource update."""
        extra = {
            'event_type': 'update',
            'user_id': user_id,
            'user_email': user_email,
            'resource_type': resource_type,
            'resource_id': str(resource_id),
            'action': 'UPDATE',
        }
        if changes:
            extra['changes'] = changes
        
        self.logger.info(
            f"Updated {resource_type} #{resource_id} by {user_email}",
            extra=extra
        )
    
    def log_delete(
        self,
        user_id: int,
        user_email: str,
        resource_type: str,
        resource_id: Any
    ):
        """Log resource deletion."""
        self.logger.warning(
            f"Deleted {resource_type} #{resource_id} by {user_email}",
            extra={
                'event_type': 'delete',
                'user_id': user_id,
                'user_email': user_email,
                'resource_type': resource_type,
                'resource_id': str(resource_id),
                'action': 'DELETE',
            }
        )
    
    def log_access(
        self,
        user_id: int,
        user_email: str,
        resource_type: str,
        resource_id: Any,
        action: str = 'READ'
    ):
        """Log resource access."""
        self.logger.info(
            f"Accessed {resource_type} #{resource_id} by {user_email}",
            extra={
                'event_type': 'access',
                'user_id': user_id,
                'user_email': user_email,
                'resource_type': resource_type,
                'resource_id': str(resource_id),
                'action': action,
            }
        )


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs to stdout only.
    """
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with structured formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    logging.getLogger('mediflow').setLevel(getattr(logging, log_level.upper()))
    logging.getLogger('mediflow.security').setLevel(logging.INFO)
    logging.getLogger('mediflow.audit').setLevel(logging.INFO)
    
    # Reduce noise from third-party libraries
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


# Global logger instances
security_logger = SecurityLogger()
audit_logger = AuditLogger()

