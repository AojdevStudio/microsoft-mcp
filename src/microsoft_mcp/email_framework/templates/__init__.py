"""
Email templates for KamDental Email Framework
"""

from .base import EmailTemplate
from .practice_report import PracticeReportTemplate
from .executive_summary import ExecutiveSummaryTemplate
from .provider_update import ProviderUpdateTemplate
from .alert_notification import AlertNotificationTemplate

__all__ = [
    "EmailTemplate",
    "PracticeReportTemplate",
    "ExecutiveSummaryTemplate",
    "ProviderUpdateTemplate",
    "AlertNotificationTemplate",
]