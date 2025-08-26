# Unified Tool Usage Patterns

## Tool Architecture Overview
5 focused tools with action-based routing:
- `email_operations(account_id, action, ...)`
- `calendar_operations(account_id, action, ...)`
- `contact_operations(account_id, action, ...)`
- `file_operations(account_id, action, ...)`
- `auth_operations(account_id, action, ...)`

## Usage Examples

### Email Operations
```python
# Send email
email_operations(
    account_id="user@company.com",
    action="send",
    to="recipient@example.com",
    subject="Monthly Report",
    body="Please find attached...",
    cc=["manager@company.com"],
    attachments=["/path/to/report.pdf"]
)

# List emails
email_operations(
    account_id="user@company.com",
    action="list",
    folder_name="Inbox",
    limit=50,
    search_query="urgent"
)
```

### Calendar Operations
```python
# Create event
calendar_operations(
    account_id="user@company.com",
    action="create",
    subject="Team Meeting",
    start_datetime="2024-12-26T10:00:00",
    end_datetime="2024-12-26T11:00:00",
    attendees=["team@company.com"]
)
```

## Migration from Old Architecture
- OLD: 61+ individual tools with different parameter patterns
- NEW: 5 focused tools with consistent `account_id` + `action` pattern
- All operations now follow unified error handling
- Pagination works consistently across all listing operations

## Multi-Account Support
- Every tool requires `account_id` as first parameter
- Supports multiple Microsoft accounts simultaneously
- Token management handled automatically per account
- Consistent authentication across all Microsoft 365 services