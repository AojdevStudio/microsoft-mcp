"""Validation utilities for Microsoft MCP operations.

This module provides error formatting and validation helper functions
for the unified email operations tool.
"""

from typing import Any, Dict, List, Optional

from pydantic import ValidationError


# Required parameters for each action
REQUIRED_PARAMS = {
    "list": ["account_id"],
    "get": ["account_id", "email_id"],
    "send": ["account_id", "to", "subject", "body"],
    "draft": ["account_id", "to", "subject", "body"],
    "reply": ["account_id", "email_id", "body"],
    "reply_all": ["account_id", "email_id", "body"],
    "forward": ["account_id", "email_id", "to"],
    "search": ["account_id", "query"],
    "delete": ["account_id", "email_id"],
    "move": ["account_id", "email_id", "destination_folder"],
    "mark": ["account_id", "email_id", "mark_as"],
    "headers": ["account_id", "email_id"],
    "attachments": ["account_id", "email_id"],
    "signature": ["account_id"],
    "folders": ["account_id", "operation"],
    "stats": ["account_id"],
    "empty_trash": ["account_id", "confirm"],
    "rules": ["account_id"],
}

# Optional parameters for each action
OPTIONAL_PARAMS = {
    "list": ["folder", "limit", "skip", "include_body", "has_attachments", "search_query"],
    "get": ["include_attachments", "include_headers"],
    "send": ["cc", "bcc", "attachments", "importance", "template"],
    "draft": ["cc", "bcc", "attachments", "importance", "template", "draft_id"],
    "reply": ["reply_all", "attachments", "include_original"],
    "reply_all": ["attachments", "include_original"],
    "forward": ["comment", "include_attachments"],
    "search": ["folder", "from_address", "to_address", "start_date", "end_date", "has_attachments", "limit"],
    "delete": ["permanent"],
    "move": [],
    "mark": [],
    "headers": [],
    "attachments": ["save_dir", "attachment_ids"],
    "signature": [],
    "folders": ["folder_name", "new_name", "parent_folder"],
    "stats": [],
    "empty_trash": [],
    "rules": [],
}

# Usage examples for each action
USAGE_EXAMPLES = {
    "list": {
        "description": "List emails from a folder",
        "example": {
            "action": "list",
            "account_id": "user@company.com",
            "folder": "inbox",
            "limit": 20
        }
    },
    "get": {
        "description": "Get a specific email by ID",
        "example": {
            "action": "get",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA="
        }
    },
    "send": {
        "description": "Send a new email",
        "example": {
            "action": "send",
            "account_id": "user@company.com",
            "to": "recipient@example.com",
            "subject": "Meeting Tomorrow",
            "body": "Let's discuss the project status."
        }
    },
    "draft": {
        "description": "Create or update an email draft",
        "example": {
            "action": "draft",
            "account_id": "user@company.com",
            "to": "recipient@example.com",
            "subject": "Draft: Project Update",
            "body": "Working on the quarterly report..."
        }
    },
    "reply": {
        "description": "Reply to an email",
        "example": {
            "action": "reply",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "body": "Thanks for your message. I agree with your proposal."
        }
    },
    "reply_all": {
        "description": "Reply to all recipients",
        "example": {
            "action": "reply_all",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "body": "Thanks everyone for your input."
        }
    },
    "forward": {
        "description": "Forward an email",
        "example": {
            "action": "forward",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "to": ["colleague@company.com"],
            "comment": "FYI - Please review this proposal."
        }
    },
    "search": {
        "description": "Search for emails",
        "example": {
            "action": "search",
            "account_id": "user@company.com",
            "query": "project proposal",
            "folder": "inbox"
        }
    },
    "delete": {
        "description": "Delete an email",
        "example": {
            "action": "delete",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "permanent": False
        }
    },
    "move": {
        "description": "Move email to another folder",
        "example": {
            "action": "move",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "destination_folder": "archive"
        }
    },
    "mark": {
        "description": "Mark email status",
        "example": {
            "action": "mark",
            "account_id": "user@company.com",
            "email_id": ["AAMkAGI2THQAA="],
            "mark_as": "read"
        }
    },
    "headers": {
        "description": "Get email headers",
        "example": {
            "action": "headers",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA="
        }
    },
    "attachments": {
        "description": "Download email attachments",
        "example": {
            "action": "attachments",
            "account_id": "user@company.com",
            "email_id": "AAMkAGI2THQAA=",
            "save_dir": "~/Downloads"
        }
    },
    "signature": {
        "description": "Get email signature",
        "example": {
            "action": "signature",
            "account_id": "user@company.com"
        }
    },
    "folders": {
        "description": "Manage email folders",
        "example": {
            "action": "folders",
            "account_id": "user@company.com",
            "operation": "list"
        }
    },
    "stats": {
        "description": "Get mailbox statistics",
        "example": {
            "action": "stats",
            "account_id": "user@company.com"
        }
    },
    "empty_trash": {
        "description": "Empty deleted items folder",
        "example": {
            "action": "empty_trash",
            "account_id": "user@company.com",
            "confirm": True
        }
    },
    "rules": {
        "description": "Get inbox rules",
        "example": {
            "action": "rules",
            "account_id": "user@company.com"
        }
    },
}


