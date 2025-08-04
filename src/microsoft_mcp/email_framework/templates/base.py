"""
Base email template class for KamDental Email Framework
Refactored for better maintainability and modularity
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re
from datetime import datetime

from ..css import (
    get_base_styles,
    get_component_styles,
    get_theme_styles,
    get_utility_styles,
    apply_email_compatibility_fixes,
    THEME_REGISTRY
)
from ..css_inliner import inline_css, minify_css, get_css_size


class EmailTemplate(ABC):
    """
    Base class for all email templates.
    Provides common functionality and enforces template structure.
    """
    
    def __init__(self, theme: str = "baytown"):
        """
        Initialize email template with theme
        
        Args:
            theme: Theme name (baytown, humble, executive)
            
        Raises:
            ValueError: If theme is not recognized
        """
        if theme and theme.lower() not in THEME_REGISTRY:
            raise ValueError(f"Unknown theme: {theme}. Available themes: {', '.join(THEME_REGISTRY.keys())}")
            
        self.theme = theme.lower() if theme else "baytown"
        self._theme_colors = THEME_REGISTRY[self.theme]
        self._css_cache = None
        
    @abstractmethod
    def get_template_name(self) -> str:
        """Get the template name for identification"""
        pass
        
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> None:
        """
        Validate input data for the template
        
        Args:
            data: Template data dictionary
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        pass
        
    @abstractmethod
    def _get_template_html(self, data: Dict[str, Any]) -> str:
        """
        Generate the inner HTML content for the template
        
        Args:
            data: Template data dictionary
            
        Returns:
            HTML string for the template content
        """
        pass
        
    def render(self, data: Dict[str, Any], inline_styles: bool = True) -> str:
        """
        Render the complete email template
        
        Args:
            data: Template data dictionary
            inline_styles: Whether to inline CSS styles
            
        Returns:
            Complete HTML email
            
        Raises:
            ValueError: If data validation fails
        """
        # Validate input data
        self.validate_data(data)
        
        # Get template content
        content_html = self._get_template_html(data)
        
        # Add signature if not already included
        if self.get_signature_html() not in content_html:
            content_html += self.get_signature_html()
        
        # Build complete HTML
        if inline_styles:
            html = self._build_html_with_inline_styles(content_html)
        else:
            html = self._build_html_with_style_tags(content_html)
            
        # Apply final optimizations
        html = self._optimize_html(html)
        
        return html
        
    def get_css(self) -> str:
        """
        Get complete CSS for the template
        
        Returns:
            Combined CSS string
        """
        if self._css_cache is None:
            # Combine all CSS modules
            css_parts = [
                get_base_styles(),
                get_component_styles(),
                get_theme_styles(self.theme),
                get_utility_styles(),
            ]
            
            # Join and apply compatibility fixes
            css = '\n'.join(css_parts)
            css = apply_email_compatibility_fixes(css)
            
            # Minify for production
            css = minify_css(css)
            
            self._css_cache = css
            
        return self._css_cache
        
    def _build_html_with_inline_styles(self, content: str) -> str:
        """Build HTML with inlined CSS styles"""
        html = self._get_html_structure(content)
        css = self.get_css()
        
        # Get theme variables for CSS variable replacement
        theme_vars = {f"--{k}": v for k, v in self._theme_colors.items()}
        
        # Inline the CSS
        html = inline_css(html, css, theme_vars)
        
        return html
        
    def _build_html_with_style_tags(self, content: str) -> str:
        """Build HTML with CSS in style tags (for testing/preview)"""
        css = self.get_css()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{self.get_template_name()} - KamDental</title>
    <style>
        {css}
    </style>
</head>
<body>
    {self._get_html_wrapper(content)}
</body>
</html>"""
        return html
        
    def _get_html_structure(self, content: str) -> str:
        """Get the complete HTML structure"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{self.get_template_name()} - KamDental</title>
</head>
<body>
    {self._get_html_wrapper(content)}
</body>
</html>"""
        
    def _get_html_wrapper(self, content: str) -> str:
        """Get the standard HTML wrapper for email content"""
        return f"""
<table cellpadding="0" cellspacing="0" width="100%" class="email-wrapper">
    <tr>
        <td align="center">
            <table cellpadding="0" cellspacing="0" class="email-container">
                <tr>
                    <td class="email-content">
                        {content}
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>"""
        
    def _optimize_html(self, html: str) -> str:
        """Apply final optimizations to HTML"""
        # Remove excessive whitespace while preserving necessary spaces
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'>\s+<', '><', html)
        html = re.sub(r'\s+style="', ' style="', html)
        
        return html.strip()
        
    def get_signature_html(self) -> str:
        """Get the executive signature HTML"""
        return """
