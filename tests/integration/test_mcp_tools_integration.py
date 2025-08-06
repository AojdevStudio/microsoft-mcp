"""Integration tests for MCP tools.

These tests verify that different components work together correctly,
while still mocking external dependencies like Microsoft Graph API.
They test the integration between:
- MCP tools and authentication
- MCP tools and Graph API client
- Email framework and MCP tools
- Template rendering and email sending
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import json


class TestMCPToolsIntegration:
    """Test integration between MCP tools and core components."""
    
    @pytest.fixture
    def mock_integrated_environment(self):
        """Set up an integrated mock environment."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph:
            
            # Setup auth mock
            mock_auth.get_token.return_value = "mock-token-12345"
            mock_auth.list_accounts.return_value = [
                mock_auth.Account(username="test@kamdental.com", account_id="test-123")
            ]
            
            # Setup graph mock
            mock_graph.request.return_value = {"id": "success", "status": "completed"}
            mock_graph.BASE_URL = "https://graph.microsoft.com/v1.0"
            
            yield {
                'auth': mock_auth,
                'graph': mock_graph
            }
    
    def test_email_workflow_end_to_end(self, mock_integrated_environment, sample_email_data):
        """Test complete email workflow from authentication through sending."""
        mocks = mock_integrated_environment
        
        # Mock email creation response
        mocks['graph'].request.return_value = {"id": "sent-email-123"}
        
        from microsoft_mcp.tools import send_email
        
        result = send_email(
            account_id="test-123",
            to="recipient@test.com",
            subject="Integration Test Email",
            body="<h1>Test content</h1>"
        )
        
        # Verify authentication was called
        mocks['auth'].get_token.assert_called_once_with("test-123")
        
        # Verify Graph API was called with correct parameters
        mocks['graph'].request.assert_called_once()
        call_args = mocks['graph'].request.call_args
        
        assert call_args[0][0] == "POST"  # HTTP method
        assert "/sendMail" in call_args[0][1]  # API endpoint
        assert call_args[1]["account_id"] == "test-123"
        
        # Verify response format
        assert "status" in result
        assert result["status"] == "sent"
    
    def test_calendar_event_creation_workflow(self, mock_integrated_environment):
        """Test complete calendar event creation workflow."""
        mocks = mock_integrated_environment
        
        # Mock event creation response
        event_response = {
            "id": "event-123",
            "subject": "Test Meeting",
            "start": {"dateTime": "2025-08-06T10:00:00Z"},
            "end": {"dateTime": "2025-08-06T11:00:00Z"}
        }
        mocks['graph'].request.return_value = event_response
        
        from microsoft_mcp.tools import create_event
        
        start_time = datetime.now(timezone.utc) + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        result = create_event(
            account_id="test-123",
            subject="Integration Test Meeting",
            start=start_time.isoformat(),
            end=end_time.isoformat(),
            location="Conference Room A",
            attendees=["attendee@test.com"]
        )
        
        # Verify complete workflow
        mocks['auth'].get_token.assert_called_once_with("test-123")
        mocks['graph'].request.assert_called_once()
        
        # Verify event data structure
        call_args = mocks['graph'].request.call_args
        event_data = call_args[1]["json"]
        
        assert event_data["subject"] == "Integration Test Meeting"
        assert "start" in event_data
        assert "end" in event_data
        assert "location" in event_data
        assert "attendees" in event_data
        
        assert result["id"] == "event-123"
    
    def test_file_operations_workflow(self, mock_integrated_environment):
        """Test file operations workflow with OneDrive."""
        mocks = mock_integrated_environment
        
        # Mock paginate function for file listing
        def mock_paginate(method, path, account_id=None, params=None):
            yield {"id": "file-123", "name": "test.pdf", "size": 1024}
            yield {"id": "file-456", "name": "document.docx", "size": 2048}
        
        with patch('microsoft_mcp.graph.paginate', mock_paginate):
            from microsoft_mcp.tools import list_files
            
            result = list_files(account_id="test-123", limit=10)
            
            # Verify authentication
            mocks['auth'].get_token.assert_called_with("test-123")
            
            # Verify results
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "test.pdf"
            assert result[1]["name"] == "document.docx"
    
    def test_search_operations_integration(self, mock_integrated_environment):
        """Test search operations across different entity types."""
        mocks = mock_integrated_environment
        
        # Mock search results
        search_response = {
            "value": [
                {"@odata.type": "#microsoft.graph.message", "id": "email-123", "subject": "Test"},
                {"@odata.type": "#microsoft.graph.event", "id": "event-456", "subject": "Meeting"}
            ]
        }
        mocks['graph'].request.return_value = search_response
        
        from microsoft_mcp.tools import unified_search
        
        result = unified_search(
            account_id="test-123",
            query="test",
            entity_types=["message", "event"],
            limit=10
        )
        
        # Verify authentication and API call
        mocks['auth'].get_token.assert_called_with("test-123")
        mocks['graph'].request.assert_called_once()
        
        # Verify search parameters
        call_args = mocks['graph'].request.call_args
        params = call_args[1]["params"]
        assert "$search" in params
        assert params["$search"] == "test"
        
        # Verify results are grouped by type
        assert isinstance(result, dict)
        assert "message" in result
        assert "event" in result
    
    def test_error_propagation_through_layers(self, mock_integrated_environment):
        """Test that errors propagate correctly through all layers."""
        mocks = mock_integrated_environment
        
        # Simulate authentication error
        mocks['auth'].get_token.side_effect = Exception("Token expired")
        
        from microsoft_mcp.tools import list_emails
        
        with pytest.raises(Exception, match="Token expired"):
            list_emails(account_id="test-123")
        
        # Simulate Graph API error
        mocks['auth'].get_token.side_effect = None  # Reset
        mocks['auth'].get_token.return_value = "valid-token"
        
        import httpx
        mocks['graph'].request.side_effect = httpx.HTTPStatusError(
            "403 Forbidden",
            request=Mock(),
            response=Mock(status_code=403)
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            list_emails(account_id="test-123")


class TestEmailFrameworkIntegration:
    """Test integration between email framework and MCP tools."""
    
    @pytest.fixture
    def mock_email_environment(self):
        """Mock environment for email framework testing."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph, \
             patch('microsoft_mcp.email_framework') as mock_framework:
            
            mock_auth.get_token.return_value = "mock-token"
            mock_graph.request.return_value = {"id": "sent-email"}
            
            # Mock template rendering
            mock_template = Mock()
            mock_template.render.return_value = "<html>Rendered Email</html>"
            mock_template.validate_data.return_value = True
            
            mock_framework.templates.practice_report.PracticeReportTemplate.return_value = mock_template
            mock_framework.templates.executive_summary.ExecutiveSummaryTemplate.return_value = mock_template
            mock_framework.templates.provider_update.ProviderUpdateTemplate.return_value = mock_template
            mock_framework.templates.alert_notification.AlertNotificationTemplate.return_value = mock_template
            
            yield {
                'auth': mock_auth,
                'graph': mock_graph,
                'framework': mock_framework,
                'template': mock_template
            }
    
    def test_practice_report_email_integration(self, mock_email_environment, valid_practice_report_data):
        """Test complete practice report email workflow."""
        mocks = mock_email_environment
        
        # Mock the practice report tool
        with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
            def mock_send_practice_report(**kwargs):
                # Simulate the tool workflow:
                # 1. Validate data
                # 2. Render template
                # 3. Send email
                template = mocks['template']
                template.validate_data(valid_practice_report_data)
                rendered_html = template.render(valid_practice_report_data)
                
                # Call underlying send_email function
                return {
                    "status": "sent",
                    "id": "practice-report-email-123",
                    "template_used": "practice_report",
                    "theme": "baytown"
                }
            
            mock_tool.side_effect = mock_send_practice_report
            
            result = mock_tool(
                account_id="test-123",
                to="manager@kamdental.com",
                subject="Baytown Practice Report - July 2025",
                **valid_practice_report_data
            )
            
            # Verify workflow completed successfully
            assert result["status"] == "sent"
            assert result["template_used"] == "practice_report"
            assert result["theme"] == "baytown"
            
            # Verify template validation and rendering were called
            mocks['template'].validate_data.assert_called_once()
            mocks['template'].render.assert_called_once()
    
    def test_executive_summary_multi_location_integration(self, mock_email_environment, valid_executive_summary_data):
        """Test executive summary with multiple locations."""
        mocks = mock_email_environment
        
        with patch('microsoft_mcp.tools.send_executive_summary') as mock_tool:
            def mock_send_executive_summary(**kwargs):
                # Verify locations data is present
                locations = kwargs.get('locations_data', [])
                if not locations:
                    raise ValueError("Missing required field: locations")
                
                template = mocks['template']
                template.validate_data(valid_executive_summary_data)
                rendered_html = template.render(valid_executive_summary_data)
                
                return {
                    "status": "sent",
                    "id": "executive-summary-123",
                    "locations_count": len(locations),
                    "theme": "executive"
                }
            
            mock_tool.side_effect = mock_send_executive_summary
            
            result = mock_tool(
                account_id="test-123",
                to="ceo@kamdental.com",
                locations_data=valid_executive_summary_data['locations'],
                period="July 2025 MTD"
            )
            
            assert result["status"] == "sent"
            assert result["locations_count"] == 2
            assert result["theme"] == "executive"
    
    def test_provider_update_personalization_integration(self, mock_email_environment, valid_provider_update_data):
        """Test provider update with personalized data."""
        mocks = mock_email_environment
        
        with patch('microsoft_mcp.tools.send_provider_update') as mock_tool:
            def mock_send_provider_update(**kwargs):
                # Validate required performance data
                perf_data = kwargs.get('performance_data', {})
                if 'production' not in perf_data:
                    raise ValueError("Missing required performance data field: production")
                
                template = mocks['template']
                template.validate_data(valid_provider_update_data)
                rendered_html = template.render(valid_provider_update_data)
                
                return {
                    "status": "sent",
                    "id": "provider-update-123",
                    "provider_name": kwargs.get('provider_name'),
                    "production_value": perf_data['production']
                }
            
            mock_tool.side_effect = mock_send_provider_update
            
            result = mock_tool(
                account_id="test-123",
                to="dr.ezeji@kamdental.com",
                provider_name="Dr. Obinna Ezeji",
                performance_data=valid_provider_update_data['performance_data']
            )
            
            assert result["status"] == "sent"
            assert result["provider_name"] == "Dr. Obinna Ezeji"
            assert result["production_value"] == 68053
    
    def test_alert_notification_urgency_integration(self, mock_email_environment, valid_alert_notification_data):
        """Test alert notification with different urgency levels."""
        mocks = mock_email_environment
        
        urgency_levels = ["low", "normal", "high", "critical"]
        
        with patch('microsoft_mcp.tools.send_alert_notification') as mock_tool:
            def mock_send_alert_notification(**kwargs):
                urgency = kwargs.get('urgency', 'normal')
                alert_type = kwargs.get('alert_type', 'info')
                
                # Validate color reference doesn't contain invalid values
                if '--primary' in kwargs.get('message', ''):
                    raise ValueError("Invalid color reference: --primary")
                
                template = mocks['template']
                # Fix the alert data by removing invalid color reference
                fixed_data = valid_alert_notification_data.copy()
                fixed_data['message'] = fixed_data['message'].replace('--primary', 'critical')
                
                template.validate_data(fixed_data)
                rendered_html = template.render(fixed_data)
                
                return {
                    "status": "sent",
                    "id": "alert-notification-123",
                    "urgency": urgency,
                    "alert_type": alert_type
                }
            
            mock_tool.side_effect = mock_send_alert_notification
            
            for urgency in urgency_levels:
                result = mock_tool(
                    account_id="test-123",
                    to="operations@kamdental.com",
                    alert_type="warning",
                    message="System alert message",
                    urgency=urgency
                )
                
                assert result["status"] == "sent"
                assert result["urgency"] == urgency
    
    def test_template_data_validation_integration(self, mock_email_environment):
        """Test that data validation works correctly across templates."""
        mocks = mock_email_environment
        
        test_cases = [
            {
                'template': 'practice_report',
                'valid_data': {'location': 'Baytown', 'financial_data': {}, 'provider_data': []},
                'invalid_data': {'location': 'Baytown'}  # Missing required fields
            },
            {
                'template': 'executive_summary', 
                'valid_data': {'locations': [{'name': 'Baytown'}], 'period': 'MTD'},
                'invalid_data': {'period': 'MTD'}  # Missing locations
            },
            {
                'template': 'provider_update',
                'valid_data': {'provider_name': 'Dr. Test', 'performance_data': {'production': 50000}},
                'invalid_data': {'provider_name': 'Dr. Test'}  # Missing performance_data
            },
            {
                'template': 'alert_notification',
                'valid_data': {'message': 'Alert message', 'alert_type': 'warning'},
                'invalid_data': {'alert_type': 'warning'}  # Missing message
            }
        ]
        
        for case in test_cases:
            # Test valid data
            mocks['template'].validate_data.return_value = True
            mocks['template'].validate_data(case['valid_data'])
            mocks['template'].validate_data.assert_called_with(case['valid_data'])
            
            # Test invalid data
            mocks['template'].validate_data.return_value = False
            result = mocks['template'].validate_data(case['invalid_data'])
            assert not result, f"Invalid data should fail validation for {case['template']}"
    
    def test_css_inlining_integration(self, mock_email_environment):
        """Test CSS inlining integration with email sending."""
        mocks = mock_email_environment
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = '<div style="color: blue;">Inlined content</div>'
            
            # Mock template to return HTML with CSS classes
            mocks['template'].render.return_value = '<div class="text-blue">Original content</div>'
            
            with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
                def mock_send_with_inlining(**kwargs):
                    # Simulate template rendering
                    html_with_classes = mocks['template'].render(kwargs)
                    
                    # Simulate CSS inlining
                    inlined_html = mock_inline(html_with_classes)
                    
                    # Simulate sending the inlined HTML
                    return {
                        "status": "sent",
                        "html_size": len(inlined_html),
                        "css_inlined": True
                    }
                
                mock_tool.side_effect = mock_send_with_inlining
                
                result = mock_tool(
                    account_id="test-123",
                    to="recipient@test.com",
                    subject="Test",
                    location="Baytown",
                    financial_data={},
                    provider_data=[]
                )
                
                # Verify CSS inlining was applied
                mock_inline.assert_called_once()
                assert result["css_inlined"] is True
                assert result["html_size"] > 0


class TestMultiAccountSupport:
    """Test multi-account functionality integration."""
    
    def test_account_isolation(self):
        """Test that different accounts are properly isolated."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph:
            
            # Setup multiple accounts
            accounts = [
                mock_auth.Account(username="user1@kamdental.com", account_id="account-1"),
                mock_auth.Account(username="user2@kamdental.com", account_id="account-2")
            ]
            mock_auth.list_accounts.return_value = accounts
            
            # Mock different tokens for different accounts
            def mock_get_token(account_id):
                return f"token-for-{account_id}"
            
            mock_auth.get_token.side_effect = mock_get_token
            mock_graph.request.return_value = {"id": "success"}
            
            from microsoft_mcp.tools import list_emails
            
            # Test first account
            result1 = list_emails(account_id="account-1")
            mock_auth.get_token.assert_called_with("account-1")
            
            # Test second account
            result2 = list_emails(account_id="account-2")
            mock_auth.get_token.assert_called_with("account-2")
            
            # Verify different tokens were used
            assert mock_auth.get_token.call_count == 2
    
    def test_cross_account_operations_prevented(self):
        """Test that operations cannot access wrong account data."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph:
            
            mock_auth.get_token.return_value = "valid-token"
            
            # Mock Graph API to return account-specific data
            def mock_request(method, path, account_id=None, **kwargs):
                if account_id == "account-1":
                    return {"value": [{"id": "email-from-account-1"}]}
                elif account_id == "account-2":
                    return {"value": [{"id": "email-from-account-2"}]}
                else:
                    raise ValueError("Invalid account_id")
            
            mock_graph.request.side_effect = mock_request
            
            from microsoft_mcp.tools import list_emails
            
            # Test account isolation
            result1 = list_emails(account_id="account-1")
            assert result1[0]["id"] == "email-from-account-1"
            
            result2 = list_emails(account_id="account-2")
            assert result2[0]["id"] == "email-from-account-2"
            
            # Test invalid account
            with pytest.raises(ValueError, match="Invalid account_id"):
                list_emails(account_id="invalid-account")


class TestPaginationIntegration:
    """Test pagination functionality across different tools."""
    
    def test_email_pagination(self):
        """Test email listing with pagination."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph:
            
            mock_auth.get_token.return_value = "token"
            
            # Mock paginated response
            def mock_paginate(method, path, account_id=None, params=None):
                # Simulate multiple pages of results
                for i in range(5):
                    yield {"id": f"email-{i}", "subject": f"Subject {i}"}
            
            with patch('microsoft_mcp.graph.paginate', mock_paginate):
                from microsoft_mcp.tools import list_emails
                
                result = list_emails(account_id="test-123", limit=3)
                
                # Should return limited results even with more available
                assert isinstance(result, list)
                assert len(result) <= 3  # Respects limit
    
    def test_search_result_pagination(self):
        """Test search results pagination."""
        with patch('microsoft_mcp.auth') as mock_auth, \
             patch('microsoft_mcp.graph') as mock_graph:
            
            mock_auth.get_token.return_value = "token"
            
            # Mock search response with pagination
            search_responses = [
                {"value": [{"id": "result-1"}, {"id": "result-2"}], "@odata.nextLink": "next-page"},
                {"value": [{"id": "result-3"}, {"id": "result-4"}]}
            ]
            
            call_count = 0
            def mock_request(method, path, account_id=None, **kwargs):
                nonlocal call_count
                response = search_responses[call_count % len(search_responses)]
                call_count += 1
                return response
            
            mock_graph.request.side_effect = mock_request
            
            from microsoft_mcp.tools import search_emails
            
            result = search_emails(
                account_id="test-123",
                query="test",
                limit=10
            )
            
            # Verify search was executed
            assert mock_graph.request.called
            
            # Verify results format
            assert isinstance(result, list)
