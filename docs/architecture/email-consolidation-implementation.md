# Email Operations Implementation Guide

## Overview

This guide provides detailed implementation specifications for the unified `email_operations()` tool, including complete parameter models, action handlers, and integration patterns.

## Parameter Models

### Base Parameter Model

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class BaseEmailParams(BaseModel):
    """Base parameters common to all email operations"""
    account_id: str = Field(..., description="Microsoft account ID from list_accounts()")
    
    class Config:
        extra = "forbid"  # Reject unknown parameters
        validate_assignment = True  # Validate on assignment
        use_enum_values = True
```

### Action-Specific Parameter Models

#### List Operations

```python
class ListEmailParams(BaseEmailParams):
    """Parameters for listing emails"""
    folder: Optional[Literal["inbox", "sent", "drafts", "deleted", "junk", "archive"]] = "inbox"
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum emails to return")
    skip: Optional[int] = Field(0, ge=0, description="Number of emails to skip for pagination")
    include_body: Optional[bool] = Field(True, description="Include email body content")
    has_attachments: Optional[bool] = Field(None, description="Filter by attachment presence")
    search_query: Optional[str] = Field(None, description="Search query to filter emails")
    order_by: Optional[Literal["received", "sent", "subject", "from"]] = "received"
    order_desc: Optional[bool] = True

class GetEmailParams(BaseEmailParams):
    """Parameters for getting a specific email"""
    email_id: str = Field(..., description="Email message ID")
    include_attachments: Optional[bool] = Field(False, description="Include attachment details")
    include_headers: Optional[bool] = Field(False, description="Include full headers")
```

#### Send Operations

```python
class SendEmailParams(BaseEmailParams):
    """Parameters for sending email"""
    to: Union[str, List[str]] = Field(..., description="Recipient email address(es)")
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, description="Email body content")
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    attachments: Optional[List[str]] = Field(None, description="File paths to attach")
    importance: Optional[Literal["low", "normal", "high"]] = "normal"
    template_name: Optional[str] = Field(None, description="Email template to use")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Data for template")
    
    @validator('to', 'cc', 'bcc', pre=True)
    def normalize_emails(cls, v):
        if isinstance(v, str):
            return [v]
        return v
    
    @validator('to', 'cc', 'bcc')
    def validate_emails(cls, v):
        if v:
            for email in v:
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    raise ValueError(f"Invalid email address: {email}")
        return v

class DraftEmailParams(SendEmailParams):
    """Parameters for creating/updating draft"""
    draft_id: Optional[str] = Field(None, description="Draft ID to update (None creates new)")
```

#### Reply/Forward Operations

```python
class ReplyEmailParams(BaseEmailParams):
    """Parameters for replying to email"""
    email_id: str = Field(..., description="Email to reply to")
    body: str = Field(..., description="Reply message content")
    reply_all: Optional[bool] = Field(False, description="Reply to all recipients")
    attachments: Optional[List[str]] = None
    include_original: Optional[bool] = Field(True, description="Include original message")

class ForwardEmailParams(BaseEmailParams):
    """Parameters for forwarding email"""
    email_id: str = Field(..., description="Email to forward")
    to: Union[str, List[str]] = Field(..., description="Forward recipients")
    comment: Optional[str] = Field(None, description="Optional forward comment")
    include_attachments: Optional[bool] = Field(True, description="Include original attachments")
```

#### Management Operations

```python
class SearchEmailParams(BaseEmailParams):
    """Parameters for searching emails"""
    query: str = Field(..., min_length=1, description="Search query")
    folder: Optional[str] = Field(None, description="Limit search to specific folder")
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    has_attachments: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: Optional[int] = Field(50, ge=1, le=100)

class DeleteEmailParams(BaseEmailParams):
    """Parameters for deleting email"""
    email_id: str = Field(..., description="Email to delete")
    permanent: Optional[bool] = Field(False, description="Permanently delete (skip trash)")

