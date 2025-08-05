"""Tests for validation utilities."""

from pydantic import ValidationError

from microsoft_mcp.email_params import SendEmailParams
from microsoft_mcp.validation import (
    format_error_response,
    format_validation_error,
    generate_contextual_hint,
    get_optional_params,
    get_required_params,
)


class TestParameterLists:
    """Test parameter list functions."""
    
    def test_get_required_params(self):
        """Test getting required parameters for actions."""
        assert get_required_params("list") == ["account_id"]
        assert get_required_params("send") == ["account_id", "to", "subject", "body"]
        assert get_required_params("delete") == ["account_id", "email_id"]
        assert get_required_params("unknown_action") == []
    
    def test_get_optional_params(self):
        """Test getting optional parameters for actions."""
        assert "folder" in get_optional_params("list")
        assert "limit" in get_optional_params("list")
        assert "cc" in get_optional_params("send")
        assert "attachments" in get_optional_params("send")
        assert get_optional_params("unknown_action") == []


class TestContextualHints:
    """Test contextual hint generation."""
    
    def test_missing_field_hint(self):
        """Test hint for missing required field."""
        errors = [{
            "loc": ["account_id"],
            "type": "missing",
            "msg": "Field required"
        }]
        hint = generate_contextual_hint("send", errors)
        assert "Missing required field 'account_id'" in hint
    
    def test_email_validation_hint(self):
        """Test hint for invalid email."""
        errors = [{
            "loc": ["to"],
            "type": "value_error",
            "msg": "Invalid email format: invalid-email"
        }]
        hint = generate_contextual_hint("send", errors)
        assert "Email address 'to' must be in format: user@example.com" in hint
    
    def test_enum_error_hint(self):
        """Test hint for invalid enum value."""
        errors = [{
            "loc": ["folder"],
            "type": "literal_error",
            "msg": "Invalid value"
        }]
        hint = generate_contextual_hint("list", errors)
        assert "Invalid value for 'folder'" in hint
    
    def test_type_error_hint(self):
        """Test hint for wrong type."""
        errors = [{
            "loc": ["limit"],
            "type": "type_error.integer",
            "msg": "value is not a valid integer"
        }]
        hint = generate_contextual_hint("list", errors)
        assert "Wrong type for 'limit'" in hint
    
    def test_multiple_errors_hint(self):
        """Test hint for multiple errors."""
        errors = [
            {
                "loc": ["account_id"],
                "type": "missing",
                "msg": "Field required"
            },
            {
                "loc": ["to"],
                "type": "value_error",
                "msg": "Invalid email format"
            }
        ]
        hint = generate_contextual_hint("send", errors)
        assert "Missing required field 'account_id'" in hint
        assert "Email address 'to' must be in format" in hint
        assert " | " in hint  # Multiple hints joined


class TestValidationErrorFormatting:
    """Test validation error formatting."""
    
    def test_format_validation_error_basic(self):
        """Test basic validation error formatting."""
        try:
            SendEmailParams(account_id="user@example.com")
        except ValidationError as e:
            result = format_validation_error("send", e)
        
        assert result["status"] == "error"
        assert result["error_type"] == "validation_error"
        assert result["action"] == "send"
        assert "Invalid parameters for 'send' action" in result["message"]
        assert result["required_params"] == ["account_id", "to", "subject", "body"]
        assert "cc" in result["optional_params"]
        assert result["example"] is not None
        assert result["documentation"] == "https://docs.microsoft-mcp.dev/email-operations#send"
    
    def test_format_validation_error_with_details(self):
        """Test validation error with field details."""
        try:
            SendEmailParams(
                account_id="user@example.com",
                to="invalid-email",
                subject="Test",
                body="Content"
            )
        except ValidationError as e:
            result = format_validation_error("send", e)
        
        assert len(result["errors"]) > 0
        error = result["errors"][0]
        assert "to" in error["field"]
        assert "Invalid email format" in error["message"]
        assert error["type"] == "value_error"
        assert error["input"] == "invalid-email"
    
    def test_format_validation_error_enum(self):
        """Test validation error for enum fields."""
        from microsoft_mcp.email_params import ListEmailParams
        
        try:
            ListEmailParams(
                account_id="user@example.com",
                folder="invalid_folder"
            )
        except ValidationError as e:
            result = format_validation_error("list", e)
        
        assert len(result["errors"]) > 0
        error = result["errors"][0]
        assert "folder" in error["field"]
        assert error["type"] == "literal_error"
        # Should include allowed values for enum errors
        if "allowed_values" in error:
            assert isinstance(error["allowed_values"], (list, str))


class TestErrorResponseFormatting:
    """Test general error response formatting."""
    
    def test_format_error_response_basic(self):
        """Test basic error response formatting."""
        error = ValueError("Something went wrong")
        result = format_error_response("send", error)
        
        assert result["status"] == "error"
        assert result["action"] == "send"
        assert result["error_type"] == "ValueError"
        assert result["message"] == "Something went wrong"
        assert "timestamp" in result
        assert result["details"] == {}
    
    def test_format_error_response_with_details(self):
        """Test error response with additional details."""
        error = RuntimeError("API call failed")
        details = {
            "status_code": 500,
            "request_id": "12345"
        }
        result = format_error_response("list", error, details)
        
        assert result["status"] == "error"
        assert result["action"] == "list"
        assert result["error_type"] == "RuntimeError"
        assert result["message"] == "API call failed"
        assert result["details"]["status_code"] == 500
        assert result["details"]["request_id"] == "12345"
    
    def test_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        error = Exception("Test error")
        result = format_error_response("test", error)
        
        # Should be able to parse as ISO datetime
        from datetime import datetime
        timestamp = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)