<div class="signature">
    <div class="signature-name">Ossie Irondi PharmD.</div>
    <div class="signature-title">Chief Operating Officer</div>
    <div class="signature-company">KC Ventures PLLC</div>
    <div class="signature-contact">
        Baytown Office: 281-421-5950<br>
        Humble Office: 281-812-3333<br>
        Cell: 346-644-0193
    </div>
    <div class="signature-contact">
        <a href="https://www.kamdental.com">https://www.kamdental.com</a><br>
        <a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled">Book Time With Me</a>
    </div>
</div>"""
        
    # Utility methods for templates
    
    def format_currency(self, amount: float) -> str:
        """Format number as currency"""
        return f"${amount:,.0f}"
        
    def format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format number as percentage"""
        # Handle both decimal (0.95) and percentage (95) inputs
        if value <= 1:
            value = value * 100
        return f"{value:.{decimals}f}%"
        
    def format_number(self, value: float, decimals: int = 0) -> str:
        """Format number with thousands separator"""
        if decimals > 0:
            return f"{value:,.{decimals}f}"
        return f"{value:,.0f}"
        
    def format_date(self, date: datetime, format_str: str = "%B %d, %Y") -> str:
        """Format datetime object"""
        return date.strftime(format_str)
        
    def truncate_text(self, text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
        
    def get_status_class(self, value: float, target: float, thresholds: Dict[str, float] = None) -> str:
        """
        Get CSS class based on performance status
        
        Args:
            value: Current value
            target: Target value
            thresholds: Optional custom thresholds
            
        Returns:
            CSS class name (status-ahead, status-normal, status-warning, status-behind)
        """
        if thresholds is None:
            thresholds = {
                "ahead": 1.0,    # 100% or more
                "normal": 0.95,  # 95% or more
                "warning": 0.85, # 85% or more
                "behind": 0,     # Less than 85%
            }
            
        ratio = value / target if target > 0 else 0
        
        if ratio >= thresholds.get("ahead", 1.0):
            return "status-ahead"
        elif ratio >= thresholds.get("normal", 0.95):
            return "status-normal"
        elif ratio >= thresholds.get("warning", 0.85):
            return "status-warning"
        else:
            return "status-behind"
            
    def build_metric_card(self, label: str, value: str, subtitle: str = "", status_class: str = "") -> str:
        """Build a metric card HTML"""
        subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''
        
        return f"""
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value {status_class}">{value}</div>
    {subtitle_html}
</div>"""
        
    def build_alert(self, title: str, message: str, alert_type: str = "info") -> str:
        """Build an alert HTML"""
        return f"""
<div class="alert alert-{alert_type}">
    <div class="alert-header">{title}</div>
    <div class="alert-body">{message}</div>
</div>"""
        
    def build_button(self, text: str, url: str, style: str = "primary", full_width: bool = False) -> str:
        """Build a button HTML"""
        width_class = "button-full" if full_width else ""
        
        return f"""
<a href="{url}" class="button button-{style} {width_class}">{text}</a>"""
        
    def build_data_table(self, headers: List[str], rows: List[List[str]], css_class: str = "data-table") -> str:
        """Build a data table HTML"""
        header_html = "".join(f"<th>{h}</th>" for h in headers)
        
        rows_html = []
        for row in rows:
            cells = "".join(f"<td>{cell}</td>" for cell in row)
            rows_html.append(f"<tr>{cells}</tr>")
            
        return f"""
<table class="{css_class}">
    <thead>
        <tr>{header_html}</tr>
    </thead>
    <tbody>
        {"".join(rows_html)}
    </tbody>
</table>"""
        
    def get_email_size(self) -> Dict[str, int]:
        """Get size information for the email"""
        css = self.get_css()
        
        return {
            "css_size": get_css_size(css),
            "css_size_kb": round(get_css_size(css) / 1024, 2),
        }
        
    def validate_accessibility(self) -> List[str]:
        """
        Validate template for accessibility issues
        
        Returns:
            List of accessibility warnings
        """
        warnings = []
        
        # Check for color contrast
        if self.theme == "baytown":
            # Blue theme - generally good contrast
            pass
        elif self.theme == "humble":
            # Green theme - check lighter greens
            warnings.append("Ensure green text has sufficient contrast on light backgrounds")
        elif self.theme == "executive":
            # Dark theme - generally good contrast
            pass
            
        # General accessibility recommendations
        warnings.extend([
            "Ensure all images have alt text",
            "Use semantic HTML where possible",
            "Test with screen readers",
            "Verify keyboard navigation for interactive elements",
        ])
        
        return warnings