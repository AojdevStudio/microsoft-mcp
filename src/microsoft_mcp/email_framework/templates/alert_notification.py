"""
Alert Notification email template for KamDental
"""

from typing import Dict, Any
from .base import EmailTemplate


class AlertNotificationTemplate(EmailTemplate):
    """Template for urgent alerts and notifications"""
    
    def get_template_name(self) -> str:
        return "alert_notification.html"
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate alert notification data"""
        required_fields = ["alert_type", "title", "message"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
    
    def _get_urgency_styles(self, urgency: str) -> Dict[str, str]:
        """Get styles based on urgency level"""
        styles = {
            "immediate": {
                "bg_color": "#E53E3E",
                "text_color": "#FFFFFF",
                "border_color": "#E53E3E",
                "icon": "🚨"
            },
            "high": {
                "bg_color": "#D69E2E",
                "text_color": "#FFFFFF",
                "border_color": "#D69E2E",
                "icon": "⚠️"
            },
            "normal": {
                "bg_color": "#3182CE",
                "text_color": "#FFFFFF",
                "border_color": "#3182CE",
                "icon": "ℹ️"
            }
        }
        return styles.get(urgency, styles["normal"])
    
    def _get_template_html(self, data: Dict[str, Any]) -> str:
        """Generate alert notification HTML"""
        alert_type = data["alert_type"]
        title = data["title"]
        message = data["message"]
        urgency = data.get("urgency", "normal")
        impact = data.get("impact", "")
        actions = data.get("recommended_actions", [])
        
        # Get urgency-based styling
        urgency_style = self._get_urgency_styles(urgency)
        
        # Build alert header with urgency-based styling
        html = f"""
        <div style="background-color: {urgency_style['bg_color']}; color: {urgency_style['text_color']}; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
            <h1 style="margin: 0; color: {urgency_style['text_color']};">
                {urgency_style['icon']} {self.escape_html(title)}
            </h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; color: {urgency_style['text_color']};">
                {urgency.upper()} ACTION REQUIRED
            </p>
        </div>
        
        <div class="section">
            <h2>Issue Details</h2>
            <p style="font-size: 16px; line-height: 1.6;">{self.escape_html(message)}</p>
        """
        
        # Add impact section if provided
        if impact:
            html += f"""
            <div class="alert alert-{alert_type}" style="margin: 20px 0;">
                <strong>Business Impact:</strong><br>
                {self.escape_html(impact)}
            </div>
            """
        
        html += "</div>"
        
        # Add recommended actions if provided
        if actions:
            html += """
            <div class="section">
                <h2>Recommended Actions</h2>
                <ol style="margin: 0; padding-left: 20px;">
            """
            for action in actions:
                html += f'<li style="margin-bottom: 10px;">{self.escape_html(action)}</li>'
            html += """
                </ol>
            </div>
            """
        
        # Add call-to-action based on urgency
        if urgency == "immediate":
            cta_text = "This requires immediate attention. Please address this issue as soon as possible."
            cta_color = urgency_style['bg_color']
        elif urgency == "high":
            cta_text = "Please prioritize addressing this issue within the next 24-48 hours."
            cta_color = urgency_style['bg_color']
        else:
            cta_text = "Please review this information and take appropriate action."
            cta_color = self._theme_colors.get('primary', '#007bff')  # Fixed: use 'primary' not '--primary'
        
        html += f"""
        <div style="text-align: center; margin: 30px 0;">
            <div style="background-color: {self._theme_colors.get('light_bg', '#f8f9fa')}; padding: 20px; border-radius: 8px; border: 2px solid {cta_color};">
                <p style="margin: 0; font-weight: 600; color: {cta_color};">
                    {cta_text}
                </p>
            </div>
        </div>
        """
        
        # Add contact information for urgent issues
        if urgency in ["immediate", "high"]:
            html += """
            <div class="highlight" style="text-align: center;">
                <p><strong>Need immediate assistance?</strong></p>
                <p>Contact the operations team directly:<br>
                Baytown: 281-421-5950<br>
                Humble: 281-812-3333<br>
                Cell: 346-644-0193</p>
            </div>
            """
        
        return html