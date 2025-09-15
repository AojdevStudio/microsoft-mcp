# Microsoft MCP Nuclear Tools Architecture

This document provides a comprehensive overview of the nuclear 5-tool architecture in the Microsoft MCP (Model Context Protocol) implementation. The tools provide complete Microsoft 365 integration through action-based interfaces.

## Nuclear Architecture Overview

The Microsoft MCP implements a **nuclear 5-tool architecture** that replaced the previous 63k token unified tool, achieving a **92% token reduction**. Each tool uses action-based routing with consistent `account_id` + `action` patterns to provide comprehensive Microsoft 365 integration including Outlook (email), OneDrive (file management), Calendar, and Contacts.

## Nuclear 5-Tool Architecture

### 1. Email Operations Tool

**`email_operations(account_id: str, action: str, **params)`**

**Description**: Comprehensive email management with action-based routing
**Actions**: `list`, `send`, `reply`, `draft`, `delete`, `move`, `search`

**Usage Examples**:
```python
# List emails
email_operations(account_id="user@company.com", action="list", folder="inbox", limit=10)

# Send email
email_operations(account_id="user@company.com", action="send",
                to="recipient@example.com", subject="Test", body="Hello")

# Reply to email
email_operations(account_id="user@company.com", action="reply",
                email_id="message-id", body="Thanks for your message")
```

### 2. Calendar Operations Tool

**`calendar_operations(account_id: str, action: str, **params)`**

**Description**: Calendar and meeting management with action-based routing
**Actions**: `list`, `create`, `update`, `delete`, `invite`

**Usage Examples**:
```python
# List calendar events
calendar_operations(account_id="user@company.com", action="list",
                   start_date="2024-01-01", end_date="2024-01-31")

# Create meeting
calendar_operations(account_id="user@company.com", action="create",
                   subject="Team Meeting", start_datetime="2024-01-15T10:00:00Z",
                   end_datetime="2024-01-15T11:00:00Z", attendees=["team@company.com"])
```

### 3. File Operations Tool

**`file_operations(account_id: str, action: str, **params)`**

**Description**: OneDrive file management with action-based routing
**Actions**: `list`, `upload`, `download`, `delete`, `share`, `search`

**Usage Examples**:
```python
# List files
file_operations(account_id="user@company.com", action="list", folder_path="/Documents")

# Upload file
file_operations(account_id="user@company.com", action="upload",
               local_path="/local/file.pdf", onedrive_path="/Documents/file.pdf")

# Share file
file_operations(account_id="user@company.com", action="share",
               file_path="/Documents/report.pdf", email="colleague@company.com")
```

### 4. Contact Operations Tool

**`contact_operations(account_id: str, action: str, **params)`**

**Description**: Contact management with action-based routing
**Actions**: `list`, `create`, `update`, `delete`, `search`

**Usage Examples**:
```python
# List contacts
contact_operations(account_id="user@company.com", action="list", limit=50)

# Create contact
contact_operations(account_id="user@company.com", action="create",
                  first_name="John", last_name="Doe", email="john@example.com")

# Search contacts
contact_operations(account_id="user@company.com", action="search", query="Smith")
```

### 5. Authentication Operations Tool

**`auth_operations(action: str, **params)`**

**Description**: Account authentication and management
**Actions**: `list`, `authenticate`, `complete_auth`

**Usage Examples**:
```python
# List authenticated accounts
auth_operations(action="list")

# Start authentication
auth_operations(action="authenticate")

# Complete authentication
auth_operations(action="complete_auth", flow_cache="device-flow-cache-data")
```

## Email Management Tools

### `list_emails(account_id, folder_name?, limit?, include_body?, search_query?, skip?)`
**Description**: List emails from a Microsoft account with filtering and pagination  
**Parameters**: 
- account_id: Microsoft account ID (required)
- folder_name: Folder to list from ('inbox', 'sent', 'drafts', etc.)
- limit: Max emails to return (default: 10, max: 50)
- include_body: Include email body content (default: True)
- search_query: Filter emails by search terms
- skip: Pagination offset (default: 0)

### `create_email_draft(account_id, to, subject, body, cc?, bcc?, attachments?)`
**Description**: Create an email draft with professional HTML formatting and automatic signature  
**Features**: Automatically formats content with professional styling, adds signature
**Attachments**: Supports file paths as attachments

### `send_email(account_id, to, subject, body, cc?, bcc?, attachments?)`
**Description**: Send an email immediately with professional HTML formatting  
**Features**: Automatic HTML formatting, signature appending, attachment support

