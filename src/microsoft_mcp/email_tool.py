"""Email operations tool for Microsoft Graph API integration.

Focused tool providing 10 email actions through action-based interface:
- list, send, reply, draft, delete, forward, move, mark, search, get

Part of nuclear simplification architecture replacing 63k token unified tool.
"""

import base64
import pathlib as pl
from typing import Any, Literal

from fastmcp import FastMCP

from . import graph
from .email_framework.utils import style_email_content

# Email folder mappings
FOLDERS = {
    "inbox": "inbox",
    "sent": "sentitems",
    "drafts": "drafts",
    "deleted": "deleteditems",
    "archive": "archive",
    "junk": "junkemail",
    "outbox": "outbox"
}


def format_email(email: dict[str, Any], include_body: bool = True) -> dict[str, Any]:
    """Format email data for output"""
    result = {
        "id": email.get("id"),
        "subject": email.get("subject"),
        "from": email.get("from", {}).get("emailAddress", {}).get("address"),
        "to": [r.get("emailAddress", {}).get("address") for r in email.get("toRecipients", [])],
        "cc": [r.get("emailAddress", {}).get("address") for r in email.get("ccRecipients", [])],
        "received_datetime": email.get("receivedDateTime"),
        "has_attachments": email.get("hasAttachments", False),
        "importance": email.get("importance"),
        "is_read": email.get("isRead", False),
    }

    if include_body and "body" in email:
        result["body"] = email["body"].get("content", "")
        result["body_preview"] = email.get("bodyPreview", "")

    return result


def parse_email_input(email_input: str | list[str]) -> list[str]:
    """Parse email input that might be a JSON string or list"""
    import json
    if isinstance(email_input, str):
        try:
            return json.loads(email_input)
        except json.JSONDecodeError:
            return [email_input]
    return email_input


def email_operations(
    account_id: str,
    action: Literal["list", "send", "reply", "draft", "delete", "forward", "move", "mark", "search", "get"],
    # List action parameters
    folder_name: str | None = None,
    limit: int = 50,
    include_body: bool = True,
    search_query: str | None = None,
    skip: int = 0,
    # Send/Draft action parameters
    to: str | None = None,
    subject: str | None = None,
    body: str | None = None,
    cc: str | list[str] | None = None,
    bcc: str | list[str] | None = None,
    attachments: str | list[str] | None = None,
    # Reply action parameters
    email_id: str | None = None,
    reply_all: bool = False,
    # Delete action parameters
    permanent: bool = False,
    # Forward action parameters
    comment: str | None = None,
    # Move action parameters
    destination_folder: str | None = None,
    # Mark action parameters
    is_read: bool = True,
    # Search action parameters
    query: str | None = None,
    folder: str | None = None,
    has_attachments: bool | None = None
) -> dict[str, Any]:
    """Email operations for Microsoft Outlook
    
    Actions:
    - list: Get emails from folder (folder_name, limit, include_body, search_query, skip)
    - send: Send email (to, subject, body, cc, bcc, attachments)
    - reply: Reply to email (email_id, body, reply_all)
    - draft: Create draft (to, subject, body, cc, bcc, attachments)
    - delete: Delete email (email_id, permanent)
    - forward: Forward email (email_id, to, comment)
    - move: Move email (email_id, destination_folder)
    - mark: Mark email as read/unread (email_id, is_read)
    - search: Search emails (query, folder, limit, has_attachments)
    - get: Get specific email (email_id)
    """
    try:
        if action == "list":
            return _list_emails(account_id, folder_name, limit, include_body, search_query, skip)
        if action == "send":
            return _send_email(account_id, to, subject, body, cc, bcc, attachments)
        if action == "reply":
            return _reply_to_email(account_id, email_id, body, reply_all)
        if action == "draft":
            return _create_draft(account_id, to, subject, body, cc, bcc, attachments)
        if action == "delete":
            return _delete_email(account_id, email_id, permanent)
        if action == "forward":
            return _forward_email(account_id, email_id, to, comment)
        if action == "move":
            return _move_email(account_id, email_id, destination_folder)
        if action == "mark":
            return _mark_email(account_id, email_id, is_read)
        if action == "search":
            return _search_emails(account_id, query, folder, limit, has_attachments)
        if action == "get":
            return _get_email(account_id, email_id)
        return {"status": "error", "message": f"Unknown email action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _list_emails(
    account_id: str,
    folder_name: str | None = None,
    limit: int = 10,
    include_body: bool = True,
    search_query: str | None = None,
    skip: int = 0
) -> dict[str, Any]:
    """List emails from a Microsoft account"""
    folder = FOLDERS.get(folder_name.lower() if folder_name else "inbox", "inbox")
    endpoint = f"/me/mailFolders/{folder}/messages"

    params = {
        "$top": min(limit, 50),
        "$skip": skip,
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments,importance,isRead",
    }

    if include_body:
        params["$select"] += ",body,bodyPreview"

    if search_query:
        params["$search"] = f'"{search_query}"'

    messages = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))
    return {
        "status": "success",
        "emails": [format_email(msg, include_body) for msg in messages],
        "count": len(messages)
    }


