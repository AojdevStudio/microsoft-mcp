"""Calendar operations tool for Microsoft Graph API integration.

Focused tool providing 8 calendar actions through action-based interface:
- list, create, update, delete, search, availability, invite, get

Part of nuclear simplification architecture replacing 63k token unified tool.
"""

from typing import Any, Literal

from . import graph


def format_calendar_event(event: dict[str, Any]) -> dict[str, Any]:
    """Format calendar event data for output"""
    return {
        "id": event.get("id"),
        "subject": event.get("subject"),
        "start": event.get("start", {}),
        "end": event.get("end", {}),
        "location": event.get("location", {}).get("displayName"),
        "attendees": [
            {
                "name": att.get("emailAddress", {}).get("name"),
                "email": att.get("emailAddress", {}).get("address"),
                "response": att.get("status", {}).get("response")
            }
            for att in event.get("attendees", [])
        ],
        "organizer": event.get("organizer", {}).get("emailAddress", {}),
        "body": event.get("body", {}).get("content"),
        "is_online_meeting": event.get("isOnlineMeeting", False),
        "web_link": event.get("webLink"),
        "created_datetime": event.get("createdDateTime"),
        "modified_datetime": event.get("lastModifiedDateTime"),
    }


def calendar_operations(
    account_id: str,
    action: Literal["list", "create", "update", "delete", "search", "availability", "invite", "get"],
    # List action parameters
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    calendar_id: str | None = None,
    # Create/Update action parameters
    subject: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    attendees: list[str] | None = None,
    location: str | None = None,
    body: str | None = None,
    is_online_meeting: bool = False,
    # Update/Delete/Get action parameters
    event_id: str | None = None,
    # Delete action parameters
    send_cancellation: bool = True,
    # Search action parameters
    query: str | None = None,
    # Availability action parameters
    duration_minutes: int = 30
) -> dict[str, Any]:
    """Calendar operations for Microsoft Outlook
    
    Actions:
    - list: Get calendar events (start_date, end_date, limit, calendar_id)
    - create: Create calendar event (subject, start_datetime, end_datetime, attendees, location, body, is_online_meeting)
    - update: Update calendar event (event_id, subject, start_datetime, end_datetime, location, body)
    - delete: Delete calendar event (event_id, send_cancellation)
    - search: Search calendar events (query, start_date, end_date)
    - availability: Find available time slots (start_date, end_date, duration_minutes)
    - invite: Send calendar invitation (subject, start_datetime, end_datetime, attendees, location, body)
    - get: Get specific calendar event (event_id)
    """
    try:
        if action == "list":
            return _list_calendar_events(account_id, start_date, end_date, limit, calendar_id)
        if action == "create":
            return _create_calendar_event(account_id, subject, start_datetime, end_datetime, attendees, location, body, is_online_meeting)
        if action == "update":
            return _update_calendar_event(account_id, event_id, subject, start_datetime, end_datetime, location, body)
        if action == "delete":
            return _delete_calendar_event(account_id, event_id, send_cancellation)
        if action == "search":
            return _search_calendar_events(account_id, query, start_date, end_date)
        if action == "availability":
            return _get_calendar_availability(account_id, start_date, end_date, duration_minutes)
        if action == "invite":
            return _send_calendar_invite(account_id, subject, start_datetime, end_datetime, attendees, location, body)
        if action == "get":
            return _get_calendar_event(account_id, event_id)
        return {"status": "error", "message": f"Unknown calendar action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _list_calendar_events(
    account_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    calendar_id: str | None = None
) -> dict[str, Any]:
    """List calendar events for a Microsoft account"""
    import datetime as dt

    if not start_date:
        start_date = dt.datetime.now().date().isoformat()

    if not end_date:
        end_dt = dt.datetime.fromisoformat(start_date) + dt.timedelta(days=30)
        end_date = end_dt.date().isoformat()

    endpoint = "/me/events" if not calendar_id else f"/me/calendars/{calendar_id}/events"

    params = {
        "$filter": f"start/dateTime ge '{start_date}T00:00:00' and end/dateTime le '{end_date}T23:59:59'",
        "$orderby": "start/dateTime",
        "$top": min(limit, 50),
        "$select": "id,subject,start,end,location,attendees,organizer,body,isOnlineMeeting,webLink,createdDateTime,lastModifiedDateTime",
    }

    events = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))
    return {
        "status": "success",
        "events": [format_calendar_event(event) for event in events],
        "count": len(events)
    }


def _create_calendar_event(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str] | None = None,
    location: str | None = None,
    body: str | None = None,
    is_online_meeting: bool = False,
    calendar_id: str | None = None
) -> dict[str, Any]:
    """Create a new calendar event"""
    event = {
        "subject": subject,
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
    }

    if location:
        event["location"] = {"displayName": location}

    if body:
        event["body"] = {"contentType": "text", "content": body}

    if attendees:
        event["attendees"] = [
            {"emailAddress": {"address": email}, "type": "required"}
            for email in attendees
        ]

    if is_online_meeting:
        event["isOnlineMeeting"] = True

    endpoint = "/me/events" if not calendar_id else f"/me/calendars/{calendar_id}/events"
    response = graph.request("POST", endpoint, account_id, json=event)

    return {
        "status": "success",
        "event": format_calendar_event(response),
        "message": "Calendar event created successfully"
    }


