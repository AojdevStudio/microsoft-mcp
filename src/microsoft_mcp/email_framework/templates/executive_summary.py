"""
Executive Summary email template for KamDental
"""

from typing import Dict, Any
from .base import EmailTemplate


class ExecutiveSummaryTemplate(EmailTemplate):
    """Template for executive summary reports"""
    
    def __init__(self, theme: str = "executive"):
        """Initialize with executive theme by default"""
        super().__init__(theme)
    
    def get_template_name(self) -> str:
        return "executive_summary.html"
    
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
        """Generate executive summary HTML"""
        period = data["period"]
        locations = data["locations"]
        insights = data.get("key_insights", [])
        total_production = data.get("total_production", sum(loc["production"] for loc in locations))
        total_goal = data.get("total_goal", sum(loc.get("goal", 0) for loc in locations))
        overall_percentage = data.get("overall_percentage", total_production / total_goal if total_goal > 0 else 0)
        
        # Build header
        html = f"""
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
        """
        
        # Build locations grid
        html += '<div style="margin-bottom: 30px;">'
        for i, location in enumerate(locations):
            percentage = location.get("percentage", location["production"] / location.get("goal", 1))
            status = location.get("status", "normal")
            
            html += f"""
            <div style="display: inline-block; width: 48%; margin-right: {4 if i % 2 == 0 else 0}%; margin-bottom: 15px;">
                <div class="metric-card">
                    <div class="metric-label">{location['name']}</div>
                    <div class="metric-value status-{status}">
                        {self.format_currency(location['production'])}
                    </div>
                    <div class="metric-subtitle">
                        {self.format_percentage(percentage)} to goal
                    </div>
                </div>
            </div>
            """
        html += '</div>'
        
        # Build insights section
        if insights:
            html += '<div class="section"><h2>Key Insights</h2>'
            for insight in insights:
                insight_type = insight.get("type", "info")
                icon = "✓" if insight_type == "success" else "⚠️" if insight_type == "challenge" else "ℹ️"
                html += f"""
                <div class="highlight">
                    <strong>{icon} {insight.get('location', 'Overall')}</strong>: {insight['message']}
                </div>
                """
            html += '</div>'
        
        # Add summary table
        html += """
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
        """
        
        for location in locations:
            goal = location.get("goal", 0)
            percentage = location.get("percentage", location["production"] / goal if goal > 0 else 0)
            status = location.get("status", "normal")
            status_text = {
                "behind": "Behind",
                "on_track": "On Track",
                "ahead": "Ahead",
                "warning": "Warning"
            }.get(status, "Normal")
            
            html += f"""
            <tr>
                <td><strong>{location['name']}</strong></td>
                <td>{self.format_currency(location['production'])}</td>
                <td>{self.format_currency(goal)}</td>
                <td class="status-{status}">{self.format_percentage(percentage)}</td>
                <td class="status-{status}">{status_text}</td>
            </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html