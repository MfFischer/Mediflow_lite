"""
Input sanitization utilities to prevent XSS and injection attacks.
"""
import re
import html
from typing import Any, Dict, List, Union


class InputSanitizer:
    """
    Sanitize user input to prevent XSS and injection attacks.
    """
    
    # Patterns for detecting malicious input
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers like onclick=
        r'<iframe',
        r'<object',
        r'<embed',
        r'<applet',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*--)",
    ]
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """
        Escape HTML special characters to prevent XSS.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text with HTML entities escaped
        """
        if not text:
            return text
        return html.escape(text)
    
    @classmethod
    def detect_xss(cls, text: str) -> bool:
        """
        Detect potential XSS attempts.
        
        Args:
            text: Input text to check
            
        Returns:
            True if XSS pattern detected
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def detect_sql_injection(cls, text: str) -> bool:
        """
        Detect potential SQL injection attempts.
        
        Args:
            text: Input text to check
            
        Returns:
            True if SQL injection pattern detected
        """
        if not text:
            return False
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def sanitize_string(cls, text: str, max_length: int = None) -> str:
        """
        Sanitize a string input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValueError: If malicious content detected
        """
        if not text:
            return text
        
        # Check for XSS
        if cls.detect_xss(text):
            raise ValueError("Potential XSS attack detected")
        
        # Check for SQL injection
        if cls.detect_sql_injection(text):
            raise ValueError("Potential SQL injection detected")
        
        # Trim whitespace
        text = text.strip()
        
        # Enforce max length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = cls.sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @classmethod
    def sanitize_list(cls, data: List[Any]) -> List[Any]:
        """
        Recursively sanitize list values.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """
        Validate Philippine phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid phone format
        """
        # Philippine mobile: +639XXXXXXXXX or 09XXXXXXXXX
        # Landline: +632XXXXXXXX or 02XXXXXXXX
        patterns = [
            r'^\+639\d{9}$',  # +639171234567
            r'^09\d{9}$',     # 09171234567
            r'^\+632\d{7,8}$',  # +6328123456
            r'^02\d{7,8}$',   # 028123456
        ]
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Remove leading dots
        filename = filename.lstrip('.')
        
        # Only allow alphanumeric, dash, underscore, and dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        return filename