def get_required_params(action: str) -> List[str]:
    """Get required parameters for an action."""
    return REQUIRED_PARAMS.get(action, [])


def get_optional_params(action: str) -> List[str]:
    """Get optional parameters for an action."""
    return OPTIONAL_PARAMS.get(action, [])


def generate_contextual_hint(action: str, errors: List[Dict[str, Any]]) -> str:
    """Generate contextual hints based on validation errors."""
    hints = []
    
    for error in errors:
        field = error.get("loc", [])[-1] if error.get("loc") else "unknown"
        error_type = error.get("type", "")
        
        if "missing" in error_type:
            hints.append(f"Missing required field '{field}'")
        elif "email" in str(error.get("msg", "")).lower():
            hints.append(f"Email address '{field}' must be in format: user@example.com")
        elif "literal_error" in error_type or "enum" in error_type:
            hints.append(f"Invalid value for '{field}'. Check allowed values in the error details.")
        elif "type_error" in error_type:
            hints.append(f"Wrong type for '{field}'. Check the expected type in the error details.")
    
    if not hints:
        hints.append("Check the error details and ensure all required fields are provided with correct types.")
    
    return " | ".join(hints)


def format_validation_error(
    action: str,
    validation_error: ValidationError,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format validation errors with actionable guidance.
    
    Args:
        action: The email action being performed
        validation_error: The Pydantic validation error
        params: The parameters that caused the error
        
    Returns:
        Formatted error response with guidance
    """
    errors = []
    
    for error in validation_error.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        
        # Add input value if available
        if error.get("input") is not None:
            error_detail["input"] = error["input"]
            
        # Add allowed values for enum errors
        if error["type"] == "literal_error" and "expected" in error.get("ctx", {}):
            error_detail["allowed_values"] = error["ctx"]["expected"]
            
        errors.append(error_detail)
    
    return {
        "status": "error",
        "error_type": "validation_error",
        "action": action,
        "message": f"Invalid parameters for '{action}' action",
        "errors": errors,
        "required_params": get_required_params(action),
        "optional_params": get_optional_params(action),
        "example": USAGE_EXAMPLES.get(action),
        "hint": generate_contextual_hint(action, errors),
        "documentation": f"https://docs.microsoft-mcp.dev/email-operations#{action}"
    }


def format_error_response(
    action: str,
    error: Exception,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format general error responses.
    
    Args:
        action: The action that caused the error
        error: The exception that occurred
        details: Additional error details
        
    Returns:
        Formatted error response
    """
    from datetime import datetime, timezone
    
    return {
        "status": "error",
        "action": action,
        "error_type": type(error).__name__,
        "message": str(error),
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }