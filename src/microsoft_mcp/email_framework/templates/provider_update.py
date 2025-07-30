"""
Provider Update email template for KamDental
SECURITY: All user inputs are now properly escaped to prevent XSS attacks
"""

from typing import Dict, Any, List
from markupsafe import escape, Markup
from .base import EmailTemplate


class ProviderUpdateTemplate(EmailTemplate):
    """Template for individual provider performance updates"""
    
    def get_template_name(self) -> str:
        return "Provider Update"
    
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
        """Generate provider update HTML with proper escaping"""
        # SECURITY: Escape all user inputs
        provider_name = escape(data["provider_name"])
        period = escape(data.get("period", "Current Period"))
        performance = data["performance_data"]
        highlights = data.get("highlights", [])
        recommendations = data.get("recommendations", [])
        
        # Personalized greeting
        html = Markup(f"""
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
        """)
        
        # Add additional metrics if available
        if "appointments" in performance:
            avg_production = performance.get('average_production_per_visit', 
                                          performance['production'] / performance['appointments'] if performance['appointments'] > 0 else 0)
            html += Markup(f"""
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
                                {self.format_currency(avg_production)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """)
        
        if "case_acceptance" in performance:
            case_status = 'good' if performance['case_acceptance'] > 0.35 else 'warning'
            html += Markup(f"""
            <div class="metric-card" style="width: 48%; display: inline-block;">
                <div class="metric-label">Case Acceptance Rate</div>
                <div class="metric-value status-{escape(case_status)}">
                    {self.format_percentage(performance['case_acceptance'])}
                </div>
            </div>
            """)
        
        html += Markup("</div>")
        
        # Add highlights section
        if highlights:
            html += Markup('<div class="section"><h2>Your Highlights</h2><ul>')
            for highlight in highlights:
                # SECURITY: Escape each highlight
                safe_highlight = escape(highlight)
                html += Markup(f'<li>{safe_highlight}</li>')
            html += Markup('</ul></div>')
        
        # Add recommendations section
        if recommendations:
            html += Markup('<div class="section"><h2>Recommendations for Growth</h2>')
            for i, rec in enumerate(recommendations, 1):
                # SECURITY: Escape each recommendation
                safe_rec = escape(rec)
                html += Markup(f'<div class="highlight">{i}. {safe_rec}</div>')
            html += Markup('</div>')
        
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
        
        html += Markup(f"""
        <div class="highlight" style="margin-top: 30px; text-align: center;">
            <p><strong>{escape(closing)}</strong></p>
        </div>
        """)
        
        return str(html)
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample provider update data"""
        return {
            "provider_name": "Dr. Sarah Johnson",
            "period": "January 2024",
            "performance_data": {
                "production": 125000,
                "goal": 120000,
                "percentage": 1.04,
                "appointments": 180,
                "average_production_per_visit": 694,
                "case_acceptance": 0.42
            },
            "highlights": [
                "Achieved highest monthly production in the past 6 months",
                "Excellent patient satisfaction scores (4.9/5.0)",
                "Successfully completed advanced implant certification"
            ],
            "recommendations": [
                "Continue focusing on high-value procedures - your case acceptance rate is excellent",
                "Consider adding one more new patient slot per day to capitalize on your strong conversion rate",
                "Your morning appointments show higher production - try to schedule complex cases in AM slots"
            ]
        }