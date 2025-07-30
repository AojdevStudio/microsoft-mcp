"""
Alert Notification email template for KamDental
SECURITY: All user inputs are now properly escaped to prevent XSS attacks
"""

from typing import Dict, Any, List
from markupsafe import escape, Markup
from .base import EmailTemplate


class AlertNotificationTemplate(EmailTemplate):
    """Template for urgent alerts and notifications"""
    
    def get_template_name(self) -> str:
        return "Alert Notification"
    
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
        """Generate alert notification HTML with proper escaping"""
        # SECURITY: Escape all user inputs to prevent XSS
        alert_type = escape(data["alert_type"])
        title = escape(data["title"])
        message = escape(data["message"])
        urgency = escape(data.get("urgency", "normal"))
        impact = escape(data.get("impact", ""))
        actions = data.get("recommended_actions", [])
        
        # Get urgency-based styling
        urgency_style = self._get_urgency_styles(str(urgency).lower())
        
        # Build alert header with urgency-based styling
        html = Markup(f"""
        <div style="background-color: {urgency_style['bg_color']}; color: {urgency_style['text_color']}; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
            <h1 style="margin: 0; color: {urgency_style['text_color']};">
                {urgency_style['icon']} {title}
            </h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; color: {urgency_style['text_color']};">
                {str(urgency).upper()} ACTION REQUIRED
            </p>
        </div>
        
        <div class="section">
            <h2>Issue Details</h2>
            <p style="font-size: 16px; line-height: 1.6;">{message}</p>
        """)
        
        # Add impact section if provided
        if impact:
            html += Markup(f"""
            <div class="alert alert-{alert_type}" style="margin: 20px 0;">
                <strong>Business Impact:</strong><br>
                {impact}
            </div>
            """)
        
        html += Markup("</div>")
        
        # Add recommended actions if provided
        if actions:
            html += Markup("""
            <div class="section">
                <h2>Recommended Actions</h2>
                <ol style="margin: 0; padding-left: 20px;">
            """)
            for action in actions:
                # SECURITY: Escape each action item
                safe_action = escape(action)
                html += Markup(f'<li style="margin-bottom: 10px;">{safe_action}</li>')
            html += Markup("""
                </ol>
            </div>
            """)
        
        # Add call-to-action based on urgency
        urgency_lower = str(urgency).lower()
        if urgency_lower == "immediate":
            cta_text = "This requires immediate attention. Please address this issue as soon as possible."
            cta_color = urgency_style['bg_color']
        elif urgency_lower == "high":
            cta_text = "Please prioritize addressing this issue within the next 24-48 hours."
            cta_color = urgency_style['bg_color']
        else:
            cta_text = "Please review this information and take appropriate action."
            cta_color = self._theme_colors['--primary']
        
        html += Markup(f"""
        <div style="text-align: center; margin: 30px 0;">
            <div style="background-color: {self._theme_colors['--light-bg']}; padding: 20px; border-radius: 8px; border: 2px solid {cta_color};">
                <p style="margin: 0; font-weight: 600; color: {cta_color};">
                    {escape(cta_text)}
                </p>
            </div>
        </div>
        """)
        
        # Add contact information for urgent issues
        if urgency_lower in ["immediate", "high"]:
            html += Markup("""
            <div class="highlight" style="text-align: center;">
                <p><strong>Need immediate assistance?</strong></p>
                <p>Contact the operations team directly:<br>
                Baytown: 281-421-5950<br>
                Humble: 281-812-3333<br>
                Cell: 346-644-0193</p>
            </div>
            """)
        
        return str(html)
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample alert data for testing"""
        return {
            "alert_type": "warning",
            "title": "High Call Abandonment Rate Detected",
            "message": "The call abandonment rate at the Baytown location has exceeded 15% for the past 3 days. This is significantly above the target threshold of 5% and requires immediate attention to prevent patient dissatisfaction.",
            "urgency": "high",
            "impact": "Potential loss of 20-30 new patient appointments per day. Estimated revenue impact of $15,000-$20,000 per week if not addressed.",
            "recommended_actions": [
                "Review current staffing levels during peak call hours (9 AM - 12 PM)",
                "Check phone system for technical issues or call routing problems",
                "Implement callback queue system for overflow calls",
                "Schedule emergency staff meeting to address phone coverage",
                "Consider temporary staffing support from other locations"
            ]
        }