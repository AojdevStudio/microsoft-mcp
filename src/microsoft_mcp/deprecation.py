"""
Deprecation utilities for Microsoft MCP Story 1.7: Migration and Deprecation Layer

This module provides deprecation decorators and warning systems to enable smooth
transition from legacy tools to unified tools without breaking changes.
"""

import functools
import warnings
from collections.abc import Callable
from typing import Any
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def deprecated_tool(
    migration_message: str,
    unified_action: str | None = None,
    removal_timeline: str = "30 days"
) -> Callable[[F], F]:
    """
    Decorator to mark tools as deprecated with migration guidance.
    
    Provides clear warnings and migration instructions while maintaining
    full backward compatibility during the transition period.
    
    Args:
        migration_message: Clear guidance on how to migrate to unified tools
        unified_action: The equivalent unified action (e.g., "email.send")
        removal_timeline: When the legacy tool will be removed
        
    Returns:
        Decorated function with deprecation warnings
        
    Example:
        @deprecated_tool(
            "Use microsoft_operations with action='email.send'",
            unified_action="email.send",
            removal_timeline="30 days"
        )
        def send_email(...):
            # Legacy implementation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function name, handling FastMCP FunctionTool objects
            func_name = getattr(func, "__name__", getattr(func, "name", "unknown_function"))

            # Create comprehensive deprecation warning
            warning_message = _create_deprecation_warning(
                func_name,
                migration_message,
                unified_action,
                removal_timeline
            )

            # Issue deprecation warning (appears in logs but doesn't break execution)
            warnings.warn(
                warning_message,
                DeprecationWarning,
                stacklevel=2
            )

            # Execute original function (zero breaking changes)
            # Handle FastMCP FunctionTool objects
            if hasattr(func, "fn"):
                return func.fn(*args, **kwargs)
            return func(*args, **kwargs)

        # Mark function as deprecated for introspection
        wrapper._deprecated = True  # type: ignore
        wrapper._migration_message = migration_message  # type: ignore
        wrapper._unified_action = unified_action  # type: ignore
        wrapper._removal_timeline = removal_timeline  # type: ignore

        return wrapper  # type: ignore
    return decorator


def _create_deprecation_warning(
    tool_name: str,
    migration_message: str,
    unified_action: str | None,
    removal_timeline: str
) -> str:
    """
    Create comprehensive deprecation warning with migration guidance.
    
    Args:
        tool_name: Name of the deprecated tool
        migration_message: Migration guidance message
        unified_action: Equivalent unified action
        removal_timeline: Timeline for removal
        
    Returns:
        Formatted deprecation warning message
    """
    warning_parts = [
        f"DEPRECATION WARNING: '{tool_name}' is deprecated and will be removed in {removal_timeline}.",
        "",
        f"MIGRATION GUIDANCE: {migration_message}",
    ]

    if unified_action:
        warning_parts.extend([
            "",
            f"UNIFIED EQUIVALENT: Use microsoft_operations(action='{unified_action}', ...)",
            "",
            "EXAMPLE MIGRATION:",
            f"  OLD: {tool_name}(account_id, ...)",
            f"  NEW: microsoft_operations(account_id, action='{unified_action}', data={{...}})",
        ])

    warning_parts.extend([
        "",
        "For complete migration guide, use get_help(topic='migration') or visit:",
        "https://github.com/ossieirondi/Projects/local-mcps/microsoft-mcp/docs/stories/story-1.7-migration-deprecation.md"
    ])

    return "\n".join(warning_parts)


def get_deprecation_info(func: Callable) -> dict[str, Any] | None:
    """
    Get deprecation information for a function.
    
    Args:
        func: Function to check for deprecation info
        
    Returns:
        Deprecation information dict or None if not deprecated
    """
    if not hasattr(func, "_deprecated"):
        return None

    return {
        "deprecated": True,
        "migration_message": getattr(func, "_migration_message", ""),
        "unified_action": getattr(func, "_unified_action", None),
        "removal_timeline": getattr(func, "_removal_timeline", "Unknown")
    }


def list_deprecated_tools() -> list[dict[str, Any]]:
    """
    List all deprecated tools and their migration information.
    
    This is used by the help system to provide migration guidance.
    
    Returns:
        List of deprecated tool information
    """
    # This would be populated by scanning all tools at runtime
    # For now, return structure that can be extended
    return []


class MigrationHelper:
    """
    Helper class for managing migration-related operations.
    
    Provides utilities for migration guidance, parameter mapping,
    and backward compatibility validation.
    """

    @staticmethod
    def get_migration_examples() -> dict[str, dict[str, str]]:
        """
        Get migration examples for common legacy tool patterns.
        
        Returns:
            Dictionary mapping legacy patterns to unified equivalents
        """
        return {
            "email_operations": {
                "send_email": "microsoft_operations(action='email.send', data={'to': '...', 'subject': '...', 'body': '...'})",
                "list_emails": "microsoft_operations(action='email.list', data={'folder': 'inbox', 'limit': 10})",
                "reply_to_email": "microsoft_operations(action='email.reply', data={'email_id': '...', 'body': '...'})",
                "delete_email": "microsoft_operations(action='email.delete', data={'email_id': '...'})"
            },
            "calendar_operations": {
                "list_calendar_events": "microsoft_operations(action='calendar.list', data={'start_date': '...', 'end_date': '...'})",
                "create_calendar_event": "microsoft_operations(action='calendar.create', data={'subject': '...', 'start_datetime': '...'})"
            },
            "file_operations": {
                "list_files": "microsoft_operations(action='file.list', data={'folder_path': '/Documents'})",
                "upload_file": "microsoft_operations(action='file.upload', data={'local_path': '...', 'onedrive_path': '...'})"
            },
            "contact_operations": {
                "list_contacts": "microsoft_operations(action='contact.list', data={'limit': 20})",
                "create_contact": "microsoft_operations(action='contact.create', data={'first_name': '...', 'last_name': '...'})"
            }
        }

    @staticmethod
    def validate_migration_compatibility(legacy_args: dict, unified_action: str) -> dict[str, Any]:
        """
        Validate that legacy arguments can be successfully mapped to unified action.
        
        Args:
            legacy_args: Legacy function arguments
            unified_action: Target unified action
            
        Returns:
            Validation result with success status and mapped parameters
        """
        # This would contain the actual validation logic
        # For now, return success structure
        return {
            "compatible": True,
            "mapped_parameters": legacy_args,
            "warnings": [],
            "required_changes": []
        }
