# Microsoft MCP

Powerful MCP server for Microsoft Graph API - a complete AI assistant toolkit for Outlook, Calendar, OneDrive, and Contacts.

## Features

- **Email Management**: Read, send, reply, manage attachments, organize folders
- **Professional Email Templates**: KamDental-branded templates with automatic theme selection
- **Calendar Intelligence**: Create, update, check availability, respond to invitations
- **OneDrive Files**: Upload, download, browse with pagination
- **Contacts**: Search and list contacts from your address book
- **Multi-Account**: Support for multiple Microsoft accounts (personal, work, school)
- **Unified Search**: Search across emails, files, events, and people

## Quick Start with Claude Desktop

```bash
# Add Microsoft MCP server (replace with your Azure app ID)
claude mcp add microsoft-mcp -e MICROSOFT_MCP_CLIENT_ID=your-app-id-here -- uvx --from git+https://github.com/elyxlz/microsoft-mcp.git microsoft-mcp

# Start Claude Desktop
claude
```

### Usage Examples

```bash
# Email examples
> read my latest emails with full content
> reply to the email from John saying "I'll review this today"
> send an email with attachment to alice@example.com

# Professional email templates
> send a practice report for Baytown location with this month's financial data
> send an executive summary across all locations
> send a provider performance update for Dr. Johnson
> send an alert notification about system downtime

# Calendar examples  
> show my calendar for next week
> check if I'm free tomorrow at 2pm
> create a meeting with Bob next Monday at 10am

# File examples
> list files in my OneDrive
> upload this report to OneDrive
> search for "project proposal" across all my files

# Multi-account
> list all my Microsoft accounts
> send email from my work account
```

## Available Tools

### Email Tools
- **`list_emails`** - List emails with optional body content
- **`get_email`** - Get specific email with attachments
- **`create_email_draft`** - Create email draft with attachments support
- **`send_email`** - Send email immediately with CC/BCC and attachments
- **`reply_to_email`** - Reply maintaining thread context
- **`reply_all_email`** - Reply to all recipients in thread
- **`update_email`** - Mark emails as read/unread
- **`move_email`** - Move emails between folders
- **`delete_email`** - Delete emails
- **`get_attachment`** - Get email attachment content
- **`search_emails`** - Search emails by query

### Professional Email Templates
- **`send_practice_report`** - Send branded practice performance report
- **`send_executive_summary`** - Send multi-location executive overview
- **`send_provider_update`** - Send provider performance update
- **`send_alert_notification`** - Send urgent alerts and notifications

#### Email Template Features
- **Automatic Theme Selection**: Baytown (blue), Humble (green), or Executive (dark) based on location/recipient
- **Mobile Responsive**: Optimized for all devices and email clients
- **Professional Design**: Consistent branding with KamDental visual identity
- **Performance Optimized**: <2 second rendering, <100KB total size
- **Accessibility**: WCAG 2.1 AA compliant with screen reader support

### Calendar Tools
- **`list_events`** - List calendar events with details
- **`get_event`** - Get specific event details
- **`create_event`** - Create events with location and attendees
- **`update_event`** - Reschedule or modify events
- **`delete_event`** - Cancel events
- **`respond_event`** - Accept/decline/tentative response to invitations
- **`check_availability`** - Check free/busy times for scheduling
- **`search_events`** - Search calendar events

### Contact Tools
- **`list_contacts`** - List all contacts
- **`get_contact`** - Get specific contact details
- **`create_contact`** - Create new contact
- **`update_contact`** - Update contact information
- **`delete_contact`** - Delete contact
- **`search_contacts`** - Search contacts by query

### File Tools
- **`list_files`** - Browse OneDrive files and folders
- **`get_file`** - Download file content
- **`create_file`** - Upload files to OneDrive
- **`update_file`** - Update existing file content
- **`delete_file`** - Delete files or folders
- **`search_files`** - Search files in OneDrive

### Utility Tools
- **`unified_search`** - Search across emails, events, and files
- **`list_accounts`** - Show authenticated Microsoft accounts
- **`authenticate_account`** - Start authentication for a new Microsoft account
- **`complete_authentication`** - Complete the authentication process after entering device code

## Manual Setup

### 1. Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Microsoft Entra ID → App registrations
2. New registration → Name: `microsoft-mcp`
3. Supported account types: Personal + Work/School
4. Authentication → Allow public client flows: Yes
5. API permissions → Add these delegated permissions:
   - Mail.ReadWrite
   - Calendars.ReadWrite
   - Files.ReadWrite
   - Contacts.Read
   - People.Read
   - User.Read
6. Copy Application ID

### 2. Installation

```bash
git clone https://github.com/elyxlz/microsoft-mcp.git
cd microsoft-mcp
uv sync
```

### 3. Authentication

