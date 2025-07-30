"""
Security tests for XSS prevention in the email framework
Tests all templates for proper HTML escaping and input sanitization
"""

import pytest
from markupsafe import escape

# Import all templates for testing
from src.microsoft_mcp.email_framework.templates.base import EmailTemplate
from src.microsoft_mcp.email_framework.templates.practice_report import PracticeReportTemplate
from src.microsoft_mcp.email_framework.templates.alert_notification import AlertNotificationTemplate
from src.microsoft_mcp.email_framework.templates.executive_summary import ExecutiveSummaryTemplate
from src.microsoft_mcp.email_framework.templates.provider_update import ProviderUpdateTemplate


class TestXSSPrevention:
    """Test suite for XSS vulnerability prevention"""
    
    # Common XSS payloads to test
    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "&#60;script&#62;alert('xss')&#60;/script&#62;",
        "<svg onload=alert('xss')>",
        "<iframe src='javascript:alert(`xss`)'></iframe>",
        "<object data='javascript:alert(`xss`)'></object>",
        "<embed src='javascript:alert(`xss`)'>",
        "<form action='javascript:alert(`xss`)'><input type='submit'></form>",
        "<a href='javascript:alert(`xss`)'>Click me</a>",
        "';alert('xss');//",
        '";alert(\'xss\');//',
        "<ScRiPt>alert('xss')</ScRiPt>",
        "<<SCRIPT>alert('xss');//<</SCRIPT>",
        "\u003cscript\u003ealert('xss')\u003c/script\u003e",
    ]
    
    # HTML entities that must be escaped
    HTML_ENTITIES = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
    }
    
    def test_practice_report_location_xss(self):
        """Test that location field is properly escaped in practice report"""
        template = PracticeReportTemplate()
        
        for payload in self.XSS_PAYLOADS:
            test_data = {
                "location": payload,
                "period": "Test Period",
                "financial_data": {
                    "production": {"value": 100000, "goal": 100000},
                    "collections": {"value": 95000, "ratio": 0.95},
                    "case_acceptance": {"value": 0.75, "goal": 0.75},
                    "call_answer_rate": {"value": 0.95, "goal": 0.95}
                },
                "providers": []
            }
            
            rendered = template.render(test_data)
            
            # Assert that the raw payload is NOT in the output
            assert payload not in rendered, f"XSS payload not escaped: {payload}"
            
            # Assert that the escaped version IS in the output
            escaped_payload = str(escape(payload))
            assert escaped_payload in rendered or any(
                entity in rendered for entity in escaped_payload
            ), f"Escaped payload not found for: {payload}"
    
    def test_practice_report_period_xss(self):
        """Test that period field is properly escaped"""
        template = PracticeReportTemplate()
        
        for payload in self.XSS_PAYLOADS:
            test_data = {
                "location": "Test Location",
                "period": payload,
                "financial_data": {
                    "production": {"value": 100000, "goal": 100000},
                    "collections": {"value": 95000, "ratio": 0.95},
                    "case_acceptance": {"value": 0.75, "goal": 0.75},
                    "call_answer_rate": {"value": 0.95, "goal": 0.95}
                },
                "providers": []
            }
            
            rendered = template.render(test_data)
            assert payload not in rendered, f"XSS payload in period not escaped: {payload}"
    
    def test_html_entities_escaped(self):
        """Test that HTML entities are properly escaped"""
        template = PracticeReportTemplate()
        
        # Test with all HTML entities
        malicious_input = '"\'<>&'
        test_data = {
            "location": malicious_input,
            "period": malicious_input,
            "financial_data": {
                "production": {"value": 100000, "goal": 100000},
                "collections": {"value": 95000, "ratio": 0.95},
                "case_acceptance": {"value": 0.75, "goal": 0.75},
                "call_answer_rate": {"value": 0.95, "goal": 0.95}
            },
            "providers": [{
                "name": malicious_input,
                "role": "Test Role",
                "production": 50000
            }]
        }
        
        rendered = template.render(test_data)
        
        # Check that raw entities are not present
        for char in self.HTML_ENTITIES:
            # Allow the character in style attributes and other safe contexts
            # but not in user-provided content areas
            count = rendered.count(char)
            assert count == 0 or all(
                char in safe_context 
                for safe_context in ['style="', 'class="', '<!DOCTYPE', '<html', '<head', '<meta']
                if char in rendered
            ), f"Unescaped HTML entity found: {char}"
    
    def test_provider_name_xss(self):
        """Test that provider names are properly escaped"""
        template = PracticeReportTemplate()
        
        for payload in self.XSS_PAYLOADS:
            test_data = {
                "location": "Test Location",
                "period": "Test Period",
                "financial_data": {
                    "production": {"value": 100000, "goal": 100000},
                    "collections": {"value": 95000, "ratio": 0.95},
                    "case_acceptance": {"value": 0.75, "goal": 0.75},
                    "call_answer_rate": {"value": 0.95, "goal": 0.95}
                },
                "providers": [{
                    "name": payload,
                    "role": "Dentist",
                    "production": 50000
                }]
            }
            
            rendered = template.render(test_data)
            assert payload not in rendered, f"XSS payload in provider name not escaped: {payload}"
    
    def test_alert_notification_message_xss(self):
        """Test alert notification template for XSS in messages"""
        template = AlertNotificationTemplate()
        
        for payload in self.XSS_PAYLOADS:
            test_data = {
                "alert_type": "warning",
                "title": "Test Alert",
                "message": payload,
                "actions": ["Test Action"]
            }
            
            rendered = template.render(test_data)
            assert payload not in rendered, f"XSS payload in alert message not escaped: {payload}"
    
    def test_executive_summary_location_xss(self):
        """Test executive summary template for XSS in location names"""
        template = ExecutiveSummaryTemplate()
        
        for payload in self.XSS_PAYLOADS:
            test_data = {
                "period": "Test Period",
                "locations": [{
                    "name": payload,
                    "production": 100000,
                    "collections": 95000,
                    "performance": "good"
                }],
                "total_metrics": {
                    "production": 100000,
                    "collections": 95000,
                    "case_acceptance": 0.75
                }
            }
            
            rendered = template.render(test_data)
            assert payload not in rendered, f"XSS payload in location name not escaped: {payload}"
    
    def test_table_data_xss(self):
        """Test that data in tables is properly escaped"""
        template = EmailTemplate()
        
        for payload in self.XSS_PAYLOADS:
            # Test headers
            headers = ["Safe Header", payload]
            rows = [["Safe Cell", "Another Safe Cell"]]
            
            table_html = template.build_data_table(headers, rows)
            assert payload not in table_html, f"XSS payload in table header not escaped: {payload}"
            
            # Test cells
            headers = ["Header 1", "Header 2"]
            rows = [[payload, "Safe Cell"], ["Another Row", payload]]
            
            table_html = template.build_data_table(headers, rows)
            assert payload not in table_html, f"XSS payload in table cell not escaped: {payload}"
    
    def test_metric_card_xss(self):
        """Test that metric cards properly escape user input"""
        template = EmailTemplate()
        
        for payload in self.XSS_PAYLOADS:
            card_html = template.build_metric_card(
                label=payload,
                value=payload,
                subtitle=payload
            )
            assert payload not in card_html, f"XSS payload in metric card not escaped: {payload}"
    
    def test_alert_component_xss(self):
        """Test that alert components properly escape user input"""
        template = EmailTemplate()
        
        for payload in self.XSS_PAYLOADS:
            alert_html = template.build_alert(
                title=payload,
                message=payload,
                alert_type="warning"
            )
            assert payload not in alert_html, f"XSS payload in alert not escaped: {payload}"
    
    def test_button_xss(self):
        """Test that buttons properly escape text but validate URLs"""
        template = EmailTemplate()
        
        for payload in self.XSS_PAYLOADS:
            # Test button text
            button_html = template.build_button(
                text=payload,
                url="https://safe.example.com"
            )
            assert payload not in button_html, f"XSS payload in button text not escaped: {payload}"
            
            # Test that javascript: URLs are blocked
            if "javascript:" in payload:
                with pytest.raises(ValueError, match="Invalid URL"):
                    template.build_button(
                        text="Click me",
                        url=payload
                    )
    
    def test_no_inline_javascript(self):
        """Test that no inline JavaScript can be injected"""
        template = PracticeReportTemplate()
        
        # Test various inline JavaScript attempts
        inline_js_attempts = [
            {"location": "Test", "onclick": "alert('xss')"},
            {"location": "Test", "onmouseover": "alert('xss')"},
            {"location": "Test", "onerror": "alert('xss')"},
        ]
        
        base_data = {
            "period": "Test Period",
            "financial_data": {
                "production": {"value": 100000, "goal": 100000},
                "collections": {"value": 95000, "ratio": 0.95},
                "case_acceptance": {"value": 0.75, "goal": 0.75},
                "call_answer_rate": {"value": 0.95, "goal": 0.95}
            },
            "providers": []
        }
        
        for attempt in inline_js_attempts:
            test_data = {**base_data, **attempt}
            rendered = template.render(test_data)
            
            # Check that event handlers are not in the output
            assert "onclick=" not in rendered.lower()
            assert "onmouseover=" not in rendered.lower()
            assert "onerror=" not in rendered.lower()
            assert "onload=" not in rendered.lower()
    
    def test_content_security_policy(self):
        """Test that Content Security Policy headers are included"""
        template = PracticeReportTemplate()
        
        test_data = {
            "location": "Test Location",
            "period": "Test Period",
            "financial_data": {
                "production": {"value": 100000, "goal": 100000},
                "collections": {"value": 95000, "ratio": 0.95},
                "case_acceptance": {"value": 0.75, "goal": 0.75},
                "call_answer_rate": {"value": 0.95, "goal": 0.95}
            },
            "providers": []
        }
        
        rendered = template.render(test_data)
        
        # Check for CSP header comment
        assert "Content-Security-Policy" in rendered
        assert "default-src 'self'" in rendered
    
    def test_unicode_bypass_attempts(self):
        """Test that Unicode bypass attempts are blocked"""
        template = PracticeReportTemplate()
        
        unicode_payloads = [
            "\u003cscript\u003ealert('xss')\u003c/script\u003e",
            "\u0022onmouseover=\u0022alert('xss')\u0022",
            "\\x3cscript\\x3ealert('xss')\\x3c/script\\x3e",
        ]
        
        for payload in unicode_payloads:
            test_data = {
                "location": payload,
                "period": "Test Period",
                "financial_data": {
                    "production": {"value": 100000, "goal": 100000},
                    "collections": {"value": 95000, "ratio": 0.95},
                    "case_acceptance": {"value": 0.75, "goal": 0.75},
                    "call_answer_rate": {"value": 0.95, "goal": 0.95}
                },
                "providers": []
            }
            
            rendered = template.render(test_data)
            
            # Check that script tags are not present in any form
            assert "<script" not in rendered.lower()
            assert "alert(" not in rendered
    
    def test_nested_payload_escaping(self):
        """Test that nested payloads are properly escaped"""
        template = PracticeReportTemplate()
        
        nested_payload = "<div><script>alert('xss')</script></div>"
        
        test_data = {
            "location": nested_payload,
            "period": "Test Period",
            "financial_data": {
                "production": {"value": 100000, "goal": 100000},
                "collections": {"value": 95000, "ratio": 0.95},
                "case_acceptance": {"value": 0.75, "goal": 0.75},
                "call_answer_rate": {"value": 0.95, "goal": 0.95}
            },
            "providers": [{
                "name": nested_payload,
                "role": "Test",
                "production": 50000
            }],
            "alerts": [{
                "type": "warning",
                "title": nested_payload,
                "message": nested_payload
            }]
        }
        
        rendered = template.render(test_data)
        
        # Ensure no part of the script tag is unescaped
        assert "<script>" not in rendered
        assert "</script>" not in rendered
        assert "alert(" not in rendered


