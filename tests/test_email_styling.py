"""
Tests for email styling functionality in Microsoft MCP tools.
These tests verify HTML structure, inline styling, and professional formatting.
"""

from microsoft_mcp.tools import ensure_html_structure


class TestEmailStyling:
    """Test suite for email HTML structure and styling."""
    
    def test_ensure_html_structure_adds_proper_html_wrapper(self):
        """Test that ensure_html_structure adds complete HTML structure with inline styles."""
        plain_content = "Hello, this is a test email."
        result = ensure_html_structure(plain_content)
        
        # Should have DOCTYPE
        assert result.startswith('<!DOCTYPE html>')
        
        # Should have html, head, and body tags
        assert '<html>' in result
        assert '<head>' in result
        assert '<body' in result
        assert '</body>' in result
        assert '</html>' in result
        
        # Should have meta tags for proper rendering
        assert '<meta charset="UTF-8">' in result
        assert '<meta name="viewport"' in result
        
        # Should have inline styles on body
        assert 'style=' in result
        assert 'font-family:' in result
        assert 'background-color:' in result
    
    def test_no_css_gradients_present(self):
        """Test that no CSS gradients are used in the styling."""
        content = "Test content"
        result = ensure_html_structure(content)
        
        # Should not contain any gradient CSS
        assert 'gradient' not in result.lower()
        assert 'linear-gradient' not in result.lower()
        assert 'radial-gradient' not in result.lower()
        assert 'conic-gradient' not in result.lower()
    
    def test_all_styles_are_inline(self):
        """Test that all styles are inline, not in style blocks."""
        content = "Test content"
        result = ensure_html_structure(content)
        
        # Should not have style tags
        assert '<style>' not in result
        assert '</style>' not in result
        
        # Should have inline styles
        assert 'style="' in result
    
    def test_professional_email_template_structure(self):
        """Test that email has professional template structure."""
        content = "Email body content"
        result = ensure_html_structure(content)
        
        # Should have container div with styling
        assert '<div' in result
        assert 'max-width:' in result
        assert 'margin:' in result
        assert 'padding:' in result
        
        # Should have proper background colors
        assert 'background-color:' in result
        assert '#f5f5f5' in result or '#f9f9f9' in result  # Light gray background
        assert '#ffffff' in result  # White content area
    
    def test_signature_formatting(self):
        """Test that signature is properly formatted with HTML."""
        signature = """**Ossie Irondi PharmD.**
KC Ventures PLLC, 
Chief Operating Officer 
Baytown Office: 281-421-5950
Humble Office: 281-812-3333
Cell: 346-644-0193
https://www.kamdental.com
<a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled">Book Time With Me</a>"""
        
        content = f"Email body\n\n{signature}"
        result = ensure_html_structure(content)
        
        # Signature should be in a separate div
        assert '<div' in result
        assert 'border-top:' in result  # Should have separator
        
        # Bold text should be properly formatted
        assert '<strong>Ossie Irondi PharmD.</strong>' in result
        
        # Links should be properly formatted
        assert '<a href="https://www.kamdental.com"' in result
        assert 'color:' in result  # Links should have color styling
        assert 'text-decoration:' in result
        
        # Phone numbers should be formatted
        assert 'Baytown Office: 281-421-5950' in result
        assert '<br>' in result  # Line breaks should be HTML breaks
    
    def test_color_contrast_no_white_on_white(self):
        """Test that text has proper contrast, no white-on-white."""
        content = "Test email content"
        result = ensure_html_structure(content)
        
        # Should have dark text color
        assert 'color: #' in result
        assert 'color: #333333' in result or 'color: #2c3e50' in result or 'color: #1a1a1a' in result
        
        # Should not have white text on white background
        assert 'color: #ffffff' not in result or 'background-color: #ffffff' not in result
        assert 'color: white' not in result or 'background-color: white' not in result
    
    def test_responsive_email_design(self):
        """Test that email has responsive design elements."""
        content = "Responsive email content"
        result = ensure_html_structure(content)
        
        # Should have viewport meta tag
        assert 'viewport' in result
        assert 'width=device-width' in result
        
        # Should have max-width for content
        assert 'max-width: 600px' in result or 'max-width:600px' in result
        
        # Should have proper table structure for email clients
        assert '<table' in result
        assert 'width="100%"' in result
        assert 'cellpadding=' in result
        assert 'cellspacing=' in result
    
    def test_handles_existing_html_content(self):
        """Test that function properly handles content that already has HTML."""
        html_content = "<p>This is already <strong>HTML</strong> content.</p>"
        result = ensure_html_structure(html_content)
        
        # Should not double-wrap HTML
        assert result.count('<!DOCTYPE html>') == 1
        assert result.count('<html>') == 1
        assert result.count('<body') == 1
        
        # Original HTML should be preserved
        assert '<p>This is already <strong>HTML</strong> content.</p>' in result
    
    def test_email_client_compatibility(self):
        """Test that HTML is compatible with major email clients."""
        content = "Email for all clients"
        result = ensure_html_structure(content)
        
        # Should use table-based layout for Outlook compatibility
        assert '<table' in result
        
        # Should not use unsupported CSS properties
        assert 'display: flex' not in result
        assert 'display: grid' not in result
        assert 'position: fixed' not in result
        assert 'position: absolute' not in result
        
        # Should use bgcolor attribute for older clients
        assert 'bgcolor=' in result
    
    def test_professional_styling_elements(self):
        """Test that email includes professional styling elements."""
        content = "Professional email content"
        result = ensure_html_structure(content)
        
        # Should have professional fonts
        assert 'Arial' in result or 'Helvetica' in result or 'sans-serif' in result
        
        # Should have proper spacing
        assert 'line-height:' in result
        assert '1.6' in result or '1.5' in result or '24px' in result
        
        # Should have professional colors
        assert '#' in result  # Hex colors
        assert 'border-radius:' in result  # Rounded corners for modern look
        
        # Should have shadow for depth
        assert 'box-shadow:' in result


