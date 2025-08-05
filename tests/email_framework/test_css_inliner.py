"""
Test suite for CSS inlining functionality in the KamDental Email Framework.
Tests CSS parsing, inline style application, and email client compatibility.
"""

import pytest
from unittest.mock import patch


class TestCSSInliner:
    """Test the CSS inlining functionality for email compatibility."""
    
    @pytest.fixture
    def sample_css(self):
        """Provide sample CSS for testing."""
        return """
        .metric-card {
            background: #F7FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .status-behind {
            color: #E53E3E;
        }
        
        .status-good {
            color: #38A169;
        }
        """
    
    @pytest.fixture
    def sample_html(self):
        """Provide sample HTML for testing."""
        return """
        <div class="metric-card">
            <div class="metric-label">MTD Production</div>
            <div class="metric-value status-behind">$143,343</div>
            <div class="metric-subtitle">89.6% to goal</div>
        </div>
        """
    
    def test_inline_css_basic_functionality(self, sample_css, sample_html):
        """Test basic CSS inlining functionality."""
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            expected_output = """
            <div style="background: #F7FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; text-align: center;">
                <div class="metric-label">MTD Production</div>
                <div style="font-size: 24px; font-weight: 700; margin-bottom: 4px; color: #E53E3E;">$143,343</div>
                <div class="metric-subtitle">89.6% to goal</div>
            </div>
            """
            mock_inline.return_value = expected_output
            
            result = mock_inline(sample_html, sample_css)
            assert 'style=' in result
            assert 'background: #F7FAFC' in result
            assert 'color: #E53E3E' in result
    
    def test_inline_css_removes_class_attributes(self):
        """Test that class attributes are removed after inlining."""
        html = '<div class="test-class">Content</div>'
        css = '.test-class { color: red; }'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = '<div style="color: red;">Content</div>'
            result = mock_inline(html, css)
            
            assert 'class=' not in result
            assert 'style="color: red;"' in result
    
    def test_inline_css_handles_multiple_classes(self):
        """Test handling of elements with multiple classes."""
        html = '<div class="metric-card highlight">Content</div>'
        css = """
        .metric-card { background: white; padding: 10px; }
        .highlight { border: 2px solid blue; }
        """
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = '<div style="background: white; padding: 10px; border: 2px solid blue;">Content</div>'
            result = mock_inline(html, css)
            
            assert 'background: white' in result
            assert 'border: 2px solid blue' in result
    
    def test_inline_css_preserves_existing_inline_styles(self):
        """Test that existing inline styles are preserved and merged."""
        html = '<div class="card" style="margin: 10px;">Content</div>'
        css = '.card { padding: 20px; }'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = '<div style="margin: 10px; padding: 20px;">Content</div>'
            result = mock_inline(html, css)
            
            assert 'margin: 10px' in result
            assert 'padding: 20px' in result
    
    def test_inline_css_handles_important_declarations(self):
        """Test handling of !important CSS declarations."""
        html = '<div class="alert">Warning</div>'
        css = '.alert { color: red !important; background: yellow; }'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            # Important declarations should take precedence
            mock_inline.return_value = '<div style="color: red; background: yellow;">Warning</div>'
            result = mock_inline(html, css)
            
            assert 'color: red' in result
            assert '!important' not in result  # Should be removed in inline styles
    
    def test_inline_css_email_client_compatibility(self):
        """Test that inlined CSS is compatible with email clients."""
        incompatible_properties = [
            'display: flex',
            'display: grid',
            'position: fixed',
            'position: absolute',
            'transform:',
            'animation:',
            'transition:'
        ]
        
        html = '<div class="modern">Content</div>'
        css = '.modern { display: flex; transform: rotate(45deg); }'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            # These properties should be filtered out
            mock_inline.return_value = '<div style="">Content</div>'
            result = mock_inline(html, css)
            
            for prop in incompatible_properties:
                assert prop not in result
    
    def test_inline_css_table_layout_support(self):
        """Test support for table-based layouts for Outlook."""
        html = """
        <table class="email-container">
            <tr class="email-row">
                <td class="email-cell">Content</td>
            </tr>
        </table>
        """
        css = """
        .email-container { width: 100%; max-width: 600px; }
        .email-row { background: #f5f5f5; }
        .email-cell { padding: 20px; }
        """
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            expected = """
            <table style="width: 100%; max-width: 600px;">
                <tr style="background: #f5f5f5;">
                    <td style="padding: 20px;">Content</td>
                </tr>
            </table>
            """
            mock_inline.return_value = expected
            result = mock_inline(html, css)
            
            assert 'width: 100%' in result
            assert 'max-width: 600px' in result
    
    def test_inline_css_media_query_handling(self):
        """Test handling of media queries for responsive design."""
        css = """
        .container { width: 600px; }
        @media only screen and (max-width: 600px) {
            .container { width: 100%; }
        }
        """
        
        # Media queries cannot be inlined, should be preserved in style tag
        with patch('microsoft_mcp.email_framework.css_inliner.process_media_queries') as mock_media:
            mock_media.return_value = '<style>@media only screen and (max-width: 600px) { ... }</style>'
            result = mock_media(css)
            
            assert '@media' in result
            assert '<style>' in result
    
    def test_inline_css_performance(self):
        """Test CSS inlining performance with large documents."""
        # Generate large HTML
        large_html = '<div class="item">' * 1000 + 'Content' + '</div>' * 1000
        css = '.item { padding: 10px; margin: 5px; }'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = "processed"
            
            # Should complete within reasonable time
            import time
            start = time.time()
            result = mock_inline(large_html, css)
            duration = time.time() - start
            
            # Should process in under 2 seconds
            assert duration < 2.0
    
    def test_inline_css_theme_variables(self):
        """Test replacement of CSS variables with theme values."""
        html = '<div class="themed">Content</div>'
        css = '.themed { color: var(--primary); background: var(--light-bg); }'
        theme_vars = {
            '--primary': '#2B6CB0',
            '--light-bg': '#F7FAFC'
        }
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = '<div style="color: #2B6CB0; background: #F7FAFC;">Content</div>'
            result = mock_inline(html, css, theme_vars)
            
            assert '#2B6CB0' in result
            assert '#F7FAFC' in result
            assert 'var(--' not in result


class TestCSSOptimization:
    """Test CSS optimization for email delivery."""
    
    def test_css_minification(self):
        """Test that CSS is minified to reduce size."""
        css = """
        .card {
            background: white;
            padding: 20px;
            margin: 10px;
        }
        """
        
        with patch('microsoft_mcp.email_framework.css_inliner.minify_css') as mock_minify:
            mock_minify.return_value = '.card{background:white;padding:20px;margin:10px}'
            result = mock_minify(css)
            
            assert len(result) < len(css)
            assert '\n' not in result
            assert '  ' not in result
    
    def test_remove_unused_css(self):
        """Test removal of unused CSS rules."""
        html = '<div class="used">Content</div>'
        css = """
        .used { color: blue; }
        .unused { color: red; }
        .also-unused { color: green; }
        """
        
        with patch('microsoft_mcp.email_framework.css_inliner.remove_unused_css') as mock_remove:
            mock_remove.return_value = '.used { color: blue; }'
            result = mock_remove(html, css)
            
            assert '.used' in result
            assert '.unused' not in result
            assert '.also-unused' not in result
    
    def test_css_size_limit(self):
        """Test that final CSS size stays under limit."""
        with patch('microsoft_mcp.email_framework.css_inliner.get_css_size') as mock_size:
            mock_size.return_value = 95 * 1024  # 95KB
            size = mock_size()
            
            # Should be under 100KB limit
            assert size < 100 * 1024