def _send_email(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None
) -> dict[str, Any]:
    """Send an email immediately"""
    # Parse cc and bcc if they're JSON strings
    if cc is not None:
        cc = parse_email_input(cc) if not isinstance(cc, list) else cc
    if bcc is not None:
        bcc = parse_email_input(bcc) if not isinstance(bcc, list) else bcc

    to_list = [to]

    # Style email content professionally
    content = style_email_content(body, subject)

    message = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": content},
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list],
    }

    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]
    if bcc:
        message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]

    # Handle attachments
    if attachments:
        _add_attachments_to_message(message, attachments, account_id)

    graph.request("POST", "/me/sendMail", account_id, json={"message": message})
    return {"status": "success", "message": "Email sent successfully"}


def _create_draft(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None
) -> dict[str, Any]:
    """Create an email draft"""
    # Parse cc and bcc if they're JSON strings
    if cc is not None:
        cc = parse_email_input(cc) if not isinstance(cc, list) else cc
    if bcc is not None:
        bcc = parse_email_input(bcc) if not isinstance(bcc, list) else bcc

    to_list = [to]

    # Style email content professionally
    content = style_email_content(body, subject)

    message = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": content},
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list],
    }

    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]
    if bcc:
        message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]

    response = graph.request("POST", "/me/messages", account_id, json=message)
    message_id = response["id"]

    # Handle attachments for draft
    if attachments:
        _add_attachments_to_draft(message_id, attachments, account_id)

    return {"status": "success", "id": message_id, "message": "Draft created successfully"}


def _reply_to_email(
    account_id: str,
    email_id: str,
    body: str,
    reply_all: bool = False
) -> dict[str, Any]:
    """Reply to an email"""
    content = style_email_content(body, "Reply")

    reply_data = {
        "message": {
            "body": {"contentType": "HTML", "content": content}
        }
    }

    action = "replyAll" if reply_all else "reply"
    graph.request("POST", f"/me/messages/{email_id}/{action}", account_id, json=reply_data)

    return {"status": "success", "message": f"Reply sent successfully ({'reply all' if reply_all else 'reply'})"}


def _delete_email(account_id: str, email_id: str, permanent: bool = False) -> dict[str, Any]:
    """Delete an email"""
    if permanent:
        graph.request("DELETE", f"/me/messages/{email_id}", account_id)
        return {"status": "success", "message": "Email permanently deleted"}
    # Move to deleted items
    graph.request("POST", f"/me/messages/{email_id}/move", account_id,
                 json={"destinationId": "deleteditems"})
    return {"status": "success", "message": "Email moved to deleted items"}


