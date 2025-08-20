"""
Comprehensive tests for utility tools (Story 1.6)

Tests the 8 new utility tools that complete the 15-tool architecture:
- list_resources: API discovery
- export_data: Bulk export operations  
- import_data: Bulk import operations
- get_settings: Configuration retrieval
- update_settings: Configuration updates
- validate_data: Data validation framework
- get_system_status: Health monitoring
- get_help: Context-aware help system

Note: get_user_info, get_mailbox_statistics, and unified_search are tested separately
as they were existing tools before Story 1.6.
"""

import json
import os
from unittest.mock import patch

from microsoft_mcp.tools import export_data
from microsoft_mcp.tools import get_help
from microsoft_mcp.tools import get_settings
from microsoft_mcp.tools import get_system_status
from microsoft_mcp.tools import import_data
from microsoft_mcp.tools import list_resources
from microsoft_mcp.tools import update_settings
from microsoft_mcp.tools import validate_data


class TestListResources:
    """Test the list_resources utility tool"""

    def test_list_resources_structure(self):
        """Test that list_resources returns proper structure"""
        result = list_resources.fn()

        assert result["status"] == "success"
        assert "resources" in result

        resources = result["resources"]
        assert "core_operations" in resources
        assert "authentication" in resources
        assert "utilities" in resources
        assert "system_info" in resources

        # Verify system info
        system_info = resources["system_info"]
        assert system_info["total_tools"] == 15
        assert system_info["architecture"] == "ultra-consolidated"
        assert "75%" in system_info["reduction_achieved"]

        # Verify utilities section has all 11 tools
        utilities = resources["utilities"]
        expected_tools = [
            "get_user_info", "get_mailbox_statistics", "unified_search",
            "list_resources", "export_data", "import_data",
            "get_settings", "update_settings", "validate_data",
            "get_system_status", "get_help"
        ]
        for tool in expected_tools:
            assert tool in utilities
            assert "description" in utilities[tool]


class TestExportData:
    """Test the export_data utility tool"""

    @patch("microsoft_mcp.tools.export_contacts")
    def test_export_contacts_success(self, mock_export_contacts):
        """Test successful contact export"""
        mock_export_contacts.return_value = {
            "status": "success",
            "format": "json",
            "data": [{"name": "Test Contact"}]
        }

        result = export_data.fn(
            account_id="test@example.com",
            data_type="contacts",
            format="json",
            filters={"limit": 100}
        )

        assert result["status"] == "success"
        mock_export_contacts.assert_called_once_with("test@example.com", "json", 100)

    @patch("microsoft_mcp.tools.list_emails")
    def test_export_emails_success(self, mock_list_emails):
        """Test successful email export"""
        mock_list_emails.return_value = [
            {"id": "1", "subject": "Test Email"}
        ]

        result = export_data.fn(
            account_id="test@example.com",
            data_type="emails",
            format="json",
            filters={"folder": "inbox", "limit": 50}
        )

        assert result["status"] == "success"
        assert result["data_type"] == "emails"
        assert result["count"] == 1
        assert "data" in result
        mock_list_emails.assert_called_once_with("test@example.com", "inbox", 50, 0, True, None)

    def test_export_invalid_data_type(self):
        """Test export with invalid data type"""
        result = export_data.fn(
            account_id="test@example.com",
            data_type="invalid_type",
            format="json"
        )

        assert result["status"] == "error"
        assert "Unsupported data_type" in result["message"]


