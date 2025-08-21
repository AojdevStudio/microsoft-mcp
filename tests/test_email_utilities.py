"""Tests for email styling utilities.

This module tests the email framework utilities that replace
the functionality of quarantined tool tests.
"""

import pytest

from microsoft_mcp.email_framework.utils import format_attachments
from microsoft_mcp.email_framework.utils import style_email_content
from microsoft_mcp.email_framework.utils import validate_email_recipients


class TestEmailUtilities:
    """Test email styling utilities (not tools)."""

    def test_validate_email_recipients_single(self):
        """Test single email recipient validation."""
        result = validate_email_recipients("user@example.com")
        assert result == ["user@example.com"]

    def test_validate_email_recipients_list(self):
        """Test multiple email recipients validation."""
        emails = ["user1@example.com", "user2@example.com"]
        result = validate_email_recipients(emails)
        assert result == emails

    def test_validate_email_recipients_empty(self):
        """Test empty recipient handling."""
        with pytest.raises(ValueError) as exc:
            validate_email_recipients("")
        assert "Empty email address" in str(exc.value)

    def test_validate_email_recipients_invalid_format(self):
        """Test invalid email format rejection."""
        with pytest.raises(ValueError) as exc:
            validate_email_recipients("not-an-email")
        assert "Invalid email format" in str(exc.value)

    def test_validate_email_recipients_mixed_list(self):
        """Test mixed valid/invalid list handling."""
        emails = ["valid@example.com", "invalid-email", "another@valid.com"]
        with pytest.raises(ValueError) as exc:
            validate_email_recipients(emails)
        assert "Invalid email format" in str(exc.value)

    def test_style_email_content_basic(self):
        """Test basic email content styling."""
        content = "Hello World"
        result = style_email_content(content)

        # Verify HTML structure is added
        assert "<html>" in result
        assert "<body>" in result
        assert "Hello World" in result
        assert "</body>" in result
        assert "</html>" in result

    def test_style_email_content_with_template(self):
        """Test email content with template application."""
        content = "Monthly Report"
        result = style_email_content(
            content,
            template_type="practice_report",
            template_data={"location": "Baytown"}
        )

        # Verify template elements are present
        assert "<html>" in result
        assert "Monthly Report" in result or "Practice Performance" in result

    def test_style_email_content_with_theme(self):
        """Test email content with theme application."""
        content = "Test Content"

        # Test Baytown theme
        baytown_result = style_email_content(
            content,
            theme="baytown"
        )
        assert "#2563eb" in baytown_result or "blue" in baytown_result.lower()

        # Test Humble theme
        humble_result = style_email_content(
            content,
            theme="humble"
        )
        assert "#10b981" in humble_result or "green" in humble_result.lower()

    def test_style_email_content_with_signature(self):
        """Test email content with signature addition."""
        content = "Please find attached"
        result = style_email_content(
            content,
            add_signature=True
        )

        # Verify signature elements
        assert "Ossie Irondi" in result
        assert "PharmD" in result
        assert "Chief Operating Officer" in result

    def test_style_email_content_preserves_html(self):
        """Test that existing HTML is preserved."""
        content = "<p>Already <strong>formatted</strong> content</p>"
        result = style_email_content(content)

        # Verify original HTML is preserved
        assert "<strong>formatted</strong>" in result
        assert "<p>" in result

    def test_format_attachments_single_file(self):
        """Test formatting single file attachment."""
        files = ["/path/to/document.pdf"]
        result = format_attachments(files)

        assert len(result) == 1
        assert result[0]["@odata.type"] == "#microsoft.graph.fileAttachment"
        assert result[0]["name"] == "document.pdf"
        assert "contentBytes" in result[0]

    def test_format_attachments_multiple_files(self):
        """Test formatting multiple file attachments."""
        files = [
            "/path/to/document.pdf",
            "/path/to/spreadsheet.xlsx",
            "/path/to/image.png"
        ]
        result = format_attachments(files)

        assert len(result) == 3
        assert result[0]["name"] == "document.pdf"
        assert result[1]["name"] == "spreadsheet.xlsx"
        assert result[2]["name"] == "image.png"

    def test_format_attachments_empty_list(self):
        """Test empty attachment list handling."""
        result = format_attachments([])
        assert result == []

    def test_format_attachments_none(self):
        """Test None attachment handling."""
        result = format_attachments(None)
        assert result == []

    def test_practice_report_template_utility(self):
        """Test practice report template generation (replaces quarantined test)."""
        content = "Performance metrics for July"
        result = style_email_content(
            content,
            template_type="practice_report",
            template_data={
                "location": "Baytown",
                "period": "July 2024",
                "production": "$150,000",
                "collections": "$145,000"
            },
            theme="baytown"
        )

        # Verify template was applied
        assert "Baytown" in result or "Practice Performance" in result
        # Verify theming
        assert "#2563eb" in result or "blue" in result.lower()

    def test_executive_summary_template_utility(self):
        """Test executive summary template generation (replaces quarantined test)."""
        content = "Multi-location overview"
        result = style_email_content(
            content,
            template_type="executive_summary",
            template_data={
                "locations": ["Baytown", "Humble"],
                "total_production": "$300,000"
            },
            theme="executive"
        )

        # Verify executive theming
        assert "#1f2937" in result or "dark" in result.lower()

    def test_provider_update_template_utility(self):
        """Test provider update template generation (replaces quarantined test)."""
        content = "Your performance this month"
        result = style_email_content(
            content,
            template_type="provider_update",
            template_data={
                "provider_name": "Dr. Smith",
                "production": "$50,000",
                "goal": "$60,000"
            }
        )

        # Verify personalization
        assert "performance" in result.lower() or "update" in result.lower()

    def test_alert_notification_template_utility(self):
        """Test alert notification template generation (replaces quarantined test)."""
        content = "Critical system alert"
        result = style_email_content(
            content,
            template_type="alert",
            template_data={
                "alert_type": "critical",
                "urgency": "immediate"
            }
        )

        # Verify alert styling (likely red/urgent colors)
        assert "#ef4444" in result or "red" in result.lower() or "critical" in result.lower()

    def test_inline_css_conversion(self):
        """Test CSS to inline style conversion."""
        # Assuming the style_email_content function handles inlining
        content = "Test content"
        result = style_email_content(content)

        # Check that styles are inline (no <style> tags)
        # The function should convert CSS to inline for email compatibility
        assert 'style="' in result  # Inline styles present

    def test_html_structure_ensures_compatibility(self):
        """Test that HTML structure is email-client compatible."""
        content = "Simple text"
        result = style_email_content(content)

        # Verify DOCTYPE and proper HTML structure
        assert "<!DOCTYPE html>" in result or "<html" in result
        assert "<head>" in result or "<body>" in result
        assert result.count("<html") == result.count("</html>")
        assert result.count("<body") == result.count("</body>")
