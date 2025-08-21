"""Global test configuration and fixtures for Microsoft MCP tests.

This file provides shared fixtures, mock utilities, and test data factories
that can be used across all test modules. It follows pytest best practices
for test isolation and maintainability.
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
import pytest
from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

# Test environment configuration
os.environ["MICROSOFT_MCP_CLIENT_ID"] = "test-client-id-12345"
os.environ["MICROSOFT_MCP_TENANT_ID"] = "test-tenant-id"


@pytest.fixture
def mock_account():
    """Provide a mock Microsoft account for testing."""
    return {
        "username": "test.user@kamdental.com",
        "account_id": "test-account-12345",
        "home_account_id": "test-account-12345"
    }


@pytest.fixture
def mock_accounts_list(mock_account):
    """Provide a list of mock accounts."""
    return [mock_account]


@pytest.fixture
def mock_msal_app():
    """Mock MSAL PublicClientApplication."""
    mock_app = Mock()
    mock_app.get_accounts.return_value = [
        {
            "username": "test.user@kamdental.com",
            "home_account_id": "test-account-12345"
        }
    ]
    mock_app.acquire_token_silent.return_value = {
        "access_token": "mock-access-token-12345",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    return mock_app


@pytest.fixture
def mock_graph_response():
    """Mock successful Graph API response."""
    return {
        "id": "mock-id-12345",
        "subject": "Test Email",
        "from": {"name": "Test Sender", "address": "sender@test.com"},
        "body": {"content": "Test email content", "contentType": "text"},
        "receivedDateTime": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def mock_mcp_session():
    """Mock MCP ClientSession for tool testing."""
    session = Mock(spec=ClientSession)
    
    def mock_call_tool(tool_name: str, params: Dict[str, Any]):
        # Create mock successful response
        result = Mock(spec=CallToolResult)
        result.isError = False
        result.content = [TextContent(type="text", text='{"status": "success"}')]
        return result
    
    session.call_tool = mock_call_tool
    return session


@pytest.fixture
def sample_email_data():
    """Sample email data for testing."""
    return {
        "id": "email-12345",
        "subject": "Test Email Subject",
        "from": {"name": "Test Sender", "address": "sender@test.com"},
        "to": [{"name": "Test Recipient", "address": "recipient@test.com"}],
        "body": {"content": "Test email body content", "contentType": "text"},
        "receivedDateTime": "2025-08-05T10:00:00Z",
        "isRead": False,
        "hasAttachments": False
    }


@pytest.fixture
def sample_calendar_event():
    """Sample calendar event data for testing."""
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    return {
        "id": "event-12345",
        "subject": "Test Meeting",
        "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        "location": {"displayName": "Conference Room A"},
        "attendees": [
            {"emailAddress": {"address": "attendee@test.com", "name": "Test Attendee"}}
        ]
    }


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "id": "contact-12345",
        "first_name": "John",
        "last_name": "Doe",
        "email_addresses": [{"address": "john.doe@test.com", "name": "John Doe"}],
        "phone_numbers": [{"number": "+1234567890", "type": "mobile"}]
    }


@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        "id": "file-12345",
        "name": "test-document.pdf",
        "size": 1024,
        "webUrl": "https://test.sharepoint.com/file.pdf",
        "createdDateTime": datetime.now(timezone.utc).isoformat()
    }


# Email Framework Test Fixtures
@pytest.fixture
def valid_practice_report_data():
    """Valid data for practice report template."""
    return {
        "location": "Baytown",
        "period": "July 2025 MTD",
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
            {"type": "critical", "message": "Call answer rate below target"}
        ],
        "recommendations": [
            {
                "priority": "IMMEDIATE",
                "title": "Improve phone coverage",
                "outcome": "$13,000 potential"
            }
        ]
    }


@pytest.fixture
def valid_executive_summary_data():
    """Valid data for executive summary template."""
    return {
        "period": "July 2025 MTD",
        "locations": [
            {"name": "Baytown", "production": 143343, "goal": 160000, "status": "behind"},
            {"name": "Humble", "production": 178000, "goal": 175000, "status": "on_track"}
        ],
        "total_production": 321343,
        "total_goal": 335000,
        "overall_status": "behind"
    }


@pytest.fixture
def valid_provider_update_data():
    """Valid data for provider update template."""
    return {
        "provider_name": "Dr. Obinna Ezeji",
        "period": "July 2025 MTD",
        "performance_data": {
            "production": 68053,
            "goal": 90000,
            "percentage": 0.756,
            "appointments": 125,
            "case_acceptance": 0.42
        },
        "achievements": ["Top producer this month"],
        "areas_for_improvement": ["Increase case acceptance rate"]
    }


@pytest.fixture
def valid_alert_notification_data():
    """Valid data for alert notification template."""
    return {
        "alert_type": "critical",
        "title": "System Alert",
        "message": "Call answer rate below target threshold",
        "urgency": "high",
        "location": "Baytown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_required": "Review phone coverage schedule"
    }


@pytest.fixture
def mock_email_templates():
    """Mock email template instances."""
    templates = {}
    
    # Mock practice report template
    practice_template = Mock()
    practice_template.render.return_value = "<html>Practice Report</html>"
    practice_template.validate_data.return_value = True
    templates['practice_report'] = practice_template
    
    # Mock executive summary template
    executive_template = Mock()
    executive_template.render.return_value = "<html>Executive Summary</html>"
    executive_template.validate_data.return_value = True
    templates['executive_summary'] = executive_template
    
    # Mock provider update template
    provider_template = Mock()
    provider_template.render.return_value = "<html>Provider Update</html>"
    provider_template.validate_data.return_value = True
    templates['provider_update'] = provider_template
    
    # Mock alert notification template
    alert_template = Mock()
    alert_template.render.return_value = "<html>Alert Notification</html>"
    alert_template.validate_data.return_value = True
    templates['alert_notification'] = alert_template
    
    return templates


# Mock patches that can be used across tests
@pytest.fixture
def mock_auth_module():
    """Mock the entire auth module."""
    # Create a proper mock account object
    mock_account = Mock()
    mock_account.username = "test@kamdental.com"
    mock_account.account_id = "test-123"
    
    mock_auth = Mock()
    mock_auth.list_accounts.return_value = [mock_account]
    mock_auth.get_token.return_value = "mock-token-12345"
    mock_auth.get_app.return_value = Mock()
    
    yield mock_auth


@pytest.fixture
def mock_graph_module():
    """Mock the graph module for API calls."""
    with patch('microsoft_mcp.graph') as mock_graph:
        mock_graph.request.return_value = {"id": "mock-response", "status": "success"}
        yield mock_graph


class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_email(override_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create email data with optional field overrides."""
        base_email = {
            "id": f"email-{uuid.uuid4()}",
            "subject": "Test Email",
            "from": {"name": "Test Sender", "address": "sender@test.com"},
            "to": [{"name": "Test Recipient", "address": "recipient@test.com"}],
            "body": {"content": "Test content", "contentType": "text"},
            "receivedDateTime": datetime.now(timezone.utc).isoformat(),
            "isRead": False
        }
        if override_fields:
            base_email.update(override_fields)
        return base_email
    
    @staticmethod
    def create_calendar_event(override_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create calendar event data with optional field overrides."""
        start_time = datetime.now(timezone.utc) + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        base_event = {
            "id": f"event-{uuid.uuid4()}",
            "subject": "Test Meeting",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "location": {"displayName": "Test Location"}
        }
        if override_fields:
            base_event.update(override_fields)
        return base_event


@pytest.fixture
def test_data_factory():
    """Provide access to test data factory."""
    return TestDataFactory


# Test markers for organization
pytestmark = pytest.mark.unit