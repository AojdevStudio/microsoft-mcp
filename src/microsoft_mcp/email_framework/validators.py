"""
Validation utilities for email framework
Provides comprehensive validation for email data and templates
SECURITY: Includes XSS prevention and input sanitization functions
"""

from typing import Dict, Any, List, Optional, Union, Callable
import re
from datetime import datetime
from markupsafe import escape


class ValidationError(ValueError):
    """Custom validation error with detailed information"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "message": str(self),
            "field": self.field,
            "value": self.value,
        }


class EmailValidator:
    """Validator for email addresses and related data"""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def validate_email(cls, email: str, field_name: str = "email") -> str:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email or not isinstance(email, str):
            raise ValidationError(f"{field_name} must be a non-empty string", field_name, email)
            
        email = email.strip().lower()
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid email address format: {email}", field_name, email)
            
        return email
        
    @classmethod
    def validate_email_list(cls, emails: List[str], field_name: str = "emails") -> List[str]:
        """Validate a list of email addresses"""
        if not isinstance(emails, list):
            raise ValidationError(f"{field_name} must be a list", field_name, emails)
            
        validated = []
        for i, email in enumerate(emails):
            try:
                validated.append(cls.validate_email(email, f"{field_name}[{i}]"))
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid email in {field_name} at position {i}: {e}",
                    field_name,
                    emails
                )
                
        return validated


class DataValidator:
    """General data validation utilities"""
    
    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        context: str = "data"
    ) -> None:
        """
        Validate that all required fields are present
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            context: Context for error messages
            
        Raises:
            ValidationError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise ValidationError(f"{context} must be a dictionary", context, data)
            
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields in {context}: {', '.join(missing_fields)}",
                context,
                missing_fields
            )
            
    @staticmethod
    def validate_numeric_range(
        value: Union[int, float],
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> Union[int, float]:
        """
        Validate numeric value is within range
        
        Args:
            value: Value to validate
            field_name: Field name for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If value is out of range
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{field_name} must be a number",
                field_name,
                value
            )
            
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"{field_name} must be at least {min_value}",
                field_name,
                value
            )
            
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"{field_name} must be at most {max_value}",
                field_name,
                value
            )
            
        return value
        
    @staticmethod
    def validate_percentage(
        value: float,
        field_name: str,
        allow_decimal: bool = True
    ) -> float:
        """
        Validate percentage value
        
        Args:
            value: Percentage value
            field_name: Field name for error messages
            allow_decimal: Whether to allow decimal format (0.95) or require percentage format (95)
            
        Returns:
            Validated percentage as decimal (0.0-1.0)
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{field_name} must be a number",
                field_name,
                value
            )
            
        # Convert percentage format to decimal if needed
        if value > 1.0 and value <= 100:
            value = value / 100.0
        elif value > 100:
            raise ValidationError(
                f"{field_name} must be a valid percentage",
                field_name,
                value
            )
            
        return DataValidator.validate_numeric_range(
            value, field_name, 0.0, 1.0
        )
        
    @staticmethod
    def validate_currency(
        value: Union[int, float],
        field_name: str,
        allow_negative: bool = False
    ) -> float:
        """Validate currency amount"""
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{field_name} must be a number",
                field_name,
                value
            )
            
        if not allow_negative and value < 0:
            raise ValidationError(
                f"{field_name} cannot be negative",
                field_name,
                value
            )
            
        return float(value)
        
    @staticmethod
    def validate_date_string(
        date_str: str,
        field_name: str,
        format_str: str = "%Y-%m-%d"
    ) -> datetime:
        """Validate date string and return datetime object"""
        if not isinstance(date_str, str):
            raise ValidationError(
                f"{field_name} must be a string",
                field_name,
                date_str
            )
            
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError as e:
            raise ValidationError(
                f"{field_name} must be a valid date in format {format_str}",
                field_name,
                date_str
            )


