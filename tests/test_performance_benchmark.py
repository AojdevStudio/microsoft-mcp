"""Performance benchmarks for microsoft_operations tool.

This module tests that the unified tool meets performance requirements.
"""

import time
from unittest.mock import patch

import pytest

from microsoft_mcp.tools import create_calendar_event_deprecated
from microsoft_mcp.tools import create_contact_deprecated
from microsoft_mcp.tools import list_emails_deprecated
from microsoft_mcp.tools import list_files_deprecated
from microsoft_mcp.tools import microsoft_operations
from microsoft_mcp.tools import send_email_deprecated

# Access the actual function from the FunctionTool decorator
microsoft_operations_func = microsoft_operations.fn


class TestPerformanceBenchmarks:
    """Test performance metrics for unified tool."""

    @pytest.fixture
    def mock_graph_request(self):
        """Mock Graph API request with minimal delay."""
        with patch("microsoft_mcp.tools.graph.request") as mock:
            # Simulate fast API response
            mock.return_value = {"value": [], "status": "success"}
            yield mock

    def test_action_routing_under_100ms(self, mock_graph_request):
        """Test that action routing takes less than 100ms."""
        # Measure routing time for each action
        actions = [
            ("email.list", {}),
            ("email.send", {"to": "test@example.com", "subject": "Test", "body": "Content"}),
            ("email.reply", {"email_id": "msg123", "body": "Reply"}),
            ("email.draft", {"to": "test@example.com", "subject": "Draft", "body": "Content"}),
            ("email.delete", {"email_id": "msg123"}),
        ]

        for action, data in actions:
            # Mock validation to avoid errors
            with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock_validate:
                mock_validate.return_value = ["test@example.com"]

                start_time = time.perf_counter()

                try:
                    microsoft_operations_func(
                        account_id="test@example.com",
                        action=action,
                        data=data
                    )
                except Exception:
                    # We're only measuring routing time, not full execution
                    pass

                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000

                # Assert routing is under 100ms
                assert elapsed_ms < 100, f"Action {action} took {elapsed_ms:.2f}ms (> 100ms limit)"

    def test_bulk_operation_performance(self, mock_graph_request):
        """Test performance with multiple operations."""
        operations = 100  # Run 100 operations

        with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock_validate:
            mock_validate.return_value = ["test@example.com"]

            start_time = time.perf_counter()

            for i in range(operations):
                # Alternate between different actions
                if i % 5 == 0:
                    action = "email.list"
                    data = {}
                elif i % 5 == 1:
                    action = "email.send"
                    data = {"to": f"user{i}@example.com", "subject": f"Test {i}", "body": "Content"}
                elif i % 5 == 2:
                    action = "email.reply"
                    data = {"email_id": f"msg{i}", "body": "Reply"}
                elif i % 5 == 3:
                    action = "email.draft"
                    data = {"to": f"user{i}@example.com", "subject": f"Draft {i}", "body": "Content"}
                else:
                    action = "email.delete"
                    data = {"email_id": f"msg{i}"}

                try:
                    microsoft_operations_func(
                        account_id="test@example.com",
                        action=action,
                        data=data
                    )
                except Exception:
                    pass

            end_time = time.perf_counter()
            elapsed_seconds = end_time - start_time
            ops_per_second = operations / elapsed_seconds

            # Should handle at least 100 ops/second
            assert ops_per_second > 100, f"Only {ops_per_second:.2f} ops/sec (< 100 ops/sec requirement)"

    def test_memory_efficiency(self, mock_graph_request):
        """Test that operations don't leak memory."""
        import gc

        # Get initial memory baseline
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Run many operations
        with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock_validate:
            mock_validate.return_value = ["test@example.com"]

            for i in range(1000):
                try:
                    microsoft_operations_func(
                        account_id="test@example.com",
                        action="email.list",
                        data={}
                    )
                except Exception:
                    pass

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not accumulate more than 10% additional objects
        object_growth = (final_objects - initial_objects) / initial_objects
        assert object_growth < 0.1, f"Object count grew by {object_growth*100:.1f}% (> 10% limit)"

    def test_error_handling_performance(self):
        """Test that error handling is fast."""
        # Test invalid action error
        start_time = time.perf_counter()

        with pytest.raises(ValueError):
            microsoft_operations_func(
                account_id="test@example.com",
                action="invalid.action"
            )

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

        # Error detection should be near-instant (< 10ms)
        assert elapsed_ms < 10, f"Error detection took {elapsed_ms:.2f}ms (> 10ms limit)"

    def test_parameter_validation_performance(self):
        """Test that parameter validation is efficient."""
        with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock_validate:
            # Make validation fast
            mock_validate.side_effect = ValueError("Invalid email")

            start_time = time.perf_counter()

            with pytest.raises(ValueError):
                microsoft_operations_func(
                    account_id="test@example.com",
                    action="email.send",
                    data={"to": "invalid", "subject": "Test", "body": "Content"}
                )

            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000

            # Validation should be fast (< 50ms)
            assert elapsed_ms < 50, f"Validation took {elapsed_ms:.2f}ms (> 50ms limit)"

    @pytest.mark.parametrize("payload_size", [100, 1000, 10000, 100000])
    def test_large_payload_handling(self, payload_size, mock_graph_request):
        """Test performance with different payload sizes."""
        # Create large email body
        large_body = "x" * payload_size

        with patch("microsoft_mcp.email_framework.utils.validate_email_recipients") as mock_validate:
            mock_validate.return_value = ["test@example.com"]

            start_time = time.perf_counter()

            microsoft_operations_func(
                account_id="test@example.com",
                action="email.send",
                data={
                    "to": "test@example.com",
                    "subject": "Large Email",
                    "body": large_body
                }
            )

            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000

            # Should handle even large payloads in reasonable time
            # Allow more time for larger payloads
            max_time = 100 + (payload_size / 1000)  # Base 100ms + 1ms per KB
            assert elapsed_ms < max_time, f"Large payload ({payload_size} chars) took {elapsed_ms:.2f}ms (> {max_time}ms limit)"