```bash
# Set your Azure app ID
export MICROSOFT_MCP_CLIENT_ID="your-app-id-here"

# Run authentication script
uv run authenticate.py

# Follow the prompts to authenticate your Microsoft accounts
```

### 4. Claude Desktop Configuration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "microsoft": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/elyxlz/microsoft-mcp.git", "microsoft-mcp"],
      "env": {
        "MICROSOFT_MCP_CLIENT_ID": "your-app-id-here"
      }
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "microsoft": {
      "command": "uv",
      "args": ["--directory", "/path/to/microsoft-mcp", "run", "microsoft-mcp"],
      "env": {
        "MICROSOFT_MCP_CLIENT_ID": "your-app-id-here"
      }
    }
  }
}
```

## Multi-Account Support

All tools require an `account_id` parameter as the first argument:

```python
# List accounts to get IDs
accounts = list_accounts()
account_id = accounts[0]["account_id"]

# Use account for operations
send_email(account_id, "user@example.com", "Subject", "Body")
list_emails(account_id, limit=10, include_body=True)
create_event(account_id, "Meeting", "2024-01-15T10:00:00Z", "2024-01-15T11:00:00Z")
```

## Professional Email Templates

The KamDental Email Framework provides professional, branded email templates:

### Practice Report Example
```python
await send_practice_report(
    account_id="default",
    to="manager@kamdental.com",
    subject="Baytown Practice Report - January 2024",
    location="Baytown",
    financial_data={
        "production": {"value": 285000, "goal": 300000},
        "collections": {"value": 270000, "ratio": 0.947},
        "case_acceptance": {"value": 0.72, "goal": 0.75},
        "call_answer_rate": {"value": 0.91, "goal": 0.95}
    },
    provider_data=[
        {
            "name": "Dr. Sarah Johnson",
            "role": "General Dentist",
            "production": 125000,
            "goal_percentage": 1.04
        }
    ],
    period="January 2024",
    alerts=[
        {
            "type": "warning",
            "title": "Production Below Target",
            "message": "Current production is 5% below monthly target."
        }
    ]
)
```

### Executive Summary Example
```python
await send_executive_summary(
    account_id="default",
    to="executive@kamdental.com",
    locations_data=[
        {
            "name": "Baytown",
            "production": 285000,
            "target": 300000,
            "status": "warning"
        },
        {
            "name": "Humble",
            "production": 195000,
            "target": 180000,
            "status": "ahead"
        }
    ],
    period="Q1 2024",
    key_insights=[
        {
            "title": "Overall Performance",
            "description": "Combined production at 96% of target"
        }
    ]
)
```

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Type checking
uv run pyright

# Format code
uvx ruff format .

# Lint
uvx ruff check --fix --unsafe-fixes .

# Test email framework
uv run python -m microsoft_mcp.email_framework.test_runner
```

## Example: AI Assistant Scenarios

### Smart Email Management
```python
# Get account ID first
accounts = list_accounts()
account_id = accounts[0]["account_id"]

# List latest emails with full content
emails = list_emails(account_id, limit=10, include_body=True)

# Reply maintaining thread
reply_to_email(account_id, email_id, "Thanks for your message. I'll review and get back to you.")

# Forward with attachments
email = get_email(email_id, account_id)
attachments = [get_attachment(email_id, att["id"], account_id) for att in email["attachments"]]
send_email(account_id, "boss@company.com", f"FW: {email['subject']}", email["body"]["content"], attachments=attachments)
```

### Intelligent Scheduling
```python
# Get account ID first
accounts = list_accounts()
account_id = accounts[0]["account_id"]

# Check availability before scheduling
availability = check_availability(account_id, "2024-01-15T10:00:00Z", "2024-01-15T18:00:00Z", ["colleague@company.com"])

# Create meeting with details
create_event(
    account_id,
    "Project Review",
    "2024-01-15T14:00:00Z", 
    "2024-01-15T15:00:00Z",
    location="Conference Room A",
    body="Quarterly review of project progress",
    attendees=["colleague@company.com", "manager@company.com"]
)
```

## Security Notes

- Tokens are cached locally in `~/.microsoft_mcp_token_cache.json`
- Use app-specific passwords if you have 2FA enabled
- Only request permissions your app actually needs
- Consider using a dedicated app registration for production

## Troubleshooting

- **Authentication fails**: Check your CLIENT_ID is correct
- **"Need admin approval"**: Use `MICROSOFT_MCP_TENANT_ID=consumers` for personal accounts
- **Missing permissions**: Ensure all required API permissions are granted in Azure
- **Token errors**: Delete `~/.microsoft_mcp_token_cache.json` and re-authenticate

## Documentation

- [Email Framework Guide](docs/email-framework-guide.md) - Comprehensive guide to professional email templates
- [API Documentation](docs/api.md) - Detailed API reference
- [Examples](examples/) - Code examples and use cases

## License

MIT