class MoveEmailParams(BaseEmailParams):
    """Parameters for moving email"""
    email_id: str = Field(..., description="Email to move")
    destination_folder: str = Field(..., description="Target folder name")

class MarkEmailParams(BaseEmailParams):
    """Parameters for marking email"""
    email_id: Union[str, List[str]] = Field(..., description="Email ID(s) to mark")
    mark_as: Literal["read", "unread", "important", "not_important"] = Field(...)
    
    @validator('email_id', pre=True)
    def normalize_ids(cls, v):
        if isinstance(v, str):
            return [v]
        return v
```

#### Metadata Operations

```python
class AttachmentsParams(BaseEmailParams):
    """Parameters for attachment operations"""
    email_id: str = Field(..., description="Email containing attachments")
    save_dir: Optional[str] = Field("~/Downloads", description="Directory to save attachments")
    attachment_ids: Optional[List[str]] = Field(None, description="Specific attachments to download")

class FolderParams(BaseEmailParams):
    """Parameters for folder operations"""
    operation: Literal["list", "create", "rename", "delete"] = "list"
    folder_name: Optional[str] = Field(None, description="Folder name for create/rename/delete")
    new_name: Optional[str] = Field(None, description="New name for rename operation")
    parent_folder: Optional[str] = Field(None, description="Parent folder for create")
```

## Action Handlers

### Core Handler Structure

```python
from typing import Dict, Any
import asyncio

# Action handler signatures
async def handle_list_emails(params: ListEmailParams) -> Dict[str, Any]:
    """List emails with filtering and pagination"""
    try:
        # Convert folder name to Graph API format
        folder = FOLDER_MAPPINGS.get(params.folder, params.folder)
        
        # Build query parameters
        query_params = {
            "$top": params.limit,
            "$skip": params.skip,
            "$orderby": f"{params.order_by}DateTime {'desc' if params.order_desc else 'asc'}"
        }
        
        # Add search filter if provided
        if params.search_query:
            query_params["$search"] = f'"{params.search_query}"'
        
        # Add attachment filter
        if params.has_attachments is not None:
            query_params["$filter"] = f"hasAttachments eq {str(params.has_attachments).lower()}"
        
        # Execute Graph API call
        emails = await graph.list_emails(
            account_id=params.account_id,
            folder=folder,
            params=query_params
        )
        
        # Format response
        return {
            "status": "success",
            "action": "list",
            "count": len(emails),
            "emails": [format_email(e, params.include_body) for e in emails],
            "pagination": {
                "skip": params.skip,
                "limit": params.limit,
                "has_more": len(emails) == params.limit
            }
        }
    except Exception as e:
        return format_error_response("list", str(e))

async def handle_send_email(params: SendEmailParams) -> Dict[str, Any]:
    """Send email with optional template"""
    try:
        # Process template if specified
        if params.template_name:
            body_content = await process_template(
                template_name=params.template_name,
                template_data=params.template_data,
                user_content=params.body
            )
        else:
            body_content = params.body
        
        # Apply professional formatting
        formatted_body = apply_email_formatting(
            content=body_content,
            format_type="html"
        )
        
        # Prepare email message
        message = {
            "subject": params.subject,
            "importance": params.importance,
            "body": {
                "contentType": "HTML",
                "content": formatted_body
            },
            "toRecipients": [{"emailAddress": {"address": addr}} for addr in params.to],
        }
        
        # Add CC recipients
        if params.cc:
            message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in params.cc]
        
        # Add BCC recipients
        if params.bcc:
            message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in params.bcc]
        
        # Handle attachments
        if params.attachments:
            attachments = await process_attachments(params.attachments)
            message["attachments"] = attachments
        
        # Send via Graph API
        result = await graph.send_email(
            account_id=params.account_id,
            message=message
        )
        
        return {
            "status": "success",
            "action": "send",
            "message_id": result.get("id"),
            "recipients": {
                "to": params.to,
                "cc": params.cc or [],
                "bcc": params.bcc or []
            }
        }
    except Exception as e:
        return format_error_response("send", str(e))
