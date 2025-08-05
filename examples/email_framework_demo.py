#!/usr/bin/env python3
"""
Demo script showing how to use the KamDental Email Framework tools
"""

# Example 1: Send a Practice Report
practice_report_data = {
    "account_id": "your-account-id",
    "to": "executive@kamdental.com",
    "subject": "Baytown Practice Report - July 2025 MTD",
    "location": "Baytown",
    "period": "July 2025 MTD",
    "financial_data": {
        "production": {"value": 143343, "goal": 160000, "status": "behind"},
        "collections": {"value": 107113, "ratio": 0.747},
        "case_acceptance": {"value": 0.3586, "status": "good"},
        "call_answer_rate": {"value": 0.693, "goal": 0.85, "status": "warning"}
    },
    "provider_data": [
        {
            "name": "Dr. Obinna Ezeji",
            "role": "Lead Producer",
            "production": 68053,
            "goal_percentage": 0.756,
            "status": "good"
        },
        {
            "name": "Adriane (DHAA)",
            "role": "Hygienist", 
            "production": 21418,
            "goal_percentage": 0.892,
            "status": "good"
        }
    ],
    "alerts": [
        {
            "type": "critical",
            "icon": "🚨",
            "title": "Critical Issue",
            "message": "Call answer rate at 69.3% vs 85% goal"
        }
    ],
    "recommendations": [
        {
            "priority": "IMMEDIATE",
            "title": "Phone Coverage Improvement",
            "details": "Target 85% answer rate by month-end",
            "outcome": "Expected outcome: $13,000+ additional production"
        }
    ],
    "cc": ["manager@kamdental.com"]
}

# Use: send_practice_report(**practice_report_data)

# Example 2: Send Executive Summary
executive_summary_data = {
    "account_id": "your-account-id",
    "to": "ceo@kamdental.com",
    "locations_data": [
        {
            "name": "Baytown",
            "status": "behind",
            "production": 143343,
            "goal": 160000,
            "percentage": 0.896
        },
        {
            "name": "Humble",
            "status": "on_track",
            "production": 178000,
            "goal": 175000,
            "percentage": 1.017
        }
    ],
    "period": "July 2025 MTD",
    "key_insights": [
        {
            "type": "challenge",
            "location": "Baytown",
            "message": "$16,656 behind production goal"
        },
        {
            "type": "success",
            "location": "Humble",
            "message": "Exceeding goal by 1.7%"
        }
    ]
}

# Use: send_executive_summary(**executive_summary_data)

# Example 3: Send Provider Update
provider_update_data = {
    "account_id": "your-account-id",
    "to": "dr.ezeji@kamdental.com",
    "provider_name": "Dr. Obinna Ezeji",
    "performance_data": {
        "production": 68053,
        "goal": 90000,
        "percentage": 0.756,
        "appointments": 125,
        "case_acceptance": 0.42,
        "average_production_per_visit": 544
    },
    "period": "July 2025 MTD",
    "highlights": [
        "Strong case acceptance at 42%",
        "Consistent daily production",
        "High patient satisfaction scores"
    ],
    "recommendations": [
        "Schedule more high-value procedures",
        "Focus on crown and bridge cases",
        "Consider additional CE for implant procedures"
    ]
}

# Use: send_provider_update(**provider_update_data)

# Example 4: Send Alert Notification
alert_notification_data = {
    "account_id": "your-account-id",
    "to": "operations@kamdental.com",
    "alert_type": "critical",
    "title": "Phone Coverage Critical",
    "message": "Answer rate has dropped to 69.3% vs 85% goal",
    "urgency": "immediate",
    "impact": "Estimated $13,000 in lost production opportunity",
    "recommended_actions": [
        "Review phone coverage schedule",
        "Assign dedicated receptionist during peak hours",
        "Implement call-back protocol for missed calls"
    ],
    "cc": ["manager@kamdental.com", "supervisor@kamdental.com"]
}

# Use: send_alert_notification(**alert_notification_data)

print("Email Framework Demo")
print("=" * 50)
print("\nAvailable tools:")
print("1. send_practice_report() - Send detailed practice performance reports")
print("2. send_executive_summary() - Send multi-location executive summaries")
print("3. send_provider_update() - Send personalized provider performance updates")
print("4. send_alert_notification() - Send urgent alerts with custom urgency levels")
print("\nEach tool automatically:")
print("- Applies professional HTML formatting")
print("- Uses location-specific themes (Baytown, Humble, Executive)")
print("- Includes the executive signature")
print("- Inlines CSS for email client compatibility")
print("\nSee the examples above for usage patterns.")