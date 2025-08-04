"""
Practice Report email template for KamDental
Refactored for improved maintainability and reusability
"""

from typing import Dict, Any, List
from datetime import datetime
from .base import EmailTemplate


class PracticeReportTemplate(EmailTemplate):
    """Template for practice performance reports"""
    
    def get_template_name(self) -> str:
        return "Practice Report"
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate practice report data"""
        required_fields = ["location", "financial_data", "providers"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate financial_data structure
        financial_required = ["production", "collections", "case_acceptance", "call_answer_rate"]
        for field in financial_required:
            if field not in data["financial_data"]:
                raise ValueError(f"Missing required financial data field: {field}")
                
            # Validate each financial metric has required fields
            metric = data["financial_data"][field]
            if "value" not in metric:
                raise ValueError(f"Missing 'value' in financial data field: {field}")
                
        # Validate providers structure
        if not isinstance(data["providers"], list):
            raise ValueError("Providers must be a list")
            
        for i, provider in enumerate(data["providers"]):
            if "name" not in provider:
                raise ValueError(f"Missing 'name' in provider {i}")
            if "production" not in provider:
                raise ValueError(f"Missing 'production' in provider {i}")
    
    def _get_template_html(self, data: Dict[str, Any]) -> str:
        """Generate practice report HTML"""
        location = data["location"]
        period = data.get("period", "Current Period")
        financial = data["financial_data"]
        providers = data["providers"]
        alerts = data.get("alerts", [])
        recommendations = data.get("recommendations", [])
        
        # Build HTML sections
        header_html = self._build_header(location, period)
        metrics_html = self._build_financial_metrics(financial)
        providers_html = self._build_providers_section(providers)
        alerts_html = self._build_alerts_section(alerts)
        recommendations_html = self._build_recommendations_section(recommendations)
        
        # Combine all sections
        return f"""
        {header_html}
        {metrics_html}
        {providers_html}
        {alerts_html}
        {recommendations_html}
        """
        
    def _build_header(self, location: str, period: str) -> str:
        """Build the header section"""
        return f"""
        <div class="header">
            <h1 class="text-center">{location} Practice Report</h1>
            <p class="text-center text-light">{period}</p>
        </div>
        """
        
    def _build_financial_metrics(self, financial: Dict[str, Any]) -> str:
        """Build the financial metrics section"""
        # Production metric
        production = financial["production"]
        production_value = production["value"]
        production_goal = production.get("goal", production_value)
        production_ratio = production_value / production_goal if production_goal > 0 else 0
        production_status = self.get_status_class(production_value, production_goal)
        
        # Collections metric
        collections = financial["collections"]
        collections_value = collections["value"]
        collections_ratio = collections.get("ratio", 0.95)
        
        # Case acceptance metric
        case_acceptance = financial["case_acceptance"]
        case_acceptance_value = case_acceptance["value"]
        case_acceptance_goal = case_acceptance.get("goal", 0.75)
        case_acceptance_status = self.get_status_class(case_acceptance_value, case_acceptance_goal)
        
        # Call answer rate metric
        call_answer = financial["call_answer_rate"]
        call_answer_value = call_answer["value"]
        call_answer_goal = call_answer.get("goal", 0.95)
        call_answer_status = self.get_status_class(call_answer_value, call_answer_goal)
        
        return f"""
        <div class="metric-grid">
            <div class="metric-row">
                <div class="metric-col">
                    {self.build_metric_card(
                        "MTD Production",
                        self.format_currency(production_value),
                        f"{self.format_percentage(production_ratio)} to goal",
                        production_status
                    )}
                </div>
                <div class="metric-col">
                    {self.build_metric_card(
                        "Collections",
                        self.format_currency(collections_value),
                        f"{self.format_percentage(collections_ratio)} collection rate"
                    )}
                </div>
            </div>
            
            <div class="metric-row">
                <div class="metric-col">
                    {self.build_metric_card(
                        "Case Acceptance",
                        self.format_percentage(case_acceptance_value),
                        f"Goal: {self.format_percentage(case_acceptance_goal)}",
                        case_acceptance_status
                    )}
                </div>
                <div class="metric-col">
                    {self.build_metric_card(
                        "Call Answer Rate",
                        self.format_percentage(call_answer_value),
                        f"Goal: {self.format_percentage(call_answer_goal)}",
                        call_answer_status
                    )}
                </div>
            </div>
        </div>
        """
        
    def _build_providers_section(self, providers: List[Dict[str, Any]]) -> str:
        """Build the providers performance section"""
        if not providers:
            return ""
            
        # Sort providers by production (highest first)
        sorted_providers = sorted(providers, key=lambda p: p.get("production", 0), reverse=True)
        
        # Build table rows
        rows = []
        for provider in sorted_providers:
            name = provider["name"]
            production = provider.get("production", 0)
            role = provider.get("role", "Provider")
            goal_percentage = provider.get("goal_percentage", production / 100000)  # Default goal of 100k
            status_class = self.get_status_class(goal_percentage, 1.0)
            
            rows.append([
                f"<strong>{name}</strong>",
                role,
                self.format_currency(production),
                f'<span class="{status_class}">{self.format_percentage(goal_percentage)}</span>'
            ])
            
        table_html = self.build_data_table(
            ["Provider", "Role", "Production", "% to Goal"],
            rows
        )
        
        return f"""
        <div class="section">
            <h2 class="section-header">Provider Performance</h2>
            {table_html}
        </div>
        """
        
    def _build_alerts_section(self, alerts: List[Dict[str, Any]]) -> str:
        """Build the alerts section"""
        if not alerts:
            return ""
            
        alerts_html = []
        for alert in alerts:
            alert_type = alert.get("type", "warning")
            title = alert.get("title", "Alert")
            message = alert.get("message", "")
            
            if alert_type == "critical":
                alert_type = "danger"
                
            alerts_html.append(self.build_alert(title, message, alert_type))
            
        return f"""
        <div class="section">
            <h2 class="section-header">Alerts & Notifications</h2>
            {"".join(alerts_html)}
        </div>
        """
        
    def _build_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> str:
        """Build the recommendations section"""
        if not recommendations:
            return ""
            
        rec_items = []
        for rec in recommendations:
            priority = rec.get("priority", "Medium")
            title = rec.get("title", "")
            details = rec.get("details", "")
            outcome = rec.get("outcome", "")
            
            priority_class = f"priority-{priority.lower()}"
            priority_badge = f'<span class="recommendation-priority {priority_class}">{priority.upper()}</span>'
            
            outcome_html = f'<div class="text-sm text-light mt-2">{outcome}</div>' if outcome else ''
            
            rec_items.append(f"""
            <div class="recommendation-item">
                <div class="font-semibold">{title} {priority_badge}</div>
                <div class="mt-1">{details}</div>
                {outcome_html}
            </div>
            """)
            
        return f"""
        <div class="recommendations">
            <h2 class="recommendations-header">Recommendations</h2>
            {"".join(rec_items)}
        </div>
        """
        
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for testing"""
        return {
            "location": "Baytown",
            "period": f"Month to Date - {datetime.now().strftime('%B %Y')}",
            "financial_data": {
                "production": {
                    "value": 285000,
                    "goal": 300000,
                    "status": "warning"
                },
                "collections": {
                    "value": 270000,
                    "ratio": 0.947
                },
                "case_acceptance": {
                    "value": 0.72,
                    "goal": 0.75,
                    "status": "warning"
                },
                "call_answer_rate": {
                    "value": 0.91,
                    "goal": 0.95,
                    "status": "warning"
                }
            },
            "providers": [
                {
                    "name": "Dr. Sarah Johnson",
                    "role": "General Dentist",
                    "production": 125000,
                    "goal_percentage": 1.04
                },
                {
                    "name": "Dr. Michael Chen",
                    "role": "Orthodontist",
                    "production": 98000,
                    "goal_percentage": 0.82
                },
                {
                    "name": "Dr. Emily Rodriguez",
                    "role": "Hygienist",
                    "production": 62000,
                    "goal_percentage": 1.24
                }
            ],
            "alerts": [
                {
                    "type": "warning",
                    "title": "Production Below Target",
                    "message": "Current production is 5% below monthly target. Focus on case acceptance and treatment planning."
                },
                {
                    "type": "critical",
                    "title": "Call Answer Rate Critical",
                    "message": "Call answer rate has dropped below 92% for 3 consecutive days. Immediate attention required."
                }
            ],
            "recommendations": [
                {
                    "priority": "High",
                    "title": "Schedule team meeting to address call answer rate",
                    "details": "Review phone protocols and staffing during peak hours.",
                    "outcome": "Expected improvement: 5-7% within one week"
                },
                {
                    "priority": "Medium",
                    "title": "Implement case acceptance training",
                    "details": "Focus on value communication and treatment presentation skills.",
                    "outcome": "Target: Increase case acceptance to 75%+"
                },
                {
                    "priority": "Low",
                    "title": "Review fee schedule",
                    "details": "Quarterly fee schedule review and competitive analysis.",
                    "outcome": "Ensure pricing remains competitive"
                }
            ]
        }