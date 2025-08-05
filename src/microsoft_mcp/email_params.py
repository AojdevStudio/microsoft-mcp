"""Email parameter models for Microsoft MCP operations.

This module defines Pydantic models for validating parameters
across all email operations in the unified email_operations tool.
"""

import re
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BaseEmailParams(BaseModel):
    """Base parameter model for all email operations.
    
    Provides common fields and configuration for all email operations.
    All operation-specific models inherit from this base class.
    """
    
    account_id: str = Field(
        ...,
        min_length=1,
        description="Microsoft account ID from list_accounts()",
        examples=["user@company.com"]
    )
    
    model_config = ConfigDict(
        extra="forbid",  # Reject unknown parameters for security
        validate_assignment=True,  # Validate on assignment
        use_enum_values=True,  # Use enum values directly
        json_schema_extra={
            "example": {
                "account_id": "user@company.com"
            }
        }
    )


# Email validation regex pattern
EMAIL_REGEX = re.compile(r'^[^@]+@[^@]+\.[^@]+$')


def _validate_email_list(email_list: List[str]) -> List[str]:
    """Validate and normalize a list of email addresses.
    
    Args:
        email_list: List of email addresses to validate
        
    Returns:
        List of validated and normalized (lowercase) email addresses
        
    Raises:
        ValueError: If any email address is invalid
    """
    validated = []
    for email in email_list:
        if not email:  # Check for empty string
            raise ValueError("Email address cannot be empty")
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email format: {email}")
        validated.append(email.lower())
    return validated


def _normalize_to_list(value: Union[str, List[str], None]) -> Optional[List[str]]:
    """Convert single item to list or return None/list unchanged.
    
    Args:
        value: Single item, list, or None
        
    Returns:
        List, None, or original list unchanged
    """
    if value is None:
        return value
    if isinstance(value, str):
        return [value]
    return value


class ListEmailParams(BaseEmailParams):
    """Parameters for listing emails.
    
    Retrieves emails from a specified folder with optional filtering
    and pagination support.
    """
    
    folder: Optional[Literal["inbox", "sent", "drafts", "deleted", "junk", "archive"]] = Field(
        default="inbox",
        description="Folder to list emails from"
    )
    limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=250,
        description="Maximum number of emails to return (1-250)"
    )
    skip: Optional[int] = Field(
        default=0,
        ge=0,
        description="Number of emails to skip for pagination"
    )
    include_body: Optional[bool] = Field(
        default=True,
        description="Whether to include email body content"
    )
    has_attachments: Optional[bool] = Field(
        default=None,
        description="Filter for emails with attachments"
    )
    search_query: Optional[str] = Field(
        default=None,
        description="Optional search query to filter emails"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "folder": "inbox",
                "limit": 20,
                "include_body": True
            }
        }
    )


class GetEmailParams(BaseEmailParams):
    """Parameters for retrieving a specific email.
    
    Fetches detailed information about a single email message
    by its unique identifier.
    """
    
    email_id: str = Field(
        ...,
        description="Unique identifier of the email message"
    )
    include_attachments: Optional[bool] = Field(
        default=True,
        description="Whether to include attachment metadata"
    )
    include_headers: Optional[bool] = Field(
        default=False,
        description="Whether to include full email headers"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "include_attachments": True
            }
        }
    )


class SendEmailParams(BaseEmailParams):
    """Parameters for sending an email.
    
    Creates and sends a new email message with optional attachments
    and professional templates.
    """
    
    to: Union[str, List[str]] = Field(
        ...,
        description="Primary recipient email address(es)"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Email subject line"
    )
    body: str = Field(
        ...,
        description="Email body content (plain text or HTML)"
    )
    cc: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="CC recipient email address(es)"
    )
    bcc: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="BCC recipient email address(es)"
    )
    attachments: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="File path(s) to attach"
    )
    importance: Optional[Literal["low", "normal", "high"]] = Field(
        default="normal",
        description="Email importance level"
    )
    template: Optional[str] = Field(
        default=None,
        description="Email template to use for formatting"
    )
    
    @field_validator("to", "cc", "bcc", mode="before")
    @classmethod
    def normalize_recipients(cls, v):
        """Convert single recipient to list."""
        return _normalize_to_list(v)
    
    @field_validator("to", "cc", "bcc", mode="after")
    @classmethod
    def validate_email_list(cls, v):
        """Validate email addresses in list."""
        if v is None:
            return v
        return _validate_email_list(v)
    
    @field_validator("attachments", mode="before")
    @classmethod
    def normalize_attachments(cls, v):
        """Convert single attachment to list."""
        return _normalize_to_list(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "to": "recipient@example.com",
                "subject": "Meeting Tomorrow",
                "body": "Let's discuss the project status.",
                "cc": ["manager@company.com"],
                "importance": "high"
            }
        }
    )


