# [FEATURE] Ultra-Consolidation: Single Email Operations Tool

## Metadata
- **Priority:** High
- **Status:** Backlog
- **Assignee:** AI Agent
- **Estimate:** 16 Story Points
- **Issue ID:** MSFT-701
- **Labels:** 
  - type:feature
  - priority:high
  - agent-ready
  - ultra-consolidation
  - api-redesign
  - breaking-change

## Problem Statement

### What
Consolidate all 25+ email tools into a single `email_operations()` tool with action-based parameters, reducing the API surface area by 96% while maintaining full functionality and improving discoverability.

### Why
**Current Issues:**
- **API Sprawl:** 25+ email tools create cognitive overload for users
- **Discovery Nightmare:** Users don't know which tool to use for specific tasks
- **Maintenance Burden:** Each tool requires separate documentation, tests, and updates
- **Inconsistent Patterns:** Similar operations have different parameter names across tools
- **Context Switching:** Users must remember different tool names for related operations

**Business Impact:**
- Reduce onboarding time from hours to minutes
- Eliminate tool selection paralysis
- Simplify documentation from 25+ pages to 1 comprehensive guide
- Enable faster feature development with unified patterns
- Improve AI assistant performance with fewer tool choices

### Context
Analysis of the 25+ email tools shows significant overlap:
- List operations: `list_emails`, `list_my_issues`, `list_mail_folders`, `list_shared_files`
- Send operations: `send_email`, `reply_to_email`, `forward_email`, `schedule_email`
- Management: `mark_as_read`, `delete_email`, `move_email`, `empty_deleted_items`
- Search: `search_emails`, `search_people`, `unified_search`

A single tool with action parameters can handle all operations more intuitively.

## Acceptance Criteria

- [ ] **AC1:** Single `email_operations()` tool replaces all 25+ email tools with full functionality preservation
- [ ] **AC2:** Action parameter supports: list, send, reply, forward, draft, get, search, delete, move, mark_read, get_headers, get_signature
- [ ] **AC3:** Smart parameter validation - only relevant parameters required based on action
- [ ] **AC4:** Template support integrated seamlessly - templates work with send/draft/reply actions
- [ ] **AC5:** All 25+ legacy email tools completely removed from codebase
- [ ] **AC6:** Attachment handling unified - works across send/reply/forward/draft actions
- [ ] **AC7:** Comprehensive error messages guide users to correct action/parameter combinations
- [ ] **AC8:** Performance remains within 5% of current implementation
- [ ] **AC9:** Auto-complete/IntelliSense provides action options and required parameters
- [ ] **AC10:** Clean implementation with zero legacy code or compatibility layers

## Technical Requirements

### Implementation Notes

**Core Design Pattern:**
```python
from typing import Literal, Any, Optional
from pydantic import Field
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool
async def email_operations(
    action: Literal[
        "list",      # List emails with filters
        "get",       # Get specific email by ID
        "send",      # Send new email
        "draft",     # Create draft
        "reply",     # Reply to email
        "forward",   # Forward email
        "search",    # Search emails
        "delete",    # Delete email
        "move",      # Move to folder
        "mark_read", # Mark read/unread
        "headers",   # Get email headers
        "signature", # Get user signature
        "stats",     # Get mailbox statistics
        "folders",   # List/manage folders
        "download_attachments"  # Download attachments
    ],
    account_id: str,
    # Context-sensitive parameters based on action
    **kwargs: Any
) -> dict[str, Any]:
    """Unified email operations for Microsoft 365."""
```

**Parameter Validation Matrix:**
```python
from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field

class ListEmailParams(BaseModel):
    folder: Optional[str] = Field(default="inbox", description="Email folder")
    limit: Optional[int] = Field(default=50, ge=1, le=100)
    skip: Optional[int] = Field(default=0, ge=0)
    include_body: Optional[bool] = Field(default=True)
    has_attachments: Optional[bool] = None

class SendEmailParams(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    template_name: Optional[str] = None
    template_data: Optional[dict] = None
    location: Optional[str] = None

# Map actions to their parameter models
ACTION_PARAMS = {
    "list": ListEmailParams,
    "send": SendEmailParams,
    # ... etc
}
```

**Smart Parameter Resolution:**
- Use Pydantic models or TypedDict for each action's parameters
- Runtime validation using Python type hints and FastMCP
- Clear error messages for missing/invalid parameters
- Auto-suggest correct parameters for common mistakes
- No legacy code paths or compatibility checks

