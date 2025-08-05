# Coding Standards

## Overview

This document defines the coding standards for the Microsoft MCP project. All code must adhere to these standards to ensure consistency, maintainability, and quality.

## Python Code Style

### General Principles
- **Clarity over cleverness** - Write code that is easy to understand
- **Explicit over implicit** - Be clear about intentions
- **Consistency** - Follow established patterns in the codebase
- **Type safety** - Use type hints everywhere

### Code Formatting
- **Formatter**: Black with line length 100
- **Import sorting**: isort with Black compatibility
- **Indentation**: 4 spaces (no tabs)
- **Max line length**: 100 characters

### Naming Conventions

#### Variables and Functions
```python
# Variables: snake_case
user_email = "user@example.com"
account_id = "123456"

# Functions: snake_case with verb prefixes
def get_user_emails(account_id: str) -> List[Email]:
    pass

def validate_email_address(email: str) -> bool:
    pass
```

#### Classes
```python
# Classes: PascalCase
class EmailValidator:
    pass

class BaseEmailParams:
    pass

# Pydantic models: end with Params or Response
class SendEmailParams(BaseModel):
    pass

class EmailListResponse(BaseModel):
    pass
```

#### Constants
```python
# Constants: UPPER_SNAKE_CASE
MAX_EMAIL_SIZE = 25 * 1024 * 1024  # 25MB
DEFAULT_PAGE_SIZE = 50
GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
```

### Type Hints

#### Required Everywhere
```python
# Always use type hints for function signatures
def process_email(
    email_id: str,
    account_id: str,
    include_attachments: bool = False
) -> Dict[str, Any]:
    pass

# Use Optional for nullable types
def find_user(email: str) -> Optional[User]:
    pass

# Use Union for multiple types
def normalize_recipients(
    recipients: Union[str, List[str]]
) -> List[str]:
    pass
```

#### Type Aliases
```python
# Define type aliases for complex types
from typing import TypeAlias

EmailAddress: TypeAlias = str
MessageId: TypeAlias = str
AccountId: TypeAlias = str

# Use for better readability
def forward_email(
    message_id: MessageId,
    to: List[EmailAddress],
    account_id: AccountId
) -> MessageId:
    pass
```

### Error Handling

#### Exception Patterns
```python
# Specific exceptions over generic ones
class EmailValidationError(ValueError):
    """Raised when email validation fails"""
    pass

class GraphAPIError(Exception):
    """Raised when Graph API returns an error"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Graph API error {status_code}: {message}")

# Always provide context in errors
def validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise EmailValidationError(
            f"Invalid email format: '{email}'. "
            "Email must contain @ symbol."
        )
```

#### Error Returns
```python
# Consistent error response format
def format_error_response(
    action: str,
    error: Exception,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "status": "error",
        "action": action,
        "error_type": type(error).__name__,
        "message": str(error),
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Async Patterns

#### Async Functions
```python
# Always use async/await for I/O operations
async def fetch_emails(
    account_id: str,
    folder: str = "inbox"
) -> List[Email]:
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f"{GRAPH_API_BASE_URL}/users/{account_id}/messages"
        )
        return await response.json()

# Use asyncio.gather for concurrent operations
async def process_multiple_accounts(
    account_ids: List[str]
) -> List[Result]:
    tasks = [
        fetch_emails(account_id) 
        for account_id in account_ids
    ]
    return await asyncio.gather(*tasks)
```

### Documentation

#### Docstrings
```python
def send_email(
    params: SendEmailParams,
    account_id: str
) -> Dict[str, Any]:
    """Send an email through Microsoft Graph API.
    
    Sends an email with optional attachments and templates.
    Automatically formats the email with professional HTML
    styling and appends the user's signature.
    
    Args:
        params: Email parameters including recipients, subject, body
        account_id: Microsoft account ID from authentication
        
    Returns:
        Dictionary containing:
            - message_id: Unique identifier of sent message
            - status: "success" or "error"
            - timestamp: When the email was sent
            
    Raises:
        EmailValidationError: If email parameters are invalid
        GraphAPIError: If Graph API request fails
        
    Example:
        >>> params = SendEmailParams(
        ...     to="user@example.com",
        ...     subject="Test",
        ...     body="Hello"
        ... )
        >>> result = await send_email(params, "account123")
        >>> print(result["message_id"])
    """
    pass