class TestImportData:
    """Test the import_data utility tool"""

    @patch("microsoft_mcp.tools.create_contact")
    def test_import_contacts_json_string(self, mock_create_contact):
        """Test importing contacts from JSON string"""
        mock_create_contact.return_value = {"id": "contact123"}

        contact_data = json.dumps([{
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }])

        result = import_data.fn(
            account_id="test@example.com",
            data_type="contacts",
            source=contact_data
        )

        assert result["status"] == "success"
        assert result["imported"] == 1
        assert result["errors"] == 0
        mock_create_contact.assert_called_once()

    @patch("microsoft_mcp.tools.create_calendar_event")
    def test_import_calendar_events(self, mock_create_event):
        """Test importing calendar events"""
        mock_create_event.return_value = {"id": "event123"}

        event_data = json.dumps([{
            "subject": "Test Meeting",
            "start_datetime": "2025-08-19T10:00:00",
            "end_datetime": "2025-08-19T11:00:00"
        }])

        result = import_data.fn(
            account_id="test@example.com",
            data_type="calendar",
            source=event_data
        )

        assert result["status"] == "success"
        assert result["imported"] == 1
        assert result["errors"] == 0
        mock_create_event.assert_called_once()

    def test_import_invalid_json(self):
        """Test import with invalid JSON"""
        result = import_data.fn(
            account_id="test@example.com",
            data_type="contacts",
            source="invalid json data"
        )

        assert result["status"] == "error"
        assert "Failed to parse source data" in result["message"]

    def test_import_unsupported_type(self):
        """Test import with unsupported data type"""
        result = import_data.fn(
            account_id="test@example.com",
            data_type="unsupported",
            source="{}"
        )

        assert result["status"] == "error"
        assert "Unsupported data_type" in result["message"]


class TestGetSettings:
    """Test the get_settings utility tool"""

    @patch.dict(os.environ, {"MICROSOFT_MCP_CLIENT_ID": "test-client-id"})
    def test_get_all_settings(self):
        """Test getting all configuration settings"""
        result = get_settings.fn()

        assert result["status"] == "success"
        assert "all_settings" in result

        settings = result["all_settings"]
        assert "server" in settings
        assert "email" in settings
        assert "auth" in settings
        assert "graph_api" in settings

        # Verify auth settings reflect environment
        assert settings["auth"]["client_id_configured"] is True

    def test_get_specific_category(self):
        """Test getting settings for specific category"""
        result = get_settings.fn(category="server")

        assert result["status"] == "success"
        assert result["category"] == "server"
        assert "settings" in result

        settings = result["settings"]
        assert settings["total_tools"] == 15
        assert settings["framework"] == "FastMCP"

    def test_get_invalid_category(self):
        """Test getting settings for invalid category"""
        result = get_settings.fn(category="invalid")

        assert result["status"] == "error"
        assert "Unknown category" in result["message"]


class TestUpdateSettings:
    """Test the update_settings utility tool"""

    def test_update_email_settings_success(self):
        """Test successful email settings update"""
        new_settings = {
            "signature_enabled": False,
            "styling": "minimal"
        }

        result = update_settings.fn(
            category="email",
            settings=new_settings
        )

        assert result["status"] == "success"
        assert result["category"] == "email"
        assert result["updated_settings"] == new_settings

    def test_update_invalid_category(self):
        """Test update with invalid category"""
        result = update_settings.fn(
            category="invalid",
            settings={"test": "value"}
        )

        assert result["status"] == "error"
        assert "Invalid category" in result["message"]

    def test_update_auth_settings_readonly(self):
        """Test that auth settings are read-only"""
        result = update_settings.fn(
            category="auth",
            settings={"client_id": "new-id"}
        )

        assert result["status"] == "error"
        assert "read-only" in result["message"]

    def test_update_invalid_email_settings(self):
        """Test update with invalid email setting keys"""
        result = update_settings.fn(
            category="email",
            settings={"invalid_key": "value"}
        )

        assert result["status"] == "error"
        assert "Invalid email settings" in result["message"]


