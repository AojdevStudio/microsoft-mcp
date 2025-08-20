"""
Legacy tool mapping and routing for Microsoft MCP Story 1.7: Migration and Deprecation Layer

This module provides the routing logic to map legacy tools to unified tools
with proper parameter transformation and backward compatibility.
"""

from collections.abc import Callable
from typing import Any

from .migration import parameter_mapper


class LegacyToolRouter:
    """
    Routes legacy tool calls to unified tools with parameter transformation.
    
    Handles the complete routing process from legacy tool invocation
    to unified tool execution with proper parameter mapping.
    """

    def __init__(self, microsoft_operations_func: Callable):
        """
        Initialize the legacy tool router.
        
        Args:
            microsoft_operations_func: The unified microsoft_operations function
        """
        self.microsoft_operations = microsoft_operations_func
        self.mapper = parameter_mapper

    def route_email_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Route legacy email tool to unified operations.
        
        Args:
            tool_name: Name of the legacy email tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Result from unified tool execution
        """
        try:
            # Map legacy parameters to unified format
            mapped_params = self.mapper.map_email_parameters(tool_name, **kwargs)

            # Execute unified operation
            return self.microsoft_operations(**mapped_params)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Legacy tool routing failed for {tool_name}: {str(e)}",
                "legacy_tool": tool_name,
                "original_params": kwargs
            }

    def route_calendar_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Route legacy calendar tool to unified operations.
        
        Args:
            tool_name: Name of the legacy calendar tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Result from unified tool execution
        """
        try:
            # Map legacy parameters to unified format
            mapped_params = self.mapper.map_calendar_parameters(tool_name, **kwargs)

            # Execute unified operation
            return self.microsoft_operations(**mapped_params)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Legacy tool routing failed for {tool_name}: {str(e)}",
                "legacy_tool": tool_name,
                "original_params": kwargs
            }

    def route_file_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Route legacy file tool to unified operations.
        
        Args:
            tool_name: Name of the legacy file tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Result from unified tool execution
        """
        try:
            # Map legacy parameters to unified format
            mapped_params = self.mapper.map_file_parameters(tool_name, **kwargs)

            # Execute unified operation
            return self.microsoft_operations(**mapped_params)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Legacy tool routing failed for {tool_name}: {str(e)}",
                "legacy_tool": tool_name,
                "original_params": kwargs
            }

    def route_contact_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Route legacy contact tool to unified operations.
        
        Args:
            tool_name: Name of the legacy contact tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Result from unified tool execution
        """
        try:
            # Map legacy parameters to unified format
            mapped_params = self.mapper.map_contact_parameters(tool_name, **kwargs)

            # Execute unified operation
            return self.microsoft_operations(**mapped_params)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Legacy tool routing failed for {tool_name}: {str(e)}",
                "legacy_tool": tool_name,
                "original_params": kwargs
            }