class DraftEmailParams(SendEmailParams):
    """Parameters for creating or updating an email draft.
    
    Extends SendEmailParams with an optional draft_id for updating
    existing drafts.
    """
    
    draft_id: Optional[str] = Field(
        default=None,
        description="ID of existing draft to update (None creates new draft)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "to": "recipient@example.com",
                "subject": "Draft: Project Update",
                "body": "Working on the quarterly report...",
                "draft_id": "AAMkAGI2THQAA="
            }
        }
    )


class ReplyEmailParams(BaseEmailParams):
    """Parameters for replying to an email.
    
    Creates a reply to an existing email message with optional
    inclusion of the original message content.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email to reply to"
    )
    body: str = Field(
        ...,
        description="Reply message body content"
    )
    reply_all: Optional[bool] = Field(
        default=False,
        description="Whether to reply to all recipients"
    )
    attachments: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="File path(s) to attach to the reply"
    )
    include_original: Optional[bool] = Field(
        default=True,
        description="Whether to include the original message in the reply"
    )
    
    @field_validator("attachments", mode="before")
    @classmethod
    def normalize_attachments(cls, v):
        """Convert single attachment to list."""
        return _normalize_to_list(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "body": "Thanks for your message. I agree with your proposal.",
                "reply_all": True,
                "include_original": True
            }
        }
    )


class ForwardEmailParams(BaseEmailParams):
    """Parameters for forwarding an email.
    
    Forwards an existing email message to new recipients with
    an optional comment.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email to forward"
    )
    to: Union[str, List[str]] = Field(
        ...,
        description="Recipient email address(es) to forward to"
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional comment to add to the forwarded email"
    )
    include_attachments: Optional[bool] = Field(
        default=True,
        description="Whether to include original attachments"
    )
    
    @field_validator("to", mode="before")
    @classmethod
    def normalize_recipients(cls, v):
        """Convert single recipient to list."""
        return _normalize_to_list(v)
    
    @field_validator("to", mode="after")
    @classmethod
    def validate_email_list(cls, v):
        """Validate email addresses in list."""
        return _validate_email_list(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "to": ["colleague@company.com"],
                "comment": "FYI - Please review this proposal.",
                "include_attachments": True
            }
        }
    )


class SearchEmailParams(BaseEmailParams):
    """Parameters for searching emails.
    
    Searches emails across folders with comprehensive filtering options
    including query, date ranges, and sender/recipient filters.
    """
    
    query: str = Field(
        ...,
        description="Search query (searches in subject, body, from, to fields)"
    )
    folder: Optional[Literal["inbox", "sent", "drafts", "deleted", "junk", "archive"]] = Field(
        default=None,
        description="Optional folder to search in (searches all if not specified)"
    )
    from_address: Optional[str] = Field(
        default=None,
        description="Filter by sender email address"
    )
    to_address: Optional[str] = Field(
        default=None,
        description="Filter by recipient email address"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date for date range filter (ISO format: YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date for date range filter (ISO format: YYYY-MM-DD)"
    )
    has_attachments: Optional[bool] = Field(
        default=None,
        description="Filter for emails with attachments"
    )
    limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=250,
        description="Maximum number of results to return (1-250)"
    )
    
    @field_validator("from_address", "to_address")
    @classmethod
    def validate_email_format(cls, email: Optional[str]) -> Optional[str]:
        """Validate email addresses if provided."""
        if email and not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email format: {email}")
        return email.lower() if email else email
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "query": "project proposal",
                "folder": "inbox",
                "from_address": "manager@company.com",
                "start_date": "2024-01-01",
                "limit": 20
            }
        }
    )