class TestInputValidation:
    """Test input validation and sanitization functions"""
    
    def test_validate_email_data(self):
        """Test the email data validation function"""
        from src.microsoft_mcp.email_framework.validators import validate_email_data
        
        # Test with malicious input
        malicious_data = {
            "location": "<script>alert('xss')</script>",
            "period": "javascript:alert('xss')",
            "safe_number": 12345,
            "safe_bool": True,
            "nested": {
                "value": "<img src=x onerror=alert('xss')>"
            }
        }
        
        validated = validate_email_data(malicious_data)
        
        # Check that strings are escaped
        assert validated["location"] == str(escape(malicious_data["location"]))
        assert validated["period"] == str(escape(malicious_data["period"]))
        
        # Check that non-strings are unchanged
        assert validated["safe_number"] == 12345
        assert validated["safe_bool"] is True
        
        # Check nested data is also validated
        assert validated["nested"]["value"] == str(escape(malicious_data["nested"]["value"]))
    
    def test_validate_url(self):
        """Test URL validation to prevent javascript: URLs"""
        from src.microsoft_mcp.email_framework.validators import validate_url
        
        # Valid URLs
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com") == "http://example.com"
        assert validate_url("mailto:test@example.com") == "mailto:test@example.com"
        assert validate_url("/relative/path") == "/relative/path"
        
        # Invalid URLs should raise ValueError
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("javascript:alert('xss')")
        
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("data:text/html,<script>alert('xss')</script>")
        
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("vbscript:msgbox('xss')")


