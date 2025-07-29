"""
Test runner for email framework validation
Verifies functionality, performance, and compatibility
"""

import time
import sys
from typing import Dict, Any, List, Tuple
from datetime import datetime

from .renderer import EmailRenderer
from .templates.practice_report import PracticeReportTemplate
from .validators import EmailValidator, DataValidator, ValidationError


class EmailFrameworkTester:
    """Test runner for email framework validation"""
    
    def __init__(self):
        self.renderer = EmailRenderer()
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "details": []
        }
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("Starting Email Framework Validation...\n")
        
        # Test categories
        self.test_template_rendering()
        self.test_theme_selection()
        self.test_performance()
        self.test_validation()
        self.test_css_size()
        self.test_accessibility()
        
        # Summary
        self._print_summary()
        
        return self.results
        
    def test_template_rendering(self):
        """Test that all templates render correctly"""
        print("Testing Template Rendering...")
        
        templates = ["practice_report", "executive_summary", "provider_update", "alert_notification"]
        
        for template_name in templates:
            try:
                # Get sample data if available
                template_class = self.renderer.TEMPLATE_REGISTRY.get(template_name)
                if template_class:
                    template = template_class()
                    if hasattr(template, "generate_sample_data"):
                        data = template.generate_sample_data()
                    else:
                        # Create minimal test data
                        data = self._get_minimal_test_data(template_name)
                        
                    # Render template
                    start_time = time.time()
                    html = self.renderer.render(template_name, data)
                    render_time = time.time() - start_time
                    
                    # Verify output
                    if html and len(html) > 100:
                        self._add_success(f"{template_name} rendered successfully in {render_time:.3f}s")
                    else:
                        self._add_failure(f"{template_name} rendered empty or invalid HTML")
                else:
                    self._add_failure(f"{template_name} not found in registry")
                    
            except Exception as e:
                self._add_failure(f"{template_name} rendering failed: {str(e)}")
                
        print()
        
    def test_theme_selection(self):
        """Test automatic theme selection"""
        print("Testing Theme Selection...")
        
        test_cases = [
            ({"location": "Baytown", "to": "test@example.com"}, "baytown"),
            ({"location": "Humble", "to": "test@example.com"}, "humble"),
            ({"to": "executive@kamdental.com", "location": "Main"}, "executive"),
            ({"recipient_level": "executive", "to": "test@example.com"}, "executive"),
        ]
        
        for data, expected_theme in test_cases:
            theme = self.renderer._get_theme_for_recipient(data)
            if theme == expected_theme or (theme is None and expected_theme == "baytown"):
                self._add_success(f"Theme selection correct for {data}")
            else:
                self._add_failure(f"Theme selection failed: expected {expected_theme}, got {theme}")
                
        print()
        
    def test_performance(self):
        """Test rendering performance"""
        print("Testing Performance...")
        
        # Test with practice report (most complex template)
        template = PracticeReportTemplate()
        data = template.generate_sample_data()
        
        # Warm up
        self.renderer.render("practice_report", data)
        
        # Measure rendering time
        times = []
        for i in range(10):
            start_time = time.time()
            html = self.renderer.render("practice_report", data)
            render_time = time.time() - start_time
            times.append(render_time)
            
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Check performance criteria
        if avg_time < 2.0:  # < 2 seconds
            self._add_success(f"Average render time: {avg_time:.3f}s (< 2s requirement)")
        else:
            self._add_failure(f"Average render time: {avg_time:.3f}s (exceeds 2s requirement)")
            
        if max_time < 3.0:
            self._add_success(f"Max render time: {max_time:.3f}s")
        else:
            self._add_warning(f"Max render time: {max_time:.3f}s (may be slow)")
            
        print()
        
    def test_validation(self):
        """Test data validation"""
        print("Testing Data Validation...")
        
        # Test email validation
        valid_emails = ["test@example.com", "user.name@company.co.uk"]
        invalid_emails = ["invalid", "@example.com", "test@", "test @example.com"]
        
        for email in valid_emails:
            try:
                EmailValidator.validate_email(email)
                self._add_success(f"Email validation passed: {email}")
            except ValidationError:
                self._add_failure(f"Valid email rejected: {email}")
                
        for email in invalid_emails:
            try:
                EmailValidator.validate_email(email)
                self._add_failure(f"Invalid email accepted: {email}")
            except ValidationError:
                self._add_success(f"Invalid email rejected: {email}")
                
        # Test template data validation
        invalid_data = {
            "location": "Test",
            # Missing required fields
        }
        
        result = self.renderer.validate_template_data("practice_report", invalid_data)
        if not result["valid"]:
            self._add_success("Invalid data correctly rejected")
        else:
            self._add_failure("Invalid data incorrectly accepted")
            
        print()
        
    def test_css_size(self):
        """Test CSS framework size"""
        print("Testing CSS Size...")
        
        template = PracticeReportTemplate()
        css = template.get_css()
        css_size_kb = len(css.encode('utf-8')) / 1024
        
        # Get full email size
        data = template.generate_sample_data()
        html = template.render(data)
        html_size_kb = len(html.encode('utf-8')) / 1024
        
        # Check size requirements
        if css_size_kb < 50:  # CSS should be under 50KB
            self._add_success(f"CSS size: {css_size_kb:.1f}KB (< 50KB)")
        else:
            self._add_warning(f"CSS size: {css_size_kb:.1f}KB (large)")
            
        if html_size_kb < 100:  # Total email under 100KB
            self._add_success(f"Email size: {html_size_kb:.1f}KB (< 100KB requirement)")
        else:
            self._add_failure(f"Email size: {html_size_kb:.1f}KB (exceeds 100KB requirement)")
            
        print()
        
    def test_accessibility(self):
        """Test accessibility features"""
        print("Testing Accessibility...")
        
        template = PracticeReportTemplate()
        warnings = template.validate_accessibility()
        
        if warnings:
            for warning in warnings:
                self._add_warning(f"Accessibility: {warning}")
        else:
            self._add_success("No accessibility warnings")
            
        # Check for semantic HTML
        data = template.generate_sample_data()
        html = template.render(data, inline_styles=False)
        
        semantic_tags = ["<h1", "<h2", "<table", "<th", "<td"]
        for tag in semantic_tags:
            if tag in html:
                self._add_success(f"Uses semantic HTML: {tag}>")
            else:
                self._add_warning(f"Missing semantic HTML: {tag}>")
                
        print()
        
    def _get_minimal_test_data(self, template_name: str) -> Dict[str, Any]:
        """Get minimal test data for a template"""
        base_data = {
            "to": "test@example.com",
            "subject": "Test Email",
        }
        
        if template_name == "practice_report":
            base_data.update({
                "location": "Test Location",
                "financial_data": {
                    "production": {"value": 100000},
                    "collections": {"value": 95000, "ratio": 0.95},
                    "case_acceptance": {"value": 0.75},
                    "call_answer_rate": {"value": 0.92},
                },
                "providers": []
            })
        elif template_name == "executive_summary":
            base_data.update({
                "locations_data": [
                    {"name": "Location 1", "metrics": {}}
                ],
                "period": "Test Period"
            })
        elif template_name == "provider_update":
            base_data.update({
                "provider_name": "Dr. Test",
                "performance_data": {}
            })
        elif template_name == "alert_notification":
            base_data.update({
                "alert_type": "warning",
                "title": "Test Alert",
                "message": "Test message"
            })
            
        return base_data
        
    def _add_success(self, message: str):
        """Add a success result"""
        self.results["passed"] += 1
        self.results["details"].append(("PASS", message))
        print(f"  ✓ {message}")
        
    def _add_failure(self, message: str):
        """Add a failure result"""
        self.results["failed"] += 1
        self.results["details"].append(("FAIL", message))
        print(f"  ✗ {message}")
        
    def _add_warning(self, message: str):
        """Add a warning result"""
        self.results["warnings"] += 1
        self.results["details"].append(("WARN", message))
        print(f"  ⚠ {message}")
        
    def _print_summary(self):
        """Print test summary"""
        total = self.results["passed"] + self.results["failed"]
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.results['passed']} ({self.results['passed']/total*100:.1f}%)")
        print(f"Failed: {self.results['failed']}")
        print(f"Warnings: {self.results['warnings']}")
        
        if self.results["failed"] == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed. Please review the details above.")
            

def run_validation():
    """Run validation tests"""
    tester = EmailFrameworkTester()
    results = tester.run_all_tests()
    
    # Return exit code
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(run_validation())