def _update_calendar_event(
    account_id: str,
    event_id: str,
    subject: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    location: str | None = None,
    body: str | None = None
) -> dict[str, Any]:
    """Update an existing calendar event"""
    update_data = {}

    if subject is not None:
        update_data["subject"] = subject
    if start_datetime is not None:
        update_data["start"] = {"dateTime": start_datetime, "timeZone": "UTC"}
    if end_datetime is not None:
        update_data["end"] = {"dateTime": end_datetime, "timeZone": "UTC"}
    if location is not None:
        update_data["location"] = {"displayName": location}
    if body is not None:
        update_data["body"] = {"contentType": "text", "content": body}

    if not update_data:
        return {"status": "error", "message": "No update fields provided"}

    graph.request("PATCH", f"/me/events/{event_id}", account_id, json=update_data)
    return {"status": "success", "message": "Calendar event updated successfully"}


def _delete_calendar_event(
    account_id: str,
    event_id: str,
    send_cancellation: bool = True
) -> dict[str, Any]:
    """Delete a calendar event"""
    if send_cancellation:
        # Send cancellation notice
        cancel_data = {
            "comment": "Event has been cancelled"
        }
        graph.request("POST", f"/me/events/{event_id}/cancel", account_id, json=cancel_data)
    else:
        # Delete without notice
        graph.request("DELETE", f"/me/events/{event_id}", account_id)

    return {"status": "success", "message": "Calendar event deleted successfully"}


def _search_calendar_events(
    account_id: str,
    query: str,
    start_date: str | None = None,
    end_date: str | None = None
) -> dict[str, Any]:
    """Search calendar events by keyword"""
    endpoint = "/me/events"

    params = {
        "$search": f'"{query}"',
        "$orderby": "start/dateTime",
        "$select": "id,subject,start,end,location,attendees,organizer,bodyPreview,isOnlineMeeting",
    }

    if start_date and end_date:
        params["$filter"] = f"start/dateTime ge '{start_date}T00:00:00' and end/dateTime le '{end_date}T23:59:59'"

    events = list(graph.paginate(endpoint, account_id, params=params, max_items=50))
    return {
        "status": "success",
        "events": [format_calendar_event(event) for event in events],
        "count": len(events)
    }


def _get_calendar_availability(
    account_id: str,
    start_date: str,
    end_date: str,
    duration_minutes: int = 30
) -> dict[str, Any]:
    """Find available time slots in calendar"""
    # Get busy times from calendar
    free_busy_data = {
        "schedules": [f"{account_id}"],
        "startTime": {"dateTime": f"{start_date}T09:00:00", "timeZone": "UTC"},
        "endTime": {"dateTime": f"{end_date}T17:00:00", "timeZone": "UTC"},
        "availabilityViewInterval": duration_minutes
    }

    response = graph.request("POST", "/me/calendar/getSchedule", account_id, json=free_busy_data)

    # Parse busy times and find free slots
    free_slots = []
    if response and "value" in response and len(response["value"]) > 0:
        busy_times = response["value"][0].get("freeBusyViewData", [])

        # Simple availability parsing - in production would need more sophisticated logic
        import datetime as dt
        start_dt = dt.datetime.fromisoformat(start_date + "T09:00:00")
        end_dt = dt.datetime.fromisoformat(end_date + "T17:00:00")

        current_time = start_dt
        while current_time < end_dt:
            slot_end = current_time + dt.timedelta(minutes=duration_minutes)
            if slot_end <= end_dt:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": slot_end.isoformat(),
                    "duration_minutes": duration_minutes
                })
            current_time += dt.timedelta(minutes=duration_minutes)

    return {
        "status": "success",
        "available_slots": free_slots[:20],  # Limit to 20 slots
        "count": len(free_slots[:20])
    }


def _send_calendar_invite(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str],
    location: str | None = None,
    body: str | None = None
) -> dict[str, Any]:
    """Create and send a calendar invitation"""
    event = {
        "subject": subject,
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
        "attendees": [
            {"emailAddress": {"address": email}, "type": "required"}
            for email in attendees
        ],
    }

    if location:
        event["location"] = {"displayName": location}

    if body:
        event["body"] = {"contentType": "text", "content": body}

    response = graph.request("POST", "/me/events", account_id, json=event)

    return {
        "status": "success",
        "event": format_calendar_event(response),
        "message": "Calendar invitation sent successfully"
    }


def _get_calendar_event(account_id: str, event_id: str) -> dict[str, Any]:
    """Get a specific calendar event by ID"""
    params = {
        "$select": "id,subject,start,end,location,attendees,organizer,body,isOnlineMeeting,webLink,createdDateTime,lastModifiedDateTime"
    }

    event = graph.request("GET", f"/me/events/{event_id}", account_id, params=params)
    return {
        "status": "success",
        "event": format_calendar_event(event)
    }