### `get_email(account_id, email_id)`
**Description**: Get detailed information about a specific email  
**Returns**: Complete email data including headers, body, attachments

### `search_emails(account_id, query, folder?, limit?, has_attachments?)`
**Description**: Search emails using Microsoft Graph search capabilities  
**Parameters**: Advanced search with attachment filtering and folder targeting

### `reply_to_email(account_id, email_id, body, reply_all?, attachments?)`
**Description**: Reply to an existing email with professional formatting  
**Features**: Maintains conversation threading, optional reply-all

### `forward_email(account_id, email_id, to, comment?)`
**Description**: Forward an email to specified recipients with optional comment

### `mark_email_as_read(account_id, email_id, is_read?)`
**Description**: Mark emails as read or unread  
**Use Case**: Email status management

### `schedule_email(account_id, to, subject, body, send_datetime, cc?, bcc?)`
**Description**: Schedule an email to be sent at a specific future time  
**Parameters**: send_datetime in ISO format

### `delete_email(account_id, email_id, permanent?)`
**Description**: Delete an email (soft delete to recycle bin or permanent)

### `move_email(account_id, email_id, destination_folder)`
**Description**: Move an email to a different folder

### `download_email_attachments(account_id, email_id, save_dir?)`
**Description**: Download all attachments from an email to local directory

### `batch_download_attachments(account_id, email_ids, save_dir?)`
**Description**: Download attachments from multiple emails in batch

### `add_email_attachment_from_onedrive(account_id, email_id, file_path)`
**Description**: Attach a OneDrive file to an existing email

### `get_email_headers(account_id, email_id)`
**Description**: Get detailed email headers for technical analysis

### `get_mailbox_statistics(account_id)`
**Description**: Get mailbox statistics including size, message counts

### `get_email_signature(account_id)`
**Description**: Retrieve the user's email signature

### `get_email_categories(account_id)`
**Description**: List available email categories for organization

### `empty_deleted_items(account_id)`
**Description**: Permanently empty the deleted items folder

## Mail Folder Management

### `list_mail_folders(account_id)`
**Description**: List all mail folders in the user's mailbox  
**Returns**: Folder hierarchy with IDs and names

### `create_mail_folder(account_id, folder_name, parent_folder_id?)`
**Description**: Create a new mail folder, optionally under a parent folder

## Calendar Tools

### `list_calendar_events(account_id, start_date?, end_date?, limit?, calendar_id?)`
**Description**: List calendar events with date range filtering  
**Parameters**: Date filtering, specific calendar targeting

### `create_calendar_event(account_id, subject, start_datetime, end_datetime, attendees?, location?, body?, is_online_meeting?, calendar_id?)`
**Description**: Create new calendar events with meeting options  
**Features**: Teams meeting integration, attendee management

### `update_calendar_event(account_id, event_id, subject?, start_datetime?, end_datetime?, location?, body?)`
**Description**: Update existing calendar event properties

### `delete_calendar_event(account_id, event_id, send_cancellation?)`
**Description**: Delete calendar event with optional cancellation notifications

### `send_calendar_invite(account_id, subject, start_datetime, end_datetime, attendees, location?, body?, send_invitation?)`
**Description**: Send calendar invitation to attendees

### `search_calendar_events(account_id, query, start_date?, end_date?)`
**Description**: Search calendar events by text within date ranges

### `get_calendar_availability(account_id, start_date, end_date, duration_minutes?)`
**Description**: Find available time slots for scheduling meetings

### `get_calendar_list(account_id)`
**Description**: List all calendars accessible to the user

## File Management (OneDrive)

### `list_files(account_id, folder_path?, search_query?, limit?)`
**Description**: List files and folders in OneDrive with search capabilities

### `download_file(account_id, file_path, save_path?)`
**Description**: Download a file from OneDrive to local system

### `upload_file(account_id, local_path, onedrive_path?)`
**Description**: Upload a local file to OneDrive with path specification

### `create_folder(account_id, folder_name, parent_path?)`
**Description**: Create new folders in OneDrive hierarchy

### `delete_file(account_id, file_path)`
**Description**: Delete files or folders from OneDrive

### `share_file(account_id, file_path, email?, permission?, expiration_days?)`
**Description**: Share OneDrive files with permission and expiration controls  
**Permissions**: view, edit options with time-limited access

### `search_files(account_id, query, file_type?, limit?)`
**Description**: Search OneDrive files by content and type

