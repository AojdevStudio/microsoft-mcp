"""
Comprehensive unit tests for the create_calendar_event tool in the Microsoft MCP server.

This test suite covers:
- Successful event creation with various parameter combinations  
- Error handling scenarios (authentication failures, API errors)
- Parameter validation and edge cases
- MCP tool response format compliance
- Mocking of Microsoft Graph API calls

The tests follow Test-Driven Development (TDD) principles and ensure robust
functionality of the calendar event creation tool.

Note: Since create_calendar_event is decorated with @mcp.tool (FastMCP), we access
the underlying function via create_calendar_event.fn for unit testing purposes.
The FunctionTool wrapper is tested separately through integration tests.
"""

import pytest

pytestmark = pytest.mark.legacy  # Mark all tests in this file as legacy

from typing import Any
from unittest.mock import patch

# Import the function under test
from microsoft_mcp.tools import create_calendar_event

# Access the underlying function from the FastMCP tool wrapper
create_calendar_event_fn = create_calendar_event.fn


class TestCreateCalendarEvent:
    """Test suite for the create_calendar_event tool."""

    @pytest.fixture
    def valid_event_data(self) -> dict[str, Any]:
        """Provide valid event data for testing."""
        return {
            "account_id": "test-account-123",
            "subject": "Team Meeting",
            "start_datetime": "2024-12-15T10:00:00",
            "end_datetime": "2024-12-15T11:00:00",
            "attendees": ["john.doe@example.com", "jane.smith@example.com"],
            "location": "Conference Room A",
            "body": "Weekly team sync meeting",
            "is_online_meeting": False,
            "calendar_id": None
        }

    @pytest.fixture
    def mock_graph_response(self) -> dict[str, Any]:
        """Mock successful Graph API response."""
        return {
            "id": "event-123-456",
            "subject": "Team Meeting",
            "start": {
                "dateTime": "2024-12-15T10:00:00",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2024-12-15T11:00:00",
                "timeZone": "UTC"
            },
            "onlineMeetingUrl": ""
        }

    @pytest.fixture
    def mock_online_meeting_response(self) -> dict[str, Any]:
        """Mock Graph API response for online meeting."""
        return {
            "id": "event-789-012",
            "subject": "Virtual Team Meeting",
            "start": {
                "dateTime": "2024-12-15T14:00:00",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2024-12-15T15:00:00",
                "timeZone": "UTC"
            },
            "onlineMeetingUrl": "https://teams.microsoft.com/l/meetup-join/19%3ateam-id"
        }

    @patch("microsoft_mcp.tools.graph.request")
    def test_create_basic_event_success(self, mock_graph_request, valid_event_data, mock_graph_response):
        """Test successful creation of a basic calendar event."""
        # Arrange
        mock_graph_request.return_value = mock_graph_response

        # Act
        result = create_calendar_event_fn(
            account_id=valid_event_data["account_id"],
            subject=valid_event_data["subject"],
            start_datetime=valid_event_data["start_datetime"],
            end_datetime=valid_event_data["end_datetime"]
        )

        # Assert
        assert result is not None
        assert result["id"] == "event-123-456"
        assert result["subject"] == "Team Meeting"
        assert result["start"]["dateTime"] == "2024-12-15T10:00:00"
        assert result["end"]["dateTime"] == "2024-12-15T11:00:00"
        assert result["online_meeting_url"] == ""

        # Verify the Graph API was called with correct parameters
        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        assert call_args[0][0] == "POST"  # HTTP method
        assert call_args[0][1] == "/me/events"  # endpoint
        assert call_args[0][2] == valid_event_data["account_id"]  # account_id

        # Verify the event payload
        event_payload = call_args[1]["json"]
        assert event_payload["subject"] == "Team Meeting"
        assert event_payload["start"]["dateTime"] == "2024-12-15T10:00:00"
        assert event_payload["start"]["timeZone"] == "UTC"
        assert event_payload["end"]["dateTime"] == "2024-12-15T11:00:00"
        assert event_payload["end"]["timeZone"] == "UTC"

    @patch("microsoft_mcp.tools.graph.request")
    def test_create_event_with_all_parameters(self, mock_graph_request, valid_event_data, mock_graph_response):
        """Test event creation with all optional parameters provided."""
        # Arrange
        mock_graph_request.return_value = mock_graph_response

        # Act
        result = create_calendar_event_fn(**valid_event_data)

        # Assert
        assert result is not None

        # Verify the Graph API was called with correct parameters
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]

        # Check all parameters are included in the payload
        assert event_payload["subject"] == valid_event_data["subject"]
        assert event_payload["location"]["displayName"] == valid_event_data["location"]
        assert event_payload["body"]["contentType"] == "HTML"
        assert event_payload["body"]["content"] == valid_event_data["body"]
        assert len(event_payload["attendees"]) == 2
        assert event_payload["attendees"][0]["emailAddress"]["address"] == "john.doe@example.com"
        assert event_payload["attendees"][0]["type"] == "required"
        assert event_payload["attendees"][1]["emailAddress"]["address"] == "jane.smith@example.com"
        assert event_payload["attendees"][1]["type"] == "required"

    @patch("microsoft_mcp.tools.graph.request")
    def test_create_online_meeting_event(self, mock_graph_request, mock_online_meeting_response):
        """Test creation of an online Teams meeting event."""
        # Arrange
        mock_graph_request.return_value = mock_online_meeting_response

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Virtual Team Meeting",
            start_datetime="2024-12-15T14:00:00",
            end_datetime="2024-12-15T15:00:00",
            is_online_meeting=True
        )

        # Assert
        assert result is not None
        assert result["online_meeting_url"] == "https://teams.microsoft.com/l/meetup-join/19%3ateam-id"

        # Verify online meeting parameters were included
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]
        assert event_payload["isOnlineMeeting"] is True
        assert event_payload["onlineMeetingProvider"] == "teamsForBusiness"

    @patch("microsoft_mcp.tools.graph.request")
    def test_create_event_with_specific_calendar(self, mock_graph_request, mock_graph_response):
        """Test event creation in a specific calendar."""
        # Arrange
        mock_graph_request.return_value = mock_graph_response
        calendar_id = "calendar-456-789"

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Team Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            calendar_id=calendar_id
        )

        # Assert
        assert result is not None

        # Verify the correct endpoint was called
        call_args = mock_graph_request.call_args
        expected_endpoint = f"/me/calendars/{calendar_id}/events"
        assert call_args[0][1] == expected_endpoint

    @patch("microsoft_mcp.tools.graph.request")
    def test_create_event_without_optional_parameters(self, mock_graph_request, mock_graph_response):
        """Test event creation with only required parameters."""
        # Arrange
        mock_graph_request.return_value = mock_graph_response

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Simple Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00"
        )

        # Assert
        assert result is not None

        # Verify only required fields are in the payload
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]

        # Should have basic fields
        assert "subject" in event_payload
        assert "start" in event_payload
        assert "end" in event_payload

        # Should not have optional fields
        assert "location" not in event_payload
        assert "body" not in event_payload
        assert "attendees" not in event_payload
        assert "isOnlineMeeting" not in event_payload

    @patch("microsoft_mcp.tools.graph.request")
    def test_authentication_failure_error(self, mock_graph_request):
        """Test handling of authentication failures."""
        # Arrange
        mock_graph_request.side_effect = Exception("Authentication failed: Invalid token")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            create_calendar_event_fn(
                account_id="invalid-account",
                subject="Test Meeting",
                start_datetime="2024-12-15T10:00:00",
                end_datetime="2024-12-15T11:00:00"
            )

        assert "Authentication failed" in str(exc_info.value)

    @patch("microsoft_mcp.tools.graph.request")
    def test_graph_api_error_handling(self, mock_graph_request):
        """Test handling of various Graph API errors."""
        # Test different error scenarios
        error_scenarios = [
            {"error": "BadRequest", "message": "Invalid datetime format"},
            {"error": "Forbidden", "message": "Insufficient permissions"},
            {"error": "NotFound", "message": "Calendar not found"},
            {"error": "TooManyRequests", "message": "Rate limit exceeded"}
        ]

        for error_scenario in error_scenarios:
            # Arrange
            mock_graph_request.side_effect = Exception(f"{error_scenario['error']}: {error_scenario['message']}")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                create_calendar_event_fn(
                    account_id="test-account",
                    subject="Test Meeting",
                    start_datetime="2024-12-15T10:00:00",
                    end_datetime="2024-12-15T11:00:00"
                )

            assert error_scenario["error"] in str(exc_info.value)

    @patch("microsoft_mcp.tools.graph.request")
    def test_malformed_graph_response(self, mock_graph_request):
        """Test handling of malformed Graph API responses."""
        # Arrange - Mock a response missing required fields
        mock_graph_request.return_value = {
            "id": "event-123"
            # Missing subject, start, end fields
        }

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Test Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00"
        )

        # Assert - Should handle missing fields gracefully
        assert result is not None
        assert result["id"] == "event-123"
        assert result["subject"] is None  # Missing field should be None
        assert result["start"] is None
        assert result["end"] is None
        assert result["online_meeting_url"] == ""

    def test_datetime_format_validation(self):
        """Test that function accepts valid ISO datetime formats."""
        # Valid formats should not raise exceptions during the function call setup
        valid_formats = [
            "2024-12-15T10:00:00",
            "2024-12-15T10:00:00Z",
            "2024-12-15T10:00:00.000Z",
            "2024-12-15T10:00:00+00:00",
            "2024-12-15T10:00:00-05:00"
        ]

        with patch("microsoft_mcp.tools.graph.request") as mock_request:
            mock_request.return_value = {"id": "test", "subject": "test", "start": {}, "end": {}, "onlineMeetingUrl": ""}

            for date_format in valid_formats:
                # Should not raise any validation errors
                result = create_calendar_event_fn(
                    account_id="test-account",
                    subject="Test Meeting",
                    start_datetime=date_format,
                    end_datetime=date_format
                )
                assert result is not None

    @patch("microsoft_mcp.tools.graph.request")
    def test_attendees_parameter_formats(self, mock_graph_request):
        """Test different formats for attendees parameter."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "event-123",
            "subject": "Test",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Test with list of email strings
        attendees_list = ["user1@example.com", "user2@example.com", "user3@example.com"]

        # Act
        result = create_calendar_event_fn(
            account_id="test-account",
            subject="Test Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            attendees=attendees_list
        )

        # Assert
        assert result is not None

        # Check that attendees were properly formatted in the API call
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]
        assert len(event_payload["attendees"]) == 3

        for i, attendee in enumerate(event_payload["attendees"]):
            assert attendee["emailAddress"]["address"] == attendees_list[i]
            assert attendee["type"] == "required"

    @patch("microsoft_mcp.tools.graph.request")
    def test_empty_attendees_list(self, mock_graph_request):
        """Test handling of empty attendees list."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "event-123",
            "subject": "Test",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Act
        result = create_calendar_event_fn(
            account_id="test-account",
            subject="Test Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            attendees=[]
        )

        # Assert
        assert result is not None

        # Verify that no attendees field is included in the payload
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]
        assert "attendees" not in event_payload

    @patch("microsoft_mcp.tools.graph.request")
    def test_mcp_response_format_compliance(self, mock_graph_request, mock_graph_response):
        """Test that the response format complies with MCP tool standards."""
        # Arrange
        mock_graph_request.return_value = mock_graph_response

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Test Meeting",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00"
        )

        # Assert MCP response format compliance
        assert isinstance(result, dict), "Response should be a dictionary"

        # Check for required fields in MCP tool response
        required_fields = ["id", "subject", "start", "end", "online_meeting_url"]
        for field in required_fields:
            assert field in result, f"Response missing required field: {field}"

        # Verify field types
        assert isinstance(result["id"], (str, type(None))), "ID should be string or None"
        assert isinstance(result["subject"], (str, type(None))), "Subject should be string or None"
        assert isinstance(result["online_meeting_url"], str), "Online meeting URL should be string"

    @patch("microsoft_mcp.tools.graph.request")
    def test_unicode_and_special_characters(self, mock_graph_request):
        """Test handling of unicode and special characters in event data."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "event-unicode-123",
            "subject": "Réunion d'équipe 🚀",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject="Réunion d'équipe 🚀",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            location="Salle de conférence «A»",
            body="Discussion sur les projets Q4 & développement 2025 → stratégie",
            attendees=["andré.martin@example.com", "josé.garcía@example.com"]
        )

        # Assert
        assert result is not None
        assert result["subject"] == "Réunion d'équipe 🚀"

        # Verify unicode characters are properly handled in the API call
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]
        assert event_payload["subject"] == "Réunion d'équipe 🚀"
        assert event_payload["location"]["displayName"] == "Salle de conférence «A»"
        assert "Q4 & développement 2025 → stratégie" in event_payload["body"]["content"]

    @patch("microsoft_mcp.tools.graph.request")
    def test_large_event_data(self, mock_graph_request):
        """Test handling of events with large amounts of data."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "event-large-123",
            "subject": "Large Event",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Create large data sets
        large_subject = "Very Long Meeting Subject " * 50  # ~1500 characters
        large_body = "This is a very detailed meeting description. " * 100  # ~4500 characters
        many_attendees = [f"user{i}@example.com" for i in range(50)]  # 50 attendees

        # Act
        result = create_calendar_event_fn(
            account_id="test-account-123",
            subject=large_subject,
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            body=large_body,
            attendees=many_attendees
        )

        # Assert
        assert result is not None

        # Verify large data is properly handled
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]
        assert len(event_payload["subject"]) > 1000
        assert len(event_payload["body"]["content"]) > 4000
        assert len(event_payload["attendees"]) == 50

    @patch("microsoft_mcp.tools.graph.request")
    def test_concurrent_event_creation_simulation(self, mock_graph_request):
        """Test simulation of concurrent event creation calls."""
        # Arrange
        call_count = 0

        def mock_request_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return {
                "id": f"event-concurrent-{call_count}",
                "subject": f"Concurrent Event {call_count}",
                "start": {},
                "end": {},
                "onlineMeetingUrl": ""
            }

        mock_graph_request.side_effect = mock_request_side_effect

        # Act - Simulate multiple concurrent calls
        results = []
        for i in range(5):
            result = create_calendar_event_fn(
                account_id=f"test-account-{i}",
                subject=f"Concurrent Meeting {i}",
                start_datetime="2024-12-15T10:00:00",
                end_datetime="2024-12-15T11:00:00"
            )
            results.append(result)

        # Assert
        assert len(results) == 5
        assert mock_graph_request.call_count == 5

        # Verify each call received unique response
        for i, result in enumerate(results, 1):
            assert result["id"] == f"event-concurrent-{i}"
            assert result["subject"] == f"Concurrent Event {i}"


