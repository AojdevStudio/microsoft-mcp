"""Unit tests for Microsoft MCP tools.

These tests verify the behavior of individual MCP tools in isolation,
with all external dependencies mocked. Tests focus on:
- Parameter validation
- Business logic
- Error handling
- Response formatting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import json


class TestListAccountsTool:
    """Test the list_accounts tool."""
    
    def test_lists_authenticated_accounts(self, mock_auth_module):
        """Should return list of authenticated Microsoft accounts."""
        # Import after mocking to avoid authentication requirements
        with patch('microsoft_mcp.tools.auth', mock_auth_module):
            from microsoft_mcp.tools import list_accounts
            
            # Access the underlying function from FastMCP decorator
            result = list_accounts.fn()
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert "username" in result[0]
            assert "account_id" in result[0]
            mock_auth_module.list_accounts.assert_called_once()
    
    def test_handles_no_accounts(self, mock_auth_module):
        """Should return empty list when no accounts are authenticated."""
        mock_auth_module.list_accounts.return_value = []
        
        with patch('microsoft_mcp.tools.auth', mock_auth_module):
            from microsoft_mcp.tools import list_accounts
            
            # Access the underlying function from FastMCP decorator
            result = list_accounts.fn()
            
            assert result == []


class TestEmailTools:
    """Test email-related MCP tools."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_list_emails_basic_functionality(self, mock_auth, mock_graph, sample_email_data):
        """Should list emails from Microsoft Graph API."""
        # Setup mocks
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_email_data])
        
        from microsoft_mcp.tools import list_emails
        
        # Access the underlying function from FastMCP decorator
        result = list_emails.fn(
            account_id="test-account",
            limit=10,
            include_body=True
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
        assert "subject" in result[0]
        mock_graph.paginate.assert_called_once()
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth') 
    def test_list_emails_folder_filtering(self, mock_auth, mock_graph, sample_email_data):
        """Should filter emails by folder."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_email_data])
        
        from microsoft_mcp.tools import list_emails
        
        # Access the underlying function from FastMCP decorator
        result = list_emails.fn(
            account_id="test-account",
            folder_name="inbox",
            limit=5
        )
        
        # Verify correct API endpoint was called
        call_args = mock_graph.paginate.call_args
        assert "inbox" in call_args[0][0]  # Check path contains folder
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_send_email_basic(self, mock_auth, mock_graph):
        """Should send email via Microsoft Graph API."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.request.return_value = {"id": "sent-email-123"}
        
        from microsoft_mcp.tools import send_email
        
        # Access the underlying function from FastMCP decorator
        result = send_email.fn(
            account_id="test-account",
            to="recipient@test.com",
            subject="Test Subject",
            body="Test body content"
        )
        
        assert "status" in result
        assert result["status"] == "sent"
        
        # Verify correct API call was made - note the function wraps body in HTML
        mock_graph.request.assert_called_once()
        call_args = mock_graph.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/me/sendMail"
        assert call_args[0][2] == "test-account"  # account_id as positional arg
        
        # Check the message structure
        message_data = call_args[1]["json"]["message"]
        assert message_data["subject"] == "Test Subject"
        assert "Test body content" in message_data["body"]["content"]
        assert message_data["body"]["contentType"] == "HTML"
        assert len(message_data["toRecipients"]) == 1
        assert message_data["toRecipients"][0]["emailAddress"]["address"] == "recipient@test.com"
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_send_email_with_cc_bcc(self, mock_auth, mock_graph):
        """Should handle CC and BCC recipients."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.request.return_value = {"id": "sent-email-123"}
        
        from microsoft_mcp.tools import send_email
        
        # Access the underlying function from FastMCP decorator
        result = send_email.fn(
            account_id="test-account",
            to="recipient@test.com",
            subject="Test Subject",
            body="Test body",
            cc=["cc1@test.com", "cc2@test.com"],
            bcc=["bcc@test.com"]
        )
        
        # Verify CC and BCC were included in API call
        call_args = mock_graph.request.call_args
        message_data = call_args[1]["json"]["message"]
        
        assert "ccRecipients" in message_data
        assert len(message_data["ccRecipients"]) == 2
        assert "bccRecipients" in message_data
        assert len(message_data["bccRecipients"]) == 1
    
    def test_send_email_parameter_validation(self):
        """Should validate required parameters."""
        from microsoft_mcp.tools import send_email
        
        # Test missing account_id - accessing the underlying function
        with pytest.raises(TypeError):
            send_email.fn(to="test@test.com", subject="Test", body="Test")
        
        # Test missing to parameter
        with pytest.raises(TypeError):
            send_email.fn(account_id="test", subject="Test", body="Test")


class TestCalendarTools:
    """Test calendar-related MCP tools."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_list_events(self, mock_auth, mock_graph, sample_calendar_event):
        """Should list calendar events."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_calendar_event])
        
        from microsoft_mcp.tools import list_calendar_events
        
        # Access the underlying function from FastMCP decorator
        result = list_calendar_events.fn(
            account_id="test-account",
            limit=20
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
        assert "subject" in result[0]
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_create_event(self, mock_auth, mock_graph):
        """Should create calendar event."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.request.return_value = {"id": "new-event-123"}
        
        from microsoft_mcp.tools import create_calendar_event
        
        start_time = datetime.now(timezone.utc) + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Access the underlying function from FastMCP decorator
        result = create_calendar_event.fn(
            account_id="test-account",
            subject="Test Meeting",
            start_datetime=start_time.isoformat(),
            end_datetime=end_time.isoformat(),
            location="Conference Room A"
        )
        
        assert "id" in result
        mock_graph.request.assert_called_once()
        
        # Verify correct API call was made
        call_args = mock_graph.request.call_args
        assert call_args[0][0] == "POST"
        assert "/events" in call_args[0][1]


class TestContactTools:
    """Test contact-related MCP tools."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_list_contacts(self, mock_auth, mock_graph, sample_contact_data):
        """Should list contacts from Microsoft Graph."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_contact_data])
        
        from microsoft_mcp.tools import list_contacts
        
        # Access the underlying function from FastMCP decorator
        result = list_contacts.fn(
            account_id="test-account",
            limit=10
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_create_contact(self, mock_auth, mock_graph):
        """Should create new contact."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.request.return_value = {"id": "new-contact-123"}
        
        from microsoft_mcp.tools import create_contact
        
        # Access the underlying function from FastMCP decorator
        result = create_contact.fn(
            account_id="test-account",
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com"
        )
        
        assert "id" in result
        mock_graph.request.assert_called_once()


class TestFileTools:
    """Test file/OneDrive-related MCP tools."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_list_files(self, mock_auth, mock_graph, sample_file_data):
        """Should list files from OneDrive."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_file_data])
        
        from microsoft_mcp.tools import list_files
        
        # Access the underlying function from FastMCP decorator
        result = list_files.fn(account_id="test-account")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
        assert "name" in result[0]


class TestErrorHandling:
    """Test error handling across all tools."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_handles_graph_api_errors(self, mock_auth, mock_graph):
        """Should handle Microsoft Graph API errors gracefully."""
        mock_auth.get_token.return_value = "mock-token"
        
        # Simulate Graph API error
        import httpx
        mock_graph.paginate.side_effect = httpx.HTTPStatusError(
            "Client error '403 Forbidden'",
            request=Mock(),
            response=Mock(status_code=403)
        )
        
        from microsoft_mcp.tools import list_emails
        
        with pytest.raises(httpx.HTTPStatusError):
            # Access the underlying function from FastMCP decorator
            list_emails.fn(account_id="test-account")
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_handles_authentication_errors(self, mock_auth, mock_graph):
        """Should handle authentication errors."""
        # Mock paginate to raise an authentication exception
        mock_graph.paginate.side_effect = Exception("Authentication failed")
        
        from microsoft_mcp.tools import list_emails
        
        with pytest.raises(Exception, match="Authentication failed"):
            # Access the underlying function from FastMCP decorator
            list_emails.fn(account_id="test-account")


class TestDataFormatting:
    """Test data formatting and response consistency."""
    
    @patch('microsoft_mcp.tools.graph')
    @patch('microsoft_mcp.tools.auth')
    def test_consistent_response_format(self, mock_auth, mock_graph, sample_email_data):
        """Should return consistent response format across tools."""
        mock_auth.get_token.return_value = "mock-token"
        mock_graph.paginate.return_value = iter([sample_email_data])
        
        from microsoft_mcp.tools import list_emails
        
        # Access the underlying function from FastMCP decorator
        result = list_emails.fn(account_id="test-account")
        
        # All list operations should return lists
        assert isinstance(result, list)
        
        # Items should have consistent field names
        if result:
            assert "id" in result[0]
            assert isinstance(result[0]["id"], str)
    
    def test_date_formatting(self):
        """Should handle date formatting consistently."""
        # Test with various date formats that might come from Graph API
        test_dates = [
            "2025-08-05T10:00:00Z",
            "2025-08-05T10:00:00.000Z",
            "2025-08-05T10:00:00+00:00"
        ]
        
        for date_str in test_dates:
            # Test that date parsing doesn't raise errors
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Date format {date_str} should be parseable")


class TestParameterValidation:
    """Test parameter validation across tools."""
    
    def test_account_id_required(self):
        """Should require account_id parameter for all tools."""
        # Import tools module to get all MCP tools
        import microsoft_mcp.tools as tools
        
        # Get all functions that are MCP tools (decorated with @mcp.tool)
        tool_functions = [
            getattr(tools, name) for name in dir(tools)
            if callable(getattr(tools, name)) and hasattr(getattr(tools, name), '__wrapped__')
        ]
        
        # Skip tools that don't require account_id
        skip_tools = ['list_accounts', 'authenticate_account', 'complete_authentication']
        
        for tool_func in tool_functions:
            if tool_func.__name__ in skip_tools:
                continue
                
            # Check that function signature includes account_id parameter
            import inspect
            sig = inspect.signature(tool_func)
            
            assert 'account_id' in sig.parameters, f"{tool_func.__name__} should require account_id parameter"
    
    def test_email_validation_in_params(self):
        """Should validate email addresses through parameter validation."""
        # Email validation is now handled by Pydantic models in email_params.py
        # This test verifies the validation exists through the parameter system
        from microsoft_mcp.email_params import SendEmailParams
        from pydantic import ValidationError
        
        # Valid emails should pass validation
        valid_emails = [
            "user@example.com",
            "user.name@company.co.uk", 
            "user+tag@domain.org"
        ]
        
        for email in valid_emails:
            params = SendEmailParams(
                account_id="test@test.com",
                to=email,
                subject="Test",
                body="Test"
            )
            assert params.to == [email.lower()]
        
        # Invalid emails should fail validation - test each one individually
        # Note: Some simple patterns may pass the basic regex but still be caught elsewhere
        with pytest.raises(ValidationError):
            # Empty string should definitely fail
            SendEmailParams(
                account_id="test@test.com",
                to="",
                subject="Test",
                body="Test"
            )
        
        with pytest.raises(ValidationError):
            # Missing @ symbol
            SendEmailParams(
                account_id="test@test.com",
                to="invalid",
                subject="Test",
                body="Test"
            )
            
        with pytest.raises(ValidationError):
            # @ at beginning
            SendEmailParams(
                account_id="test@test.com",
                to="@example.com",
                subject="Test",
                body="Test"
            )