class DeleteEmailParams(BaseEmailParams):
    """Parameters for deleting an email.
    
    Deletes an email message either permanently or by moving it
    to the Deleted Items folder.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email to delete"
    )
    permanent: Optional[bool] = Field(
        default=False,
        description="If True, permanently delete. If False, move to Deleted Items."
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "permanent": False
            }
        }
    )


class MoveEmailParams(BaseEmailParams):
    """Parameters for moving an email between folders.
    
    Moves an email message from its current folder to a
    specified destination folder.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email to move"
    )
    destination_folder: Literal["inbox", "sent", "drafts", "deleted", "junk", "archive"] = Field(
        ...,
        description="Destination folder name"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "destination_folder": "archive"
            }
        }
    )


class MarkEmailParams(BaseEmailParams):
    """Parameters for marking email status.
    
    Updates the status of one or more emails (read/unread,
    important/not important).
    """
    
    email_id: Union[str, List[str]] = Field(
        ...,
        description="Email ID(s) to mark"
    )
    mark_as: Literal["read", "unread", "important", "not_important"] = Field(
        ...,
        description="Status to set for the email(s)"
    )
    
    @field_validator("email_id", mode="before")
    @classmethod
    def normalize_email_ids(cls, v):
        """Convert single email ID to list."""
        if isinstance(v, str):
            return [v]
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": ["AAMkAGI2THQAA=", "AAMkAGI2THQBB="],
                "mark_as": "read"
            }
        }
    )


class HeadersParams(BaseEmailParams):
    """Parameters for retrieving email headers.
    
    Fetches detailed email headers including routing information
    and technical metadata.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email to get headers for"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA="
            }
        }
    )


class AttachmentsParams(BaseEmailParams):
    """Parameters for managing email attachments.
    
    Downloads attachments from an email message to a specified
    directory on the local filesystem.
    """
    
    email_id: str = Field(
        ...,
        description="ID of the email with attachments"
    )
    save_dir: Optional[str] = Field(
        default="~/Downloads",
        description="Directory to save attachments"
    )
    attachment_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific attachment IDs to download (downloads all if not specified)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "email_id": "AAMkAGI2THQAA=",
                "save_dir": "/Users/john/Documents/attachments"
            }
        }
    )


class SignatureParams(BaseEmailParams):
    """Parameters for retrieving email signature.
    
    Gets the user's configured email signature for use
    in composing messages.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com"
            }
        }
    )


class FolderParams(BaseEmailParams):
    """Parameters for folder operations.
    
    Manages email folders including listing, creating, renaming,
    and deleting folders.
    """
    
    operation: Literal["list", "create", "rename", "delete"] = Field(
        ...,
        description="Folder operation to perform"
    )
    folder_name: Optional[str] = Field(
        default=None,
        description="Folder name (required for create, rename, delete)"
    )
    new_name: Optional[str] = Field(
        default=None,
        description="New folder name (required for rename operation)"
    )
    parent_folder: Optional[str] = Field(
        default=None,
        description="Parent folder for nested folders"
    )
    
    @model_validator(mode="after")
    def validate_required_fields(self):
        """Ensure required fields are provided based on operation."""
        if self.operation in ["create", "rename", "delete"] and not self.folder_name:
            raise ValueError(f"folder_name is required for {self.operation} operation")
        if self.operation == "rename" and not self.new_name:
            raise ValueError("new_name is required for rename operation")
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "operation": "create",
                "folder_name": "Project Alpha",
                "parent_folder": "inbox"
            }
        }
    )


class StatsParams(BaseEmailParams):
    """Parameters for mailbox statistics.
    
    Retrieves statistics about the mailbox including storage
    usage and message counts.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com"
            }
        }
    )


class EmptyTrashParams(BaseEmailParams):
    """Parameters for emptying the trash folder.
    
    Permanently deletes all emails in the Deleted Items folder.
    """
    
    confirm: bool = Field(
        ...,
        description="Must be True to confirm permanent deletion"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com",
                "confirm": True
            }
        }
    )


class RulesParams(BaseEmailParams):
    """Parameters for retrieving inbox rules.
    
    Gets the configured inbox rules for automatic email processing.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "user@company.com"
            }
        }
    )