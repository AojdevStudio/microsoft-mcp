"""
Migration utilities for Microsoft MCP Story 1.7: Migration and Deprecation Layer

This module provides parameter mapping and transformation utilities to enable
seamless routing from legacy tools to unified tools.
"""

from typing import Any


class ParameterMapper:
    """
    Maps legacy tool parameters to unified tool format.
    
    Handles parameter transformation, validation, and provides
    backward compatibility for all legacy tool patterns.
    """

    def __init__(self):
        """Initialize parameter mapper with transformation rules."""
        self._email_mappings = self._init_email_mappings()
        self._calendar_mappings = self._init_calendar_mappings()
        self._file_mappings = self._init_file_mappings()
        self._contact_mappings = self._init_contact_mappings()

    def map_email_parameters(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Map legacy email tool parameters to unified format.
        
        Args:
            tool_name: Name of the legacy email tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Mapped parameters for microsoft_operations
        """
        if tool_name not in self._email_mappings:
            raise ValueError(f"Unknown email tool: {tool_name}")

        mapping = self._email_mappings[tool_name]
        return self._apply_mapping(mapping, kwargs)

    def map_calendar_parameters(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Map legacy calendar tool parameters to unified format.
        
        Args:
            tool_name: Name of the legacy calendar tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Mapped parameters for microsoft_operations
        """
        if tool_name not in self._calendar_mappings:
            raise ValueError(f"Unknown calendar tool: {tool_name}")

        mapping = self._calendar_mappings[tool_name]
        return self._apply_mapping(mapping, kwargs)

    def map_file_parameters(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Map legacy file tool parameters to unified format.
        
        Args:
            tool_name: Name of the legacy file tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Mapped parameters for microsoft_operations
        """
        if tool_name not in self._file_mappings:
            raise ValueError(f"Unknown file tool: {tool_name}")

        mapping = self._file_mappings[tool_name]
        return self._apply_mapping(mapping, kwargs)

    def map_contact_parameters(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Map legacy contact tool parameters to unified format.
        
        Args:
            tool_name: Name of the legacy contact tool
            **kwargs: Legacy tool parameters
            
        Returns:
            Mapped parameters for microsoft_operations
        """
        if tool_name not in self._contact_mappings:
            raise ValueError(f"Unknown contact tool: {tool_name}")

        mapping = self._contact_mappings[tool_name]
        return self._apply_mapping(mapping, kwargs)

    def _init_email_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize email parameter mappings."""
        return {
            "list_emails": {
                "action": "email.list",
                "parameter_map": {
                    "folder_name": "folder",
                    "limit": "limit",
                    "include_body": "include_body",
                    "search_query": "search_query",
                    "skip": "skip"
                }
            },
            "send_email": {
                "action": "email.send",
                "parameter_map": {
                    "to": "to",
                    "subject": "subject",
                    "body": "body",
                    "cc": "cc",
                    "bcc": "bcc",
                    "attachments": "attachments"
                }
            },
            "create_email_draft": {
                "action": "email.draft",
                "parameter_map": {
                    "to": "to",
                    "subject": "subject",
                    "body": "body",
                    "cc": "cc",
                    "bcc": "bcc",
                    "attachments": "attachments"
                }
            },
            "reply_to_email": {
                "action": "email.reply",
                "parameter_map": {
                    "email_id": "email_id",
                    "body": "body",
                    "reply_all": "reply_all",
                    "attachments": "attachments"
                }
            },
            "forward_email": {
                "action": "email.forward",
                "parameter_map": {
                    "email_id": "email_id",
                    "to": "to",
                    "comment": "comment"
                }
            },
            "delete_email": {
                "action": "email.delete",
                "parameter_map": {
                    "email_id": "email_id",
                    "permanent": "permanent"
                }
            },
            "mark_email_as_read": {
                "action": "email.mark",
                "parameter_map": {
                    "email_id": "email_id",
                    "is_read": "is_read"
                }
            },
            "move_email": {
                "action": "email.move",
                "parameter_map": {
                    "email_id": "email_id",
                    "destination_folder": "destination_folder"
                }
            },
            "search_emails": {
                "action": "email.search",
                "parameter_map": {
                    "query": "query",
                    "folder": "folder",
                    "limit": "limit",
                    "has_attachments": "has_attachments"
                }
            },
            "get_email": {
                "action": "email.get",
                "parameter_map": {
                    "email_id": "email_id"
                }
            },
            # Professional email templates
            "send_practice_report": {
                "action": "email.send",
                "template": "practice_report",
                "parameter_map": {
                    "to": "to",
                    "subject": "subject",
                    "location": "location",
                    "financial_data": "financial_data",
                    "provider_data": "provider_data",
                    "period": "period",
                    "alerts": "alerts",
                    "recommendations": "recommendations",
                    "cc": "cc",
                    "bcc": "bcc"
                }
            },
            "send_executive_summary": {
                "action": "email.send",
                "template": "executive_summary",
                "parameter_map": {
                    "to": "to",
                    "locations_data": "locations_data",
                    "period": "period",
                    "subject": "subject",
                    "key_insights": "key_insights",
                    "cc": "cc",
                    "bcc": "bcc"
                }
            },
            "send_provider_update": {
                "action": "email.send",
                "template": "provider_update",
                "parameter_map": {
                    "to": "to",
                    "provider_name": "provider_name",
                    "performance_data": "performance_data",
                    "period": "period",
                    "highlights": "highlights",
                    "recommendations": "recommendations",
                    "subject": "subject",
                    "cc": "cc",
                    "bcc": "bcc"
                }
            },
            "send_alert_notification": {
                "action": "email.send",
                "template": "alert_notification",
                "parameter_map": {
                    "to": "to",
                    "alert_type": "alert_type",
                    "title": "title",
                    "message": "message",
                    "urgency": "urgency",
                    "impact": "impact",
                    "recommended_actions": "recommended_actions",
                    "subject": "subject",
                    "cc": "cc",
                    "bcc": "bcc"
                }
            }
        }

    def _init_calendar_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize calendar parameter mappings."""
        return {
            "list_calendar_events": {
                "action": "calendar.list",
                "parameter_map": {
                    "start_date": "start_date",
                    "end_date": "end_date",
                    "limit": "limit",
                    "calendar_id": "calendar_id"
                }
            },
            "create_calendar_event": {
                "action": "calendar.create",
                "parameter_map": {
                    "subject": "subject",
                    "start_datetime": "start_datetime",
                    "end_datetime": "end_datetime",
                    "attendees": "attendees",
                    "location": "location",
                    "body": "body",
                    "is_online_meeting": "is_online_meeting",
                    "calendar_id": "calendar_id"
                }
            },
            "update_calendar_event": {
                "action": "calendar.update",
                "parameter_map": {
                    "event_id": "event_id",
                    "subject": "subject",
                    "start_datetime": "start_datetime",
                    "end_datetime": "end_datetime",
                    "location": "location",
                    "body": "body"
                }
            },
            "delete_calendar_event": {
                "action": "calendar.delete",
                "parameter_map": {
                    "event_id": "event_id",
                    "send_cancellation": "send_cancellation"
                }
            },
            "send_calendar_invite": {
                "action": "calendar.invite",
                "parameter_map": {
                    "subject": "subject",
                    "start_datetime": "start_datetime",
                    "end_datetime": "end_datetime",
                    "attendees": "attendees",
                    "location": "location",
                    "body": "body",
                    "send_invitation": "send_invitation"
                }
            },
            "search_calendar_events": {
                "action": "calendar.search",
                "parameter_map": {
                    "query": "query",
                    "start_date": "start_date",
                    "end_date": "end_date"
                }
            }
        }

    def _init_file_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize file parameter mappings."""
        return {
            "list_files": {
                "action": "file.list",
                "parameter_map": {
                    "folder_path": "folder_path",
                    "search_query": "search_query",
                    "limit": "limit"
                }
            },
            "upload_file": {
                "action": "file.upload",
                "parameter_map": {
                    "local_path": "local_path",
                    "onedrive_path": "onedrive_path"
                }
            },
            "download_file": {
                "action": "file.download",
                "parameter_map": {
                    "file_path": "file_path",
                    "save_path": "save_path"
                }
            },
            "delete_file": {
                "action": "file.delete",
                "parameter_map": {
                    "file_path": "file_path"
                }
            },
            "share_file": {
                "action": "file.share",
                "parameter_map": {
                    "file_path": "file_path",
                    "email": "email",
                    "permission": "permission",
                    "expiration_days": "expiration_days"
                }
            },
            "search_files": {
                "action": "file.search",
                "parameter_map": {
                    "query": "query",
                    "file_type": "file_type",
                    "limit": "limit"
                }
            },
            "get_file": {
                "action": "file.get",
                "parameter_map": {
                    "file_path": "file_path",
                    "include_metadata": "include_metadata"
                }
            }
        }

    def _init_contact_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize contact parameter mappings."""
        return {
            "list_contacts": {
                "action": "contact.list",
                "parameter_map": {
                    "search_query": "search_query",
                    "limit": "limit"
                }
            },
            "create_contact": {
                "action": "contact.create",
                "parameter_map": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "email": "email",
                    "mobile_phone": "mobile_phone",
                    "company": "company",
                    "job_title": "job_title"
                }
            },
            "update_contact": {
                "action": "contact.update",
                "parameter_map": {
                    "contact_id": "contact_id",
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "email": "email",
                    "mobile_phone": "mobile_phone",
                    "company": "company",
                    "job_title": "job_title"
                }
            },
            "delete_contact": {
                "action": "contact.delete",
                "parameter_map": {
                    "contact_id": "contact_id"
                }
            },
            "search_contacts": {
                "action": "contact.search",
                "parameter_map": {
                    "query": "query",
                    "limit": "limit"
                }
            },
            "get_contact": {
                "action": "contact.get",
                "parameter_map": {
                    "contact_id": "contact_id"
                }
            },
            "search_people": {
                "action": "contact.list",
                "parameter_map": {
                    "query": "search_query",
                    "limit": "limit"
                }
            },
            "export_contacts": {
                "action": "contact.list",
                "parameter_map": {
                    "format": "format",
                    "save_path": "save_path"
                }
            }
        }

    def _apply_mapping(self, mapping: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Apply parameter mapping transformation.
        
        Args:
            mapping: Mapping configuration
            kwargs: Original parameters
            
        Returns:
            Transformed parameters for unified tool
        """
        # Extract account_id (always first parameter)
        account_id = kwargs.pop("account_id", None)
        if not account_id:
            raise ValueError("account_id is required for all operations")

        # Build unified parameters
        result = {
            "account_id": account_id,
            "action": mapping["action"],
            "data": {},
            "options": {}
        }

        # Add template if specified
        if "template" in mapping:
            result["template"] = mapping["template"]

        # Map parameters according to mapping rules
        parameter_map = mapping.get("parameter_map", {})
        for legacy_param, unified_param in parameter_map.items():
            if legacy_param in kwargs:
                result["data"][unified_param] = kwargs[legacy_param]

        # Handle any unmapped parameters as options
        mapped_params = set(parameter_map.keys()) | {"account_id"}
        for param, value in kwargs.items():
            if param not in mapped_params:
                result["options"][param] = value

        return result


class MigrationValidator:
    """
    Validates parameter mappings and ensures backward compatibility.
    """

    def __init__(self):
        """Initialize migration validator."""
        self.mapper = ParameterMapper()

    def validate_email_migration(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Validate email tool migration.
        
        Args:
            tool_name: Legacy email tool name
            **kwargs: Legacy parameters
            
        Returns:
            Validation result
        """
        try:
            mapped = self.mapper.map_email_parameters(tool_name, **kwargs)
            return {
                "valid": True,
                "mapped_parameters": mapped,
                "warnings": [],
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "mapped_parameters": {},
                "warnings": [],
                "errors": [str(e)]
            }

    def validate_calendar_migration(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Validate calendar tool migration.
        
        Args:
            tool_name: Legacy calendar tool name
            **kwargs: Legacy parameters
            
        Returns:
            Validation result
        """
        try:
            mapped = self.mapper.map_calendar_parameters(tool_name, **kwargs)
            return {
                "valid": True,
                "mapped_parameters": mapped,
                "warnings": [],
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "mapped_parameters": {},
                "warnings": [],
                "errors": [str(e)]
            }

    def validate_file_migration(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Validate file tool migration.
        
        Args:
            tool_name: Legacy file tool name
            **kwargs: Legacy parameters
            
        Returns:
            Validation result
        """
        try:
            mapped = self.mapper.map_file_parameters(tool_name, **kwargs)
            return {
                "valid": True,
                "mapped_parameters": mapped,
                "warnings": [],
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "mapped_parameters": {},
                "warnings": [],
                "errors": [str(e)]
            }

    def validate_contact_migration(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Validate contact tool migration.
        
        Args:
            tool_name: Legacy contact tool name
            **kwargs: Legacy parameters
            
        Returns:
            Validation result
        """
        try:
            mapped = self.mapper.map_contact_parameters(tool_name, **kwargs)
            return {
                "valid": True,
                "mapped_parameters": mapped,
                "warnings": [],
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "mapped_parameters": {},
                "warnings": [],
                "errors": [str(e)]
            }


# Global instances for use in deprecation wrappers
parameter_mapper = ParameterMapper()
migration_validator = MigrationValidator()
