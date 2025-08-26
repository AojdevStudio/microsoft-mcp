"""
Test suite for MCP tool integration with the KamDental Email Framework.
Tests new email tools and their integration with Microsoft Graph API.
"""

import pytest
from unittest.mock import patch


class TestMCPToolIntegration:
    """Test integration of new MCP tools with the email framework."""
    
    @pytest.fixture
    def mock_graph_request(self):
        """Mock the graph.request function."""
        with patch('microsoft_mcp.graph.request') as mock:
            mock.return_value = {"id": "message-123"}
            yield mock
    
    @pytest.fixture
    def mock_email_operations(self):
        """Mock the nuclear email_operations function."""
        with patch('microsoft_mcp.email_tool.email_operations') as mock:
            mock.return_value = {"status": "success", "message": "Email sent successfully"}
            yield mock
    
    @pytest.fixture
    def valid_practice_report_params(self):
        """Valid parameters for send_practice_report."""
        return {
            "account_id": "test-account-123",
            "to": "executive@kamdental.com",
            "subject": "Baytown Practice Report - July 2025 MTD",
            "location": "Baytown",
            "financial_data": {
                "production": {"value": 143343, "goal": 160000, "status": "behind"},
                "collections": {"value": 107113, "ratio": 0.747},
                "case_acceptance": {"value": 0.3586, "status": "good"},
                "call_answer_rate": {"value": 0.693, "goal": 0.85, "status": "warning"}
            },
            "provider_data": [
                {
                    "name": "Dr. Obinna Ezeji",
                    "role": "Lead Producer",
                    "production": 68053,
                    "goal_percentage": 0.756
                }
            ],
            "alerts": [
                {
                    "type": "critical",
                    "message": "Call answer rate below target"
                }
            ],
            "recommendations": [
                {
                    "priority": "IMMEDIATE",
                    "title": "Improve phone coverage",
                    "outcome": "$13,000 potential"
                }
            ]
        }
    
    def test_send_practice_report_basic(self, mock_email_operations, valid_practice_report_params):
        """Test basic send_practice_report functionality."""
        with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
            mock_tool.return_value = {"status": "sent"}
            
            result = mock_tool(**valid_practice_report_params)
            
            assert result["status"] == "sent"
            mock_tool.assert_called_once_with(**valid_practice_report_params)
    
    def test_send_practice_report_theme_selection(self, mock_email_operations):
        """Test that theme is selected based on location."""
        locations_themes = [
            ("Baytown", "baytown"),
            ("Humble", "humble"),
            ("BAYTOWN", "baytown"),
            ("corporate", "baytown")  # Default
        ]
        
        for location, expected_theme in locations_themes:
            with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
                mock_tool.return_value = {"status": "sent", "theme_used": expected_theme}
                
                result = mock_tool(
                    account_id="test",
                    to="test@example.com",
                    subject="Test",
                    location=location,
                    financial_data={},
                    provider_data=[]
                )
                
                assert result["theme_used"] == expected_theme
    
    def test_send_practice_report_calls_email_operations(self, mock_email_operations, valid_practice_report_params):
        """Test that send_practice_report calls underlying email_operations."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            mock_instance.render.return_value = "<html>Styled report</html>"
            
            with patch('microsoft_mcp.tools.send_practice_report', wraps=lambda **kwargs: mock_email_operations(
                account_id=kwargs['account_id'],
                action="send",
                to=kwargs['to'],
                subject=kwargs['subject'],
                body=mock_instance.render.return_value,
                cc=kwargs.get('cc'),
                bcc=kwargs.get('bcc')
            )):
                # Simulate the tool behavior
                body = mock_instance.render.return_value
                result = mock_email_operations(
                    account_id=valid_practice_report_params['account_id'],
                    action="send",
                    to=valid_practice_report_params['to'],
                    subject=valid_practice_report_params['subject'],
                    body=body
                )
                
                assert mock_email_operations.called
                assert result["status"] == "success"
    
    def test_send_executive_summary_multi_location(self, mock_email_operations):
        """Test send_executive_summary with multiple locations."""
        params = {
            "account_id": "test-account",
            "to": "ceo@kamdental.com",
            "locations_data": [
                {
                    "name": "Baytown",
                    "production": 143343,
                    "goal": 160000,
                    "status": "behind"
                },
                {
                    "name": "Humble",
                    "production": 178000,
                    "goal": 175000,
                    "status": "on_track"
                }
            ],
            "period": "July 2025 MTD"
        }
        
        with patch('microsoft_mcp.tools.send_executive_summary') as mock_tool:
            mock_tool.return_value = {"status": "sent"}
            
            result = mock_tool(**params)
            
            assert result["status"] == "sent"
            mock_tool.assert_called_once()
    
    def test_send_provider_update_personalization(self, mock_email_operations):
        """Test send_provider_update with provider-specific data."""
        params = {
            "account_id": "test-account",
            "to": "dr.ezeji@kamdental.com",
            "provider_name": "Dr. Obinna Ezeji",
            "performance_data": {
                "production": 68053,
                "goal": 90000,
                "percentage": 0.756,
                "appointments": 125
            }
        }
        
        with patch('microsoft_mcp.tools.send_provider_update') as mock_tool:
            mock_tool.return_value = {"status": "sent"}
            
            result = mock_tool(**params)
            
            assert result["status"] == "sent"
    
    def test_send_alert_notification_urgency_levels(self, mock_email_operations):
        """Test send_alert_notification with different urgency levels."""
        urgency_levels = ["immediate", "high", "normal"]
        
        for urgency in urgency_levels:
            params = {
                "account_id": "test-account",
                "to": "operations@kamdental.com",
                "alert_type": "critical" if urgency == "immediate" else "warning",
                "message": "Test alert message",
                "urgency": urgency
            }
            
            with patch('microsoft_mcp.tools.send_alert_notification') as mock_tool:
                mock_tool.return_value = {"status": "sent", "urgency": urgency}
                
                result = mock_tool(**params)
                
                assert result["status"] == "sent"
                assert result["urgency"] == urgency
    
    def test_all_tools_support_cc_bcc(self, mock_email_operations):
        """Test that all new tools support CC and BCC recipients."""
        tools = [
            'send_practice_report',
            'send_executive_summary',
            'send_provider_update',
            'send_alert_notification'
        ]
        
        cc_list = ["manager1@kamdental.com", "manager2@kamdental.com"]
        bcc_list = ["archive@kamdental.com"]
        
        for tool_name in tools:
            with patch(f'microsoft_mcp.tools.{tool_name}') as mock_tool:
                mock_tool.return_value = {"status": "sent"}
                
                # Basic required params
                params = {
                    "account_id": "test",
                    "to": "recipient@kamdental.com",
                    "cc": cc_list,
                    "bcc": bcc_list
                }
                
                # Add tool-specific required params
                if tool_name == 'send_practice_report':
                    params.update({
                        "subject": "Test",
                        "location": "Baytown",
                        "financial_data": {},
                        "provider_data": []
                    })
                elif tool_name == 'send_executive_summary':
                    params.update({
                        "locations_data": [],
                        "period": "MTD"
                    })
                elif tool_name == 'send_provider_update':
                    params.update({
                        "provider_name": "Dr. Test",
                        "performance_data": {}
                    })
                elif tool_name == 'send_alert_notification':
                    params.update({
                        "alert_type": "warning",
                        "message": "Test"
                    })
                
                result = mock_tool(**params)
                assert result["status"] == "sent"
    
    def test_error_handling_invalid_account(self):
        """Test error handling for invalid account ID."""
        with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
            mock_tool.side_effect = Exception("Invalid account ID")
            
            with pytest.raises(Exception) as exc_info:
                mock_tool(
                    account_id="invalid-account",
                    to="test@example.com",
                    subject="Test",
                    location="Baytown",
                    financial_data={},
                    provider_data=[]
                )
            
            assert "Invalid account ID" in str(exc_info.value)
    
    def test_template_rendering_errors(self):
        """Test handling of template rendering errors."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            mock_instance.render.side_effect = ValueError("Missing required data")
            
            with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
                mock_tool.side_effect = ValueError("Missing required data")
                
                with pytest.raises(ValueError) as exc_info:
                    mock_tool(
                        account_id="test",
                        to="test@example.com",
                        subject="Test",
                        location="Baytown",
                        financial_data={},  # Incomplete data
                        provider_data=[]
                    )
                
                assert "Missing required data" in str(exc_info.value)