class TemplateDataValidator:
    """Validators for specific email template data"""
    
    @staticmethod
    def validate_financial_metric(
        metric: Dict[str, Any],
        metric_name: str
    ) -> Dict[str, Any]:
        """Validate a financial metric structure"""
        DataValidator.validate_required_fields(
            metric,
            ["value"],
            f"financial_data.{metric_name}"
        )
        
        # Validate value
        metric["value"] = DataValidator.validate_currency(
            metric["value"],
            f"financial_data.{metric_name}.value"
        )
        
        # Validate optional fields
        if "goal" in metric:
            metric["goal"] = DataValidator.validate_currency(
                metric["goal"],
                f"financial_data.{metric_name}.goal"
            )
            
        if "ratio" in metric:
            metric["ratio"] = DataValidator.validate_percentage(
                metric["ratio"],
                f"financial_data.{metric_name}.ratio"
            )
            
        if "status" in metric:
            valid_statuses = ["ahead", "normal", "warning", "behind"]
            if metric["status"] not in valid_statuses:
                raise ValidationError(
                    f"Invalid status: {metric['status']}. Must be one of: {', '.join(valid_statuses)}",
                    f"financial_data.{metric_name}.status",
                    metric["status"]
                )
                
        return metric
        
    @staticmethod
    def validate_provider(
        provider: Dict[str, Any],
        index: int
    ) -> Dict[str, Any]:
        """Validate provider data structure"""
        DataValidator.validate_required_fields(
            provider,
            ["name", "production"],
            f"providers[{index}]"
        )
        
        # Validate name
        if not isinstance(provider["name"], str) or not provider["name"].strip():
            raise ValidationError(
                "Provider name must be a non-empty string",
                f"providers[{index}].name",
                provider["name"]
            )
            
        # Validate production
        provider["production"] = DataValidator.validate_currency(
            provider["production"],
            f"providers[{index}].production"
        )
        
        # Validate optional fields
        if "case_acceptance" in provider:
            provider["case_acceptance"] = DataValidator.validate_percentage(
                provider["case_acceptance"],
                f"providers[{index}].case_acceptance"
            )
            
        return provider
        
    @staticmethod
    def validate_alert(
        alert: Dict[str, Any],
        index: int
    ) -> Dict[str, Any]:
        """Validate alert structure"""
        DataValidator.validate_required_fields(
            alert,
            ["message"],
            f"alerts[{index}]"
        )
        
        # Validate type
        if "type" in alert:
            valid_types = ["info", "warning", "danger", "critical", "success"]
            if alert["type"] not in valid_types:
                raise ValidationError(
                    f"Invalid alert type: {alert['type']}. Must be one of: {', '.join(valid_types)}",
                    f"alerts[{index}].type",
                    alert["type"]
                )
                
        return alert
        
    @staticmethod
    def validate_recommendation(
        rec: Dict[str, Any],
        index: int
    ) -> Dict[str, Any]:
        """Validate recommendation structure"""
        # At least one of title or text should be present
        if "title" not in rec and "text" not in rec:
            raise ValidationError(
                "Recommendation must have either 'title' or 'text'",
                f"recommendations[{index}]",
                rec
            )
            
        # Validate priority
        if "priority" in rec:
            valid_priorities = ["low", "medium", "high", "critical"]
            priority = rec["priority"].lower()
            if priority not in valid_priorities:
                raise ValidationError(
                    f"Invalid priority: {rec['priority']}. Must be one of: {', '.join(valid_priorities)}",
                    f"recommendations[{index}].priority",
                    rec["priority"]
                )
                
        return rec


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
        self.validated_data: Optional[Dict[str, Any]] = None
        
    @property
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return len(self.errors) == 0
        
    def add_error(self, error: Union[str, ValidationError]) -> None:
        """Add an error to the result"""
        if isinstance(error, str):
            error = ValidationError(error)
        self.errors.append(error)
        
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result"""
        self.warnings.append(warning)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
            "validated_data": self.validated_data,
        }


def create_validator(
    validation_func: Callable[[Dict[str, Any]], Dict[str, Any]]
) -> Callable[[Dict[str, Any]], ValidationResult]:
    """
    Create a validator function that returns ValidationResult
    
    Args:
        validation_func: Function that validates and returns cleaned data
        
    Returns:
        Validator function that returns ValidationResult
    """
    def validator(data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        try:
            result.validated_data = validation_func(data)
        except ValidationError as e:
            result.add_error(e)
        except Exception as e:
            result.add_error(ValidationError(str(e)))
            
        return result
        
    return validator


# ===== SECURITY FUNCTIONS =====

def validate_email_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize email template data by escaping all string values
    This prevents XSS attacks by ensuring all user inputs are properly escaped
    
    Args:
        data: Dictionary containing email template data
        
    Returns:
        Dictionary with all string values escaped
    """
    if not isinstance(data, dict):
        return data
        
    validated = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Escape all string values to prevent XSS
            validated[key] = escape(value)
        elif isinstance(value, dict):
            # Recursively validate nested dictionaries
            validated[key] = validate_email_data(value)
        elif isinstance(value, list):
            # Validate each item in lists
            validated[key] = [
                validate_email_data(item) if isinstance(item, dict) 
                else escape(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            # Non-string values are safe
            validated[key] = value
            
    return validated


def validate_url(url: str) -> str:
    """
    Validate URL to prevent javascript: and other dangerous protocols
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValueError: If URL contains dangerous protocol
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
        
    # List of allowed protocols
    allowed_protocols = ['http://', 'https://', 'mailto:', '/']
    
    # Check if URL starts with a dangerous protocol
    dangerous_protocols = [
        'javascript:', 'data:', 'vbscript:', 'file:', 'about:'
    ]
    
    url_lower = url.lower().strip()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            raise ValueError(f"Invalid URL protocol: {protocol} URLs are not allowed")
    
    # If URL doesn't start with allowed protocol and isn't relative, reject it
    if not any(url_lower.startswith(p) for p in allowed_protocols) and not url.startswith('/'):
        # Check if it's a relative path without protocol
        if ':' in url.split('/')[0]:
            raise ValueError(f"Invalid URL: Unknown protocol")
    
    return url


def add_security_headers(html: str) -> str:
    """
    Add security headers to the HTML email to prevent content injection
    
    Args:
        html: HTML content
        
    Returns:
        HTML with security headers added
    """
    # Security headers as HTML comments (for email clients that support them)
    security_headers = """<!--
Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none';
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
-->
"""
    
    # Insert security headers after DOCTYPE but before html tag
    if '<!DOCTYPE' in html:
        parts = html.split('<html', 1)
        if len(parts) == 2:
            return parts[0] + security_headers + '<html' + parts[1]
    
    # Fallback: add at the beginning
    return security_headers + html


def sanitize_html_attribute(value: str) -> str:
    """
    Sanitize a value for use in HTML attributes
    
    Args:
        value: Value to sanitize
        
    Returns:
        Sanitized value safe for HTML attributes
    """
    # Escape quotes and other special characters
    return escape(value).replace('"', '&quot;').replace("'", '&#39;')


def is_safe_css_value(value: str) -> bool:
    """
    Check if a CSS value is safe (doesn't contain JavaScript)
    
    Args:
        value: CSS value to check
        
    Returns:
        True if safe, False otherwise
    """
    if not isinstance(value, str):
        return True
        
    value_lower = value.lower()
    
    # Check for dangerous patterns
    dangerous_patterns = [
        'javascript:', 'expression(', 'behavior:', 'binding:',
        '-moz-binding:', 'vbscript:', '@import'
    ]
    
    return not any(pattern in value_lower for pattern in dangerous_patterns)