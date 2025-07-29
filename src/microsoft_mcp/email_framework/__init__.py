"""
KamDental Email Framework
Professional email templates and styling for KamDental practice communications.
"""

from .templates.base import EmailTemplate
from .templates.practice_report import PracticeReportTemplate
from .templates.executive_summary import ExecutiveSummaryTemplate
from .templates.provider_update import ProviderUpdateTemplate
from .templates.alert_notification import AlertNotificationTemplate
from .css_inliner import inline_css

__all__ = [
    "EmailTemplate",
    "PracticeReportTemplate",
    "ExecutiveSummaryTemplate",
    "ProviderUpdateTemplate",
    "AlertNotificationTemplate",
    "inline_css",
]