class TestDeprecationLayerPerformance:
    """Performance tests specifically for the deprecation layer."""

    @patch("microsoft_mcp.tools.legacy_router.microsoft_operations")
    def test_deprecation_wrapper_overhead_under_50ms(self, mock_operations):
        """Test that deprecation wrapper adds less than 50ms overhead per Story 1.7."""
        mock_operations.return_value = {"status": "success", "emails": []}

        # Test multiple deprecated tools
        deprecated_tools = [
            (list_emails_deprecated, {"account_id": "test@example.com", "folder_name": "inbox"}),
            (send_email_deprecated, {"account_id": "test@example.com", "to": "test@example.com", "subject": "Test", "body": "Body"}),
            (create_calendar_event_deprecated, {"account_id": "test@example.com", "subject": "Meeting", "start_datetime": "2025-08-20T10:00:00", "end_datetime": "2025-08-20T11:00:00"}),
            (list_files_deprecated, {"account_id": "test@example.com", "folder_path": "/Documents"}),
            (create_contact_deprecated, {"account_id": "test@example.com", "first_name": "John", "last_name": "Doe", "email": "john@example.com"})
        ]

        for tool_func, kwargs in deprecated_tools:
            # Measure wrapper overhead (without network calls)
            start_time = time.perf_counter()

            result = tool_func(**kwargs)

            end_time = time.perf_counter()
            overhead_ms = (end_time - start_time) * 1000

            # Story 1.7 requirement: < 50ms overhead
            assert overhead_ms < 50, f"Tool {tool_func.__name__} overhead: {overhead_ms:.2f}ms (> 50ms limit)"

            # Verify it actually worked
            assert result["status"] == "success"
            mock_operations.assert_called()
            mock_operations.reset_mock()

    @patch("microsoft_mcp.tools.legacy_router.microsoft_operations")
    def test_bulk_deprecated_tool_performance(self, mock_operations):
        """Test performance with many deprecated tool calls."""
        mock_operations.return_value = {"status": "success", "emails": []}

        operations_count = 100
        start_time = time.perf_counter()

        # Run 100 deprecated tool calls
        for i in range(operations_count):
            list_emails_deprecated(
                account_id="test@example.com",
                folder_name="inbox",
                limit=10
            )

        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time_ms = (total_time / operations_count) * 1000

        # Average should be well under 50ms per call
        assert avg_time_ms < 20, f"Average deprecated tool time: {avg_time_ms:.2f}ms (> 20ms target)"

        # Should handle at least 50 deprecated calls per second
        ops_per_sec = operations_count / total_time
        assert ops_per_sec > 50, f"Only {ops_per_sec:.1f} deprecated ops/sec (< 50 target)"

    @patch("microsoft_mcp.tools.legacy_router.microsoft_operations")
    def test_parameter_mapping_performance(self, mock_operations):
        """Test that parameter mapping is fast."""
        mock_operations.return_value = {"status": "success"}

        # Test complex parameter mapping
        complex_params = {
            "account_id": "test@example.com",
            "folder_name": "inbox",
            "limit": 100,
            "include_body": True,
            "search_query": "urgent meeting",
            "skip": 50
        }

        start_time = time.perf_counter()

        list_emails_deprecated(**complex_params)

        end_time = time.perf_counter()
        mapping_time_ms = (end_time - start_time) * 1000

        # Parameter mapping should be very fast (< 10ms)
        assert mapping_time_ms < 10, f"Parameter mapping took {mapping_time_ms:.2f}ms (> 10ms limit)"

        # Verify correct mapping occurred
        mock_operations.assert_called_once()
        call_args = mock_operations.call_args[1]
        assert call_args["action"] == "email.list"
        assert call_args["data"]["folder"] == "inbox"
        assert call_args["data"]["limit"] == 100
        assert call_args["data"]["include_body"] is True

    @patch("microsoft_mcp.tools.legacy_router.microsoft_operations")
    def test_error_handling_overhead(self, mock_operations):
        """Test that error handling in deprecation layer is fast."""
        # Mock an error in the underlying operation
        mock_operations.side_effect = Exception("Graph API error")

        start_time = time.perf_counter()

        result = list_emails_deprecated(
            account_id="test@example.com",
            folder_name="invalid_folder"
        )

        end_time = time.perf_counter()
        error_handling_time_ms = (end_time - start_time) * 1000

        # Error handling should be fast (< 20ms)
        assert error_handling_time_ms < 20, f"Error handling took {error_handling_time_ms:.2f}ms (> 20ms limit)"

        # Verify error was handled gracefully
        assert result["status"] == "error"
        assert "Graph API error" in result["message"]
        assert result["legacy_tool"] == "list_emails"

    def test_deprecation_warning_performance(self):
        """Test that deprecation warnings don't significantly impact performance."""
        import warnings

        # Capture warnings to measure overhead
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with patch("microsoft_mcp.tools.legacy_router.microsoft_operations") as mock_operations:
                mock_operations.return_value = {"status": "success"}

                # Measure time with warning system active
                start_time = time.perf_counter()

                # Run multiple operations to get stable measurement
                for _ in range(10):
                    list_emails_deprecated(
                        account_id="test@example.com",
                        folder_name="inbox"
                    )

                end_time = time.perf_counter()
                total_time_ms = (end_time - start_time) * 1000
                avg_time_ms = total_time_ms / 10

                # Warning generation should add minimal overhead (< 5ms per call)
                assert avg_time_ms < 25, f"Average time with warnings: {avg_time_ms:.2f}ms (> 25ms with 5ms warning overhead)"

    @patch("microsoft_mcp.tools.legacy_router.microsoft_operations")
    def test_memory_usage_with_deprecated_tools(self, mock_operations):
        """Test that deprecated tools don't leak memory."""
        import gc

        mock_operations.return_value = {"status": "success"}

        # Get baseline memory
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Run many deprecated tool calls
        for i in range(1000):
            list_emails_deprecated(
                account_id="test@example.com",
                folder_name="inbox",
                limit=10
            )

            # Occasionally collect garbage during the test
            if i % 100 == 0:
                gc.collect()

        # Final cleanup and measurement
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory growth should be minimal (< 10% considering warning objects)
        memory_growth = (final_objects - initial_objects) / initial_objects
        assert memory_growth < 0.10, f"Memory grew by {memory_growth*100:.1f}% (> 10% limit)"