```

#### Inline Comments
```python
# Use comments sparingly for non-obvious logic
def calculate_retry_delay(attempt: int) -> float:
    # Exponential backoff with jitter to prevent thundering herd
    base_delay = 2 ** attempt
    jitter = random.uniform(0, 0.1 * base_delay)
    return min(base_delay + jitter, 60)  # Cap at 60 seconds
```

### Pydantic Models

#### Model Definition
```python
class BaseEmailParams(BaseModel):
    """Base parameters for all email operations."""
    
    account_id: str = Field(
        ...,
        description="Microsoft account ID from list_accounts()",
        example="user@company.com"
    )
    
    class Config:
        # Forbid extra parameters for security
        extra = "forbid"
        # Validate on assignment for immediate feedback
        validate_assignment = True
        # Use enum values directly
        use_enum_values = True
        # Provide schema examples
        schema_extra = {
            "example": {
                "account_id": "user@company.com"
            }
        }
```

#### Validators
```python
class SendEmailParams(BaseEmailParams):
    to: Union[str, List[str]] = Field(..., description="Recipients")
    subject: str = Field(..., min_length=1, max_length=255)
    
    @validator("to", pre=True)
    def normalize_recipients(cls, v):
        """Convert single recipient to list."""
        if isinstance(v, str):
            return [v]
        return v
    
    @validator("to", each_item=True)
    def validate_email_format(cls, email: str) -> str:
        """Validate each email address."""
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError(f"Invalid email: {email}")
        return email.lower()  # Normalize to lowercase
```

### Testing Standards

#### Test Organization
```python
# File: tests/test_email_params.py

class TestSendEmailParams:
    """Test send email parameter validation."""
    
    def test_valid_params(self):
        """Test creating params with valid values."""
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test",
            body="Content"
        )
        assert params.to == ["recipient@example.com"]
    
    def test_invalid_email_format(self):
        """Test that invalid emails are rejected."""
        with pytest.raises(ValidationError) as exc:
            SendEmailParams(
                account_id="user@example.com",
                to="invalid-email",
                subject="Test",
                body="Content"
            )
        assert "Invalid email" in str(exc.value)
```

#### Test Patterns
```python
# Use fixtures for common test data
@pytest.fixture
def valid_email_params():
    return {
        "account_id": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test Subject",
        "body": "Test content"
    }

# Test both success and failure cases
def test_email_validation_success(valid_email_params):
    params = SendEmailParams(**valid_email_params)
    assert params.subject == "Test Subject"

def test_email_validation_failure():
    with pytest.raises(ValidationError):
        SendEmailParams(
            account_id="test@example.com",
            to="",  # Empty recipient
            subject="Test",
            body="Content"
        )
```

### Security Guidelines

#### Input Validation
- Always validate user input with Pydantic
- Never trust external data
- Sanitize data before using in queries
- Use parameterized queries

#### Secrets Management
```python
# Never hardcode secrets
# Bad
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS

# Good
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

#### Error Messages
```python
# Don't leak sensitive information in errors
# Bad
raise Exception(f"Database connection failed: {connection_string}")

# Good
raise Exception("Database connection failed. Check configuration.")
```

## Code Review Checklist

Before submitting code:
- [ ] All functions have type hints
- [ ] Complex logic has comments
- [ ] Error handling is comprehensive
- [ ] Tests cover happy path and edge cases
- [ ] No hardcoded secrets or credentials
- [ ] Follows naming conventions
- [ ] Docstrings for public functions
- [ ] No unused imports or variables
- [ ] Performance considerations addressed
- [ ] Security implications considered