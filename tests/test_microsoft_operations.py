"""Tests for microsoft_operations unified tool.

This module tests the action-based routing and parameter validation
of the new unified microsoft_operations tool.
"""

from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from microsoft_mcp.tools import microsoft_operations

# Access the actual function from the FunctionTool decorator
microsoft_operations_func = microsoft_operations.fn


class TestMicrosoftOperations:
    """Test the unified microsoft_operations tool."""

    @pytest.fixture
    def mock_graph_request(self):
        """Mock Graph API request function."""
        with patch("microsoft_mcp.tools.graph.request") as mock:
            yield mock

    def test_unknown_action_raises_error(self):
        """Test that unknown action raises ValueError."""
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="unknown.action"
            )
        assert "Unknown action: unknown.action" in str(exc.value)

    def test_email_list_action(self, mock_graph_request):
        """Test email.list action handler."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "value": [
                {
                    "id": "msg1",
                    "subject": "Test Email",
                    "from": {"emailAddress": {"address": "sender@example.com"}}
                }
            ]
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.list",
            data={"folder": "inbox"},
            options={"limit": 10}
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.list"
        assert result["count"] == 1
        assert len(result["emails"]) == 1
        assert result["emails"][0]["id"] == "msg1"

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "GET"
        assert "/me/mailFolders/inbox/messages" in call_args[0][1]

    def test_email_send_action_validation(self):
        """Test email.send action parameter validation."""
        # Missing required parameter: to
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.send",
                data={"subject": "Test", "body": "Content"}
            )
        assert "Missing required parameter: to" in str(exc.value)

        # Missing required parameter: subject
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.send",
                data={"to": "recipient@example.com", "body": "Content"}
            )
        assert "Missing required parameter: subject" in str(exc.value)

        # Missing required parameter: body
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.send",
                data={"to": "recipient@example.com", "subject": "Test"}
            )
        assert "Missing required parameter: body" in str(exc.value)

    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_send_action_success(self, mock_validate, mock_graph_request):
        """Test successful email.send action."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.send",
            data={
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test content"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.send"
        assert result["to"] == ["recipient@example.com"]
        assert result["subject"] == "Test Subject"
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/sendMail" in call_args[0][1]

    @patch("microsoft_mcp.email_framework.utils.style_email_content")
    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_send_with_template(self, mock_validate, mock_style, mock_graph_request):
        """Test email.send action with template styling."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock email styling
        mock_style.return_value = "<html><body>Styled content</body></html>"

        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with template
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.send",
            data={
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test content",
                "template_data": {"location": "Baytown"}
            },
            template="practice_report",
            options={"theme": "baytown"}
        )

        # Verify template was used
        assert result["template_used"] == "practice_report"

        # Verify styling was applied
        mock_style.assert_called_once()
        style_args = mock_style.call_args[1]
        assert style_args["template_type"] == "practice_report"
        assert style_args["theme"] == "baytown"

    def test_email_reply_action_validation(self):
        """Test email.reply action parameter validation."""
        # Missing email_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.reply",
                data={"body": "Reply content"}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

        # Missing body
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.reply",
                data={"email_id": "msg123"}
            )
        assert "Missing required parameter: body" in str(exc.value)

    def test_email_reply_action_success(self, mock_graph_request):
        """Test successful email.reply action."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.reply",
            data={
                "email_id": "msg123",
                "body": "Reply content"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.reply"
        assert result["email_id"] == "msg123"
        assert result["reply_all"] is False

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/messages/msg123/reply" in call_args[0][1]

    def test_email_reply_all_action(self, mock_graph_request):
        """Test email.reply action with reply_all."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with reply_all
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.reply",
            data={
                "email_id": "msg123",
                "body": "Reply to all",
                "reply_all": True
            }
        )

        # Verify reply_all was used
        assert result["reply_all"] is True

        # Verify Graph API call
        call_args = mock_graph_request.call_args
        assert "/me/messages/msg123/replyAll" in call_args[0][1]

    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_draft_action(self, mock_validate, mock_graph_request):
        """Test email.draft action."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock Graph API response
        mock_graph_request.return_value = {"id": "draft123"}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.draft",
            data={
                "to": "recipient@example.com",
                "subject": "Draft Subject",
                "body": "Draft content"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.draft"
        assert result["draft_id"] == "draft123"
        assert result["to"] == ["recipient@example.com"]

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/messages" in call_args[0][1]

    def test_email_delete_action_validation(self):
        """Test email.delete action parameter validation."""
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.delete",
                data={}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

    def test_email_delete_to_trash(self, mock_graph_request):
        """Test email.delete action (move to trash)."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action (default: move to trash)
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.delete",
            data={"email_id": "msg123"}
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.delete"
        assert result["email_id"] == "msg123"
        assert result["action_taken"] == "moved_to_trash"

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/messages/msg123/move" in call_args[0][1]

    def test_email_delete_permanent(self, mock_graph_request):
        """Test email.delete action (permanent delete)."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with permanent delete
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.delete",
            data={"email_id": "msg123", "permanent": True}
        )

        # Verify result
        assert result["action_taken"] == "permanently_deleted"

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/me/messages/msg123" in call_args[0][1]

    def test_email_list_with_search(self, mock_graph_request):
        """Test email.list action with search query."""
        # Mock Graph API response
        mock_graph_request.return_value = {"value": []}

        # Execute action with search
        microsoft_operations_func(
            account_id="test@example.com",
            action="email.list",
            data={"search_query": "important meeting"}
        )

        # Verify search parameter was included
        call_kwargs = mock_graph_request.call_args[1]
        assert "params" in call_kwargs
        assert "$search" in call_kwargs["params"]
        assert "important meeting" in call_kwargs["params"]["$search"]

    def test_email_list_pagination(self, mock_graph_request):
        """Test email.list action with pagination options."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "value": [],
            "@odata.nextLink": "next_page_url"
        }

        # Execute action with pagination
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.list",
            options={"limit": 25, "skip": 50}
        )

        # Verify pagination was applied
        call_kwargs = mock_graph_request.call_args[1]
        assert call_kwargs["params"]["$top"] == 25
        assert call_kwargs["params"]["$skip"] == 50

        # Verify has_more flag
        assert result["has_more"] is True

    @patch("microsoft_mcp.email_framework.utils.format_attachments")
    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_send_with_attachments(self, mock_validate, mock_attachments, mock_graph_request):
        """Test email.send action with attachments."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock attachment formatting
        mock_attachments.return_value = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "document.pdf",
                "contentBytes": "base64content"
            }
        ]

        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with attachments
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.send",
            data={
                "to": "recipient@example.com",
                "subject": "Test with Attachment",
                "body": "See attached",
                "attachments": ["/path/to/document.pdf"]
            }
        )

        # Verify attachments were processed
        mock_attachments.assert_called_once_with(["/path/to/document.pdf"])

        # Verify Graph API call includes attachments
        call_json = mock_graph_request.call_args[1]["json"]
        assert "attachments" in call_json["message"]
        assert len(call_json["message"]["attachments"]) == 1

    # Tests for NEW email actions from Story 1.3

    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_forward_action_validation(self, mock_validate):
        """Test email.forward action parameter validation."""
        # Missing email_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.forward",
                data={"to": "recipient@example.com"}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

        # Missing to recipients
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.forward",
                data={"email_id": "msg123"}
            )
        assert "Missing required parameter: to" in str(exc.value)

    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_forward_action_success(self, mock_validate, mock_graph_request):
        """Test successful email.forward action."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.forward",
            data={
                "email_id": "msg123",
                "to": "recipient@example.com",
                "comment": "Please review this"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.forward"
        assert result["email_id"] == "msg123"
        assert result["to"] == ["recipient@example.com"]
        assert result["comment_added"] is True
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/messages/msg123/forward" in call_args[0][1]

    @patch("microsoft_mcp.email_framework.utils.style_email_content")
    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_email_forward_with_template(self, mock_validate, mock_style, mock_graph_request):
        """Test email.forward action with template styling."""
        # Mock email validation
        mock_validate.return_value = ["recipient@example.com"]

        # Mock email styling
        mock_style.return_value = "<html><body>Styled forward comment</body></html>"

        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with template
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.forward",
            data={
                "email_id": "msg123",
                "to": "recipient@example.com",
                "comment": "Please review this urgent matter"
            },
            template="professional"
        )

        # Verify template was used
        assert result["template_used"] == "professional"

        # Verify styling was applied
        mock_style.assert_called_once()

    def test_email_move_action_validation(self):
        """Test email.move action parameter validation."""
        # Missing email_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.move",
                data={"destination_folder": "inbox"}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

        # Missing destination_folder
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.move",
                data={"email_id": "msg123"}
            )
        assert "Missing required parameter: destination_folder" in str(exc.value)

        # Invalid destination folder
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.move",
                data={
                    "email_id": "msg123",
                    "destination_folder": "invalid_folder"
                }
            )
        assert "Unknown folder: invalid_folder" in str(exc.value)

    def test_email_move_action_success(self, mock_graph_request):
        """Test successful email.move action."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.move",
            data={
                "email_id": "msg123",
                "destination_folder": "archive"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.move"
        assert result["email_id"] == "msg123"
        assert result["destination_folder"] == "archive"
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/messages/msg123/move" in call_args[0][1]

        # Verify move data
        call_json = mock_graph_request.call_args[1]["json"]
        assert call_json["destinationId"] == "archive"

    def test_email_mark_action_validation(self):
        """Test email.mark action parameter validation."""
        # Missing email_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.mark",
                data={"mark_as": "read"}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

        # Missing mark_as
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.mark",
                data={"email_id": "msg123"}
            )
        assert "Missing required parameter: mark_as" in str(exc.value)

        # Invalid mark_as value
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.mark",
                data={
                    "email_id": "msg123",
                    "mark_as": "invalid_mark"
                }
            )
        assert "Invalid mark_as value: invalid_mark" in str(exc.value)

    def test_email_mark_single_action_success(self, mock_graph_request):
        """Test successful email.mark action with single email."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action - mark as read
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.mark",
            data={
                "email_id": "msg123",
                "mark_as": "read"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.mark"
        assert result["email_ids"] == ["msg123"]
        assert result["mark_as"] == "read"
        assert result["count"] == 1
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "PATCH"
        assert "/me/messages/msg123" in call_args[0][1]

        # Verify update data
        call_json = mock_graph_request.call_args[1]["json"]
        assert call_json["isRead"] is True

    def test_email_mark_multiple_emails(self, mock_graph_request):
        """Test email.mark action with multiple emails."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action with multiple emails
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.mark",
            data={
                "email_id": ["msg123", "msg456", "msg789"],
                "mark_as": "important"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["count"] == 3
        assert result["email_ids"] == ["msg123", "msg456", "msg789"]
        assert result["mark_as"] == "important"

        # Verify Graph API was called for each email
        assert mock_graph_request.call_count == 3

    def test_email_search_action_validation(self):
        """Test email.search action parameter validation."""
        # Missing query
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.search",
                data={}
            )
        assert "Missing required parameter: query" in str(exc.value)

    def test_email_search_action_success(self, mock_graph_request):
        """Test successful email.search action."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "value": [
                {
                    "id": "msg1",
                    "subject": "Important Meeting",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
                    "receivedDateTime": "2024-01-15T10:00:00Z",
                    "hasAttachments": True,
                    "bodyPreview": "Please join us for an important meeting..."
                }
            ]
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.search",
            data={"query": "important meeting"},
            options={"limit": 10}
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "email.search"
        assert result["query"] == "important meeting"
        assert result["count"] == 1
        assert len(result["emails"]) == 1
        assert result["emails"][0]["id"] == "msg1"
        assert result["emails"][0]["subject"] == "Important Meeting"
        assert result["emails"][0]["from"] == "sender@example.com"
        assert result["emails"][0]["has_attachments"] is True
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "GET"
        assert "/me/messages" in call_args[0][1]

        # Verify search parameters
        call_kwargs = mock_graph_request.call_args[1]
        assert "$search" in call_kwargs["params"]
        assert "important meeting" in call_kwargs["params"]["$search"]

    def test_email_search_with_folder(self, mock_graph_request):
        """Test email.search action with specific folder."""
        # Mock Graph API response
        mock_graph_request.return_value = {"value": []}

        # Execute action with folder
        microsoft_operations_func(
            account_id="test@example.com",
            action="email.search",
            data={
                "query": "project update",
                "folder": "sent"
            }
        )

        # Verify folder-specific endpoint was used
        call_args = mock_graph_request.call_args
        assert "/me/mailFolders/sentitems/messages" in call_args[0][1]

    def test_email_search_with_filters(self, mock_graph_request):
        """Test email.search action with advanced filters."""
        # Mock Graph API response
        mock_graph_request.return_value = {"value": []}

        # Execute action with filters
        microsoft_operations_func(
            account_id="test@example.com",
            action="email.search",
            data={
                "query": "project",
                "from_email": "manager@example.com",
                "subject_contains": "update",
                "has_attachments": True
            }
        )

        # Verify filters were applied
        call_kwargs = mock_graph_request.call_args[1]
        assert "$filter" in call_kwargs["params"]
        filter_param = call_kwargs["params"]["$filter"]
        assert "from/emailAddress/address eq 'manager@example.com'" in filter_param
        assert "contains(subject, 'update')" in filter_param
        assert "hasAttachments eq true" in filter_param

    def test_email_get_action_validation(self):
        """Test email.get action parameter validation."""
        # Missing email_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="email.get",
                data={}
            )
        assert "Missing required parameter: email_id" in str(exc.value)

    def test_email_get_action_success(self, mock_graph_request):
        """Test successful email.get action."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "id": "msg123",
            "subject": "Test Email",
            "from": {"emailAddress": {"address": "sender@example.com", "name": "Sender Name"}},
            "toRecipients": [{"emailAddress": {"address": "recipient@example.com", "name": "Recipient Name"}}],
            "ccRecipients": [],
            "bccRecipients": [],
            "receivedDateTime": "2024-01-15T10:00:00Z",
            "sentDateTime": "2024-01-15T09:59:00Z",
            "importance": "normal",
            "isRead": True,
            "hasAttachments": False,
            "categories": ["Important"],
            "flag": {},
            "internetMessageId": "<msg123@example.com>",
            "body": {
                "contentType": "HTML",
                "content": "<html><body>Test email content</body></html>"
            },
            "bodyPreview": "Test email content"
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.get",
            data={"email_id": "msg123"}
        )

        # Verify result structure
        assert result["status"] == "success"
        assert result["action"] == "email.get"
        assert "email" in result
        assert "timestamp" in result

        # Verify email details
        email = result["email"]
        assert email["id"] == "msg123"
        assert email["subject"] == "Test Email"
        assert email["from"]["address"] == "sender@example.com"
        assert len(email["to"]) == 1
        assert email["to"][0]["address"] == "recipient@example.com"
        assert email["importance"] == "normal"
        assert email["is_read"] is True
        assert email["has_attachments"] is False
        assert email["categories"] == ["Important"]
        assert email["body"]["contentType"] == "HTML"

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "GET"
        assert "/me/messages/msg123" in call_args[0][1]

    def test_email_get_with_attachments(self, mock_graph_request):
        """Test email.get action with attachments."""
        # Mock email response
        email_response = {
            "id": "msg123",
            "subject": "Email with Attachments",
            "from": {"emailAddress": {"address": "sender@example.com"}},
            "toRecipients": [],
            "ccRecipients": [],
            "bccRecipients": [],
            "hasAttachments": True,
            "body": {"contentType": "HTML", "content": "Email content"},
            "receivedDateTime": "2024-01-15T10:00:00Z"
        }

        # Mock attachments response
        attachments_response = {
            "value": [
                {
                    "id": "att1",
                    "name": "document.pdf",
                    "contentType": "application/pdf",
                    "size": 1024,
                    "isInline": False
                },
                {
                    "id": "att2",
                    "name": "image.png",
                    "contentType": "image/png",
                    "size": 512,
                    "isInline": True
                }
            ]
        }

        # Configure mock to return different responses for different endpoints
        def mock_request_side_effect(method, endpoint, account_id, **kwargs):
            if "/attachments" in endpoint:
                return attachments_response
            return email_response

        mock_graph_request.side_effect = mock_request_side_effect

        # Execute action with attachments
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.get",
            data={
                "email_id": "msg123",
                "include_attachments": True
            }
        )

        # Verify attachments were included
        email = result["email"]
        assert "attachments" in email
        assert len(email["attachments"]) == 2

        # Verify attachment details
        assert email["attachments"][0]["name"] == "document.pdf"
        assert email["attachments"][0]["content_type"] == "application/pdf"
        assert email["attachments"][0]["size"] == 1024
        assert email["attachments"][0]["is_inline"] is False

        assert email["attachments"][1]["name"] == "image.png"
        assert email["attachments"][1]["is_inline"] is True

        # Verify two Graph API calls were made
        assert mock_graph_request.call_count == 2

    def test_email_get_without_full_body(self, mock_graph_request):
        """Test email.get action without full body."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "id": "msg123",
            "subject": "Test Email",
            "from": {"emailAddress": {"address": "sender@example.com"}},
            "toRecipients": [],
            "ccRecipients": [],
            "bccRecipients": [],
            "bodyPreview": "Email preview text...",
            "receivedDateTime": "2024-01-15T10:00:00Z"
        }

        # Execute action without full body
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="email.get",
            data={
                "email_id": "msg123",
                "include_full_body": False
            }
        )

        # Verify body_preview is used instead of full body
        email = result["email"]
        assert "body_preview" in email
        assert "body" not in email
        assert email["body_preview"] == "Email preview text..."

    # Tests for NEW calendar actions from Story 1.4

    def test_calendar_list_action_validation(self):
        """Test calendar.list action parameter validation."""
        # Test with invalid dates format
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.list",
                data={"start_date": "invalid-date"}
            )
        # Note: The function itself handles date validation internally

    def test_calendar_list_action_success(self, mock_graph_request):
        """Test successful calendar.list action."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "value": [
                {
                    "id": "event1",
                    "subject": "Team Meeting",
                    "start": {"dateTime": "2024-01-15T10:00:00Z"},
                    "end": {"dateTime": "2024-01-15T11:00:00Z"},
                    "location": {"displayName": "Conference Room A"},
                    "isAllDay": False,
                    "isOnlineMeeting": True,
                    "onlineMeetingUrl": "https://teams.microsoft.com/meeting",
                    "organizer": {"emailAddress": {"address": "organizer@example.com"}},
                    "attendees": [
                        {
                            "emailAddress": {"address": "attendee@example.com", "name": "Attendee"},
                            "status": {"response": "accepted"}
                        }
                    ],
                    "body": {"content": "Team sync meeting"}
                }
            ]
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.list",
            data={"start_date": "2024-01-15", "end_date": "2024-01-16"},
            options={"limit": 10}
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.list"
        assert result["count"] == 1
        assert len(result["events"]) == 1
        assert result["events"][0]["id"] == "event1"
        assert result["events"][0]["subject"] == "Team Meeting"
        assert result["events"][0]["is_online_meeting"] is True
        assert len(result["events"][0]["attendees"]) == 1
        assert "timestamp" in result

    def test_calendar_get_action_validation(self):
        """Test calendar.get action parameter validation."""
        # Missing event_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.get",
                data={}
            )
        assert "Missing required parameter: event_id" in str(exc.value)

    def test_calendar_get_action_success(self, mock_graph_request):
        """Test successful calendar.get action."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "id": "event123",
            "subject": "Important Meeting",
            "start": {"dateTime": "2024-01-15T14:00:00Z", "timeZone": "UTC"},
            "end": {"dateTime": "2024-01-15T15:00:00Z", "timeZone": "UTC"},
            "location": {"displayName": "Boardroom"},
            "isAllDay": False,
            "isOnlineMeeting": False,
            "organizer": {
                "emailAddress": {"address": "boss@example.com", "name": "Boss"}
            },
            "attendees": [
                {
                    "emailAddress": {"address": "attendee1@example.com", "name": "Attendee 1"},
                    "status": {"response": "accepted"},
                    "type": "required"
                }
            ],
            "body": {"content": "Quarterly review meeting", "contentType": "HTML"},
            "importance": "high",
            "categories": ["Work"],
            "createdDateTime": "2024-01-10T10:00:00Z",
            "lastModifiedDateTime": "2024-01-12T15:00:00Z"
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.get",
            data={"event_id": "event123"}
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.get"
        assert "event" in result

        event = result["event"]
        assert event["id"] == "event123"
        assert event["subject"] == "Important Meeting"
        assert event["start_time"] == "2024-01-15T14:00:00Z"
        assert event["end_time"] == "2024-01-15T15:00:00Z"
        assert event["location"] == "Boardroom"
        assert event["is_all_day"] is False
        assert event["organizer"]["email"] == "boss@example.com"
        assert len(event["attendees"]) == 1
        assert event["importance"] == "high"
        assert "timestamp" in result

    def test_calendar_create_action_validation(self):
        """Test calendar.create action parameter validation."""
        # Missing subject
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.create",
                data={
                    "start_datetime": "2024-01-15T10:00:00Z",
                    "end_datetime": "2024-01-15T11:00:00Z"
                }
            )
        assert "Missing required parameter: subject" in str(exc.value)

        # Missing start_datetime
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.create",
                data={
                    "subject": "Test Meeting",
                    "end_datetime": "2024-01-15T11:00:00Z"
                }
            )
        assert "Missing required parameter: start_datetime" in str(exc.value)

        # Missing end_datetime
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.create",
                data={
                    "subject": "Test Meeting",
                    "start_datetime": "2024-01-15T10:00:00Z"
                }
            )
        assert "Missing required parameter: end_datetime" in str(exc.value)

    @patch("microsoft_mcp.email_framework.utils.validate_email_recipients")
    def test_calendar_create_action_success(self, mock_validate, mock_graph_request):
        """Test successful calendar.create action."""
        # Mock email validation
        mock_validate.return_value = ["attendee@example.com"]

        # Mock Graph API response
        mock_graph_request.return_value = {
            "id": "new_event_123",
            "subject": "New Team Meeting",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"},
            "onlineMeetingUrl": "https://teams.microsoft.com/meet/123"
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.create",
            data={
                "subject": "New Team Meeting",
                "start_datetime": "2024-01-15T10:00:00Z",
                "end_datetime": "2024-01-15T11:00:00Z",
                "attendees": ["attendee@example.com"],
                "location": "Conference Room B",
                "body": "Weekly team sync",
                "is_online_meeting": True
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.create"
        assert result["event_id"] == "new_event_123"
        assert result["subject"] == "New Team Meeting"
        assert result["start_time"] == "2024-01-15T10:00:00Z"
        assert result["end_time"] == "2024-01-15T11:00:00Z"
        assert result["meeting_url"] == "https://teams.microsoft.com/meet/123"
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/events" in call_args[0][1]

        # Verify event data
        event_data = call_args[1]["json"]
        assert event_data["subject"] == "New Team Meeting"
        assert event_data["location"]["displayName"] == "Conference Room B"
        assert event_data["isOnlineMeeting"] is True
        assert len(event_data["attendees"]) == 1

    def test_calendar_update_action_validation(self):
        """Test calendar.update action parameter validation."""
        # Missing event_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.update",
                data={"subject": "Updated Meeting"}
            )
        assert "Missing required parameter: event_id" in str(exc.value)

    def test_calendar_update_action_success(self, mock_graph_request):
        """Test successful calendar.update action."""
        # Mock Graph API response
        mock_graph_request.return_value = {"id": "event123"}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.update",
            data={
                "event_id": "event123",
                "subject": "Updated Meeting Title",
                "location": "New Conference Room",
                "start_datetime": "2024-01-15T14:00:00Z",
                "end_datetime": "2024-01-15T15:30:00Z"
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.update"
        assert result["event_id"] == "event123"
        assert "subject" in result["updated_fields"]
        assert "location" in result["updated_fields"]
        assert "start" in result["updated_fields"]
        assert "end" in result["updated_fields"]
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "PATCH"
        assert "/me/events/event123" in call_args[0][1]

        # Verify update data
        update_data = call_args[1]["json"]
        assert update_data["subject"] == "Updated Meeting Title"
        assert update_data["location"]["displayName"] == "New Conference Room"

    def test_calendar_delete_action_validation(self):
        """Test calendar.delete action parameter validation."""
        # Missing event_id
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.delete",
                data={}
            )
        assert "Missing required parameter: event_id" in str(exc.value)

    def test_calendar_delete_action_success(self, mock_graph_request):
        """Test successful calendar.delete action."""
        # Mock Graph API response
        mock_graph_request.return_value = {}

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.delete",
            data={
                "event_id": "event123",
                "send_cancellation": False
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.delete"
        assert result["event_id"] == "event123"
        assert result["send_cancellation"] is False
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/me/events/event123" in call_args[0][1]

    def test_calendar_availability_action_validation(self):
        """Test calendar.availability action parameter validation."""
        # Missing start_date
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.availability",
                data={"end_date": "2024-01-16"}
            )
        assert "Missing required parameter: start_date" in str(exc.value)

        # Missing end_date
        with pytest.raises(ValueError) as exc:
            microsoft_operations_func(
                account_id="test@example.com",
                action="calendar.availability",
                data={"start_date": "2024-01-15"}
            )
        assert "Missing required parameter: end_date" in str(exc.value)

    def test_calendar_availability_action_success(self, mock_graph_request):
        """Test successful calendar.availability action."""
        # Mock Graph API response
        mock_graph_request.return_value = {
            "value": [
                {
                    "busyViewData": [],
                    "availabilityView": ["0", "0", "0", "0", "0"]
                }
            ]
        }

        # Execute action
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.availability",
            data={
                "start_date": "2024-01-15",
                "end_date": "2024-01-15",
                "duration_minutes": 60
            }
        )

        # Verify result
        assert result["status"] == "success"
        assert result["action"] == "calendar.availability"
        assert result["start_date"] == "2024-01-15"
        assert result["end_date"] == "2024-01-15"
        assert result["duration_minutes"] == 60
        assert "available_slots" in result
        assert isinstance(result["available_slots"], list)
        assert "total_slots_found" in result
        assert "timestamp" in result

        # Verify Graph API call
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/calendar/getSchedule" in call_args[0][1]

    def test_calendar_actions_with_specific_calendar_id(self, mock_graph_request):
        """Test calendar actions with specific calendar ID."""
        mock_graph_request.return_value = {"id": "test_event"}

        # Test calendar.get with calendar_id
        result = microsoft_operations_func(
            account_id="test@example.com",
            action="calendar.get",
            data={
                "event_id": "event123",
                "calendar_id": "calendar456"
            }
        )

        # Verify endpoint includes calendar ID
        call_args = mock_graph_request.call_args
        assert "/me/calendars/calendar456/events/event123" in call_args[0][1]


# ============================================================================
# FILE ACTION TESTS
# ============================================================================

class TestFileActions:
    """Test file operations in microsoft_operations tool"""

    @patch("microsoft_mcp.tools.graph.request")
    def test_file_list_action_success(self, mock_graph_request):
        """Test successful file listing action"""
        # Mock the graph response
        mock_graph_request.return_value = {
            "value": [
                {
                    "id": "file123",
                    "name": "document.pdf",
                    "size": 1024,
                    "createdDateTime": "2025-01-15T10:00:00Z"
                }
            ]
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="file.list",
            data={"folder_path": "/Documents"},
            options={"limit": 10}
        )

        assert result["status"] == "success"
        assert len(result["files"]) == 1
        assert result["files"][0]["name"] == "document.pdf"

        # Verify correct endpoint was called
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert "/me/drive/root:/Documents:/children" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_file_list_root_folder(self, mock_graph_request):
        """Test file listing in root folder"""
        mock_graph_request.return_value = {"value": []}

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="file.list",
            data={},
            options={}
        )

        assert result["status"] == "success"
        assert result["files"] == []

        # Verify root endpoint was called
        call_args = mock_graph_request.call_args
        assert "/me/drive/root/children" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_file_get_action_success(self, mock_graph_request):
        """Test successful file get action"""
        mock_graph_request.return_value = {
            "id": "file123",
            "name": "document.pdf",
            "size": 1024,
            "downloadUrl": "https://example.com/download",
            "createdDateTime": "2025-01-15T10:00:00Z"
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="file.get",
            data={"file_path": "/Documents/document.pdf"},
            options={}
        )

        assert result["status"] == "success"
        assert result["file"]["name"] == "document.pdf"
        assert result["file"]["size"] == 1024

        # Verify correct endpoint was called
        call_args = mock_graph_request.call_args
        assert "/me/drive/root:/Documents/document.pdf" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    @patch("pathlib.Path.exists", return_value=True)
    def test_file_upload_action_success(self, mock_path_exists, mock_request):
        """Test successful file upload action"""
        mock_request.return_value = {
            "id": "file123",
            "name": "document.pdf",
            "size": 12
        }

        with patch("builtins.open", mock_open(read_data=b"file content")):
            result = microsoft_operations_func(
                account_id="test@example.com",
                action="file.upload",
                data={
                    "local_path": "/local/document.pdf",
                    "onedrive_path": "/Documents/document.pdf"
                },
                options={}
            )

        assert result["status"] == "success"
        assert result["file"]["name"] == "document.pdf"

        # Verify upload was called
        mock_request.assert_called_once()

    def test_file_upload_missing_local_file(self):
        """Test file upload with missing local file"""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(ValueError, match="Local file not found"):
                microsoft_operations_func(
                    account_id="test@example.com",
                    action="file.upload",
                    data={"local_path": "/nonexistent/file.pdf"},
                    options={}
                )

    @patch("microsoft_mcp.tools.graph.request")
    @patch("microsoft_mcp.tools.graph.download_raw")
    def test_file_download_action_success(self, mock_download_raw, mock_request):
        """Test successful file download action"""
        mock_request.return_value = {
            "name": "document.pdf",
            "size": 12
        }
        mock_download_raw.return_value = b"file content"

        with patch("builtins.open", mock_open()) as mock_open_func, \
             patch("os.makedirs") as mock_makedirs:
            result = microsoft_operations_func(
                account_id="test@example.com",
                action="file.download",
                data={
                    "file_path": "/Documents/document.pdf",
                    "save_path": "/local/downloads/document.pdf"
                },
                options={}
            )

        assert result["status"] == "success"
        assert result["save_path"] == "/local/downloads/document.pdf"
        assert result["file_size"] == 12

        # Verify download was called
        mock_download_raw.assert_called_once()

    @patch("microsoft_mcp.tools.graph.request")
    def test_file_share_action_success(self, mock_graph_request):
        """Test successful file share action"""
        mock_graph_request.return_value = {
            "link": {
                "webUrl": "https://example.com/share/file123"
            }
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="file.share",
            data={
                "file_path": "/Documents/document.pdf",
                "email": "recipient@example.com",
                "permission": "read"
            },
            options={}
        )

        assert result["status"] == "success"
        assert "example.com/share" in result["share_url"]

        # Verify correct endpoint was called
        call_args = mock_graph_request.call_args
        assert "/invite" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_file_delete_action_success(self, mock_graph_request):
        """Test successful file delete action"""
        mock_graph_request.return_value = None

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="file.delete",
            data={"file_path": "/Documents/document.pdf"},
            options={}
        )

        assert result["status"] == "success"
        assert result["file_path"] == "Documents/document.pdf"

        # Verify correct endpoint was called with DELETE method
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/me/drive/root:/Documents/document.pdf" in call_args[0][1]


# ============================================================================
# CONTACT ACTION TESTS
# ============================================================================

class TestContactActions:
    """Test contact operations in microsoft_operations tool"""

    @patch("microsoft_mcp.tools.graph.request")
    def test_contact_list_action_success(self, mock_graph_request):
        """Test successful contact listing action"""
        mock_graph_request.return_value = {
            "value": [
                {
                    "id": "contact123",
                    "displayName": "John Doe",
                    "emailAddresses": [{"address": "john@example.com"}],
                    "mobilePhone": "+1234567890"
                }
            ]
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="contact.list",
            data={"search_query": "John"},
            options={"limit": 10}
        )

        assert result["status"] == "success"
        assert len(result["contacts"]) == 1
        assert result["contacts"][0]["display_name"] == "John Doe"

        # Verify correct endpoint was called
        call_args = mock_graph_request.call_args
        assert "/me/contacts" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_contact_get_action_success(self, mock_graph_request):
        """Test successful contact get action"""
        mock_graph_request.return_value = {
            "id": "contact123",
            "displayName": "John Doe",
            "givenName": "John",
            "surname": "Doe",
            "emailAddresses": [{"address": "john@example.com"}],
            "mobilePhone": "+1234567890"
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="contact.get",
            data={"contact_id": "contact123"},
            options={}
        )

        assert result["status"] == "success"
        assert result["contact"]["display_name"] == "John Doe"
        assert result["contact"]["first_name"] == "John"

        # Verify correct endpoint was called
        call_args = mock_graph_request.call_args
        assert "/me/contacts/contact123" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_contact_create_action_success(self, mock_graph_request):
        """Test successful contact create action"""
        mock_graph_request.return_value = {
            "id": "contact123",
            "displayName": "Jane Smith",
            "givenName": "Jane",
            "surname": "Smith",
            "emailAddresses": [{"address": "jane@example.com"}]
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="contact.create",
            data={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "mobile_phone": "+1987654321"
            },
            options={}
        )

        assert result["status"] == "success"
        assert result["contact"]["display_name"] == "Jane Smith"

        # Verify correct endpoint was called with POST method
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"
        assert "/me/contacts" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_contact_update_action_success(self, mock_graph_request):
        """Test successful contact update action"""
        mock_graph_request.return_value = {
            "id": "contact123",
            "displayName": "John Updated",
            "givenName": "John",
            "surname": "Updated"
        }

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="contact.update",
            data={
                "contact_id": "contact123",
                "last_name": "Updated",
                "email": "john.updated@example.com"
            },
            options={}
        )

        assert result["status"] == "success"
        assert result["contact_id"] == "contact123"
        assert "surname" in result["updated_fields"]

        # Verify correct endpoint was called with PATCH method
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "PATCH"
        assert "/me/contacts/contact123" in call_args[0][1]

    @patch("microsoft_mcp.tools.graph.request")
    def test_contact_delete_action_success(self, mock_graph_request):
        """Test successful contact delete action"""
        mock_graph_request.return_value = None

        result = microsoft_operations_func(
            account_id="test@example.com",
            action="contact.delete",
            data={"contact_id": "contact123"},
            options={}
        )

        assert result["status"] == "success"
        assert result["contact_id"] == "contact123"

        # Verify correct endpoint was called with DELETE method
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "DELETE"
        assert "/me/contacts/contact123" in call_args[0][1]

    def test_contact_create_missing_required_fields(self):
        """Test contact creation with missing required fields"""
        with pytest.raises(ValueError, match="Missing required parameters"):
            microsoft_operations_func(
                account_id="test@example.com",
                action="contact.create",
                data={"first_name": "John"},  # Missing last_name
                options={}
            )