class TestValidateData:
    """Test the validate_data utility tool"""

    def test_validate_email_success(self):
        """Test successful email validation"""
        email_data = {
            "to": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test body content"
        }

        result = validate_data.fn(
            data_type="email",
            data=email_data
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "valid"
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_email_missing_fields(self):
        """Test email validation with missing required fields"""
        email_data = {
            "subject": "Test Subject"
            # Missing 'to' field
        }

        result = validate_data.fn(
            data_type="email",
            data=email_data
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "invalid"
        assert result["valid"] is False
        assert any("Missing required field: to" in error for error in result["errors"])

    def test_validate_contact_success(self):
        """Test successful contact validation"""
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }

        result = validate_data.fn(
            data_type="contact",
            data=contact_data
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "valid"
        assert result["valid"] is True

    def test_validate_calendar_datetime_validation(self):
        """Test calendar validation with datetime checks"""
        calendar_data = {
            "subject": "Test Meeting",
            "start_datetime": "2025-08-19T11:00:00",
            "end_datetime": "2025-08-19T10:00:00"  # End before start
        }

        result = validate_data.fn(
            data_type="calendar",
            data=calendar_data
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "invalid"
        assert any("Start time must be before end time" in error for error in result["errors"])

    def test_validate_file_path_security(self):
        """Test file validation with security checks"""
        file_data = {
            "file_path": "/some/path/../../../etc/passwd"
        }

        result = validate_data.fn(
            data_type="file",
            data=file_data
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "invalid"
        assert any("unsafe" in error for error in result["errors"])

    def test_validate_unsupported_type(self):
        """Test validation with unsupported data type"""
        result = validate_data.fn(
            data_type="unsupported",
            data={}
        )

        assert result["status"] == "success"
        assert result["validation_status"] == "invalid"
        assert any("Unsupported data_type" in error for error in result["errors"])


class TestGetSystemStatus:
    """Test the get_system_status utility tool"""

    @patch("microsoft_mcp.tools.list_accounts.fn")
    @patch.dict(os.environ, {"MICROSOFT_MCP_CLIENT_ID": "test-client-id"})
    @patch("pathlib.Path.exists", return_value=True)
    def test_system_status_healthy(self, mock_path_exists, mock_list_accounts_fn):
        """Test system status when everything is healthy"""
        mock_list_accounts_fn.return_value = [{"id": "account1"}]

        result = get_system_status.fn()

        assert result["status"] == "success"
        assert result["health_status"] == "healthy"
        assert len(result["issues"]) == 0

        # Verify system info
        system_info = result["system_info"]
        assert system_info["total_tools"] == 15
        assert system_info["architecture"] == "ultra-consolidated"

        # Verify authentication status
        auth = result["authentication"]
        assert auth["client_id_configured"] is True
        assert auth["token_storage_available"] is True
        assert auth["active_accounts"] == 1

        # Verify services
        services = result["services"]
        assert all(status == "available" for status in services.values())

    @patch("microsoft_mcp.tools.list_accounts.fn")
    @patch.dict(os.environ, {}, clear=True)  # Clear MICROSOFT_MCP_CLIENT_ID
    @patch("pathlib.Path.exists", return_value=False)
    def test_system_status_degraded(self, mock_path_exists, mock_list_accounts_fn):
        """Test system status when there are issues"""
        mock_list_accounts_fn.return_value = []

        result = get_system_status.fn()

        assert result["status"] == "success"
        assert result["health_status"] == "degraded"
        assert len(result["issues"]) > 0

        # Should have issues for missing client ID and token storage
        issues = result["issues"]
        assert any("MICROSOFT_MCP_CLIENT_ID" in issue for issue in issues)
        assert any("Token storage" in issue for issue in issues)


class TestGetHelp:
    """Test the get_help utility tool"""

    def test_get_general_help(self):
        """Test getting general help overview"""
        result = get_help.fn()

        assert result["status"] == "success"
        assert result["help_type"] == "overview"

        # Verify architecture info
        architecture = result["architecture"]
        assert architecture["total_tools"] == 15
        assert "75%" in architecture["reduction"]

        # Verify quick start info
        quick_start = result["quick_start"]
        assert "MICROSOFT_MCP_CLIENT_ID" in quick_start["authentication"]
        assert "microsoft_operations" in quick_start["basic_usage"]

        # Verify main tools listed
        main_tools = result["main_tools"]
        assert "microsoft_operations" in main_tools
        assert "utilities" in main_tools

    def test_get_topic_help_operations(self):
        """Test getting help for operations topic"""
        result = get_help.fn(topic="operations")

        assert result["status"] == "success"
        assert result["help_type"] == "topic"
        assert result["topic"] == "operations"

        help_content = result["help"]
        assert help_content["main_tool"] == "microsoft_operations"

        # Verify categories are listed
        categories = help_content["categories"]
        assert "email" in categories
        assert "calendar" in categories
        assert "file" in categories
        assert "contact" in categories

    def test_get_topic_help_authentication(self):
        """Test getting help for authentication topic"""
        result = get_help.fn(topic="authentication")

        assert result["status"] == "success"
        assert result["help_type"] == "topic"

        help_content = result["help"]
        assert "list_accounts" in help_content["tools"]
        assert "authenticate_account" in help_content["tools"]
        assert len(help_content["workflow"]) > 0

    def test_get_action_help_email_send(self):
        """Test getting help for specific email.send action"""
        result = get_help.fn(action="email.send")

        assert result["status"] == "success"
        assert result["help_type"] == "action"
        assert result["action"] == "email.send"

        help_content = result["help"]
        assert "Send email" in help_content["description"]

        # Verify parameters are documented
        params = help_content["parameters"]
        assert "account_id" in params
        assert "action" in params
        assert "data" in params

        # Verify example is provided
        example = help_content["example"]
        assert example["action"] == "email.send"
        assert "to" in example["data"]

    def test_get_help_invalid_topic(self):
        """Test getting help for invalid topic"""
        result = get_help.fn(topic="invalid_topic")

        assert result["status"] == "error"
        assert "No help available" in result["message"]

    def test_get_help_invalid_action(self):
        """Test getting help for invalid action"""
        result = get_help.fn(action="invalid.action")

        assert result["status"] == "error"
        assert "No help available" in result["message"]


# Integration test to verify all utility tools work together
class TestUtilityToolsIntegration:
    """Integration tests for utility tools working together"""

    def test_help_system_describes_all_utilities(self):
        """Test that help system properly describes all utility tools"""
        # Get list of available utilities
        resources_result = list_resources.fn()
        utilities = resources_result["resources"]["utilities"]

        # Get help for utilities topic
        help_result = get_help.fn(topic="utilities")
        help_tools = help_result["help"]["tools"]

        # Verify all utilities are documented in help
        for utility_name in utilities.keys():
            assert any(utility_name in tool_desc for tool_desc in help_tools)

    @patch("microsoft_mcp.tools.list_accounts.fn")
    def test_system_status_reflects_utility_architecture(self, mock_list_accounts_fn):
        """Test that system status reflects the 15-tool architecture"""
        mock_list_accounts_fn.return_value = [{"id": "account1"}]
        result = get_system_status.fn()

        system_info = result["system_info"]
        assert system_info["total_tools"] == 15
        assert system_info["architecture"] == "ultra-consolidated"

        # Verify utility services are available
        services = result["services"]
        assert "validation_framework" in services
        assert "unified_operations" in services

    @patch("microsoft_mcp.tools.list_accounts.fn")
    @patch.dict(os.environ, {"MICROSOFT_MCP_CLIENT_ID": "test-client-id"})
    def test_settings_and_status_consistency(self, mock_list_accounts_fn):
        """Test that settings and status report consistent information"""
        mock_list_accounts_fn.return_value = [{"id": "account1"}]
        settings_result = get_settings.fn()
        status_result = get_system_status.fn()

        # Both should report client ID as configured
        assert settings_result["all_settings"]["auth"]["client_id_configured"] is True
        assert status_result["authentication"]["client_id_configured"] is True

        # Both should report the same architecture info
        assert settings_result["all_settings"]["server"]["total_tools"] == 15
        assert status_result["system_info"]["total_tools"] == 15
