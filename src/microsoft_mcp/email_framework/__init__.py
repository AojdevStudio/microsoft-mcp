"""
KamDental Email Framework
Professional email templates and styling for KamDental practice communications.
"""

from . import utils
from .css_inliner import inline_css
from .templates.alert_notification import AlertNotificationTemplate
from .templates.base import EmailTemplate
from .templates.executive_summary import ExecutiveSummaryTemplate
from .templates.practice_report import PracticeReportTemplate
from .templates.provider_update import ProviderUpdateTemplate

__all__ = [
    "EmailTemplate",
    "PracticeReportTemplate",
    "ExecutiveSummaryTemplate",
    "ProviderUpdateTemplate",
    "AlertNotificationTemplate",
    "inline_css",
    "utils",
]
