"""
Email template renderer with theme selection and optimization
"""

from typing import Dict, Any, Optional, Type
from .templates.base import EmailTemplate
from .templates.practice_report import PracticeReportTemplate
from .templates.executive_summary import ExecutiveSummaryTemplate
from .templates.provider_update import ProviderUpdateTemplate
from .templates.alert_notification import AlertNotificationTemplate


class EmailRenderer:
    """
    Central renderer for all email templates.
    Handles template selection, theme management, and rendering optimization.
    """
    
    # Template registry
    TEMPLATE_REGISTRY: Dict[str, Type[EmailTemplate]] = {
        "practice_report": PracticeReportTemplate,
        "executive_summary": ExecutiveSummaryTemplate,
        "provider_update": ProviderUpdateTemplate,
        "alert_notification": AlertNotificationTemplate,
    }
    
    def __init__(self, default_theme: str = "baytown"):
        """
        Initialize email renderer
        
        Args:
            default_theme: Default theme to use if not specified
        """
        self.default_theme = default_theme
        self._template_cache: Dict[str, EmailTemplate] = {}
        
    def render(
        self,
        template_name: str,
        data: Dict[str, Any],
        theme: Optional[str] = None,
        inline_styles: bool = True
    ) -> str:
        """
        Render an email template with data
        
        Args:
            template_name: Name of the template to render
            data: Template data
            theme: Theme to use (overrides default)
            inline_styles: Whether to inline CSS styles
            
        Returns:
            Rendered HTML email
            
        Raises:
            ValueError: If template not found or data invalid
        """
        if template_name not in self.TEMPLATE_REGISTRY:
            raise ValueError(
                f"Unknown template: {template_name}. "
                f"Available templates: {', '.join(self.TEMPLATE_REGISTRY.keys())}"
            )
            
        # Get or create template instance
        theme = theme or self._get_theme_for_recipient(data) or self.default_theme
        cache_key = f"{template_name}:{theme}"
        
        if cache_key not in self._template_cache:
            template_class = self.TEMPLATE_REGISTRY[template_name]
            self._template_cache[cache_key] = template_class(theme=theme)
            
        template = self._template_cache[cache_key]
        
        # Render the template
        return template.render(data, inline_styles=inline_styles)
        
    def _get_theme_for_recipient(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Determine appropriate theme based on recipient or location
        
        Args:
            data: Template data
            
        Returns:
            Theme name or None to use default
        """
        # Check for explicit theme in data
        if "theme" in data:
            return data["theme"]
            
        # Check location-based theme selection
        location = data.get("location", "").lower()
        if "baytown" in location:
            return "baytown"
        elif "humble" in location:
            return "humble"
        elif "executive" in data.get("to", "").lower():
            return "executive"
            
        # Check if this is an executive-level recipient
        if data.get("recipient_level") == "executive":
            return "executive"
            
        return None
        
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template information dictionary
        """
        if template_name not in self.TEMPLATE_REGISTRY:
            raise ValueError(f"Unknown template: {template_name}")
            
        template_class = self.TEMPLATE_REGISTRY[template_name]
        template = template_class()
        
        return {
            "name": template.get_template_name(),
            "class": template_class.__name__,
            "themes": ["baytown", "humble", "executive"],
            "has_sample_data": hasattr(template, "generate_sample_data"),
        }
        
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available templates
        
        Returns:
            Dictionary of template information
        """
        templates = {}
        for name in self.TEMPLATE_REGISTRY:
            templates[name] = self.get_template_info(name)
        return templates
        
    def preview_template(
        self,
        template_name: str,
        theme: str = "baytown",
        use_sample_data: bool = True
    ) -> str:
        """
        Preview a template with sample data
        
        Args:
            template_name: Name of the template
            theme: Theme to preview
            use_sample_data: Whether to use sample data
            
        Returns:
            Rendered HTML preview
        """
        if template_name not in self.TEMPLATE_REGISTRY:
            raise ValueError(f"Unknown template: {template_name}")
            
        template_class = self.TEMPLATE_REGISTRY[template_name]
        template = template_class(theme=theme)
        
        if use_sample_data and hasattr(template, "generate_sample_data"):
            data = template.generate_sample_data()
        else:
            raise ValueError(f"No sample data available for template: {template_name}")
            
        # Render without inlining for preview
        return template.render(data, inline_styles=False)
        
    def validate_template_data(
        self,
        template_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data for a template without rendering
        
        Args:
            template_name: Name of the template
            data: Data to validate
            
        Returns:
            Validation result with any warnings
        """
        if template_name not in self.TEMPLATE_REGISTRY:
            raise ValueError(f"Unknown template: {template_name}")
            
        template_class = self.TEMPLATE_REGISTRY[template_name]
        template = template_class()
        
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            template.validate_data(data)
        except ValueError as e:
            result["valid"] = False
            result["errors"].append(str(e))
            
        # Check for recommended fields
        if template_name == "practice_report":
            if "period" not in data:
                result["warnings"].append("Missing 'period' field - will use default")
            if "alerts" not in data:
                result["warnings"].append("No alerts provided")
            if "recommendations" not in data:
                result["warnings"].append("No recommendations provided")
                
        return result
        
    def get_email_stats(
        self,
        template_name: str,
        data: Dict[str, Any],
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about the rendered email
        
        Args:
            template_name: Name of the template
            data: Template data
            theme: Theme to use
            
        Returns:
            Email statistics
        """
        html = self.render(template_name, data, theme=theme)
        
        # Calculate statistics
        stats = {
            "html_size": len(html),
            "html_size_kb": round(len(html) / 1024, 2),
            "estimated_load_time": round(len(html) / 50000, 2),  # Rough estimate
            "inline_styles": True,
            "theme": theme or self.default_theme,
        }
        
        # Get template-specific stats
        template = self._template_cache.get(f"{template_name}:{theme or self.default_theme}")
        if template:
            stats.update(template.get_email_size())
            
        return stats


# Convenience functions for direct access
_default_renderer = EmailRenderer()

def render_email(
    template_name: str,
    data: Dict[str, Any],
    theme: Optional[str] = None,
    inline_styles: bool = True
) -> str:
    """Render an email template"""
    return _default_renderer.render(template_name, data, theme, inline_styles)

def list_email_templates() -> Dict[str, Dict[str, Any]]:
    """List all available email templates"""
    return _default_renderer.list_templates()

def preview_email_template(
    template_name: str,
    theme: str = "baytown"
) -> str:
    """Preview an email template with sample data"""
    return _default_renderer.preview_template(template_name, theme)