"""
HTML-only email formatter for Microsoft MCP.

This module provides utilities to ensure all email content is formatted as HTML
for consistent rendering in Outlook, solving text spacing issues.
"""

from html import escape
from typing import Any


class HTMLEmailFormatter:
    """
    Converts any text content to properly formatted HTML for email.
    
    Designed for Outlook compatibility with proper spacing and formatting.
    """

    # Base HTML template for emails
    BASE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        p {{
            margin: 1em 0;
        }}
        .email-content {{
            max-width: 600px;
        }}
    </style>
</head>
<body>
    <div class="email-content">
        {content}
    </div>
</body>
</html>"""

    @classmethod
    def format_to_html(cls, content: str) -> dict[str, Any]:
        """
        Convert any text content to HTML format for Microsoft Graph API.
        
        Args:
            content: Raw text or HTML content
            
        Returns:
            Dict with contentType='html' and formatted content
        """
        if cls._is_already_html(content):
            # Already HTML, ensure it's complete
            html_content = cls._ensure_complete_html(content)
        else:
            # Convert plain text to HTML
            html_content = cls._text_to_html(content)

        return {
            "contentType": "html",
            "content": html_content
        }

    @classmethod
    def _is_already_html(cls, content: str) -> bool:
        """Check if content is already HTML formatted."""
        content_lower = content.lower().strip()
        return (
            content_lower.startswith("<!doctype html") or
            content_lower.startswith("<html") or
            "<p>" in content_lower or
            "<br>" in content_lower or
            "<div>" in content_lower
        )

    @classmethod
    def _ensure_complete_html(cls, html_content: str) -> str:
        """Ensure HTML content has proper structure."""
        content_lower = html_content.lower().strip()

        # If it's already a complete HTML document, return as-is
        if content_lower.startswith("<!doctype html") or content_lower.startswith("<html"):
            return html_content

        # If it has HTML tags but no document structure, wrap it
        if any(tag in content_lower for tag in ["<p>", "<div>", "<br>", "<span>"]):
            return cls.BASE_TEMPLATE.format(content=html_content)

        # Fallback: treat as text
        return cls._text_to_html(html_content)

    @classmethod
    def _text_to_html(cls, text: str) -> str:
        """Convert plain text to properly formatted HTML."""
        if not text.strip():
            return cls.BASE_TEMPLATE.format(content="<p></p>")

        # Escape HTML characters
        escaped_text = escape(text)

        # Split into paragraphs (double newlines)
        paragraphs = escaped_text.split("\n\n")

        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # Convert single newlines within paragraphs to <br> tags
                formatted_para = para.replace("\n", "<br>")
                formatted_paragraphs.append(f"<p>{formatted_para}</p>")

        # If no paragraphs found, treat the whole thing as one paragraph
        if not formatted_paragraphs:
            content_with_breaks = escaped_text.replace("\n", "<br>")
            formatted_paragraphs = [f"<p>{content_with_breaks}</p>"]

        content = "\n".join(formatted_paragraphs)
        return cls.BASE_TEMPLATE.format(content=content)

    @classmethod
    def format_simple_message(cls, message: str) -> dict[str, Any]:
        """
        Format simple messages (like 'Yes', 'Thanks', etc.) as HTML.
        
        Args:
            message: Simple text message
            
        Returns:
            Dict with contentType='html' and formatted content
        """
        if not message.strip():
            message = " "  # Ensure non-empty content

        escaped_message = escape(message.strip())
        simple_html = f"<p>{escaped_message}</p>"

        return {
            "contentType": "html",
            "content": cls.BASE_TEMPLATE.format(content=simple_html)
        }

    @classmethod
    def preserve_existing_html(cls, html_content: str) -> dict[str, Any]:
        """
        Preserve existing HTML content (for your styled templates).
        
        Args:
            html_content: Pre-formatted HTML content
            
        Returns:
            Dict with contentType='html' and content
        """
        return {
            "contentType": "html",
            "content": html_content
        }


# Convenience functions for common use cases
def ensure_html_email_body(content: str) -> dict[str, Any]:
    """
    Main function to ensure any content becomes HTML email body.
    
    This is the primary function to use in email tools.
    """
    return HTMLEmailFormatter.format_to_html(content)


def format_simple_reply(message: str) -> dict[str, Any]:
    """Format simple reply messages as HTML."""
    return HTMLEmailFormatter.format_simple_message(message)


def preserve_styled_html(html_content: str) -> dict[str, Any]:
    """Preserve pre-styled HTML content."""
    return HTMLEmailFormatter.preserve_existing_html(html_content)