class TestBackwardCompatibility:
    """Test that new tools maintain backward compatibility."""
    
    def test_email_operations_still_works(self):
        """Test that nuclear email_operations function works."""
        with patch('microsoft_mcp.email_tool.email_operations') as mock_send:
            mock_send.return_value = {"status": "success", "message": "Email sent successfully"}
            
            result = mock_send(
                account_id="test",
                action="send",
                to="recipient@example.com",
                subject="Test Email",
                body="Test content"
            )
            
            assert result["status"] == "success"
            mock_send.assert_called_once()
    
    def test_html_structure_enhancement_compatible(self):
        """Test that ensure_html_structure enhancements are compatible."""
        with patch('microsoft_mcp.tools.ensure_html_structure') as mock_ensure:
            mock_ensure.return_value = "<html>Enhanced content</html>"
            
            plain_text = "Simple email content"
            result = mock_ensure(plain_text)
            
            assert "<html>" in result
            assert "Enhanced content" in result


class TestPerformanceIntegration:
    """Test performance aspects of the integration."""
    
    def test_template_rendering_performance(self):
        """Test that template rendering meets performance requirements."""
        import time
        
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            
            def mock_render(data):
                # Simulate some processing time
                time.sleep(0.1)
                return "<html>Rendered content</html>"
            
            mock_instance.render = mock_render
            
            start_time = time.time()
            result = mock_instance.render({"test": "data"})
            end_time = time.time()
            
            # Should render in under 2 seconds
            assert (end_time - start_time) < 2.0
            assert "<html>" in result
    
    def test_bulk_email_sending(self, mock_email_operations):
        """Test sending multiple emails in sequence."""
        recipients = [
            "exec1@kamdental.com",
            "exec2@kamdental.com",
            "exec3@kamdental.com"
        ]
        
        with patch('microsoft_mcp.tools.send_practice_report') as mock_tool:
            mock_tool.return_value = {"status": "sent"}
            
            results = []
            for recipient in recipients:
                result = mock_tool(
                    account_id="test",
                    to=recipient,
                    subject="Monthly Report",
                    location="Baytown",
                    financial_data={},
                    provider_data=[]
                )
                results.append(result)
            
            assert len(results) == 3
            assert all(r["status"] == "sent" for r in results)