class TestCreateCalendarEventEdgeCases:
    """Test edge cases and boundary conditions for create_calendar_event."""

    @patch("microsoft_mcp.tools.graph.request")
    def test_minimum_required_parameters(self, mock_graph_request):
        """Test creation with absolute minimum required parameters."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "minimal-event",
            "subject": "",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Act - Only provide required parameters
        result = create_calendar_event_fn(
            account_id="test",
            subject="",  # Empty subject
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T10:00:00"  # Same start/end time
        )

        # Assert
        assert result is not None

        # Verify minimal payload structure
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]

        # Should only contain basic required fields
        expected_keys = {"subject", "start", "end"}
        assert set(event_payload.keys()) == expected_keys

    @patch("microsoft_mcp.tools.graph.request")
    def test_boundary_datetime_values(self, mock_graph_request):
        """Test with boundary datetime values."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "boundary-event",
            "subject": "Boundary Test",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Test various boundary datetime scenarios
        boundary_cases = [
            # Far future date
            ("2099-12-31T23:59:59", "2099-12-31T23:59:59"),
            # Past date (should still work for API call)
            ("2020-01-01T00:00:00", "2020-01-01T01:00:00"),
            # Leap year date
            ("2024-02-29T12:00:00", "2024-02-29T13:00:00")
        ]

        for start_dt, end_dt in boundary_cases:
            # Act
            result = create_calendar_event_fn(
                account_id="test-account",
                subject="Boundary Test Event",
                start_datetime=start_dt,
                end_datetime=end_dt
            )

            # Assert
            assert result is not None
            assert result["id"] == "boundary-event"

    @patch("microsoft_mcp.tools.graph.request")
    def test_none_values_for_optional_parameters(self, mock_graph_request):
        """Test explicit None values for optional parameters."""
        # Arrange
        mock_graph_request.return_value = {
            "id": "none-test-event",
            "subject": "None Test",
            "start": {},
            "end": {},
            "onlineMeetingUrl": ""
        }

        # Act - Explicitly pass None for optional parameters
        result = create_calendar_event_fn(
            account_id="test-account",
            subject="None Test Event",
            start_datetime="2024-12-15T10:00:00",
            end_datetime="2024-12-15T11:00:00",
            attendees=None,
            location=None,
            body=None,
            is_online_meeting=False,
            calendar_id=None
        )

        # Assert
        assert result is not None

        # Verify None values don't create corresponding fields in payload
        call_args = mock_graph_request.call_args
        event_payload = call_args[1]["json"]

        assert "attendees" not in event_payload
        assert "location" not in event_payload
        assert "body" not in event_payload
        assert "isOnlineMeeting" not in event_payload