```

### Handler Mapping

```python
# Complete action to handler mapping
ACTION_HANDLERS = {
    # Core operations
    "list": handle_list_emails,
    "get": handle_get_email,
    "send": handle_send_email,
    "draft": handle_draft_email,
    
    # Response operations
    "reply": handle_reply_email,
    "reply_all": handle_reply_all_email,
    "forward": handle_forward_email,
    
    # Management operations
    "search": handle_search_emails,
    "delete": handle_delete_email,
    "move": handle_move_email,
    "mark": handle_mark_email,
    
    # Metadata operations
    "headers": handle_get_headers,
    "attachments": handle_attachments,
    "signature": handle_get_signature,
    
    # Folder operations
    "folders": handle_folders,
    "stats": handle_get_stats,
    
    # Utility operations
    "empty_trash": handle_empty_trash,
    "rules": handle_get_rules
}
```

## Error Handling

### Comprehensive Error Messages

```python
def format_validation_error(action: str, error: ValidationError) -> Dict[str, Any]:
    """Format validation errors with helpful guidance"""
    errors = []
    for err in error.errors():
        field = ".".join(str(x) for x in err['loc'])
        message = err['msg']
        errors.append({
            "field": field,
            "message": message,
            "type": err['type']
        })
    
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

def format_unknown_action_error(action: str) -> Dict[str, Any]:
    """Format error for unknown action"""
    similar = find_similar_actions(action)
    return {
        "status": "error",
        "error_type": "unknown_action",
        "message": f"Unknown action: '{action}'",
        "available_actions": list(ACTION_HANDLERS.keys()),
        "did_you_mean": similar[:3] if similar else None,
        "hint": "Use one of the available actions listed above",
        "documentation": "https://docs.microsoft-mcp.dev/email-operations"
    }