### API Design Specification

#### Unified Email Operations
```python
# List emails
result = email_operations(
    action="list",
    account_id="user@company.com",
    folder="inbox",
    limit=50,
    has_attachments=True
)

# Send email with template
result = email_operations(
    action="send",
    account_id="user@company.com",
    to="recipient@example.com",
    subject="Monthly Report",
    body="See attached report",
    template_name="practice_report",
    template_data={
        "location": "baytown",
        "financial_data": {...},
        "provider_data": [...]
    }
)

# Reply to email
result = email_operations(
    action="reply",
    account_id="user@company.com",
    email_id="AAMkAGI2...",
    body="Thanks for your message",
    reply_all=True
)

# Search emails
result = email_operations(
    action="search",
    account_id="user@company.com",
    query="project deadline",
    folder="sent",
    limit=20
)
```

#### Clean Implementation
```python
# Only the new unified API exists
email_operations(action="send", account_id="...", to="...", subject="...", body="...")

# Old tools are completely removed - no legacy code
# No deprecation warnings needed
# No translation layers
```

### Testing Requirements
- [ ] **Unit Tests** - Framework: pytest, Coverage: 95%, Location: `tests/test_email_operations.py`
- [ ] **Parameter Validation Tests** - Test all action/parameter combinations
- [ ] **Performance Tests** - Benchmark to ensure <5% regression
- [ ] **Integration Tests** - Test with real Graph API calls
- [ ] **Edge Case Tests** - Invalid actions, missing parameters, etc.

### Dependencies
- **Files to Create:**
  - `src/microsoft_mcp/tools.py` - Replace with new unified tool implementation
  - `src/microsoft_mcp/email_operations.py` - Email operation handlers
  - `src/microsoft_mcp/email_params.py` - Parameter type definitions
- **Files to Delete:**
  - All 25+ individual email tool implementations

## Definition of Done
- [ ] All acceptance criteria met and validated
- [ ] Code reviewed with focus on clean API design
- [ ] 95% test coverage achieved
- [ ] Performance benchmarks within 5% tolerance
- [ ] Documentation created fresh with comprehensive examples
- [ ] All legacy email tools completely removed
- [ ] No compatibility code or deprecation warnings exist
- [ ] IntelliSense/auto-complete configuration added

## Agent Context

### Implementation Strategy
1. **Phase 1:** Design and implement `email_operations()` with all actions
2. **Phase 2:** Remove all 25+ legacy email tools
3. **Phase 3:** Update tests to use new unified API
4. **Phase 4:** Create fresh documentation
5. **Phase 5:** Deploy clean implementation

### Clean API Design

**Only This Exists:**
```python
# Single unified tool for all email operations
emails = email_operations(action="list", account_id="...", folder="inbox", limit=10)
email_operations(action="send", account_id="...", to="...", subject="...", body="...")
email_operations(action="reply", account_id="...", email_id="...", body="...", reply_all=True)
email_operations(action="search", account_id="...", query="important", folder="inbox")
email_operations(action="mark_read", account_id="...", email_id="...", is_read=True)

# No legacy functions exist - clean implementation only
```

## Validation Steps

### Automated Verification
- [ ] All email operations work through unified tool
- [ ] Parameter validation catches invalid combinations
- [ ] No legacy code paths exist in codebase
- [ ] Performance tests show <5% regression
- [ ] Clean implementation with zero tech debt

### Manual Verification
1. **Tool Discovery:** New users can understand email operations in <5 minutes
2. **Action Selection:** IntelliSense shows all available actions
3. **Parameter Guidance:** Clear errors for missing/invalid parameters
4. **Template Integration:** All email templates work seamlessly
5. **Complex Operations:** Multi-step workflows simplified

## Success Metrics
- **API Reduction:** 25+ tools → 1 tool (96% reduction)
- **Documentation:** 25+ pages → 1 comprehensive page (96% reduction)
- **Learning Curve:** 2 hours → 10 minutes (88% reduction)
- **Tool Selection Time:** 30 seconds → instant (action parameter)
- **Maintenance Burden:** 25+ implementations → 1 clean implementation
- **Technical Debt:** 100% eliminated - no legacy code

## Clean Implementation Benefits
- **No Migration Needed:** Fresh start with optimal design
- **Zero Legacy Code:** No compatibility layers to maintain
- **Performance:** No overhead from compatibility checks
- **Simplicity:** Single code path for all operations
- **Maintainability:** No deprecation timelines to manage