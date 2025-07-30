"""
Executive Summary email template for KamDental
SECURITY: All user inputs are now properly escaped to prevent XSS attacks
"""

from typing import Dict, Any, List
from markupsafe import escape, Markup
from .base import EmailTemplate


class ExecutiveSummaryTemplate(EmailTemplate):
    """Template for executive summary reports"""
    
    def __init__(self, theme: str = "executive"):
        """Initialize with executive theme by default"""
        super().__init__(theme)
    
    def get_template_name(self) -> str:
        return "Executive Summary"
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate executive summary data"""
        required_fields = ["period", "locations"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate locations structure
        if not data["locations"]:
            raise ValueError("At least one location is required")
        
        for location in data["locations"]:
            if "name" not in location or "production" not in location:
                raise ValueError("Each location must have name and production")
    
    def _get_template_html(self, data: Dict[str, Any]) -> str:
        """Generate executive summary HTML with proper escaping"""
        # SECURITY: Escape user inputs
        period = escape(data["period"])
        locations = data["locations"]
        insights = data.get("key_insights", [])
        
        # Calculate totals
        total_production = data.get("total_production", sum(loc["production"] for loc in locations))
        total_goal = data.get("total_goal", sum(loc.get("goal", 0) for loc in locations))
        overall_percentage = data.get("overall_percentage", total_production / total_goal if total_goal > 0 else 0)
        
        # Build header
        html = Markup(f"""
        <div class="header">
            <h1>Executive Summary</h1>
            <p>{period}</p>
        </div>
        
        <div class="metric-card" style="margin-bottom: 30px;">
            <div class="metric-label">Total Production</div>
            <div class="metric-value">{self.format_currency(total_production)}</div>
            <div class="metric-subtitle">
                {self.format_percentage(overall_percentage)} of combined goal ({self.format_currency(total_goal)})
            </div>
        </div>
        """)
        
        # Build locations grid
        html += Markup('<div style="margin-bottom: 30px;">')
        for i, location in enumerate(locations):
            # SECURITY: Escape location name
            location_name = escape(location['name'])
            percentage = location.get("percentage", location["production"] / location.get("goal", 1))
            status = escape(location.get("status", "normal"))
            
            html += Markup(f"""
            <div style="display: inline-block; width: 48%; margin-right: {4 if i % 2 == 0 else 0}%; margin-bottom: 15px;">
                <div class="metric-card">
                    <div class="metric-label">{location_name}</div>
                    <div class="metric-value status-{status}">
                        {self.format_currency(location['production'])}
                    </div>
                    <div class="metric-subtitle">
                        {self.format_percentage(percentage)} to goal
                    </div>
                </div>
            </div>
            """)
        html += Markup('</div>')
        
        # Build insights section
        if insights:
            html += Markup('<div class="section"><h2>Key Insights</h2>')
            for insight in insights:
                # SECURITY: Escape insight data
                insight_type = escape(insight.get("type", "info"))
                insight_location = escape(insight.get('location', 'Overall'))
                insight_message = escape(insight['message'])
                
                icon = "✓" if str(insight_type) == "success" else "⚠️" if str(insight_type) == "challenge" else "ℹ️"
                html += Markup(f"""
                <div class="highlight">
                    <strong>{icon} {insight_location}</strong>: {insight_message}
                </div>
                """)
            html += Markup('</div>')
        
        # Add summary table
        html += Markup("""
        <div class="section">
            <h2>Location Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Production</th>
                        <th>Goal</th>
                        <th>% to Goal</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """)
        
        for location in locations:
            # SECURITY: Escape all location data
            location_name = escape(location['name'])
            goal = location.get("goal", 0)
            percentage = location.get("percentage", location["production"] / goal if goal > 0 else 0)
            status = escape(location.get("status", "normal"))
            
            status_text = {
                "behind": "Behind",
                "on_track": "On Track",
                "ahead": "Ahead",
                "warning": "Warning"
            }.get(str(status), "Normal")
            
            html += Markup(f"""
            <tr>
                <td><strong>{location_name}</strong></td>
                <td>{self.format_currency(location['production'])}</td>
                <td>{self.format_currency(goal)}</td>
                <td class="status-{status}">{self.format_percentage(percentage)}</td>
                <td class="status-{status}">{escape(status_text)}</td>
            </tr>
            """)
        
        html += Markup("""
                </tbody>
            </table>
        </div>
        """)
        
        return str(html)
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample executive summary data"""
        return {
            "period": "January 2024 - Month to Date",
            "total_production": 750000,
            "total_goal": 800000,
            "overall_percentage": 0.9375,
            "locations": [
                {
                    "name": "Baytown",
                    "production": 285000,
                    "goal": 300000,
                    "percentage": 0.95,
                    "status": "on_track"
                },
                {
                    "name": "Humble",
                    "production": 265000,
                    "goal": 280000,
                    "percentage": 0.946,
                    "status": "on_track"
                },
                {
                    "name": "Cypress",
                    "production": 200000,
                    "goal": 220000,
                    "percentage": 0.909,
                    "status": "warning"
                }
            ],
            "key_insights": [
                {
                    "type": "success",
                    "location": "Baytown",
                    "message": "Achieved highest single-day production record of $45,000"
                },
                {
                    "type": "challenge",
                    "location": "Cypress",
                    "message": "Provider shortage impacting production - recruitment in progress"
                },
                {
                    "type": "info",
                    "location": "Overall",
                    "message": "On track to meet quarterly targets with current growth trajectory"
                }
            ]
        }