class LegacyToolRegistry:
    """
    Registry of all legacy tools and their routing configurations.
    
    Provides categorization and metadata for legacy tools to support
    the deprecation and migration process.
    """

    EMAIL_TOOLS = {
        "list_emails": {"category": "email", "action": "email.list"},
        "send_email": {"category": "email", "action": "email.send"},
        "create_email_draft": {"category": "email", "action": "email.draft"},
        "reply_to_email": {"category": "email", "action": "email.reply"},
        "forward_email": {"category": "email", "action": "email.forward"},
        "delete_email": {"category": "email", "action": "email.delete"},
        "mark_email_as_read": {"category": "email", "action": "email.mark"},
        "move_email": {"category": "email", "action": "email.move"},
        "search_emails": {"category": "email", "action": "email.search"},
        "get_email": {"category": "email", "action": "email.get"},
        "download_email_attachments": {"category": "email", "action": "email.get"},
        "list_mail_folders": {"category": "email", "action": "email.list"},
        "create_mail_folder": {"category": "email", "action": "email.list"},
        "get_email_signature": {"category": "email", "action": "email.list"},
        "add_email_attachment_from_onedrive": {"category": "email", "action": "email.draft"},
        "get_inbox_rules": {"category": "email", "action": "email.list"},
        "get_email_categories": {"category": "email", "action": "email.list"},
        "schedule_email": {"category": "email", "action": "email.send"},
        "batch_download_attachments": {"category": "email", "action": "email.get"},
        "get_email_headers": {"category": "email", "action": "email.get"},
        "empty_deleted_items": {"category": "email", "action": "email.delete"},
        "get_out_of_office": {"category": "email", "action": "email.list"},
        "set_out_of_office": {"category": "email", "action": "email.send"},
        "disable_out_of_office": {"category": "email", "action": "email.send"},
        # Professional email templates
        "send_practice_report": {"category": "email", "action": "email.send", "template": "practice_report"},
        "send_executive_summary": {"category": "email", "action": "email.send", "template": "executive_summary"},
        "send_provider_update": {"category": "email", "action": "email.send", "template": "provider_update"},
        "send_alert_notification": {"category": "email", "action": "email.send", "template": "alert_notification"},
    }

    CALENDAR_TOOLS = {
        "list_calendar_events": {"category": "calendar", "action": "calendar.list"},
        "create_calendar_event": {"category": "calendar", "action": "calendar.create"},
        "update_calendar_event": {"category": "calendar", "action": "calendar.update"},
        "delete_calendar_event": {"category": "calendar", "action": "calendar.delete"},
        "get_calendar_availability": {"category": "calendar", "action": "calendar.list"},
        "send_calendar_invite": {"category": "calendar", "action": "calendar.invite"},
        "search_calendar_events": {"category": "calendar", "action": "calendar.search"},
        "get_calendar_list": {"category": "calendar", "action": "calendar.list"},
    }

    FILE_TOOLS = {
        "list_files": {"category": "file", "action": "file.list"},
        "download_file": {"category": "file", "action": "file.download"},
        "upload_file": {"category": "file", "action": "file.upload"},
        "create_folder": {"category": "file", "action": "file.list"},
        "delete_file": {"category": "file", "action": "file.delete"},
        "share_file": {"category": "file", "action": "file.share"},
        "search_files": {"category": "file", "action": "file.search"},
        "get_recent_files": {"category": "file", "action": "file.list"},
        "get_file_preview": {"category": "file", "action": "file.get"},
        "get_file_versions": {"category": "file", "action": "file.get"},
        "restore_file_version": {"category": "file", "action": "file.get"},
        "get_file_permissions": {"category": "file", "action": "file.get"},
        "list_shared_files": {"category": "file", "action": "file.list"},
    }

    CONTACT_TOOLS = {
        "list_contacts": {"category": "contact", "action": "contact.list"},
        "create_contact": {"category": "contact", "action": "contact.create"},
        "update_contact": {"category": "contact", "action": "contact.update"},
        "delete_contact": {"category": "contact", "action": "contact.delete"},
        "export_contacts": {"category": "contact", "action": "contact.list"},
        "search_people": {"category": "contact", "action": "contact.list"},
    }

    @classmethod
    def get_all_legacy_tools(cls) -> dict[str, dict[str, str]]:
        """
        Get all legacy tools with their routing information.
        
        Returns:
            Dictionary mapping tool names to routing info
        """
        all_tools = {}
        all_tools.update(cls.EMAIL_TOOLS)
        all_tools.update(cls.CALENDAR_TOOLS)
        all_tools.update(cls.FILE_TOOLS)
        all_tools.update(cls.CONTACT_TOOLS)
        return all_tools

    @classmethod
    def get_tools_by_category(cls, category: str) -> dict[str, dict[str, str]]:
        """
        Get legacy tools by category.
        
        Args:
            category: Tool category ("email", "calendar", "file", "contact")
            
        Returns:
            Dictionary of tools in the specified category
        """
        if category == "email":
            return cls.EMAIL_TOOLS
        if category == "calendar":
            return cls.CALENDAR_TOOLS
        if category == "file":
            return cls.FILE_TOOLS
        if category == "contact":
            return cls.CONTACT_TOOLS
        return {}

    @classmethod
    def get_tool_info(cls, tool_name: str) -> dict[str, str] | None:
        """
        Get routing information for a specific tool.
        
        Args:
            tool_name: Name of the legacy tool
            
        Returns:
            Tool routing information or None if not found
        """
        all_tools = cls.get_all_legacy_tools()
        return all_tools.get(tool_name)

    @classmethod
    def is_legacy_tool(cls, tool_name: str) -> bool:
        """
        Check if a tool is a legacy tool.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if the tool is a legacy tool
        """
        return tool_name in cls.get_all_legacy_tools()

    @classmethod
    def count_legacy_tools(cls) -> dict[str, int]:
        """
        Count legacy tools by category.
        
        Returns:
            Dictionary with counts by category and total
        """
        return {
            "email": len(cls.EMAIL_TOOLS),
            "calendar": len(cls.CALENDAR_TOOLS),
            "file": len(cls.FILE_TOOLS),
            "contact": len(cls.CONTACT_TOOLS),
            "total": len(cls.get_all_legacy_tools())
        }


def create_deprecation_wrapper(tool_name: str, unified_action: str, template: str | None = None):
    """
    Factory function to create deprecation wrapper for a legacy tool.
    
    Args:
        tool_name: Name of the legacy tool
        unified_action: Corresponding unified action
        template: Optional template for email tools
        
    Returns:
        Deprecation wrapper function
    """
    from .deprecation import deprecated_tool

    # Determine migration message based on tool category
    tool_info = LegacyToolRegistry.get_tool_info(tool_name)
    if not tool_info:
        raise ValueError(f"Unknown legacy tool: {tool_name}")

    category = tool_info["category"]

    if template:
        migration_message = f"Use microsoft_operations with action='{unified_action}' and template='{template}'"
    else:
        migration_message = f"Use microsoft_operations with action='{unified_action}'"

    @deprecated_tool(
        migration_message=migration_message,
        unified_action=unified_action,
        removal_timeline="30 days"
    )
    def wrapper(*args, **kwargs):
        # This will be implemented in the actual deprecation wrappers
        # For now, just return a placeholder
        return {
            "status": "deprecated",
            "tool_name": tool_name,
            "migration_message": migration_message,
            "unified_action": unified_action
        }

    return wrapper


# Export key components for use in tools.py
__all__ = [
    "LegacyToolRouter",
    "LegacyToolRegistry",
    "create_deprecation_wrapper"
]