class TestEmailSendingWithStyling:
    """Test suite for email sending with proper styling."""
    
    def test_ensure_html_structure_with_classes(self):
        """Test that CSS classes are converted to inline styles."""
        content = '<div class="header">Header</div><div class="section">Section</div>'
        result = ensure_html_structure(content)
        
        # Should have inline styles instead of classes
        assert 'style="background-color: #667eea; color: white;' in result
        assert 'style="background-color: #f8f9fa;' in result
        assert 'class="header"' not in result
        assert 'class="section"' not in result
    
    def test_ensure_html_structure_with_highlight_class(self):
        """Test that highlight class is converted to inline styles."""
        content = '<div class="highlight">Important info</div>'
        result = ensure_html_structure(content)
        
        # Should have inline styles for highlight
        assert 'style="background-color: #e3f2fd;' in result
        assert 'class="highlight"' not in result
    
    def test_ensure_html_structure_with_strong_yes_class(self):
        """Test that strong-yes class is converted to inline styles."""
        content = '<div class="strong-yes">YES</div>'
        result = ensure_html_structure(content)
        
        # Should have inline styles for strong-yes
        assert 'style="background-color: #28a745; color: white;' in result
        assert 'font-weight: bold;' in result
        assert 'class="strong-yes"' not in result


class TestSignatureIntegration:
    """Test suite for signature integration in emails."""
    
    def test_signature_appended_to_email_body(self):
        """Test that signature is automatically appended to email body."""
        body_content = "This is the main email content."
        result = ensure_html_structure(body_content)
        
        # Should contain the signature
        assert 'Ossie Irondi PharmD.' in result
        assert 'KC Ventures PLLC' in result
        assert 'Chief Operating Officer' in result
        assert '281-421-5950' in result
        assert 'https://www.kamdental.com' in result
        assert 'Book Time With Me' in result
    
    def test_signature_has_proper_separator(self):
        """Test that signature is separated from body with a styled separator."""
        body_content = "Email body text."
        result = ensure_html_structure(body_content)
        
        # Should have a visual separator before signature
        assert 'border-top:' in result
        assert '1px solid' in result
        assert '#e0e0e0' in result or '#ddd' in result or '#ccc' in result
        
        # Should have proper spacing
        assert 'margin-top:' in result
        assert 'padding-top:' in result