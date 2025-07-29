"""
Provider Update email template for KamDental
"""

from typing import Dict, Any
from .base import EmailTemplate


class ProviderUpdateTemplate(EmailTemplate):
    """Template for individual provider performance updates"""
    
    def get_template_name(self) -> str:
        return "provider_update.html"
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate provider update data"""
        required_fields = ["provider_name", "performance_data"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate performance_data structure
        perf_required = ["production", "goal", "percentage"]
        for field in perf_required:
            if field not in data["performance_data"]:
                raise ValueError(f"Missing required performance data field: {field}")
    
    def _get_template_html(self, data: Dict[str, Any]) -> str:
        """Generate provider update HTML"""
        provider_name = data["provider_name"]
        period = data.get("period", "Current Period")
        performance = data["performance_data"]
        highlights = data.get("highlights", [])
        recommendations = data.get("recommendations", [])
        
        # Personalized greeting
        html = f"""
        <div class="header">
            <h1>Performance Update</h1>
            <p>Dear {provider_name}</p>
        </div>
        
        <p>Here's your performance summary for {period}:</p>
        
        <div style="margin: 20px 0;">
            <div class="metric-card" style="margin-bottom: 15px;">
                <div class="metric-label">Your Production</div>
                <div class="metric-value">{self.format_currency(performance['production'])}</div>
                <div class="metric-subtitle">
                    {self.format_percentage(performance['percentage'])} of your goal ({self.format_currency(performance['goal'])})
                </div>
            </div>
        """
        
        # Add additional metrics if available
        if "appointments" in performance:
            html += f"""
            <div style="display: table; width: 100%; margin-bottom: 15px;">
                <div style="display: table-row;">
                    <div style="display: table-cell; width: 48%; padding-right: 2%;">
                        <div class="metric-card">
                            <div class="metric-label">Appointments</div>
                            <div class="metric-value">{performance['appointments']}</div>
                        </div>
                    </div>
                    <div style="display: table-cell; width: 48%;">
                        <div class="metric-card">
                            <div class="metric-label">Avg Production/Visit</div>
                            <div class="metric-value">
                                {self.format_currency(performance.get('average_production_per_visit', performance['production'] / performance['appointments'] if performance['appointments'] > 0 else 0))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        if "case_acceptance" in performance:
            html += f"""
            <div class="metric-card" style="width: 48%; display: inline-block;">
                <div class="metric-label">Case Acceptance Rate</div>
                <div class="metric-value status-{'good' if performance['case_acceptance'] > 0.35 else 'warning'}">
                    {self.format_percentage(performance['case_acceptance'])}
                </div>
            </div>
            """
        
        html += "</div>"
        
        # Add highlights section
        if highlights:
            html += '<div class="section"><h2>Your Highlights</h2><ul>'
            for highlight in highlights:
                html += f'<li>{highlight}</li>'
            html += '</ul></div>'
        
        # Add recommendations section
        if recommendations:
            html += '<div class="section"><h2>Recommendations for Growth</h2>'
            for i, rec in enumerate(recommendations, 1):
                html += f'<div class="highlight">{i}. {rec}</div>'
            html += '</div>'
        
        # Add motivational closing
        percentage = performance['percentage']
        if percentage >= 1.0:
            closing = "Excellent work! You're exceeding your goals. Keep up the outstanding performance!"
        elif percentage >= 0.9:
            closing = "You're very close to your goal! A little extra push will get you there."
        elif percentage >= 0.75:
            closing = "Good progress! You're on track to meet your goals with continued effort."
        else:
            closing = "Let's work together to identify opportunities to boost your production. I'm here to support you!"
        
        html += f"""
        <div class="highlight" style="margin-top: 30px; text-align: center;">
            <p><strong>{closing}</strong></p>
        </div>
        """
        
        return html