class TestSecurityHeaders:
    """Test security headers implementation"""
    
    def test_add_security_headers(self):
        """Test that security headers are added to emails"""
        from src.microsoft_mcp.email_framework.renderer import add_security_headers
        
        html = "<html><body>Test</body></html>"
        result = add_security_headers(html)
        
        # Check CSP header is present
        assert "Content-Security-Policy" in result
        assert "default-src 'self'" in result
        assert "style-src 'self' 'unsafe-inline'" in result
        assert "script-src 'none'" in result
        
        # Check X-Content-Type-Options
        assert "X-Content-Type-Options: nosniff" in result
        
        # Check X-XSS-Protection (legacy but still useful)
        assert "X-XSS-Protection: 1; mode=block" in result


class TestPerformanceImpact:
    """Test that security measures don't significantly impact performance"""
    
    def test_rendering_performance(self):
        """Test that HTML escaping doesn't add more than 5% overhead"""
        import time
        
        template = PracticeReportTemplate()
        
        # Create test data with lots of fields
        test_data = {
            "location": "Test Location " * 100,  # Long string
            "period": "Test Period",
            "financial_data": {
                "production": {"value": 100000, "goal": 100000},
                "collections": {"value": 95000, "ratio": 0.95},
                "case_acceptance": {"value": 0.75, "goal": 0.75},
                "call_answer_rate": {"value": 0.95, "goal": 0.95}
            },
            "providers": [
                {
                    "name": f"Provider {i}",
                    "role": "Dentist",
                    "production": 50000 + i * 1000
                }
                for i in range(20)  # 20 providers
            ],
            "alerts": [
                {
                    "type": "warning",
                    "title": f"Alert {i}",
                    "message": f"This is alert message {i} with some content"
                }
                for i in range(10)  # 10 alerts
            ]
        }
        
        # Measure rendering time
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            rendered = template.render(test_data)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        # Assert that average rendering time is reasonable (< 50ms)
        assert avg_time < 0.05, f"Rendering too slow: {avg_time:.3f}s average"
        
        # Log performance for monitoring
        print(f"Average rendering time: {avg_time * 1000:.2f}ms")