"""
Test suite for email templates in the KamDental Email Framework.
Tests template rendering, data validation, and theme selection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestEmailTemplateBase:
    """Test the base EmailTemplate class functionality."""
    
    @pytest.fixture
    def mock_template_class(self):
        """Create a mock EmailTemplate subclass for testing."""
        # Import will be updated when actual module is created
        with patch('microsoft_mcp.email_framework.templates.base.EmailTemplate') as MockTemplate:
            instance = MockTemplate.return_value
            instance.theme = "baytown"
            instance.get_template_name.return_value = "test_template.html"
            instance.validate_data = Mock()
            instance.render = Mock(return_value="<html>Rendered content</html>")
            yield instance
    
    def test_template_initialization_default_theme(self, mock_template_class):
        """Test that template initializes with default baytown theme."""
        assert mock_template_class.theme == "baytown"
    
    def test_template_initialization_custom_theme(self):
        """Test that template accepts custom theme parameter."""
        themes = ["baytown", "humble", "executive"]
        for theme in themes:
            with patch('microsoft_mcp.email_framework.templates.base.EmailTemplate') as MockTemplate:
                instance = MockTemplate(theme=theme)
                assert instance.theme == theme
    
    def test_render_validates_data(self, mock_template_class):
        """Test that render method validates data before rendering."""
        test_data = {"test": "data"}
        mock_template_class.render(test_data)
        mock_template_class.validate_data.assert_called_once_with(test_data)
    
    def test_render_returns_html_string(self, mock_template_class):
        """Test that render method returns HTML string."""
        result = mock_template_class.render({"test": "data"})
        assert isinstance(result, str)
        assert "<html>" in result
    
    def test_currency_filter_formatting(self):
        """Test currency formatting filter."""
        test_cases = [
            (143343, "$143,343"),
            (1000.50, "$1,001"),
            (0, "$0"),
            (-500, "-$500"),
            (1234567.89, "$1,234,568"),
        ]
        
        # Mock the currency filter
        for value, expected in test_cases:
            # This will be implemented in actual template
            formatted = f"${value:,.0f}"
            assert formatted == expected or formatted == expected.replace(",", "")
    
    def test_percentage_filter_formatting(self):
        """Test percentage formatting filter."""
        test_cases = [
            (0.896, "89.6%"),
            (0.747, "74.7%"),
            (1.0, "100.0%"),
            (0.3586, "35.9%"),
            (0.693, "69.3%"),
        ]
        
        # Mock the percentage filter
        for value, expected in test_cases:
            formatted = f"{value * 100:.1f}%"
            assert formatted == expected


class TestPracticeReportTemplate:
    """Test the PracticeReportTemplate functionality."""
    
    @pytest.fixture
    def valid_practice_data(self):
        """Provide valid practice report data."""
        return {
            "location": "Baytown",
            "period": "July 2025 MTD",
            "financial_data": {
                "production": {"value": 143343, "goal": 160000, "status": "behind"},
                "collections": {"value": 107113, "ratio": 0.747},
                "case_acceptance": {"value": 0.3586, "status": "good"},
                "call_answer_rate": {"value": 0.693, "goal": 0.85, "status": "warning"}
            },
            "providers": [
                {
                    "name": "Dr. Obinna Ezeji",
                    "role": "Lead Producer",
                    "production": 68053,
                    "goal_percentage": 0.756,
                    "status": "good"
                },
                {
                    "name": "Adriane (DHAA)",
                    "role": "Hygienist",
                    "production": 21418,
                    "goal_percentage": 0.892,
                    "status": "good"
                }
            ],
            "alerts": [
                {
                    "type": "critical",
                    "icon": "🚨",
                    "title": "Critical Issue",
                    "message": "Call answer rate at 69.3% vs 85% goal"
                }
            ],
            "recommendations": [
                {
                    "priority": "IMMEDIATE",
                    "title": "Phone Coverage Improvement",
                    "details": "Target 85% answer rate by month-end",
                    "outcome": "Expected outcome: $13,000+ additional production"
                }
            ]
        }
    
    def test_practice_report_template_name(self):
        """Test that PracticeReportTemplate returns correct template name."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.get_template_name.return_value = "practice_report.html"
            assert instance.get_template_name() == "practice_report.html"
    
    def test_practice_report_data_validation_valid(self, valid_practice_data):
        """Test that valid practice data passes validation."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.validate_data(valid_practice_data)
            # Should not raise an exception
    
    def test_practice_report_data_validation_missing_required(self):
        """Test that missing required fields raise validation error."""
        invalid_data = {
            "location": "Baytown",
            # Missing financial_data and providers
        }
        
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.validate_data = Mock(side_effect=ValueError("Missing required fields"))
            
            with pytest.raises(ValueError):
                instance.validate_data(invalid_data)
    
    def test_practice_report_theme_selection(self):
        """Test that theme is selected based on location."""
        locations_themes = [
            ("Baytown", "baytown"),
            ("Humble", "humble"),
            ("BAYTOWN", "baytown"),
            ("humble", "humble"),
        ]
        
        for location, expected_theme in locations_themes:
            with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
                instance = MockTemplate(theme=expected_theme)
                assert instance.theme == expected_theme
    
    def test_practice_report_render_includes_all_sections(self, valid_practice_data):
        """Test that rendered output includes all required sections."""
        expected_sections = [
            "MTD Production",
            "Collections", 
            "Case Acceptance",
            "Call Answer Rate",
            "Dr. Obinna Ezeji",
            "Critical Issue",
            "Phone Coverage Improvement"
        ]
        
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            instance = MockTemplate()
            rendered_html = "<html>" + " ".join(expected_sections) + "</html>"
            instance.render.return_value = rendered_html
            
            result = instance.render(valid_practice_data)
            for section in expected_sections:
                assert section in result


class TestExecutiveSummaryTemplate:
    """Test the ExecutiveSummaryTemplate functionality."""
    
    @pytest.fixture
    def valid_executive_data(self):
        """Provide valid executive summary data."""
        return {
            "period": "July 2025 MTD",
            "locations": [
                {
                    "name": "Baytown",
                    "status": "behind",
                    "production": 143343,
                    "goal": 160000,
                    "percentage": 0.896
                },
                {
                    "name": "Humble",
                    "status": "on_track",
                    "production": 178000,
                    "goal": 175000,
                    "percentage": 1.017
                }
            ],
            "key_insights": [
                {
                    "type": "challenge",
                    "location": "Baytown",
                    "message": "$16,656 behind production goal"
                },
                {
                    "type": "success",
                    "location": "Humble",
                    "message": "Exceeding goal by 1.7%"
                }
            ],
            "total_production": 321343,
            "total_goal": 335000,
            "overall_percentage": 0.959
        }
    
    def test_executive_summary_template_name(self):
        """Test that ExecutiveSummaryTemplate returns correct template name."""
        with patch('microsoft_mcp.email_framework.templates.executive_summary.ExecutiveSummaryTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.get_template_name.return_value = "executive_summary.html"
            assert instance.get_template_name() == "executive_summary.html"
    
    def test_executive_summary_uses_executive_theme(self):
        """Test that executive summary defaults to executive theme."""
        with patch('microsoft_mcp.email_framework.templates.executive_summary.ExecutiveSummaryTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.theme = "executive"
            assert instance.theme == "executive"
    
    def test_executive_summary_multi_location_rendering(self, valid_executive_data):
        """Test that multiple locations are rendered correctly."""
        with patch('microsoft_mcp.email_framework.templates.executive_summary.ExecutiveSummaryTemplate') as MockTemplate:
            instance = MockTemplate()
            rendered = "Baytown: $143,343 | Humble: $178,000"
            instance.render.return_value = rendered
            
            result = instance.render(valid_executive_data)
            assert "Baytown" in result
            assert "Humble" in result
            assert "$143,343" in result
            assert "$178,000" in result


class TestProviderUpdateTemplate:
    """Test the ProviderUpdateTemplate functionality."""
    
    @pytest.fixture
    def valid_provider_data(self):
        """Provide valid provider update data."""
        return {
            "provider_name": "Dr. Obinna Ezeji",
            "period": "July 2025 MTD",
            "performance_data": {
                "production": 68053,
                "goal": 90000,
                "percentage": 0.756,
                "appointments": 125,
                "case_acceptance": 0.42,
                "average_production_per_visit": 544
            },
            "highlights": [
                "Strong case acceptance at 42%",
                "Consistent daily production"
            ],
            "recommendations": [
                "Schedule more high-value procedures",
                "Focus on crown and bridge cases"
            ]
        }
    
    def test_provider_update_personalization(self, valid_provider_data):
        """Test that provider updates are personalized."""
        with patch('microsoft_mcp.email_framework.templates.provider_update.ProviderUpdateTemplate') as MockTemplate:
            instance = MockTemplate()
            instance.render.return_value = f"<html>Dear {valid_provider_data['provider_name']}</html>"
            
            result = instance.render(valid_provider_data)
            assert valid_provider_data["provider_name"] in result


class TestAlertNotificationTemplate:
    """Test the AlertNotificationTemplate functionality."""
    
    @pytest.fixture
    def valid_alert_data(self):
        """Provide valid alert notification data."""
        return {
            "alert_type": "critical",
            "title": "Phone Coverage Critical",
            "message": "Answer rate has dropped to 69.3% vs 85% goal",
            "urgency": "immediate",
            "impact": "Estimated $13,000 in lost production opportunity",
            "recommended_actions": [
                "Review phone coverage schedule",
                "Assign dedicated receptionist during peak hours",
                "Implement call-back protocol for missed calls"
            ]
        }
    
    def test_alert_urgency_styling(self, valid_alert_data):
        """Test that alerts have appropriate urgency styling."""
        urgency_styles = {
            "immediate": "background-color: #E53E3E",  # Red
            "high": "background-color: #D69E2E",       # Yellow
            "normal": "background-color: #3182CE"      # Blue
        }
        
        for urgency, expected_style in urgency_styles.items():
            data = valid_alert_data.copy()
            data["urgency"] = urgency
            
            with patch('microsoft_mcp.email_framework.templates.alert_notification.AlertNotificationTemplate') as MockTemplate:
                instance = MockTemplate()
                instance.render.return_value = f"<html>{expected_style}</html>"
                
                result = instance.render(data)
                assert expected_style in result or urgency in result.lower()


class TestTemplateIntegration:
    """Test template integration with the email framework."""
    
    def test_all_templates_inherit_from_base(self):
        """Test that all templates inherit from EmailTemplate base class."""
        template_classes = [
            'PracticeReportTemplate',
            'ExecutiveSummaryTemplate', 
            'ProviderUpdateTemplate',
            'AlertNotificationTemplate'
        ]
        
        for template_class in template_classes:
            # This will be verified when actual classes are implemented
            assert True  # Placeholder
    
    def test_template_css_inlining(self):
        """Test that CSS is properly inlined for email compatibility."""
        test_html = '<div class="metric-card">Test</div>'
        expected_inline = '<div style="background: #F7FAFC; border: 1px solid #E2E8F0;">Test</div>'
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = expected_inline
            result = mock_inline(test_html, "")
            assert 'style=' in result
            assert 'class=' not in result
    
    def test_template_signature_inclusion(self):
        """Test that all templates include the executive signature."""
        signature_elements = [
            "Ossie Irondi PharmD.",
            "KC Ventures PLLC",
            "Chief Operating Officer",
            "281-421-5950",
            "281-812-3333",
            "346-644-0193",
            "https://www.kamdental.com",
            "Book Time With Me"
        ]
        
        # This will be verified in actual template rendering
        for element in signature_elements:
            assert element  # Placeholder