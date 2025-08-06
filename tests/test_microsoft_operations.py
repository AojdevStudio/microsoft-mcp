"""Tests for microsoft_operations unified tool.

This module tests the action-based routing and parameter validation
of the new unified microsoft_operations tool.
"""

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
