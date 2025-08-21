"""Email Framework Utilities

Utility functions for professional email styling and template rendering.
These utilities support the unified microsoft_operations tool by providing
professional HTML email generation without requiring separate tools.
"""

from datetime import datetime
from typing import Any

from .css.themes import THEME_REGISTRY as THEMES
from .css_inliner import inline_css
from .validators import EmailValidator
from .validators import TemplateDataValidator


def style_email_content(
    body: str,
    subject: str,
    theme: str = "baytown",
    signature: str | None = None,
    template_type: str | None = None,
    template_data: dict[str, Any] | None = None
) -> str:
    """Apply professional styling to email content.
    
    Args:
        body: Plain text or HTML email body content
        subject: Email subject line
        theme: Theme name (baytown, humble, executive)
        signature: Optional signature to append
        template_type: Optional template type (practice_report, executive_summary, etc.)
        template_data: Optional data for template rendering
        
    Returns:
        Professionally styled HTML email content with inline CSS
        
    Raises:
        ValueError: If theme is invalid or template rendering fails
    """
    # Validate theme
    if theme not in THEMES:
        raise ValueError(f"Invalid theme: {theme}. Must be one of: {list(THEMES.keys())}")

    # If template type specified, use template renderer
    if template_type and template_data:
        return render_email_template(template_type, template_data, theme)

    # Otherwise, apply basic styling
    from .css.themes import get_theme_styles
    
    # Generate HTML structure with theme styling
    theme_css = get_theme_styles(theme)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
        <style>{theme_css}</style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>{subject}</h1>
            </div>
            <div class="email-body">
                {body}
            </div>
            {signature or get_default_signature()}
        </div>
    </body>
    </html>
    """
    
    # Convert CSS to inline styles
    return inline_css(html_template)


def render_email_template(
    template_type: str,
    data: dict[str, Any],
    theme: str = "baytown"
) -> str:
    """Render a professional email template with data.
    
    Args:
        template_type: Template identifier (practice_report, executive_summary, etc.)
        data: Template-specific data for rendering
        theme: Theme name for styling
        
    Returns:
        Fully rendered HTML email with inline CSS
        
    Raises:
        ValueError: If template type is unknown or data validation fails
    """
    # Map template types to renderers
    template_map = {
        "practice_report": _render_practice_report,
        "executive_summary": _render_executive_summary,
        "provider_update": _render_provider_update,
        "alert_notification": _render_alert_notification,
    }

    if template_type not in template_map:
        raise ValueError(
            f"Unknown template type: {template_type}. "
            f"Available templates: {list(template_map.keys())}"
        )

    # Validate theme
    if theme not in THEMES:
        raise ValueError(f"Invalid theme: {theme}. Must be one of: {list(THEMES.keys())}")

    # Render template with data
    return template_map[template_type](data, theme)


def _render_practice_report(data: dict[str, Any], theme: str) -> str:
    """Render practice performance report template."""
    from .templates.practice_report import PracticeReportTemplate

    # Validate data structure
    validator = TemplateDataValidator()

    # Extract and validate financial data
    financial_data = data.get("financial_data", {})
    validated_financial = validator.validate_financial_data(
        production=financial_data.get("production"),
        collections=financial_data.get("collections"),
        goal=financial_data.get("goal"),
        case_acceptance=financial_data.get("case_acceptance"),
        call_answer_rate=financial_data.get("call_answer_rate")
    )

    # Extract and validate provider data
    provider_data = data.get("provider_data", [])
    validated_providers = [
        validator.validate_provider_data(
            name=p.get("name"),
            production=p.get("production"),
            goal=p.get("goal"),
            case_acceptance=p.get("case_acceptance")
        )
        for p in provider_data
    ]

    # Create template instance
    template = PracticeReportTemplate(
        location=data.get("location", "Unknown"),
        period=data.get("period", datetime.now().strftime("%B %Y")),
        financial_data=validated_financial,
        provider_data=validated_providers,
        alerts=data.get("alerts", []),
        recommendations=data.get("recommendations", [])
    )

    # Render with theme
    return template.render(theme=theme)


def _render_executive_summary(data: dict[str, Any], theme: str) -> str:
    """Render executive summary template."""
    from .templates.executive_summary import ExecutiveSummaryTemplate

    # Validate and prepare location data
    locations_data = data.get("locations_data", [])
    if not locations_data:
        raise ValueError("Executive summary requires locations_data")

    # Create template instance
    template = ExecutiveSummaryTemplate(
        period=data.get("period", datetime.now().strftime("%B %Y")),
        locations_data=locations_data,
        key_insights=data.get("key_insights", [])
    )

    # Render with theme
    return template.render(theme=theme)


def _render_provider_update(data: dict[str, Any], theme: str) -> str:
    """Render provider performance update template."""
    from .templates.provider_update import ProviderUpdateTemplate

    # Validate provider data
    validator = TemplateDataValidator()
    performance_data = data.get("performance_data", {})

    validated_performance = validator.validate_provider_data(
        name=data.get("provider_name"),
        production=performance_data.get("production"),
        goal=performance_data.get("goal"),
        case_acceptance=performance_data.get("case_acceptance")
    )

    # Create template instance
    template = ProviderUpdateTemplate(
        provider_name=data.get("provider_name", "Provider"),
        period=data.get("period", datetime.now().strftime("%B %Y")),
        performance_data=validated_performance,
        highlights=data.get("highlights", []),
        recommendations=data.get("recommendations", [])
    )

    # Render with theme
    return template.render(theme=theme)


def _render_alert_notification(data: dict[str, Any], theme: str) -> str:
    """Render alert notification template."""
    from .templates.alert_notification import AlertNotificationTemplate

    # Validate alert data
    validator = TemplateDataValidator()
    validated_alert = validator.validate_alert_data(
        alert_type=data.get("alert_type", "info"),
        title=data.get("title", "Alert"),
        message=data.get("message", ""),
        urgency=data.get("urgency", "normal")
    )

    # Create template instance
    template = AlertNotificationTemplate(
        alert_type=validated_alert["type"],
        title=validated_alert["title"],
        message=validated_alert["message"],
        urgency=validated_alert["urgency"],
        impact=data.get("impact"),
        recommended_actions=data.get("recommended_actions", [])
    )

    # Render with theme
    return template.render(theme=theme)


def validate_email_recipients(
    recipients: str | list[str]
) -> list[str]:
    """Validate and normalize email recipients.
    
    Args:
        recipients: Single email or list of emails
        
    Returns:
        Normalized list of valid email addresses
        
    Raises:
        ValueError: If any email address is invalid
    """
    validator = EmailValidator()

    # Convert to list if single string
    if isinstance(recipients, str):
        recipients = [recipients]

    # Validate each recipient
    validated = []
    for email in recipients:
        if validator.validate_email(email):
            validated.append(email.strip().lower())
        else:
            raise ValueError(f"Invalid email address: {email}")

    return validated


def format_attachments(
    attachments: str | list[str] | None
) -> list[dict[str, Any]] | None:
    """Format file attachments for email sending.
    
    Args:
        attachments: File path(s) to attach
        
    Returns:
        Formatted attachment list for Graph API
    """
    if not attachments:
        return None

    # Convert to list if single string
    if isinstance(attachments, str):
        attachments = [attachments]

    formatted = []
    for file_path in attachments:
        # Read file and encode
        import base64
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        formatted.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": path.name,
            "contentType": "application/octet-stream",
            "contentBytes": content
        })

    return formatted


def get_default_signature() -> str:
    """Get the default KamDental email signature.
    
    Returns:
        HTML formatted signature with KamDental branding
    """
    return """
    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e1e4e8;">
        <p style="margin: 0; font-weight: bold; color: #24292e;">
            Ossie Irondi PharmD.
        </p>
        <p style="margin: 0; color: #586069;">KC Ventures PLLC,</p>
        <p style="margin: 0; color: #586069;">Chief Operating Officer</p>
        <p style="margin: 5px 0; color: #586069;">
            Baytown Office: 281-421-5950<br>
            Humble Office: 281-812-3333<br>
            Cell: 346-644-0193
        </p>
        <p style="margin: 5px 0;">
            <a href="https://www.kamdental.com" style="color: #0366d6; text-decoration: none;">
                https://www.kamdental.com
            </a>
        </p>
        <p style="margin: 5px 0;">
            <a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled" 
               style="color: #0366d6; text-decoration: none;">
                Book Time With Me
            </a>
        </p>
    </div>
    """


def apply_email_theme(html_content: str, theme: str = "baytown") -> str:
    """Apply a theme to existing HTML email content.
    
    Args:
        html_content: HTML email content
        theme: Theme name to apply
        
    Returns:
        HTML content with theme CSS applied and inlined
    """
    if theme not in THEMES:
        raise ValueError(f"Invalid theme: {theme}. Must be one of: {list(THEMES.keys())}")

    from .css.themes import get_theme_styles
    theme_css = get_theme_styles(theme)
    
    # Insert theme CSS into HTML and inline it
    if '<style>' in html_content:
        html_content = html_content.replace('<style>', f'<style>{theme_css}\n')
    elif '</head>' in html_content:
        html_content = html_content.replace('</head>', f'<style>{theme_css}</style>\n</head>')
    else:
        # Add head section if missing
        html_content = f'<html><head><style>{theme_css}</style></head>{html_content}</html>'
    
    return inline_css(html_content)
