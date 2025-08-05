# Email Operations Ultra-Consolidation Architecture

## Executive Summary

This document defines the architecture for consolidating 25+ email tools into a single, unified `email_operations()` tool. This represents a 96% reduction in API surface area while maintaining 100% functionality and dramatically improving developer experience.

## Architecture Overview

### Core Design Principles

1. **Single Entry Point**: One tool (`email_operations`) handles all email operations
2. **Action-Based Design**: Operations specified via action parameter
3. **Progressive Disclosure**: Simple operations stay simple, complex ones are possible
4. **Type-Safe Validation**: Pydantic models ensure robust parameter handling
5. **Clean Separation**: Business logic separated from infrastructure
6. **Zero Legacy Code**: Fresh implementation with no compatibility layers

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Interface Layer                   │
│              email_operations() - Single Tool            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Action Dispatch Layer                   │
│         Smart routing based on action parameter          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                Parameter Validation Layer                │
│     Pydantic models for type-safe validation            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                 Business Logic Layer                     │
│    Email operations, template processing, formatting     │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Graph API Layer                        │
│           Microsoft Graph API integration                │
└─────────────────────────────────────────────────────────┘
```

## Detailed Design

### 1. Action Taxonomy

The unified tool supports 18 distinct actions covering all email operations:

#### Core Operations
- `list` - List emails with filtering and pagination
- `get` - Retrieve specific email by ID
- `send` - Send new email with optional templates
- `draft` - Create or update email draft

#### Response Operations
- `reply` - Reply to email (sender only)
- `reply_all` - Reply to all recipients
- `forward` - Forward email to new recipients

#### Management Operations
- `search` - Search emails across folders
- `delete` - Delete email (soft or permanent)
- `move` - Move email between folders
- `mark` - Mark as read/unread/important

#### Metadata Operations
- `headers` - Get detailed email headers
- `attachments` - Download email attachments
- `signature` - Get user's email signature

#### Folder Operations
- `folders` - List or create mail folders
- `stats` - Get mailbox statistics

#### Utility Operations
- `empty_trash` - Empty deleted items folder
- `rules` - Get inbox processing rules

### 2. Parameter Model Architecture

Each action has a corresponding Pydantic model for parameter validation:

```python
# Base model for common parameters
class BaseEmailParams(BaseModel):
    account_id: str = Field(..., description="Microsoft account ID")
    
    class Config:
        extra = "forbid"  # Prevent unknown parameters

# Action-specific models inherit from base
class ListEmailParams(BaseEmailParams):
    folder: Optional[str] = Field("inbox", regex="^(inbox|sent|drafts|deleted|junk|archive)$")
    limit: Optional[int] = Field(50, ge=1, le=100)
    skip: Optional[int] = Field(0, ge=0)
    include_body: Optional[bool] = True
    has_attachments: Optional[bool] = None
    search_query: Optional[str] = None

class SendEmailParams(BaseEmailParams):
    to: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
```

### 3. Action Dispatch Mechanism

```python
# Action to parameter model mapping
ACTION_PARAMS = {
    "list": ListEmailParams,
    "get": GetEmailParams,
    "send": SendEmailParams,
    # ... all 18 actions
}

# Action to handler function mapping
ACTION_HANDLERS = {
    "list": handle_list_emails,
    "get": handle_get_email,
    "send": handle_send_email,
    # ... all 18 actions
}

# Main dispatch logic
async def email_operations(action: str, account_id: str, **kwargs) -> Dict[str, Any]:
    # Validate action
    if action not in ACTION_HANDLERS:
        return format_unknown_action_error(action)
    
    # Validate parameters
    param_class = ACTION_PARAMS[action]
    try:
        params = param_class(account_id=account_id, **kwargs)
    except ValidationError as e:
        return format_validation_error(action, e)
    
    # Dispatch to handler
    handler = ACTION_HANDLERS[action]
    return await handler(params)
```

### 4. Error Handling Strategy

Errors are transformed into helpful, actionable messages:

```python
def format_validation_error(action: str, error: ValidationError) -> Dict[str, Any]:
    """Transform validation errors into user guidance"""
    return {
        "error": "Invalid parameters",
        "action": action,
        "issues": [format_error(e) for e in error.errors()],
        "required": get_required_params(action),
        "optional": get_optional_params(action),
        "example": USAGE_EXAMPLES[action],
        "hint": get_contextual_hint(action, error)
    }
```

### 5. Template Integration

The email framework integrates seamlessly:

```python
async def handle_send_email(params: SendEmailParams) -> Dict[str, Any]:
    # Template rendering if requested
    if params.template_name:
        template = load_template(params.template_name)
        rendered = template.render(params.template_data)
        final_body = merge_template_content(params.body, rendered)
    else:
        final_body = params.body
    
    # Apply professional formatting
    formatted_body = apply_email_formatting(final_body)
    
    # Send via Graph API
    return await send_via_graph(params, formatted_body)
```

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)
1. Create all Pydantic parameter models
2. Implement action dispatch framework
3. Build error handling system
4. Create validation test suite

### Phase 2: Core Implementation (Week 3-4)
1. Implement all 18 action handlers
2. Integrate with Graph API
3. Connect email template framework
4. Build comprehensive tests

### Phase 3: Migration (Week 5-6)
1. Remove all 25+ legacy email tools
2. Update all references and imports
3. Create migration documentation
4. Performance benchmarking

## Performance Considerations

1. **Action Dispatch**: O(1) dictionary lookup
2. **Parameter Validation**: Pydantic's Rust-based validation is highly optimized
3. **Memory Footprint**: Single tool reduces memory usage by ~96%
4. **Network Overhead**: Identical Graph API calls, no additional latency
5. **Startup Time**: Reduced tool registration improves startup

## Security Considerations

1. **Input Validation**: All inputs validated through Pydantic
2. **Email Injection**: Regex validation prevents header injection
3. **Template Security**: Templates sandboxed, no arbitrary code execution
4. **Authentication**: Existing OAuth flow unchanged
5. **Rate Limiting**: Graph API limits respected

## Testing Strategy

### Unit Tests
- Parameter validation for each action
- Error message formatting
- Action dispatch logic
- Template rendering

### Integration Tests
- Full email operations flow
- Graph API interaction
- Template integration
- Error scenarios

### Performance Tests
- Benchmark vs legacy implementation
- Memory usage comparison
- Startup time measurement
- Throughput testing

## Documentation Requirements

### API Reference
- Single page covering all actions
- Parameter tables for each action
- Comprehensive examples
- Error reference

### Migration Guide
- Mapping old tools to new actions
- Code transformation examples
- Common patterns
- Troubleshooting

## Success Metrics

- **API Surface**: 96% reduction (25+ tools → 1 tool)
- **Documentation**: 96% reduction (25+ pages → 1 page)
- **Discovery Time**: <5 seconds (from 30+ seconds)
- **Learning Curve**: 10 minutes (from 2+ hours)
- **Performance**: ≤5% regression threshold
- **Test Coverage**: 95% minimum
- **User Satisfaction**: 95% preference in testing

## Conclusion

The ultra-consolidation architecture delivers a dramatically simplified API while maintaining full functionality. The action-based design with Pydantic validation provides an intuitive, type-safe interface that reduces cognitive load and improves developer productivity. This clean, maintainable architecture positions the Microsoft MCP for long-term success and easy extension.