"""Test equivalence between legacy tools and unified microsoft_operations tool.

This module verifies that the new unified tool produces identical results
to the legacy 61 tools, ensuring backward compatibility.
"""

from unittest.mock import patch

import pytest

from microsoft_mcp.tools import create_email_draft
from microsoft_mcp.tools import delete_email
from microsoft_mcp.tools import list_emails
from microsoft_mcp.tools import microsoft_operations
from microsoft_mcp.tools import reply_to_email
from microsoft_mcp.tools import send_email

# Access the actual functions from the FunctionTool decorators
list_emails_func = list_emails.fn
send_email_func = send_email.fn
reply_to_email_func = reply_to_email.fn
create_email_draft_func = create_email_draft.fn
delete_email_func = delete_email.fn
microsoft_operations_func = microsoft_operations.fn


class TestToolEquivalence:
    """Verify unified tool produces same results as legacy tools."""

    @pytest.fixture
    def mock_graph_request(self):
        """Mock Graph API request function."""
        with patch("microsoft_mcp.tools.graph.request") as mock:
            yield mock

    @pytest.fixture
    def mock_validate_recipients(self):
        """Mock email recipient validation."""
        with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock:
            mock.side_effect = lambda x: [x] if isinstance(x, str) else x
            yield mock

    def test_list_emails_equivalence(self, mock_graph_request):
        """Test list_emails and email.list produce identical results."""
        # Mock response
        mock_response = {
            "value": [
                {
                    "id": "msg1",
                    "subject": "Test Email",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "receivedDateTime": "2024-01-01T10:00:00Z",
                    "bodyPreview": "Test content preview",
                }
            ]
        }
        mock_graph_request.return_value = mock_response

        # Test parameters
        account_id = "test@example.com"
        folder = "inbox"
        limit = 10

        # Call legacy tool
        legacy_result = list_emails_func(
            account_id=account_id,
            folder_name=folder,
            limit=limit,
            include_body=True
        )

        # Reset mock for clean comparison
        mock_graph_request.reset_mock()
        mock_graph_request.return_value = mock_response

        # Call unified tool
        unified_result = microsoft_operations_func(
            account_id=account_id,
            action="email.list",
            data={"folder": folder, "include_body": True},
            options={"limit": limit}
        )

        # Compare results
        assert legacy_result["status"] == unified_result["status"]
        assert len(legacy_result["emails"]) == len(unified_result["emails"])
        assert legacy_result["count"] == unified_result["count"]

        # Compare email data
        for legacy_email, unified_email in zip(legacy_result["emails"], unified_result["emails"], strict=False):
            assert legacy_email["id"] == unified_email["id"]
            assert legacy_email["subject"] == unified_email["subject"]
            assert legacy_email["from"] == unified_email["from"]

    def test_send_email_equivalence(self, mock_graph_request, mock_validate_recipients):
        """Test send_email and email.send produce identical results."""
        # Mock response
        mock_graph_request.return_value = {}

        # Test parameters
        account_id = "test@example.com"
        to = "recipient@example.com"
        subject = "Test Subject"
        body = "Test content"
        cc = ["cc@example.com"]

        # Call legacy tool
        legacy_result = send_email_func(
            account_id=account_id,
            to=to,
            subject=subject,
            body=body,
            cc=cc
        )

        # Reset mock
        mock_graph_request.reset_mock()
        mock_graph_request.return_value = {}

        # Call unified tool
        unified_result = microsoft_operations_func(
            account_id=account_id,
            action="email.send",
            data={
                "to": to,
                "subject": subject,
                "body": body,
                "cc": cc
            }
        )

        # Compare results
        assert legacy_result["status"] == unified_result["status"]
        assert legacy_result["action"] == unified_result["action"]
        assert legacy_result["to"] == unified_result["to"]
        assert legacy_result["subject"] == unified_result["subject"]
        assert legacy_result.get("cc") == unified_result.get("cc")

    def test_reply_to_email_equivalence(self, mock_graph_request):
        """Test reply_to_email and email.reply produce identical results."""
        # Mock response
        mock_graph_request.return_value = {}

        # Test parameters
        account_id = "test@example.com"
        email_id = "msg123"
        body = "Reply content"
        reply_all = False

        # Call legacy tool
        legacy_result = reply_to_email_func(
            account_id=account_id,
            email_id=email_id,
            body=body,
            reply_all=reply_all
        )

        # Reset mock
        mock_graph_request.reset_mock()
        mock_graph_request.return_value = {}

        # Call unified tool
        unified_result = microsoft_operations_func(
            account_id=account_id,
            action="email.reply",
            data={
                "email_id": email_id,
                "body": body,
                "reply_all": reply_all
            }
        )

        # Compare results
        assert legacy_result["status"] == unified_result["status"]
        assert legacy_result["action"] == unified_result["action"]
        assert legacy_result["email_id"] == unified_result["email_id"]
        assert legacy_result["reply_all"] == unified_result["reply_all"]

    def test_create_email_draft_equivalence(self, mock_graph_request, mock_validate_recipients):
        """Test create_email_draft and email.draft produce identical results."""
        # Mock response
        mock_response = {"id": "draft123", "subject": "Draft Subject"}
        mock_graph_request.return_value = mock_response

        # Test parameters
        account_id = "test@example.com"
        to = "recipient@example.com"
        subject = "Draft Subject"
        body = "Draft content"

        # Call legacy tool
        legacy_result = create_email_draft_func(
            account_id=account_id,
            to=to,
            subject=subject,
            body=body
        )

        # Reset mock
        mock_graph_request.reset_mock()
        mock_graph_request.return_value = mock_response

        # Call unified tool
        unified_result = microsoft_operations_func(
            account_id=account_id,
            action="email.draft",
            data={
                "to": to,
                "subject": subject,
                "body": body
            }
        )

        # Compare results
        assert legacy_result["status"] == unified_result["status"]
        assert legacy_result["action"] == unified_result["action"]
        assert legacy_result["draft_id"] == unified_result["draft_id"]
        assert legacy_result["to"] == unified_result["to"]
        assert legacy_result["subject"] == unified_result["subject"]

    def test_delete_email_equivalence(self, mock_graph_request):
        """Test delete_email and email.delete produce identical results."""
        # Mock response
        mock_graph_request.return_value = {}

        # Test parameters
        account_id = "test@example.com"
        email_id = "msg123"
        permanent = False

        # Call legacy tool
        legacy_result = delete_email_func(
            account_id=account_id,
            email_id=email_id,
            permanent=permanent
        )

        # Reset mock
        mock_graph_request.reset_mock()
        mock_graph_request.return_value = {}

        # Call unified tool
        unified_result = microsoft_operations_func(
            account_id=account_id,
            action="email.delete",
            data={
                "email_id": email_id,
                "permanent": permanent
            }
        )

        # Compare results
        assert legacy_result["status"] == unified_result["status"]
        assert legacy_result["action"] == unified_result["action"]
        assert legacy_result["email_id"] == unified_result["email_id"]
        assert legacy_result["action_taken"] == unified_result["action_taken"]

    @pytest.mark.parametrize("test_case", [
        {
            "legacy_tool": "list_emails",
            "unified_action": "email.list",
            "params": {"folder": "sent", "limit": 5}
        },
        {
            "legacy_tool": "send_email",
            "unified_action": "email.send",
            "params": {"to": "user@test.com", "subject": "Test", "body": "Content"}
        },
        {
            "legacy_tool": "reply_to_email",
            "unified_action": "email.reply",
            "params": {"email_id": "msg456", "body": "Reply text"}
        },
        {
            "legacy_tool": "create_email_draft",
            "unified_action": "email.draft",
            "params": {"to": "draft@test.com", "subject": "Draft", "body": "Draft text"}
        },
        {
            "legacy_tool": "delete_email",
            "unified_action": "email.delete",
            "params": {"email_id": "msg789"}
        }
    ])
    def test_parametrized_equivalence(self, test_case, mock_graph_request, mock_validate_recipients):
        """Parametrized test for all email operations equivalence."""
        # Mock appropriate response based on operation
        if test_case["legacy_tool"] == "list_emails":
            mock_graph_request.return_value = {"value": []}
        elif test_case["legacy_tool"] == "create_email_draft":
            mock_graph_request.return_value = {"id": "draft_id"}
        else:
            mock_graph_request.return_value = {}

        account_id = "test@example.com"
        params = test_case["params"]

        # Map parameters for legacy tools
        legacy_params = {"account_id": account_id}
        if test_case["legacy_tool"] == "list_emails":
            legacy_params["folder_name"] = params.get("folder", "inbox")
            legacy_params["limit"] = params.get("limit", 50)
            legacy_params["include_body"] = True
        elif test_case["legacy_tool"] in ["send_email", "create_email_draft"]:
            legacy_params.update(params)
        elif test_case["legacy_tool"] == "reply_to_email":
            legacy_params["email_id"] = params["email_id"]
            legacy_params["body"] = params["body"]
            legacy_params["reply_all"] = params.get("reply_all", False)
        elif test_case["legacy_tool"] == "delete_email":
            legacy_params["email_id"] = params["email_id"]
            legacy_params["permanent"] = params.get("permanent", False)

        # Get legacy tool function
        legacy_func = globals()[f"{test_case['legacy_tool']}_func"]

        # Call legacy tool
        legacy_result = legacy_func(**legacy_params)

        # Reset mock
        mock_graph_request.reset_mock()
        if test_case["legacy_tool"] == "list_emails":
            mock_graph_request.return_value = {"value": []}
        elif test_case["legacy_tool"] == "create_email_draft":
            mock_graph_request.return_value = {"id": "draft_id"}
        else:
            mock_graph_request.return_value = {}

        # Call unified tool
        unified_params = {
            "account_id": account_id,
            "action": test_case["unified_action"]
        }

        if test_case["unified_action"] == "email.list":
            unified_params["data"] = {"folder": params.get("folder", "inbox"), "include_body": True}
            unified_params["options"] = {"limit": params.get("limit", 50)}
        else:
            unified_params["data"] = params

        unified_result = microsoft_operations_func(**unified_params)

        # Basic equivalence check
        assert legacy_result["status"] == unified_result["status"]
        assert legacy_result["action"] == unified_result["action"]