def _forward_email(account_id: str, email_id: str, to: str, comment: str | None = None) -> dict[str, Any]:
    """Forward an email"""
    to_list = parse_email_input(to) if isinstance(to, str) else to

    forward_data = {
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list]
    }

    if comment:
        content = style_email_content(comment, "Forward")
        forward_data["message"] = {
            "body": {"contentType": "HTML", "content": content}
        }

    graph.request("POST", f"/me/messages/{email_id}/forward", account_id, json=forward_data)
    return {"status": "success", "message": "Email forwarded successfully"}


def _move_email(account_id: str, email_id: str, destination_folder: str) -> dict[str, Any]:
    """Move an email to a different folder"""
    folder_id = FOLDERS.get(destination_folder.lower(), destination_folder)

    graph.request("POST", f"/me/messages/{email_id}/move", account_id,
                 json={"destinationId": folder_id})

    return {"status": "success", "message": f"Email moved to {destination_folder}"}


def _mark_email(account_id: str, email_id: str, is_read: bool = True) -> dict[str, Any]:
    """Mark an email as read or unread"""
    graph.request("PATCH", f"/me/messages/{email_id}", account_id,
                 json={"isRead": is_read})

    status_text = "read" if is_read else "unread"
    return {"status": "success", "message": f"Email marked as {status_text}"}


def _search_emails(
    account_id: str,
    query: str,
    folder: str | None = None,
    limit: int = 20,
    has_attachments: bool | None = None
) -> dict[str, Any]:
    """Search emails using Microsoft Graph search"""
    endpoint = "/me/messages"

    params = {
        "$search": f'"{query}"',
        "$top": min(limit, 50),
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,toRecipients,receivedDateTime,hasAttachments,bodyPreview",
    }

    if folder:
        folder_id = FOLDERS.get(folder.lower(), folder)
        endpoint = f"/me/mailFolders/{folder_id}/messages"

    if has_attachments is not None:
        params["$filter"] = f"hasAttachments eq {str(has_attachments).lower()}"

    messages = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))
    return {
        "status": "success",
        "emails": [format_email(msg, include_body=False) for msg in messages],
        "count": len(messages)
    }


def _get_email(account_id: str, email_id: str) -> dict[str, Any]:
    """Get a specific email by ID"""
    params = {
        "$select": "id,subject,from,toRecipients,ccRecipients,bccRecipients,receivedDateTime,hasAttachments,importance,isRead,body,bodyPreview,attachments"
    }

    email = graph.request("GET", f"/me/messages/{email_id}", account_id, params=params)
    return {
        "status": "success",
        "email": format_email(email, include_body=True)
    }


def _add_attachments_to_message(message: dict, attachments: str | list[str], account_id: str) -> None:
    """Add attachments to a message for sending"""
    attachment_paths = [attachments] if isinstance(attachments, str) else attachments
    processed_attachments = []

    for file_path in attachment_paths:
        path = pl.Path(file_path).expanduser().resolve()
        content_bytes = path.read_bytes()

        if len(content_bytes) < 3 * 1024 * 1024:  # < 3MB
            processed_attachments.append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": path.name,
                "contentBytes": base64.b64encode(content_bytes).decode("utf-8"),
            })

    if processed_attachments:
        message["attachments"] = processed_attachments


def _add_attachments_to_draft(message_id: str, attachments: str | list[str], account_id: str) -> None:
    """Add attachments to a draft message"""
    attachment_paths = [attachments] if isinstance(attachments, str) else attachments

    for file_path in attachment_paths:
        path = pl.Path(file_path).expanduser().resolve()
        content_bytes = path.read_bytes()

        if len(content_bytes) < 3 * 1024 * 1024:  # < 3MB
            attachment_data = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": path.name,
                "contentBytes": base64.b64encode(content_bytes).decode("utf-8"),
            }
            graph.request("POST", f"/me/messages/{message_id}/attachments", account_id, json=attachment_data)
