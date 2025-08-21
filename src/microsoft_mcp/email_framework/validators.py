"""
Validation utilities for email framework
Provides comprehensive validation for email data and templates
"""

from typing import Dict, Any, List, Optional, Union, Callable
import re
from datetime import datetime


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
        except ValueError:
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

# Export main validation functions for direct import
def validate_email(email: str) -> str:
    """Validate email address - direct function export"""
    return EmailValidator.validate_email(email)


def validate_recipient_list(recipients: list[str]) -> list[str]:
    """Validate recipient list - direct function export"""  
    return EmailValidator.validate_email_list(recipients)