```

## Usage Examples

### Complete Usage Examples

```python
USAGE_EXAMPLES = {
    "list": '''email_operations(
    action="list",
    account_id="user@company.com",
    folder="inbox",
    limit=20,
    has_attachments=True
)''',
    
    "send": '''email_operations(
    action="send",
    account_id="user@company.com",
    to="recipient@example.com",
    subject="Monthly Report",
    body="Please find the attached report.",
    attachments=["/path/to/report.pdf"],
    template_name="professional",
    template_data={"month": "January"}
)''',
    
    "search": '''email_operations(
    action="search",
    account_id="user@company.com",
    query="project deadline",
    folder="sent",
    date_from=datetime(2024, 1, 1),
    limit=50
)''',
    
    "reply": '''email_operations(
    action="reply",
    account_id="user@company.com",
    email_id="AAMkAGI2...",
    body="Thank you for your message. I'll review and respond shortly.",
    reply_all=True
)''',
    
    "mark": '''email_operations(
    action="mark",
    account_id="user@company.com",
    email_id=["id1", "id2", "id3"],
    mark_as="read"
)''',
    
    "folders": '''email_operations(
    action="folders",
    account_id="user@company.com",
    operation="create",
    folder_name="Projects/2024",
    parent_folder="Projects"
)'''
}
```

## Template Integration

### Template Processing

```python
async def process_template(
    template_name: str,
    template_data: Optional[Dict[str, Any]],
    user_content: str
) -> str:
    """Process email template with user data"""
    # Load template
    template = get_template(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")
    
    # Merge user content
    if template.supports_user_content:
        template_data = template_data or {}
        template_data["user_content"] = user_content
    
    # Render template
    rendered = template.render(template_data)
    
    # Apply CSS inlining for email compatibility
    return inline_css(rendered)
```

## Performance Optimizations

### Caching Strategy

```python
from functools import lru_cache
from cachetools import TTLCache

# Cache parameter validators
@lru_cache(maxsize=32)
def get_param_validator(action: str):
    return ACTION_PARAMS.get(action)

# Cache folder mappings
folder_cache = TTLCache(maxsize=100, ttl=3600)

# Cache template renderings
template_cache = TTLCache(maxsize=50, ttl=1800)
```

### Batch Operations

```python
async def handle_batch_operations(operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Handle multiple operations efficiently"""
    tasks = []
    for op in operations:
        action = op.get("action")
        if action in ACTION_HANDLERS:
            handler = ACTION_HANDLERS[action]
            params_class = ACTION_PARAMS[action]
            params = params_class(**op)
            tasks.append(handler(params))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [format_result(r) for r in results]
```

## Testing Guidelines

### Parameter Validation Tests

```python
import pytest
from pydantic import ValidationError

def test_list_email_params_validation():
    # Valid params
    params = ListEmailParams(
        account_id="user@example.com",
        folder="inbox",
        limit=50
    )
    assert params.folder == "inbox"
    assert params.limit == 50
    
    # Invalid folder
    with pytest.raises(ValidationError) as exc:
        ListEmailParams(
            account_id="user@example.com",
            folder="invalid_folder"
        )
    assert "folder" in str(exc.value)
    
    # Invalid limit
    with pytest.raises(ValidationError) as exc:
        ListEmailParams(
            account_id="user@example.com",
            limit=200  # Exceeds max
        )
    assert "limit" in str(exc.value)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_email_operations_integration():
    # Test list operation
    result = await email_operations(
        action="list",
        account_id="test@example.com",
        folder="inbox",
        limit=10
    )
    assert result["status"] == "success"
    assert result["action"] == "list"
    assert "emails" in result
    
    # Test send operation
    result = await email_operations(
        action="send",
        account_id="test@example.com",
        to="recipient@example.com",
        subject="Test Email",
        body="Test content"
    )
    assert result["status"] == "success"
    assert result["action"] == "send"
    assert "message_id" in result
```

## Migration Guide

### Mapping Legacy Tools to New Actions

| Legacy Tool | New Action | Parameters |
|------------|------------|------------|
| `list_emails()` | `action="list"` | Same parameters |
| `send_email()` | `action="send"` | Same parameters |
| `reply_to_email()` | `action="reply"` | Same parameters |
| `search_emails()` | `action="search"` | Same parameters |
| `delete_email()` | `action="delete"` | Same parameters |
| `get_email()` | `action="get"` | `email_id` required |
| `forward_email()` | `action="forward"` | Same parameters |
| `mark_email_as_read()` | `action="mark"` | `mark_as="read"` |
| `move_email()` | `action="move"` | Same parameters |

### Code Migration Examples

#### Before (Legacy)
```python
# List emails
emails = list_emails(
    account_id="user@company.com",
    folder_name="inbox",
    limit=20
)

# Send email
send_email(
    account_id="user@company.com",
    to="recipient@example.com",
    subject="Hello",
    body="Message content"
)
```

#### After (Unified)
```python
# List emails
emails = email_operations(
    action="list",
    account_id="user@company.com",
    folder="inbox",
    limit=20
)

# Send email
email_operations(
    action="send",
    account_id="user@company.com",
    to="recipient@example.com",
    subject="Hello",
    body="Message content"
)
```

## Best Practices

1. **Always specify action first** - Makes code more readable
2. **Use keyword arguments** - Improves clarity and prevents errors
3. **Handle errors gracefully** - Check status in response
4. **Batch when possible** - Use batch operations for multiple emails
5. **Cache account IDs** - Avoid repeated `list_accounts()` calls
6. **Use templates** - Leverage templates for consistent formatting

## Conclusion

This implementation guide provides a complete blueprint for the unified email operations tool. The combination of Pydantic validation, clear action taxonomy, and comprehensive error handling creates a powerful yet approachable API that dramatically simplifies email operations while maintaining full functionality.