### `get_recent_files(account_id, limit?)`
**Description**: Get recently accessed files across OneDrive

### `get_file_preview(account_id, file_path, page?)`
**Description**: Generate preview images for supported file types

### `get_file_versions(account_id, file_path)`
**Description**: List version history for OneDrive files

### `restore_file_version(account_id, file_path, version_id)`
**Description**: Restore a previous version of a file

### `get_file_permissions(account_id, file_path)`
**Description**: View sharing permissions and access rights for files

### `list_shared_files(account_id, limit?)`
**Description**: List files shared with the user

## Contact Management

### `list_contacts(account_id, search_query?, limit?)`
**Description**: List contacts with search filtering

### `create_contact(account_id, first_name, last_name, email?, mobile_phone?, company?, job_title?)`
**Description**: Create new contacts with comprehensive information

### `update_contact(account_id, contact_id, first_name?, last_name?, email?, mobile_phone?, company?, job_title?)`
**Description**: Update existing contact information

### `delete_contact(account_id, contact_id)`
**Description**: Remove contacts from address book

### `export_contacts(account_id, format?, limit?)`
**Description**: Export contacts in JSON or other formats

### `search_people(account_id, query, limit?)`
**Description**: Search across organizational directory and contacts

## User & System Tools

### `get_user_info(account_id)`
**Description**: Get detailed user profile information

### `get_out_of_office(account_id)`
**Description**: Check current out-of-office status and message

### `set_out_of_office(account_id, message, start_time?, end_time?, external_message?)`
**Description**: Configure out-of-office automatic replies with scheduling

### `disable_out_of_office(account_id)`
**Description**: Turn off out-of-office automatic replies

### `get_inbox_rules(account_id)`
**Description**: List email processing rules and filters

### `unified_search(query, account_id, entity_types?, limit?)`
**Description**: Search across all Microsoft 365 content types simultaneously  
**Entity Types**: emails, files, events, contacts, people

## Specialized Email Templates

### `send_practice_report(account_id, to, subject, location, financial_data, provider_data, period?, alerts?, recommendations?, cc?, bcc?)`
**Description**: Send formatted practice management reports with financial and provider data  
**Use Case**: Healthcare practice reporting

### `send_executive_summary(account_id, to, locations_data, period, subject?, key_insights?, cc?, bcc?)`
**Description**: Send executive summary reports across multiple locations  
**Use Case**: Multi-location business reporting

### `send_provider_update(account_id, to, provider_name, performance_data, period?, highlights?, recommendations?, subject?, cc?, bcc?)`
**Description**: Send provider performance updates with metrics and recommendations  
**Use Case**: Healthcare provider performance tracking

### `send_alert_notification(account_id, to, alert_type, title, message, urgency?, impact?, recommended_actions?, subject?, cc?, bcc?)`
**Description**: Send urgent alert notifications with structured formatting  
**Features**: Urgency-based formatting, action recommendations

## Architecture Notes

### Authentication Flow
1. Use `authenticate_account()` to initiate device flow
2. User visits URL and enters code
3. Use `complete_authentication()` to finalize
4. Use `list_accounts()` to get account_id for subsequent operations

### HTML Email Formatting
All email tools automatically:
- Apply professional HTML styling
- Add consistent signature
- Ensure cross-client compatibility
- Support both plain text and HTML content

### Error Handling
All tools implement consistent error handling with:
- Descriptive error messages
- Proper exception types
- Authentication status checking
- Rate limiting compliance

### Data Formats
- Dates: ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- Files: Support for both local paths and OneDrive paths
- Emails: Support for single strings or arrays
- Search: Microsoft Graph search syntax

### Performance Considerations
- Pagination support for large datasets
- Batch operations for efficiency
- Selective field retrieval to minimize payload
- Configurable limits to prevent timeouts

## Integration Patterns

### Email-First Workflow
1. `list_accounts()` → Get account
2. `list_emails()` → Browse emails
3. `reply_to_email()` or `send_email()` → Respond

### File Management Workflow
1. `list_files()` → Browse OneDrive
2. `download_file()` or `upload_file()` → Transfer files
3. `share_file()` → Collaborate

### Calendar Management Workflow
1. `get_calendar_availability()` → Find free time
2. `create_calendar_event()` → Schedule meeting
3. `send_calendar_invite()` → Invite attendees

This architecture provides comprehensive Microsoft 365 integration with consistent patterns, professional formatting, and robust error handling across all tools.