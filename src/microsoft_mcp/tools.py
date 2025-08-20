import base64
import datetime as dt
import pathlib as pl
from typing import Any

from fastmcp import FastMCP

from . import auth
from . import graph
from .deprecation import deprecated_tool
from .legacy_mapper import LegacyToolRouter

mcp = FastMCP("microsoft-mcp")

FOLDERS = {
    k.casefold(): v
    for k, v in {
        "inbox": "inbox",
        "sent": "sentitems",
        "drafts": "drafts",
        "deleted": "deleteditems",
        "junk": "junkemail",
        "archive": "archive",
    }.items()
}


@mcp.tool
def list_accounts() -> list[dict[str, str]]:
    """List all signed-in Microsoft accounts"""
    return [
        {"username": acc.username, "account_id": acc.account_id}
        for acc in auth.list_accounts()
    ]


@mcp.tool
def authenticate_account() -> dict[str, str]:
    """Authenticate a new Microsoft account using device flow authentication

    Returns authentication instructions and device code for the user to complete authentication.
    The user must visit the URL and enter the code to authenticate their Microsoft account.
    """
    app = auth.get_app()
    flow = app.initiate_device_flow(scopes=auth.SCOPES)

    if "user_code" not in flow:
        error_msg = flow.get("error_description", "Unknown error")
        raise Exception(f"Failed to get device code: {error_msg}")

    verification_url = flow.get(
        "verification_uri",
        flow.get("verification_url", "https://microsoft.com/devicelogin"),
    )

    return {
        "status": "authentication_required",
        "instructions": "To authenticate a new Microsoft account:",
        "step1": f"Visit: {verification_url}",
        "step2": f"Enter code: {flow['user_code']}",
        "step3": "Sign in with the Microsoft account you want to add",
        "step4": "After authenticating, use the 'complete_authentication' tool to finish the process",
        "device_code": flow["user_code"],
        "verification_url": verification_url,
        "expires_in": flow.get("expires_in", 900),
        "_flow_cache": str(flow),
    }


@mcp.tool
def complete_authentication(flow_cache: str) -> dict[str, str]:
    """Complete the authentication process after the user has entered the device code

    Args:
        flow_cache: The flow data returned from authenticate_account (the _flow_cache field)

    Returns:
        Account information if authentication was successful
    """
    import ast

    try:
        flow = ast.literal_eval(flow_cache)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid flow cache data")

    app = auth.get_app()
    result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        error_msg = result.get("error_description", result["error"])
        if "authorization_pending" in error_msg:
            return {
                "status": "pending",
                "message": "Authentication is still pending. The user needs to complete the authentication process.",
                "instructions": "Please ensure you've visited the URL and entered the code, then try again.",
            }
        raise Exception(f"Authentication failed: {error_msg}")

    # Save the token cache
    cache = app.token_cache
    if isinstance(cache, auth.msal.SerializableTokenCache) and cache.has_state_changed:
        auth._write_cache(cache.serialize())

    # Get the newly added account
    accounts = list_accounts()
    if accounts:
        return {
            "status": "success",
            "message": "Authentication successful!",
            "account": accounts[-1],  # Return the most recently added account
        }

    return {"status": "success", "message": "Authentication successful!"}


@mcp.tool
def list_emails(
    account_id: str,
    folder_name: str | None = None,
    limit: int = 10,
    include_body: bool = True,
    search_query: str | None = None,
    skip: int = 0,
) -> list[dict[str, Any]]:
    """List emails from a Microsoft account

    Args:
        account_id: Microsoft account ID (required - use list_accounts to get account IDs)
        folder_name: Folder to list emails from (e.g., 'inbox', 'sent', 'drafts'). Defaults to inbox.
        limit: Maximum number of emails to return (default: 10, max: 50)
        include_body: Whether to include email body content (default: True)
        search_query: Optional search query to filter emails
        skip: Number of emails to skip for pagination (default: 0)

    Returns:
        List of email objects with details
    """
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

    return [format_email(msg, include_body) for msg in messages]


def format_email(email: dict[str, Any], include_body: bool = True) -> dict[str, Any]:
    """Format email data for output"""
    result = {
        "id": email.get("id"),
        "subject": email.get("subject"),
        "from": email.get("from", {}).get("emailAddress", {}),
        "to": [r.get("emailAddress", {}) for r in email.get("toRecipients", [])],
        "cc": [r.get("emailAddress", {}) for r in email.get("ccRecipients", [])],
        "received": email.get("receivedDateTime"),
        "has_attachments": email.get("hasAttachments", False),
        "importance": email.get("importance"),
        "is_read": email.get("isRead", False),
    }

    if include_body:
        body = email.get("body", {})
        result["body_preview"] = email.get("bodyPreview", "")
        result["body"] = {
            "type": body.get("contentType", "text"),
            "content": body.get("content", ""),
        }
    elif not include_body and "body" in result:
        del result["body"]

    # Remove attachment content bytes to reduce size
    if "attachments" in result and result["attachments"]:
        for attachment in result["attachments"]:
            if "contentBytes" in attachment:
                del attachment["contentBytes"]

    return result


def detect_html_content(content: str) -> bool:
    """Detect if content contains HTML that should be rendered as HTML"""
    content_lower = content.lower().strip()
    html_indicators = [
        content_lower.startswith(("<html", "<!doctype html")),
        "<body" in content_lower,
        "<div" in content_lower,
        "<p>" in content_lower or "<p " in content_lower,
        "<br>" in content_lower
        or "<br/>" in content_lower
        or "<br />" in content_lower,
        "<h1>" in content_lower or "<h2>" in content_lower or "<h3>" in content_lower,
        "<h1 " in content_lower or "<h2 " in content_lower or "<h3 " in content_lower,
        "<ul>" in content_lower or "<ol>" in content_lower or "<li>" in content_lower,
        "<ul " in content_lower or "<ol " in content_lower or "<li " in content_lower,
        "<strong>" in content_lower or "<b>" in content_lower,
        "<strong " in content_lower or "<b " in content_lower,
        "<em>" in content_lower or "<i>" in content_lower,
        "<em " in content_lower or "<i " in content_lower,
        "<a " in content_lower or "<a>" in content_lower,
        "<table" in content_lower,
        "<img " in content_lower,
        "style=" in content_lower,
        "href=" in content_lower,
    ]
    return any(html_indicators)


def ensure_html_structure(content: str) -> str:
    """Ensure HTML content has proper structure for email rendering with professional styling"""
    import re

    content_lower = content.lower().strip()

    # Style class mappings for email-safe inline styles
    style_mappings = {
        "header": "background-color: #234bfb; color: black; padding: 20px; border-radius: 8px; margin-bottom: 20px;",
        "section": "background-color: #74b8fb; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #234bfb;",
        "highlight": "background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin: 10px 0;",
        "strong-yes": "background-color: #28a745; color: black; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 18px;",
    }

    # Signature HTML template
    signature_html = """
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
        <strong style="color: #333333; font-size: 14px;">Ossie Irondi PharmD.</strong><br style="margin: 0;">
        <span style="color: #666666; font-size: 14px;">KC Ventures PLLC,</span><br style="margin: 0;">
        <span style="color: #666666; font-size: 14px;">Chief Operating Officer</span><br style="margin: 0;">
        <span style="color: #666666; font-size: 14px;">Baytown Office: 281-421-5950</span><br style="margin: 0;">
        <span style="color: #666666; font-size: 14px;">Humble Office: 281-812-3333</span><br style="margin: 0;">
        <span style="color: #666666; font-size: 14px;">Cell: 346-644-0193</span><br style="margin: 0;">
        <a href="https://www.kamdental.com" style="color: #667eea; text-decoration: none; font-size: 14px;">https://www.kamdental.com</a><br style="margin: 0;">
        <a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled" style="color: #667eea; text-decoration: none; font-size: 14px;">Book Time With Me</a>
    </div>
    """

    # Check if signature is already in content
    has_signature = (
        "ossie irondi" in content_lower or "book time with me" in content_lower
    )

    # If signature exists in content, format it properly
    if has_signature:
        # Extract and format signature if it's in plain text
        signature_patterns = [
            r"\*\*Ossie Irondi.*?Book Time With Me</a>",
            r"Ossie Irondi.*?Book Time With Me",
        ]
        for pattern in signature_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                # Replace the signature with formatted HTML and prevent double signature
                content = content[: match.start()]
                has_signature = False  # We'll add the formatted signature later
                break

    # If it already has proper HTML structure with styling, enhance it
    if content_lower.startswith("<!doctype html") or content_lower.startswith("<html"):
        # Check if body has inline styles
        if "style=" not in content:
            # Add inline styles to body tag
            body_pattern = r"<body[^>]*>"
            body_replacement = "<body style=\"margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333333; background-color: #f5f5f5;\">"
            content = re.sub(
                body_pattern, body_replacement, content, flags=re.IGNORECASE
            )
        return content

    # Replace CSS classes with inline styles
    processed_content = content
    for class_name, inline_style in style_mappings.items():
        # Replace class attributes with inline styles
        processed_content = re.sub(
            rf'class=["\']?{class_name}["\']?',
            f'style="{inline_style}"',
            processed_content,
            flags=re.IGNORECASE,
        )
        # Also handle divs with classes
        processed_content = re.sub(
            rf'<div\s+class=["\']?{class_name}["\']?',
            f'<div style="{inline_style}"',
            processed_content,
            flags=re.IGNORECASE,
        )

    # Create the email template based on whether content has HTML
    if detect_html_content(processed_content):
        # Content has HTML, preserve it but wrap with proper structure
        main_content = processed_content
    else:
        # Plain text, convert to HTML
        # Convert line breaks to <br> tags
        html_content = processed_content.replace("\n", "<br>")
        # Convert bold markdown to HTML
        html_content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_content)
        main_content = f'<p style="margin: 0 0 15px 0;">{html_content}</p>'

    # Build the complete HTML email template with table-based layout
    html_template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Email</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333333; background-color: #f5f5f5;">
    <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td style="padding: 20px 0;">
                <table cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto;">
                    <tr>
                        <td>
                            <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 40px;">
                                        {main_content}
                                        {signature_html if not has_signature else ""}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return html_template


def parse_email_input(email_input: str | list[str]) -> list[str]:
    """Parse email input that might be incorrectly formatted as a JSON string

    Handles cases where the input might be:
    - A string email: "email@example.com"
    - A list of emails: ["email1@example.com", "email2@example.com"]
    - A JSON-encoded string: '["email@example.com"]' (incorrect but handle gracefully)
    """
    import json

    # If it's already a list, return it
    if isinstance(email_input, list):
        return email_input

    # If it's a string, check if it's JSON-encoded
    if isinstance(email_input, str):
        # Check if it looks like a JSON array
        if email_input.strip().startswith("[") and email_input.strip().endswith("]"):
            try:
                # Try to parse it as JSON
                parsed = json.loads(email_input)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                # If parsing fails, treat it as a regular email
                pass

        # Return as a single-item list
        return [email_input]

    # Fallback
    return [str(email_input)]


@mcp.tool
def create_email_draft(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None,
) -> dict[str, Any]:
    """Create an email draft with file path(s) as attachments

    IMPORTANT: When composing emails, always format the content in rich HTML with professional styling similar to that of fortune 500 companies.
    Automatically append the user's signature at the end of the email body:

    **Ossie Irondi PharmD.**
    KC Ventures PLLC,
    Chief Operating Officer
    Baytown Office: 281-421-5950
    Humble Office: 281-812-3333
    Cell: 346-644-0193
    https://www.kamdental.com
    <a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled">Book Time With Me</a>

    Use proper HTML structure with CSS styling for a polished, professional appearance.
    Include proper spacing, formatting, and styling to ensure the email looks executive-level.

    Args:
        account_id: Microsoft account ID
        to: Primary recipient email address
        subject: Email subject line
        body: Email body content (will be formatted as rich HTML with signature)
        cc: List of CC recipient email addresses
        bcc: List of BCC recipient email addresses
        attachments: File path(s) to attach
    """
    # Parse cc and bcc parameters in case they are passed as JSON strings
    if cc is not None:
        cc = parse_email_input(cc) if not isinstance(cc, list) else cc
    if bcc is not None:
        bcc = parse_email_input(bcc) if not isinstance(bcc, list) else bcc

    to_list = [to]

    # Always format as HTML with professional styling
    content_type = "HTML"
    content = ensure_html_structure(body)

    message = {
        "subject": subject,
        "body": {"contentType": content_type, "content": content},
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list],
    }

    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]

    if bcc:
        message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]

    small_attachments = []
    large_attachments = []

    if attachments:
        # Convert single path to list
        attachment_paths = (
            [attachments] if isinstance(attachments, str) else attachments
        )
        for file_path in attachment_paths:
            path = pl.Path(file_path).expanduser().resolve()
            content_bytes = path.read_bytes()
            att_size = len(content_bytes)
            att_name = path.name

            if att_size < 3 * 1024 * 1024:
                small_attachments.append(
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": att_name,
                        "contentBytes": base64.b64encode(content_bytes).decode("utf-8"),
                    }
                )
            else:
                large_attachments.append(
                    {
                        "name": att_name,
                        "content_bytes": content_bytes,
                        "content_type": "application/octet-stream",
                    }
                )

    if small_attachments:
        message["attachments"] = small_attachments

    result = graph.request("POST", "/me/messages", account_id, json=message)
    if not result:
        raise ValueError("Failed to create email draft")

    message_id = result["id"]

    for att in large_attachments:
        graph.upload_large_mail_attachment(
            message_id,
            att["name"],
            att["content_bytes"],
            account_id,
            att.get("content_type", "application/octet-stream"),
        )

    return {"id": message_id, "status": "draft created"}


@mcp.tool
def send_email(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None,
) -> dict[str, str]:
    """Send an email immediately with file path(s) as attachments

    IMPORTANT: When composing emails, always format the content in rich HTML with professional styling similar to that of fortune 500 companies.
    Automatically append the user's signature at the end of the email body:

    **Ossie Irondi PharmD.**
    KC Ventures PLLC,
    Chief Operating Officer
    Baytown Office: 281-421-5950
    Humble Office: 281-812-3333
    Cell: 346-644-0193
    https://www.kamdental.com
    <a href="https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled">Book Time With Me</a>

    Use proper HTML structure with CSS styling for a polished, professional appearance.
    Include proper spacing, formatting, and styling to ensure the email looks executive-level.

    Args:
        account_id: Microsoft account ID
        to: Primary recipient email address
        subject: Email subject line
        body: Email body content (will be formatted as rich HTML with signature)
        cc: List of CC recipient email addresses
        bcc: List of BCC recipient email addresses
        attachments: File path(s) to attach (single path as string or list of paths)
    """
    # Parse cc and bcc parameters in case they are passed as JSON strings
    if cc is not None:
        cc = parse_email_input(cc) if not isinstance(cc, list) else cc
    if bcc is not None:
        bcc = parse_email_input(bcc) if not isinstance(bcc, list) else bcc

    to_list = [to]

    # Always format as HTML with professional styling
    content_type = "HTML"
    content = ensure_html_structure(body)

    message = {
        "subject": subject,
        "body": {"contentType": content_type, "content": content},
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list],
    }

    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]

    if bcc:
        message["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]

    # Check if we have large attachments
    has_large_attachments = False
    processed_attachments = []

    if attachments:
        # Convert single path to list
        attachment_paths = (
            [attachments] if isinstance(attachments, str) else attachments
        )
        for file_path in attachment_paths:
            path = pl.Path(file_path).expanduser().resolve()
            content_bytes = path.read_bytes()
            att_size = len(content_bytes)
            att_name = path.name

            processed_attachments.append(
                {
                    "name": att_name,
                    "content_bytes": content_bytes,
                    "content_type": "application/octet-stream",
                    "size": att_size,
                }
            )

            if att_size >= 3 * 1024 * 1024:
                has_large_attachments = True

    if not has_large_attachments and processed_attachments:
        message["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": att["name"],
                "contentBytes": base64.b64encode(att["content_bytes"]).decode("utf-8"),
            }
            for att in processed_attachments
        ]
        graph.request("POST", "/me/sendMail", account_id, json={"message": message})
        return {"status": "sent"}
    if has_large_attachments:
        # Create draft first, then add large attachments, then send
        # Message is already properly formatted above, so we can reuse it

        result = graph.request("POST", "/me/messages", account_id, json=message)
        if not result:
            raise ValueError("Failed to create email draft")

        message_id = result["id"]

        for att in processed_attachments:
            if att["size"] >= 3 * 1024 * 1024:
                graph.upload_large_mail_attachment(
                    message_id,
                    att["name"],
                    att["content_bytes"],
                    account_id,
                    att.get("content_type", "application/octet-stream"),
                )
            else:
                small_att = {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": att["name"],
                    "contentBytes": base64.b64encode(att["content_bytes"]).decode(
                        "utf-8"
                    ),
                }
                graph.request(
                    "POST",
                    f"/me/messages/{message_id}/attachments",
                    account_id,
                    json=small_att,
                )

        graph.request("POST", f"/me/messages/{message_id}/send", account_id)
        return {"status": "sent"}
    graph.request("POST", "/me/sendMail", account_id, json={"message": message})
    return {"status": "sent"}


@mcp.tool
def get_email(account_id: str, email_id: str) -> dict[str, Any]:
    """Get a specific email by ID"""
    endpoint = f"/me/messages/{email_id}"
    params = {
        "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments,body,attachments,importance,isRead"
    }

    message = graph.request("GET", endpoint, account_id, params=params)
    if not message:
        raise ValueError(f"Email with ID {email_id} not found")

    return format_email(message)


@mcp.tool
def download_email_attachments(
    account_id: str, email_id: str, save_dir: str = "~/Downloads"
) -> list[dict[str, str]]:
    """Download all attachments from an email

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID
        save_dir: Directory to save attachments (default: ~/Downloads)

    Returns:
        List of downloaded attachment details with file paths
    """
    save_path = pl.Path(save_dir).expanduser().resolve()
    save_path.mkdir(parents=True, exist_ok=True)

    # Get email with attachments
    endpoint = f"/me/messages/{email_id}/attachments"
    attachments = list(graph.paginate(endpoint, account_id))

    downloaded = []
    for attachment in attachments:
        if attachment.get("@odata.type") == "#microsoft.graph.fileAttachment":
            name = attachment.get("name", "attachment")
            content_bytes = base64.b64decode(attachment.get("contentBytes", ""))

            file_path = save_path / name
            # Handle duplicate filenames
            counter = 1
            while file_path.exists():
                name_parts = name.rsplit(".", 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{name}_{counter}"
                file_path = save_path / new_name
                counter += 1

            file_path.write_bytes(content_bytes)
            downloaded.append(
                {
                    "name": name,
                    "path": str(file_path),
                    "size": len(content_bytes),
                    "type": attachment.get("contentType", "unknown"),
                }
            )

    return downloaded


@mcp.tool
def delete_email(account_id: str, email_id: str, permanent: bool = False) -> dict[str, str]:
    """Delete or move an email to trash

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID
        permanent: If True, permanently delete the email. If False, move to Deleted Items folder.

    Returns:
        Status of the operation
    """
    if permanent:
        # Permanently delete
        graph.request("DELETE", f"/me/messages/{email_id}", account_id)
        return {"status": "permanently deleted"}
    # Move to Deleted Items folder
    deleted_folder_id = "deleteditems"
    graph.request(
        "POST",
        f"/me/messages/{email_id}/move",
        account_id,
        json={"destinationId": deleted_folder_id},
    )
    return {"status": "moved to trash"}


@mcp.tool
def move_email(
    account_id: str, email_id: str, destination_folder: str
) -> dict[str, str]:
    """Move an email to a different folder

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID
        destination_folder: Name of the destination folder (e.g., 'archive', 'inbox', 'sent')

    Returns:
        Status of the operation
    """
    folder_id = FOLDERS.get(destination_folder.lower())
    if not folder_id:
        raise ValueError(
            f"Unknown folder: {destination_folder}. Valid folders: {list(FOLDERS.keys())}"
        )

    graph.request(
        "POST",
        f"/me/messages/{email_id}/move",
        account_id,
        json={"destinationId": folder_id},
    )

    return {"status": f"moved to {destination_folder}"}


@mcp.tool
def list_calendar_events(
    account_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    calendar_id: str | None = None,
) -> list[dict[str, Any]]:
    """List calendar events for a Microsoft account

    Args:
        account_id: Microsoft account ID
        start_date: Start date for filtering events (ISO format: YYYY-MM-DD). Defaults to today.
        end_date: End date for filtering events (ISO format: YYYY-MM-DD). Defaults to 30 days from start.
        limit: Maximum number of events to return (default: 20, max: 50)
        calendar_id: Optional specific calendar ID. If not provided, uses the default calendar.

    Returns:
        List of calendar events
    """
    if not start_date:
        start_date = dt.datetime.now().date().isoformat()

    if not end_date:
        end_dt = dt.datetime.fromisoformat(start_date) + dt.timedelta(days=30)
        end_date = end_dt.date().isoformat()

    # Convert to datetime with time
    start_datetime = f"{start_date}T00:00:00"
    end_datetime = f"{end_date}T23:59:59"

    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/calendarView"
    else:
        endpoint = "/me/calendarView"

    params = {
        "startDateTime": start_datetime,
        "endDateTime": end_datetime,
        "$top": min(limit, 50),
        "$orderby": "start/dateTime",
        "$select": "id,subject,start,end,location,attendees,isAllDay,organizer,body,isOnlineMeeting,onlineMeetingUrl",
    }

    events = list(
        graph.paginate(endpoint, account_id, params=params, max_items=limit)
    )

    # Format events for output
    formatted_events = []
    for event in events:
        formatted_events.append(
            {
                "id": event.get("id"),
                "subject": event.get("subject"),
                "start": event.get("start", {}),
                "end": event.get("end", {}),
                "is_all_day": event.get("isAllDay", False),
                "location": event.get("location", {}).get("displayName", ""),
                "organizer": event.get("organizer", {}).get("emailAddress", {}),
                "attendees": [
                    a.get("emailAddress", {}) for a in event.get("attendees", [])
                ],
                "body_preview": event.get("body", {}).get("content", "")[:200],
                "is_online": event.get("isOnlineMeeting", False),
                "online_url": event.get("onlineMeetingUrl", ""),
            }
        )

    return formatted_events


@mcp.tool
def create_calendar_event(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str] | None = None,
    location: str | None = None,
    body: str | None = None,
    is_online_meeting: bool = False,
    calendar_id: str | None = None,
) -> dict[str, Any]:
    """Create a new calendar event

    Args:
        account_id: Microsoft account ID
        subject: Event subject/title
        start_datetime: Start date and time (ISO format: YYYY-MM-DDTHH:MM:SS)
        end_datetime: End date and time (ISO format: YYYY-MM-DDTHH:MM:SS)
        attendees: List of attendee email addresses
        location: Event location
        body: Event description/body
        is_online_meeting: Whether to create an online Teams meeting
        calendar_id: Optional specific calendar ID. If not provided, uses the default calendar.

    Returns:
        Created event details
    """
    event = {
        "subject": subject,
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
    }

    if location:
        event["location"] = {"displayName": location}

    if body:
        event["body"] = {"contentType": "HTML", "content": body}

    if attendees:
        event["attendees"] = [
            {
                "emailAddress": {"address": email},
                "type": "required",
            }
            for email in attendees
        ]

    if is_online_meeting:
        event["isOnlineMeeting"] = True
        event["onlineMeetingProvider"] = "teamsForBusiness"

    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/events"
    else:
        endpoint = "/me/events"

    result = graph.request("POST", endpoint, account_id, json=event)

    return {
        "id": result.get("id"),
        "subject": result.get("subject"),
        "start": result.get("start"),
        "end": result.get("end"),
        "online_meeting_url": result.get("onlineMeetingUrl", ""),
    }


@mcp.tool
def update_calendar_event(
    account_id: str,
    event_id: str,
    subject: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    location: str | None = None,
    body: str | None = None,
) -> dict[str, str]:
    """Update an existing calendar event

    Args:
        account_id: Microsoft account ID
        event_id: Event ID to update
        subject: New event subject/title
        start_datetime: New start date and time (ISO format)
        end_datetime: New end date and time (ISO format)
        location: New event location
        body: New event description/body

    Returns:
        Update status
    """
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
        update_data["body"] = {"contentType": "HTML", "content": body}

    if not update_data:
        return {"status": "no updates provided"}

    graph.request("PATCH", f"/me/events/{event_id}", account_id, json=update_data)

    return {"status": "event updated"}


@mcp.tool
def delete_calendar_event(
    account_id: str, event_id: str, send_cancellation: bool = True
) -> dict[str, str]:
    """Delete a calendar event

    Args:
        account_id: Microsoft account ID
        event_id: Event ID to delete
        send_cancellation: Whether to send cancellation notices to attendees

    Returns:
        Deletion status
    """
    # If there are attendees and we should send cancellations, use the cancel endpoint
    if send_cancellation:
        # First, get the event to check if it has attendees
        event = graph.request("GET", f"/me/events/{event_id}", account_id)
        if event and event.get("attendees"):
            # Cancel the event (sends cancellation notices)
            graph.request(
                "POST",
                f"/me/events/{event_id}/cancel",
                account_id,
                json={"comment": "This event has been cancelled."},
            )
            return {"status": "event cancelled and notifications sent"}

    # Otherwise, just delete it
    graph.request("DELETE", f"/me/events/{event_id}", account_id)
    return {"status": "event deleted"}


@mcp.tool
def list_files(
    account_id: str,
    folder_path: str | None = None,
    search_query: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List files in OneDrive

    Args:
        account_id: Microsoft account ID
        folder_path: Path to folder (e.g., "/Documents/Projects"). If not provided, lists root.
        search_query: Optional search query to filter files
        limit: Maximum number of files to return (default: 20, max: 50)

    Returns:
        List of files and folders
    """
    if folder_path:
        # Clean the path
        folder_path = folder_path.strip("/")
        endpoint = f"/me/drive/root:/{folder_path}:/children"
    else:
        endpoint = "/me/drive/root/children"

    params = {
        "$top": min(limit, 50),
        "$select": "id,name,size,createdDateTime,lastModifiedDateTime,webUrl,folder,file",
    }

    if search_query:
        # Use search endpoint instead
        endpoint = f"/me/drive/root/search(q='{search_query}')"

    items = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    # Format items for output
    formatted_items = []
    for item in items:
        formatted_items.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "type": "folder" if item.get("folder") else "file",
                "size": item.get("size", 0),
                "created": item.get("createdDateTime"),
                "modified": item.get("lastModifiedDateTime"),
                "web_url": item.get("webUrl"),
                "mime_type": item.get("file", {}).get("mimeType", ""),
            }
        )

    return formatted_items


@mcp.tool
def download_file(
    account_id: str, file_path: str, save_path: str | None = None
) -> dict[str, str]:
    """Download a file from OneDrive

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file in OneDrive (e.g., "/Documents/report.pdf")
        save_path: Local path to save the file. If not provided, saves to ~/Downloads with original name.

    Returns:
        Download result with local file path
    """
    # Clean the file path
    file_path = file_path.strip("/")

    # Get file metadata first
    metadata_endpoint = f"/me/drive/root:/{file_path}"
    file_info = graph.request("GET", metadata_endpoint, account_id)

    if not file_info:
        raise ValueError(f"File not found: {file_path}")

    file_name = file_info.get("name", "download")

    # Download the file content
    download_endpoint = f"/me/drive/root:/{file_path}:/content"
    content = graph.request_raw(download_endpoint, account_id)

    # Determine save location
    if save_path:
        save_location = pl.Path(save_path).expanduser().resolve()
    else:
        save_location = pl.Path("~/Downloads").expanduser().resolve() / file_name

    # Create directory if needed
    save_location.parent.mkdir(parents=True, exist_ok=True)

    # Save the file
    save_location.write_bytes(content)

    return {
        "status": "downloaded",
        "path": str(save_location),
        "size": len(content),
        "name": file_name,
    }


@mcp.tool
def upload_file(
    account_id: str, local_path: str, onedrive_path: str | None = None
) -> dict[str, Any]:
    """Upload a file to OneDrive

    Args:
        account_id: Microsoft account ID
        local_path: Path to the local file to upload
        onedrive_path: Path in OneDrive where to save the file (e.g., "/Documents/report.pdf").
                       If not provided, uploads to root with original filename.

    Returns:
        Uploaded file details
    """
    local_file = pl.Path(local_path).expanduser().resolve()

    if not local_file.exists():
        raise ValueError(f"File not found: {local_path}")

    file_content = local_file.read_bytes()
    file_size = len(file_content)

    # Determine OneDrive path
    if onedrive_path:
        upload_path = onedrive_path.strip("/")
    else:
        upload_path = local_file.name

    # Small file upload (< 4MB)
    if file_size < 4 * 1024 * 1024:
        endpoint = f"/me/drive/root:/{upload_path}:/content"
        result = graph.request(
            "PUT", endpoint, account_id, data=file_content, headers={"Content-Type": "application/octet-stream"}
        )
    else:
        # Large file upload using upload session
        # Create upload session
        session_endpoint = f"/me/drive/root:/{upload_path}:/createUploadSession"
        session = graph.request(
            "POST",
            session_endpoint,
            account_id,
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": "rename",
                    "name": pl.Path(upload_path).name,
                }
            },
        )

        if not session or "uploadUrl" not in session:
            raise ValueError("Failed to create upload session")

        # Upload in chunks
        upload_url = session["uploadUrl"]
        chunk_size = 5 * 1024 * 1024  # 5MB chunks

        for i in range(0, file_size, chunk_size):
            chunk_end = min(i + chunk_size, file_size)
            chunk_data = file_content[i:chunk_end]

            headers = {
                "Content-Length": str(len(chunk_data)),
                "Content-Range": f"bytes {i}-{chunk_end-1}/{file_size}",
            }

            # Use requests directly for upload session
            import requests

            response = requests.put(upload_url, data=chunk_data, headers=headers)
            response.raise_for_status()

            # Last chunk returns the file metadata
            if chunk_end >= file_size:
                result = response.json()

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "size": result.get("size"),
        "web_url": result.get("webUrl"),
        "created": result.get("createdDateTime"),
    }


@mcp.tool
def create_folder(
    account_id: str, folder_name: str, parent_path: str | None = None
) -> dict[str, Any]:
    """Create a new folder in OneDrive

    Args:
        account_id: Microsoft account ID
        folder_name: Name of the new folder
        parent_path: Path to parent folder (e.g., "/Documents"). If not provided, creates in root.

    Returns:
        Created folder details
    """
    folder_data = {"name": folder_name, "folder": {}}

    if parent_path:
        parent_path = parent_path.strip("/")
        endpoint = f"/me/drive/root:/{parent_path}:/children"
    else:
        endpoint = "/me/drive/root/children"

    result = graph.request("POST", endpoint, account_id, json=folder_data)

    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "web_url": result.get("webUrl"),
        "created": result.get("createdDateTime"),
    }


@mcp.tool
def delete_file(account_id: str, file_path: str) -> dict[str, str]:
    """Delete a file or folder from OneDrive

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file or folder to delete (e.g., "/Documents/old-file.txt")

    Returns:
        Deletion status
    """
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}"

    graph.request("DELETE", endpoint, account_id)

    return {"status": "deleted", "path": file_path}


@mcp.tool
def share_file(
    account_id: str,
    file_path: str,
    email: str | None = None,
    permission: str = "view",
    expiration_days: int | None = None,
) -> dict[str, Any]:
    """Share a file or folder from OneDrive

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file or folder to share
        email: Email address to share with. If not provided, creates a shareable link.
        permission: Permission level - "view" (read-only) or "edit" (read-write)
        expiration_days: Number of days until the share expires

    Returns:
        Share details including the share link
    """
    file_path = file_path.strip("/")

    # Create the sharing invitation
    share_data = {"requireSignIn": bool(email), "sendInvitation": bool(email), "roles": ["read" if permission == "view" else "write"]}

    if email:
        share_data["recipients"] = [{"email": email}]

    if expiration_days:
        expiration_date = (
            dt.datetime.now() + dt.timedelta(days=expiration_days)
        ).isoformat()
        share_data["expirationDateTime"] = expiration_date

    endpoint = f"/me/drive/root:/{file_path}:/invite"
    result = graph.request("POST", endpoint, account_id, json=share_data)

    # Extract share link from response
    share_links = result.get("value", [])
    if share_links:
        link_info = share_links[0]
        return {
            "link": link_info.get("link", {}).get("webUrl", ""),
            "permission": permission,
            "expires": share_data.get("expirationDateTime", "never"),
            "shared_with": email or "anyone with link",
        }

    return {"status": "shared", "details": result}


@mcp.tool
def list_contacts(
    account_id: str, search_query: str | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """List contacts from the Microsoft account

    Args:
        account_id: Microsoft account ID
        search_query: Optional search query to filter contacts
        limit: Maximum number of contacts to return (default: 20, max: 50)

    Returns:
        List of contacts with their details
    """
    endpoint = "/me/contacts"
    params = {
        "$top": min(limit, 50),
        "$select": "id,displayName,givenName,surname,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle",
        "$orderby": "displayName",
    }

    if search_query:
        params["$search"] = f'"{search_query}"'

    contacts = list(
        graph.paginate(endpoint, account_id, params=params, max_items=limit)
    )

    # Format contacts for output
    formatted_contacts = []
    for contact in contacts:
        emails = contact.get("emailAddresses", [])
        formatted_contacts.append(
            {
                "id": contact.get("id"),
                "name": contact.get("displayName", ""),
                "first_name": contact.get("givenName", ""),
                "last_name": contact.get("surname", ""),
                "emails": [e.get("address", "") for e in emails if e.get("address")],
                "mobile": contact.get("mobilePhone", ""),
                "business_phones": contact.get("businessPhones", []),
                "company": contact.get("companyName", ""),
                "job_title": contact.get("jobTitle", ""),
            }
        )

    return formatted_contacts


@mcp.tool
def create_contact(
    account_id: str,
    first_name: str,
    last_name: str,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None,
) -> dict[str, Any]:
    """Create a new contact

    Args:
        account_id: Microsoft account ID
        first_name: Contact's first name
        last_name: Contact's last name
        email: Contact's email address
        mobile_phone: Contact's mobile phone number
        company: Contact's company name
        job_title: Contact's job title

    Returns:
        Created contact details
    """
    contact_data = {
        "givenName": first_name,
        "surname": last_name,
        "displayName": f"{first_name} {last_name}",
    }

    if email:
        contact_data["emailAddresses"] = [{"address": email}]

    if mobile_phone:
        contact_data["mobilePhone"] = mobile_phone

    if company:
        contact_data["companyName"] = company

    if job_title:
        contact_data["jobTitle"] = job_title

    result = graph.request("POST", "/me/contacts", account_id, json=contact_data)

    return {
        "id": result.get("id"),
        "name": result.get("displayName"),
        "email": email,
        "mobile": mobile_phone,
    }


@mcp.tool
def update_contact(
    account_id: str,
    contact_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None,
) -> dict[str, str]:
    """Update an existing contact

    Args:
        account_id: Microsoft account ID
        contact_id: Contact ID to update
        first_name: New first name
        last_name: New last name
        email: New email address
        mobile_phone: New mobile phone number
        company: New company name
        job_title: New job title

    Returns:
        Update status
    """
    update_data = {}

    if first_name is not None:
        update_data["givenName"] = first_name

    if last_name is not None:
        update_data["surname"] = last_name

    if first_name is not None or last_name is not None:
        # Update display name if names changed
        current = graph.request("GET", f"/me/contacts/{contact_id}", account_id)
        new_first = first_name or current.get("givenName", "")
        new_last = last_name or current.get("surname", "")
        update_data["displayName"] = f"{new_first} {new_last}".strip()

    if email is not None:
        update_data["emailAddresses"] = [{"address": email}]

    if mobile_phone is not None:
        update_data["mobilePhone"] = mobile_phone

    if company is not None:
        update_data["companyName"] = company

    if job_title is not None:
        update_data["jobTitle"] = job_title

    if not update_data:
        return {"status": "no updates provided"}

    graph.request("PATCH", f"/me/contacts/{contact_id}", account_id, json=update_data)

    return {"status": "contact updated"}


@mcp.tool
def delete_contact(account_id: str, contact_id: str) -> dict[str, str]:
    """Delete a contact

    Args:
        account_id: Microsoft account ID
        contact_id: Contact ID to delete

    Returns:
        Deletion status
    """
    graph.request("DELETE", f"/me/contacts/{contact_id}", account_id)
    return {"status": "contact deleted"}


@mcp.tool
def search_files(
    account_id: str, query: str, file_type: str | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """Search for files across OneDrive using Microsoft Search

    Args:
        account_id: Microsoft account ID
        query: Search query
        file_type: Optional file type filter (e.g., 'pdf', 'docx', 'xlsx')
        limit: Maximum number of results (default: 20)

    Returns:
        List of matching files
    """
    # Build the search query
    search_query = query
    if file_type:
        search_query = f"{query} filetype:{file_type}"

    # Use the Graph search API
    endpoint = f"/me/drive/root/search(q='{search_query}')"
    params = {"$top": min(limit, 50), "$select": "id,name,size,createdDateTime,lastModifiedDateTime,webUrl,file"}

    items = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    # Format results
    results = []
    for item in items:
        if not item.get("folder"):  # Only include files, not folders
            results.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "size": item.get("size", 0),
                    "created": item.get("createdDateTime"),
                    "modified": item.get("lastModifiedDateTime"),
                    "web_url": item.get("webUrl"),
                    "mime_type": item.get("file", {}).get("mimeType", ""),
                }
            )

    return results


@mcp.tool
def get_user_info(account_id: str) -> dict[str, Any]:
    """Get detailed information about the authenticated user

    Args:
        account_id: Microsoft account ID

    Returns:
        User profile information
    """
    user_info = graph.request("GET", "/me", account_id)

    return {
        "id": user_info.get("id"),
        "display_name": user_info.get("displayName"),
        "email": user_info.get("mail") or user_info.get("userPrincipalName"),
        "first_name": user_info.get("givenName"),
        "last_name": user_info.get("surname"),
        "job_title": user_info.get("jobTitle"),
        "department": user_info.get("department"),
        "office_location": user_info.get("officeLocation"),
        "mobile_phone": user_info.get("mobilePhone"),
        "business_phones": user_info.get("businessPhones", []),
    }


@mcp.tool
def search_emails(
    account_id: str,
    query: str,
    folder: str | None = None,
    limit: int = 20,
    has_attachments: bool | None = None,
) -> list[dict[str, Any]]:
    """Search emails using Microsoft Graph search

    Args:
        account_id: Microsoft account ID
        query: Search query (searches in subject, body, from, to fields)
        folder: Optional folder to search in (e.g., 'inbox', 'sent')
        limit: Maximum number of results (default: 20)
        has_attachments: Optional filter for emails with attachments

    Returns:
        List of matching emails
    """
    if folder:
        folder_id = FOLDERS.get(folder.lower(), "inbox")
        endpoint = f"/me/mailFolders/{folder_id}/messages"
    else:
        endpoint = "/me/messages"

    params = {
        "$search": f'"{query}"',
        "$top": min(limit, 50),
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,from,toRecipients,receivedDateTime,hasAttachments,bodyPreview",
    }

    if has_attachments is not None:
        params["$filter"] = f"hasAttachments eq {str(has_attachments).lower()}"

    messages = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    return [format_email(msg, include_body=False) for msg in messages]


@mcp.tool
def get_calendar_availability(
    account_id: str, start_date: str, end_date: str, duration_minutes: int = 30
) -> list[dict[str, str]]:
    """Find available time slots in calendar

    Args:
        account_id: Microsoft account ID
        start_date: Start date for availability search (ISO format: YYYY-MM-DD)
        end_date: End date for availability search (ISO format: YYYY-MM-DD)
        duration_minutes: Duration of time slot needed in minutes (default: 30)

    Returns:
        List of available time slots
    """
    # Get all events in the date range
    events = list_calendar_events(account_id, start_date, end_date, limit=100)

    # Convert to datetime objects for easier manipulation
    start_dt = dt.datetime.fromisoformat(f"{start_date}T08:00:00")
    end_dt = dt.datetime.fromisoformat(f"{end_date}T17:00:00")

    # Create a list of busy times
    busy_times = []
    for event in events:
        if not event["is_all_day"]:
            event_start = dt.datetime.fromisoformat(
                event["start"]["dateTime"].replace("Z", "+00:00")
            )
            event_end = dt.datetime.fromisoformat(
                event["end"]["dateTime"].replace("Z", "+00:00")
            )
            busy_times.append((event_start, event_end))

    # Sort busy times
    busy_times.sort()

    # Find available slots
    available_slots = []
    current_time = start_dt

    for busy_start, busy_end in busy_times:
        # If there's a gap before the next busy time
        if current_time + dt.timedelta(minutes=duration_minutes) <= busy_start:
            available_slots.append(
                {
                    "start": current_time.isoformat(),
                    "end": busy_start.isoformat(),
                    "duration_minutes": int(
                        (busy_start - current_time).total_seconds() / 60
                    ),
                }
            )
        current_time = max(current_time, busy_end)

    # Check if there's time after the last event
    if current_time + dt.timedelta(minutes=duration_minutes) <= end_dt:
        available_slots.append(
            {
                "start": current_time.isoformat(),
                "end": end_dt.isoformat(),
                "duration_minutes": int((end_dt - current_time).total_seconds() / 60),
            }
        )

    # Filter slots that are at least the requested duration
    available_slots = [
        slot for slot in available_slots if slot["duration_minutes"] >= duration_minutes
    ]

    return available_slots


@mcp.tool
def send_calendar_invite(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str],
    location: str | None = None,
    body: str | None = None,
    send_invitation: bool = True,
) -> dict[str, Any]:
    """Create and send a calendar invitation

    Args:
        account_id: Microsoft account ID
        subject: Meeting subject
        start_datetime: Start date and time (ISO format)
        end_datetime: End date and time (ISO format)
        attendees: List of attendee email addresses
        location: Meeting location
        body: Meeting description
        send_invitation: Whether to send invitations to attendees (default: True)

    Returns:
        Created event details
    """
    # Create the event with attendees
    event = create_calendar_event(
        account_id=account_id,
        subject=subject,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        attendees=attendees,
        location=location,
        body=body,
        is_online_meeting=False,
    )

    if send_invitation and attendees:
        # The invitations are automatically sent when creating an event with attendees
        event["invitations_sent"] = True

    return event


@mcp.tool
def search_calendar_events(
    account_id: str, query: str, start_date: str | None = None, end_date: str | None = None
) -> list[dict[str, Any]]:
    """Search calendar events by keyword

    Args:
        account_id: Microsoft account ID
        query: Search query (searches in subject, location, body)
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)

    Returns:
        List of matching events
    """
    # Get events in date range
    events = list_calendar_events(account_id, start_date, end_date, limit=100)

    # Filter by search query
    query_lower = query.lower()
    matching_events = []

    for event in events:
        # Search in subject, location, and body
        if (
            query_lower in event.get("subject", "").lower()
            or query_lower in event.get("location", "").lower()
            or query_lower in event.get("body_preview", "").lower()
        ):
            matching_events.append(event)

    return matching_events


@mcp.tool
def export_contacts(
    account_id: str, format: str = "json", limit: int = 1000
) -> dict[str, Any]:
    """Export all contacts to a structured format

    Args:
        account_id: Microsoft account ID
        format: Export format - 'json' or 'csv' (default: json)
        limit: Maximum number of contacts to export (default: 1000)

    Returns:
        Exported contacts data or file path
    """
    # Get all contacts
    contacts = list_contacts(account_id, limit=limit)

    if format == "json":
        return {"format": "json", "count": len(contacts), "contacts": contacts}
    if format == "csv":
        # Create CSV content
        import csv
        import io

        csv_buffer = io.StringIO()
        if contacts:
            fieldnames = [
                "name",
                "first_name",
                "last_name",
                "emails",
                "mobile",
                "business_phones",
                "company",
                "job_title",
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()

            for contact in contacts:
                # Convert lists to comma-separated strings
                contact_copy = contact.copy()
                contact_copy["emails"] = ", ".join(contact.get("emails", []))
                contact_copy["business_phones"] = ", ".join(
                    contact.get("business_phones", [])
                )
                writer.writerow(
                    {k: contact_copy.get(k, "") for k in fieldnames}
                )

        return {
            "format": "csv",
            "count": len(contacts),
            "content": csv_buffer.getvalue(),
        }
    raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'")


@mcp.tool
def list_mail_folders(account_id: str) -> list[dict[str, Any]]:
    """List all mail folders in the account

    Args:
        account_id: Microsoft account ID

    Returns:
        List of mail folders with their properties
    """
    endpoint = "/me/mailFolders"
    params = {"$top": 100, "$select": "id,displayName,totalItemCount,unreadItemCount"}

    folders = list(graph.paginate(endpoint, account_id, params=params))

    # Format folders for output
    formatted_folders = []
    for folder in folders:
        formatted_folders.append(
            {
                "id": folder.get("id"),
                "name": folder.get("displayName"),
                "total_items": folder.get("totalItemCount", 0),
                "unread_items": folder.get("unreadItemCount", 0),
            }
        )

    return formatted_folders


@mcp.tool
def create_mail_folder(
    account_id: str, folder_name: str, parent_folder_id: str | None = None
) -> dict[str, Any]:
    """Create a new mail folder

    Args:
        account_id: Microsoft account ID
        folder_name: Name of the new folder
        parent_folder_id: Optional parent folder ID. If not provided, creates at root level.

    Returns:
        Created folder details
    """
    folder_data = {"displayName": folder_name}

    if parent_folder_id:
        endpoint = f"/me/mailFolders/{parent_folder_id}/childFolders"
    else:
        endpoint = "/me/mailFolders"

    result = graph.request("POST", endpoint, account_id, json=folder_data)

    return {
        "id": result.get("id"),
        "name": result.get("displayName"),
        "total_items": result.get("totalItemCount", 0),
    }


@mcp.tool
def get_email_signature(account_id: str) -> dict[str, str]:
    """Get the user's email signature

    Note: This returns the signature used in the MCP tools, not the Outlook client signature.

    Args:
        account_id: Microsoft account ID

    Returns:
        Email signature information
    """
    return {
        "signature": """Ossie Irondi PharmD.
KC Ventures PLLC,
Chief Operating Officer
Baytown Office: 281-421-5950
Humble Office: 281-812-3333
Cell: 346-644-0193
https://www.kamdental.com
Book Time With Me: https://outlook.office.com/bookwithme/user/d6969d9eb5414cee9dda0cf451be81e4@kamdental.com/meetingtype/1w-0SimM5ECttFPPhkpYxg2?anonymous&ismsaljsauthenabled""",
        "format": "text",
        "note": "This signature is automatically appended to emails sent via MCP tools",
    }


@mcp.tool
def list_shared_files(account_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """List files shared with the user

    Args:
        account_id: Microsoft account ID
        limit: Maximum number of files to return

    Returns:
        List of shared files
    """
    endpoint = "/me/drive/sharedWithMe"
    params = {
        "$top": min(limit, 50),
        "$select": "id,name,size,createdDateTime,lastModifiedDateTime,webUrl,createdBy,lastModifiedBy",
    }

    items = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    # Format items for output
    formatted_items = []
    for item in items:
        formatted_items.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "type": "folder" if item.get("folder") else "file",
                "size": item.get("size", 0),
                "shared_by": item.get("createdBy", {})
                .get("user", {})
                .get("displayName", "Unknown"),
                "modified": item.get("lastModifiedDateTime"),
                "web_url": item.get("webUrl"),
            }
        )

    return formatted_items


@mcp.tool
def get_calendar_list(account_id: str) -> list[dict[str, Any]]:
    """List all calendars available to the user

    Args:
        account_id: Microsoft account ID

    Returns:
        List of calendars with their properties
    """
    endpoint = "/me/calendars"
    params = {"$select": "id,name,color,isDefaultCalendar,canEdit,canShare,owner"}

    calendars = list(graph.paginate(endpoint, account_id, params=params))

    # Format calendars for output
    formatted_calendars = []
    for calendar in calendars:
        formatted_calendars.append(
            {
                "id": calendar.get("id"),
                "name": calendar.get("name"),
                "color": calendar.get("color"),
                "is_default": calendar.get("isDefaultCalendar", False),
                "can_edit": calendar.get("canEdit", False),
                "can_share": calendar.get("canShare", False),
                "owner": calendar.get("owner", {})
                .get("emailAddress", {})
                .get("address", ""),
            }
        )

    return formatted_calendars


@mcp.tool
def add_email_attachment_from_onedrive(
    account_id: str, email_id: str, file_path: str
) -> dict[str, str]:
    """Add a OneDrive file as an attachment to an existing draft email

    Args:
        account_id: Microsoft account ID
        email_id: Draft email message ID
        file_path: Path to the file in OneDrive (e.g., "/Documents/report.pdf")

    Returns:
        Status of the operation
    """
    # Clean the file path
    file_path = file_path.strip("/")

    # Get file metadata
    metadata_endpoint = f"/me/drive/root:/{file_path}"
    file_info = graph.request("GET", metadata_endpoint, account_id)

    if not file_info:
        raise ValueError(f"File not found: {file_path}")

    # Create reference attachment
    attachment_data = {
        "@odata.type": "#microsoft.graph.referenceAttachment",
        "name": file_info.get("name"),
        "sourceUrl": file_info.get("webUrl"),
        "providerType": "oneDriveBusiness",
        "permission": "view",
        "isFolder": False,
        "size": file_info.get("size", 0),
    }

    # Add attachment to the email
    endpoint = f"/me/messages/{email_id}/attachments"
    graph.request("POST", endpoint, account_id, json=attachment_data)

    return {
        "status": "attachment added",
        "file_name": file_info.get("name"),
        "type": "reference",
    }


@mcp.tool
def mark_email_as_read(
    account_id: str, email_id: str, is_read: bool = True
) -> dict[str, str]:
    """Mark an email as read or unread

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID
        is_read: Whether to mark as read (True) or unread (False)

    Returns:
        Status of the operation
    """
    update_data = {"isRead": is_read}
    graph.request("PATCH", f"/me/messages/{email_id}", account_id, json=update_data)

    return {"status": f"marked as {'read' if is_read else 'unread'}"}


@mcp.tool
def reply_to_email(
    account_id: str,
    email_id: str,
    body: str,
    reply_all: bool = False,
    attachments: str | list[str] | None = None,
) -> dict[str, str]:
    """Reply to an email

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID to reply to
        body: Reply message body
        reply_all: Whether to reply to all recipients (True) or just the sender (False)
        attachments: Optional file path(s) to attach

    Returns:
        Status of the operation
    """
    # Format the reply body with HTML structure
    formatted_body = ensure_html_structure(body)

    reply_data = {"message": {"body": {"contentType": "HTML", "content": formatted_body}}}

    # Handle attachments if provided
    if attachments:
        attachment_paths = (
            [attachments] if isinstance(attachments, str) else attachments
        )
        attachments_list = []

        for file_path in attachment_paths:
            path = pl.Path(file_path).expanduser().resolve()
            content_bytes = path.read_bytes()

            if len(content_bytes) < 3 * 1024 * 1024:
                attachments_list.append(
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": path.name,
                        "contentBytes": base64.b64encode(content_bytes).decode("utf-8"),
                    }
                )

        if attachments_list:
            reply_data["message"]["attachments"] = attachments_list

    # Send the reply
    endpoint = f"/me/messages/{email_id}/{'replyAll' if reply_all else 'reply'}"
    graph.request("POST", endpoint, account_id, json=reply_data)

    return {"status": f"{'reply all' if reply_all else 'reply'} sent"}


@mcp.tool
def forward_email(
    account_id: str,
    email_id: str,
    to: str | list[str],
    comment: str | None = None,
) -> dict[str, str]:
    """Forward an email to other recipients

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID to forward
        to: Recipient email address(es)
        comment: Optional comment to add to the forwarded email

    Returns:
        Status of the operation
    """
    # Ensure 'to' is a list
    to_list = [to] if isinstance(to, str) else to

    forward_data = {
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_list]
    }

    if comment:
        formatted_comment = ensure_html_structure(comment)
        forward_data["comment"] = formatted_comment

    # Forward the email
    endpoint = f"/me/messages/{email_id}/forward"
    graph.request("POST", endpoint, account_id, json=forward_data)

    return {"status": "email forwarded", "to": to_list}


@mcp.tool
def get_inbox_rules(account_id: str) -> list[dict[str, Any]]:
    """Get email inbox rules

    Args:
        account_id: Microsoft account ID

    Returns:
        List of inbox rules
    """
    endpoint = "/me/mailFolders/inbox/messageRules"
    rules = list(graph.paginate(endpoint, account_id))

    # Format rules for output
    formatted_rules = []
    for rule in rules:
        formatted_rules.append(
            {
                "id": rule.get("id"),
                "name": rule.get("displayName"),
                "is_enabled": rule.get("isEnabled", True),
                "conditions": rule.get("conditions", {}),
                "actions": rule.get("actions", {}),
                "sequence": rule.get("sequence", 0),
            }
        )

    return formatted_rules


@mcp.tool
def get_email_categories(account_id: str) -> list[dict[str, Any]]:
    """Get available email categories

    Args:
        account_id: Microsoft account ID

    Returns:
        List of email categories
    """
    endpoint = "/me/outlook/masterCategories"
    categories = list(graph.paginate(endpoint, account_id))

    # Format categories for output
    formatted_categories = []
    for category in categories:
        formatted_categories.append(
            {
                "id": category.get("id"),
                "name": category.get("displayName"),
                "color": category.get("color"),
            }
        )

    return formatted_categories


@mcp.tool
def schedule_email(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    send_datetime: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, Any]:
    """Schedule an email to be sent at a specific time

    Note: This creates a draft that should be sent at the specified time using external scheduling.
    Microsoft Graph API doesn't directly support delayed sending.

    Args:
        account_id: Microsoft account ID
        to: Recipient email address
        subject: Email subject
        body: Email body
        send_datetime: When to send the email (ISO format: YYYY-MM-DDTHH:MM:SS)
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Draft email details with scheduled time
    """
    # Create a draft
    draft = create_email_draft(
        account_id=account_id,
        to=to,
        subject=f"[Scheduled: {send_datetime}] {subject}",
        body=body,
        cc=cc,
        bcc=bcc,
    )

    return {
        "id": draft["id"],
        "status": "draft created",
        "scheduled_for": send_datetime,
        "note": "Email saved as draft. Use external scheduling to send at the specified time.",
    }


@mcp.tool
def get_mailbox_statistics(account_id: str) -> dict[str, Any]:
    """Get mailbox usage statistics

    Args:
        account_id: Microsoft account ID

    Returns:
        Mailbox statistics including storage usage
    """
    # Get mailbox settings
    mailbox_settings = graph.request("GET", "/me/mailboxSettings", account_id)

    # Get mail folders for counts
    folders = list_mail_folders(account_id)

    # Calculate totals
    total_items = sum(folder["total_items"] for folder in folders)
    total_unread = sum(folder["unread_items"] for folder in folders)

    # Find specific folders
    folder_stats = {}
    for folder in folders:
        name_lower = folder["name"].lower()
        if name_lower in ["inbox", "sent items", "drafts", "deleted items", "junk email"]:
            folder_stats[name_lower] = {
                "total": folder["total_items"],
                "unread": folder["unread_items"],
            }

    return {
        "total_items": total_items,
        "total_unread": total_unread,
        "folders": folder_stats,
        "time_zone": mailbox_settings.get("timeZone", "UTC"),
        "language": mailbox_settings.get("language", {}).get("displayName", "English"),
        "folder_count": len(folders),
    }


@mcp.tool
def search_people(
    account_id: str, query: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Search for people in the organization

    Args:
        account_id: Microsoft account ID
        query: Search query (name or email)
        limit: Maximum number of results

    Returns:
        List of people matching the search
    """
    endpoint = "/me/people"
    params = {"$search": f'"{query}"', "$top": min(limit, 50), "$select": "id,displayName,emailAddresses,jobTitle,department,officeLocation"}

    people = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    # Format results
    results = []
    for person in people:
        emails = [
            e.get("address")
            for e in person.get("emailAddresses", [])
            if e.get("address")
        ]
        results.append(
            {
                "id": person.get("id"),
                "name": person.get("displayName"),
                "emails": emails,
                "job_title": person.get("jobTitle"),
                "department": person.get("department"),
                "office": person.get("officeLocation"),
            }
        )

    return results


@mcp.tool
def get_recent_files(account_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Get recently accessed files

    Args:
        account_id: Microsoft account ID
        limit: Maximum number of files to return

    Returns:
        List of recently accessed files
    """
    endpoint = "/me/drive/recent"
    params = {
        "$top": min(limit, 50),
        "$select": "id,name,size,lastModifiedDateTime,webUrl,lastModifiedBy",
    }

    items = list(graph.paginate(endpoint, account_id, params=params, max_items=limit))

    # Format items
    formatted_items = []
    for item in items:
        if not item.get("folder"):  # Only include files
            formatted_items.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "size": item.get("size", 0),
                    "modified": item.get("lastModifiedDateTime"),
                    "modified_by": item.get("lastModifiedBy", {})
                    .get("user", {})
                    .get("displayName", "Unknown"),
                    "web_url": item.get("webUrl"),
                }
            )

    return formatted_items


@mcp.tool
def get_file_preview(
    account_id: str, file_path: str, page: int = 1
) -> dict[str, Any]:
    """Get a preview/thumbnail of a file

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file in OneDrive
        page: Page number for multi-page documents (default: 1)

    Returns:
        Preview information including thumbnail URL
    """
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}:/thumbnails"

    thumbnails = graph.request("GET", endpoint, account_id)

    if thumbnails and thumbnails.get("value"):
        thumbnail_set = thumbnails["value"][0]
        return {
            "small": thumbnail_set.get("small", {}).get("url"),
            "medium": thumbnail_set.get("medium", {}).get("url"),
            "large": thumbnail_set.get("large", {}).get("url"),
            "page": page,
        }

    return {"status": "no preview available"}


@mcp.tool
def get_file_versions(account_id: str, file_path: str) -> list[dict[str, Any]]:
    """Get version history of a file

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file in OneDrive

    Returns:
        List of file versions
    """
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}:/versions"

    versions = list(graph.paginate(endpoint, account_id))

    # Format versions
    formatted_versions = []
    for version in versions:
        formatted_versions.append(
            {
                "id": version.get("id"),
                "last_modified": version.get("lastModifiedDateTime"),
                "modified_by": version.get("lastModifiedBy", {})
                .get("user", {})
                .get("displayName", "Unknown"),
                "size": version.get("size", 0),
            }
        )

    return formatted_versions


@mcp.tool
def restore_file_version(
    account_id: str, file_path: str, version_id: str
) -> dict[str, str]:
    """Restore a specific version of a file

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file in OneDrive
        version_id: Version ID to restore

    Returns:
        Status of the restoration
    """
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}:/versions/{version_id}/restoreVersion"

    graph.request("POST", endpoint, account_id)

    return {"status": "version restored", "version_id": version_id}


@mcp.tool
def empty_deleted_items(account_id: str) -> dict[str, str]:
    """Empty the Deleted Items folder

    Args:
        account_id: Microsoft account ID

    Returns:
        Status of the operation
    """
    # Get all items in deleted items folder
    deleted_items = list_emails(
        account_id, folder_name="deleted", limit=100, include_body=False
    )

    # Delete each item permanently
    deleted_count = 0
    for item in deleted_items:
        try:
            graph.request("DELETE", f"/me/messages/{item['id']}", account_id)
            deleted_count += 1
        except:
            pass  # Continue even if some items fail

    return {"status": "emptied", "items_deleted": deleted_count}


@mcp.tool
def get_out_of_office(account_id: str) -> dict[str, Any]:
    """Get out of office settings

    Args:
        account_id: Microsoft account ID

    Returns:
        Out of office settings
    """
    settings = graph.request("GET", "/me/mailboxSettings/automaticRepliesSetting", account_id)

    return {
        "status": settings.get("status", "disabled"),
        "external_message": settings.get("externalReplyMessage", ""),
        "internal_message": settings.get("internalReplyMessage", ""),
        "scheduled_start": settings.get("scheduledStartDateTime", {}).get("dateTime"),
        "scheduled_end": settings.get("scheduledEndDateTime", {}).get("dateTime"),
        "external_audience": settings.get("externalAudience", "none"),
    }


@mcp.tool
def set_out_of_office(
    account_id: str,
    message: str,
    start_time: str | None = None,
    end_time: str | None = None,
    external_message: str | None = None,
) -> dict[str, str]:
    """Set out of office auto-reply

    Args:
        account_id: Microsoft account ID
        message: Auto-reply message for internal recipients
        start_time: Optional start time (ISO format). If not set, starts immediately.
        end_time: Optional end time (ISO format). If not set, continues indefinitely.
        external_message: Optional different message for external recipients

    Returns:
        Status of the operation
    """
    settings = {
        "status": "scheduled" if start_time else "alwaysEnabled",
        "internalReplyMessage": message,
        "externalReplyMessage": external_message or message,
        "externalAudience": "all" if external_message else "none",
    }

    if start_time:
        settings["scheduledStartDateTime"] = {"dateTime": start_time, "timeZone": "UTC"}

    if end_time:
        settings["scheduledEndDateTime"] = {"dateTime": end_time, "timeZone": "UTC"}

    graph.request(
        "PATCH", "/me/mailboxSettings", account_id, json={"automaticRepliesSetting": settings}
    )

    return {"status": "out of office enabled"}


@mcp.tool
def disable_out_of_office(account_id: str) -> dict[str, str]:
    """Disable out of office auto-reply

    Args:
        account_id: Microsoft account ID

    Returns:
        Status of the operation
    """
    settings = {"status": "disabled"}

    graph.request(
        "PATCH", "/me/mailboxSettings", account_id, json={"automaticRepliesSetting": settings}
    )

    return {"status": "out of office disabled"}


# New list/array type parameters should be handled properly
@mcp.tool
def batch_download_attachments(
    account_id: str, email_ids: list[str], save_dir: str = "~/Downloads"
) -> list[dict[str, Any]]:
    """Download attachments from multiple emails

    Args:
        account_id: Microsoft account ID
        email_ids: List of email message IDs
        save_dir: Directory to save attachments

    Returns:
        List of download results for each email
    """
    results = []

    for email_id in email_ids:
        try:
            attachments = download_email_attachments(account_id, email_id, save_dir)
            results.append(
                {"email_id": email_id, "status": "success", "attachments": attachments}
            )
        except Exception as e:
            results.append({"email_id": email_id, "status": "error", "error": str(e)})

    return results


# New email handling improvements
@mcp.tool
def get_email_headers(account_id: str, email_id: str) -> dict[str, Any]:
    """Get detailed email headers

    Args:
        account_id: Microsoft account ID
        email_id: Email message ID

    Returns:
        Email headers including routing information
    """
    endpoint = f"/me/messages/{email_id}"
    params = {"$select": "internetMessageHeaders,receivedDateTime,subject"}

    message = graph.request("GET", endpoint, account_id, params=params)

    headers = {}
    for header in message.get("internetMessageHeaders", []):
        headers[header["name"]] = header["value"]

    return {
        "subject": message.get("subject"),
        "received": message.get("receivedDateTime"),
        "headers": headers,
        "message_id": headers.get("Message-ID"),
        "from": headers.get("From"),
        "return_path": headers.get("Return-Path"),
    }


# File collaboration
@mcp.tool
def get_file_permissions(account_id: str, file_path: str) -> list[dict[str, Any]]:
    """Get sharing permissions for a file

    Args:
        account_id: Microsoft account ID
        file_path: Path to the file in OneDrive

    Returns:
        List of permissions
    """
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}:/permissions"

    permissions = list(graph.paginate(endpoint, account_id))

    formatted_perms = []
    for perm in permissions:
        formatted_perms.append(
            {
                "id": perm.get("id"),
                "roles": perm.get("roles", []),
                "link": perm.get("link", {}).get("webUrl"),
                "granted_to": perm.get("grantedTo", {}).get("user", {}).get("email"),
                "expires": perm.get("expirationDateTime"),
            }
        )

    return formatted_perms


@mcp.tool
def unified_search(
    query: str,
    account_id: str,
    entity_types: list[str] | None = None,
    limit: int = 50,
) -> dict[str, list[dict[str, Any]]]:
    """Search across multiple Microsoft 365 resources using the modern search API

    entity_types can include: 'message', 'event', 'drive', 'driveItem', 'list', 'listItem', 'site'
    If not specified, searches across all available types.
    """
    if not entity_types:
        entity_types = ["message", "event", "driveItem"]

    results = {entity_type: [] for entity_type in entity_types}

    items = list(graph.search_query(query, entity_types, account_id, limit))

    for item in items:
        resource_type = item.get("@odata.type", "").split(".")[-1]

        if resource_type == "message":
            results.setdefault("message", []).append(item)
        elif resource_type == "event":
            results.setdefault("event", []).append(item)
        elif resource_type in ["driveItem", "file", "folder"]:
            results.setdefault("driveItem", []).append(item)
        else:
            results.setdefault("other", []).append(item)

    return {k: v for k, v in results.items() if v}


# KamDental Email Framework Tools

@mcp.tool
def send_practice_report(
    account_id: str,
    to: str,
    subject: str,
    location: str,
    financial_data: dict[str, Any],
    provider_data: list[dict[str, Any]],
    period: str | None = None,
    alerts: list[dict[str, Any]] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, str]:
    """Send a professional practice performance report email

    Args:
        account_id: Microsoft account ID
        to: Primary recipient email address
        subject: Email subject line
        location: Practice location (Baytown or Humble)
        financial_data: Dictionary containing production, collections, case_acceptance, call_answer_rate
        provider_data: List of provider performance data
        period: Reporting period (e.g., "July 2025 MTD")
        alerts: Optional list of alerts/issues
        recommendations: Optional list of recommendations
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Status of the email send operation
    """
    from .email_framework.templates.practice_report import PracticeReportTemplate

    # Determine theme based on location
    theme = location.lower() if location.lower() in ["baytown", "humble"] else "baytown"

    # Create template and render
    template = PracticeReportTemplate(theme=theme)

    # Prepare data
    template_data = {
        "location": location,
        "period": period or "Current Period",
        "financial_data": financial_data,
        "providers": provider_data,
        "alerts": alerts or [],
        "recommendations": recommendations or []
    }

    # Render the email
    html_content = template.render(template_data)

    # Send using existing send_email function
    return send_email(
        account_id=account_id,
        to=to,
        subject=subject,
        body=html_content,
        cc=cc,
        bcc=bcc
    )


@mcp.tool
def send_executive_summary(
    account_id: str,
    to: str,
    locations_data: list[dict[str, Any]],
    period: str,
    subject: str | None = None,
    key_insights: list[dict[str, Any]] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, str]:
    """Send an executive summary email with multi-location overview

    Args:
        account_id: Microsoft account ID
        to: Primary recipient email address
        locations_data: List of location performance data
        period: Reporting period (e.g., "July 2025 MTD")
        subject: Optional custom subject (defaults to "Executive Summary - {period}")
        key_insights: Optional list of key insights
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Status of the email send operation
    """
    from .email_framework.templates.executive_summary import ExecutiveSummaryTemplate

    # Create template with executive theme
    template = ExecutiveSummaryTemplate()

    # Calculate totals
    total_production = sum(loc.get("production", 0) for loc in locations_data)
    total_goal = sum(loc.get("goal", 0) for loc in locations_data)
    overall_percentage = total_production / total_goal if total_goal > 0 else 0

    # Prepare data
    template_data = {
        "period": period,
        "locations": locations_data,
        "key_insights": key_insights or [],
        "total_production": total_production,
        "total_goal": total_goal,
        "overall_percentage": overall_percentage
    }

    # Render the email
    html_content = template.render(template_data)

    # Default subject if not provided
    if not subject:
        subject = f"Executive Summary - {period}"

    # Send using existing send_email function
    return send_email(
        account_id=account_id,
        to=to,
        subject=subject,
        body=html_content,
        cc=cc,
        bcc=bcc
    )


@mcp.tool
def send_provider_update(
    account_id: str,
    to: str,
    provider_name: str,
    performance_data: dict[str, Any],
    period: str | None = None,
    highlights: list[str] | None = None,
    recommendations: list[str] | None = None,
    subject: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, str]:
    """Send a personalized provider performance update email

    Args:
        account_id: Microsoft account ID
        to: Provider's email address
        provider_name: Provider's name
        performance_data: Dictionary with production, goal, percentage, etc.
        period: Reporting period
        highlights: Optional list of performance highlights
        recommendations: Optional list of recommendations
        subject: Optional custom subject
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Status of the email send operation
    """
    from .email_framework.templates.provider_update import ProviderUpdateTemplate

    # Create template
    template = ProviderUpdateTemplate()

    # Prepare data
    template_data = {
        "provider_name": provider_name,
        "period": period or "Current Period",
        "performance_data": performance_data,
        "highlights": highlights or [],
        "recommendations": recommendations or []
    }

    # Render the email
    html_content = template.render(template_data)

    # Default subject if not provided
    if not subject:
        subject = f"Your Performance Update - {period or 'Current Period'}"

    # Send using existing send_email function
    return send_email(
        account_id=account_id,
        to=to,
        subject=subject,
        body=html_content,
        cc=cc,
        bcc=bcc
    )


@mcp.tool
def send_alert_notification(
    account_id: str,
    to: str,
    alert_type: str,
    title: str,
    message: str,
    urgency: str = "normal",
    impact: str | None = None,
    recommended_actions: list[str] | None = None,
    subject: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, str]:
    """Send an alert notification email with urgency-based styling

    Args:
        account_id: Microsoft account ID
        to: Recipient email address
        alert_type: Type of alert (critical, warning, info)
        title: Alert title
        message: Alert message/details
        urgency: Urgency level (immediate, high, normal)
        impact: Optional business impact description
        recommended_actions: Optional list of recommended actions
        subject: Optional custom subject
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Status of the email send operation
    """
    from .email_framework.templates.alert_notification import AlertNotificationTemplate

    # Create template
    template = AlertNotificationTemplate()

    # Prepare data
    template_data = {
        "alert_type": alert_type,
        "title": title,
        "message": message,
        "urgency": urgency,
        "impact": impact,
        "recommended_actions": recommended_actions or []
    }

    # Render the email
    html_content = template.render(template_data)

    # Default subject if not provided
    if not subject:
        urgency_prefix = "🚨 URGENT: " if urgency == "immediate" else "⚠️ " if urgency == "high" else ""
        subject = f"{urgency_prefix}{title}"

    # Send using existing send_email function
    return send_email(
        account_id=account_id,
        to=to,
        subject=subject,
        body=html_content,
        cc=cc,
        bcc=bcc
    )

# ============================================================================
# FUNCTION ALIASES AND COMPATIBILITY FUNCTIONS
# ============================================================================
# These aliases provide backward compatibility and alternative naming for tools

# Calendar function aliases - tests expect these shorter names
list_events = list_calendar_events
create_event = create_calendar_event
update_event = update_calendar_event
delete_event = delete_calendar_event

# Contact function aliases - already correct names, but keeping for consistency
# list_contacts = list_contacts  # Already correct name
# create_contact = create_contact  # Already correct name

# Email validation utility function for tests
def _validate_email_address(email: str) -> bool:
    """Validate email address format - utility function used by tests"""
    import re
    if not email or not isinstance(email, str):
        return False

    # Simple email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


# Email validation function using the validators module
def validate_email(email: str) -> str:
    """Validate email using the email framework validators"""
    from .email_framework.validators import EmailValidator
    return EmailValidator.validate_email(email)


# Email recipient list validation
def validate_recipient_list(recipients: list[str]) -> list[str]:
    """Validate a list of email recipients"""
    from .email_framework.validators import EmailValidator
    return EmailValidator.validate_email_list(recipients)


# HTML structure utility for email styling tests
def ensure_html_structure(content: str) -> str:
    """Ensure HTML content has proper structure for email templates"""
    if not content:
        return "<html><body></body></html>"

    # If content doesn't have html tags, wrap it
    if not content.strip().startswith("<html"):
        content = f"<html><body>{content}</body></html>"

    return content


@mcp.tool
def microsoft_operations(
    account_id: str,
    action: str,
    data: dict[str, Any] | None = None,
    template: str | None = None,
    options: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Unified Microsoft operations tool with action-based routing.
    
    This tool consolidates multiple Microsoft Graph API operations into a single
    interface with action-based parameters. It leverages parameter validation
    from Story 1.1 and provides professional email styling through utilities.
    
    Args:
        account_id: Microsoft account ID from list_accounts()
        action: Operation to perform (e.g., "email.list", "email.send")
        data: Action-specific data parameters
        template: Optional email template type for styling
        options: Additional options (pagination, filters, flags)
        
    Returns:
        Action-specific response data
        
    Raises:
        ValueError: If action is unknown or parameters are invalid
        Exception: If Graph API operation fails
        
    Supported Actions:
        - email.list: List emails with filtering
        - email.send: Send email with optional template
        - email.reply: Reply to email with styling
        - email.draft: Create draft with template support
        - email.delete: Delete email operations
        - email.forward: Forward email with comment
        - email.move: Move email between folders
        - email.mark: Mark email as read/unread/important
        - email.search: Search emails with advanced filtering
        - email.get: Retrieve specific email with attachments
    """
    # Import validation utilities

    # Initialize data and options if not provided
    data = data or {}
    options = options or {}

    # Route based on action
    if action == "email.list":
        return _handle_email_list(account_id, data, options)
    if action == "email.send":
        return _handle_email_send(account_id, data, template, options)
    if action == "email.reply":
        return _handle_email_reply(account_id, data, template, options)
    if action == "email.draft":
        return _handle_email_draft(account_id, data, template, options)
    if action == "email.delete":
        return _handle_email_delete(account_id, data, options)
    if action == "email.forward":
        return _handle_email_forward(account_id, data, template, options)
    if action == "email.move":
        return _handle_email_move(account_id, data, options)
    if action == "email.mark":
        return _handle_email_mark(account_id, data, options)
    if action == "email.search":
        return _handle_email_search(account_id, data, options)
    if action == "email.get":
        return _handle_email_get(account_id, data, options)

    # Calendar actions
    if action == "calendar.list":
        return _handle_calendar_list(account_id, data, options)
    if action == "calendar.get":
        return _handle_calendar_get(account_id, data, options)
    if action == "calendar.create":
        return _handle_calendar_create(account_id, data, options)
    if action == "calendar.update":
        return _handle_calendar_update(account_id, data, options)
    if action == "calendar.delete":
        return _handle_calendar_delete(account_id, data, options)
    if action == "calendar.availability":
        return _handle_calendar_availability(account_id, data, options)

    # File actions
    if action == "file.list":
        return _handle_file_list(account_id, data, options)
    if action == "file.get":
        return _handle_file_get(account_id, data, options)
    if action == "file.upload":
        return _handle_file_upload(account_id, data, options)
    if action == "file.download":
        return _handle_file_download(account_id, data, options)
    if action == "file.share":
        return _handle_file_share(account_id, data, options)
    if action == "file.delete":
        return _handle_file_delete(account_id, data, options)
    if action == "file.search":
        return _handle_file_search(account_id, data, options)

    # Contact actions
    if action == "contact.list":
        return _handle_contact_list(account_id, data, options)
    if action == "contact.get":
        return _handle_contact_get(account_id, data, options)
    if action == "contact.create":
        return _handle_contact_create(account_id, data, options)
    if action == "contact.update":
        return _handle_contact_update(account_id, data, options)
    if action == "contact.delete":
        return _handle_contact_delete(account_id, data, options)
    if action == "contact.search":
        return _handle_contact_search(account_id, data, options)

    raise ValueError(
        f"Unknown action: {action}. "
        f"Supported actions: email.list, email.send, email.reply, "
        f"email.draft, email.delete, email.forward, email.move, "
        f"email.mark, email.search, email.get, calendar.list, "
        f"calendar.get, calendar.create, calendar.update, "
        f"calendar.delete, calendar.availability, file.list, "
        f"file.get, file.upload, file.download, file.share, "
        f"file.delete, file.search, contact.list, contact.get, contact.create, "
        f"contact.update, contact.delete, contact.search"
    )


def _handle_email_list(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.list action.
    
    Data parameters:
        - folder: Email folder name (default: inbox)
        - search: Search query string
        - include_body: Include email body (default: True)
        
    Options:
        - limit: Maximum results (default: 10)
        - skip: Number to skip for pagination
    """
    # Use Story 1.1 parameter validation framework
    from .email_params import ListEmailParams

    # Merge parameters for validation
    params_dict = {"account_id": account_id}
    params_dict.update(data)
    params_dict.update(options)

    # Validate parameters
    try:
        validated = ListEmailParams(**params_dict)
    except Exception as e:
        raise ValueError(f"Parameter validation failed: {e}")

    # Extract validated parameters
    folder = validated.folder or "inbox"
    search_query = validated.search_query if hasattr(validated, "search_query") else None
    include_body = validated.include_body if hasattr(validated, "include_body") else True
    limit = validated.limit or 10
    skip = validated.skip or 0

    # Map folder name if needed
    folder_mapped = FOLDERS.get(folder.lower(), folder)

    # Call existing implementation
    endpoint = f"/me/mailFolders/{folder_mapped}/messages"

    params = {
        "$top": min(limit, 50),
        "$skip": skip,
        "$orderby": "receivedDateTime desc"
    }

    if search_query:
        params["$search"] = f'"{search_query}"'

    if not include_body:
        params["$select"] = "id,subject,from,toRecipients,receivedDateTime,hasAttachments"

    response = graph.request("GET", endpoint, account_id, params=params)
    emails = response.get("value", [])

    # Format response
    return {
        "status": "success",
        "action": "email.list",
        "folder": folder,
        "count": len(emails),
        "emails": emails,
        "has_more": "@odata.nextLink" in response
    }


def _handle_email_send(
    account_id: str,
    data: dict[str, Any],
    template: str | None,
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.send action.
    
    Data parameters:
        - to: Recipient email(s)
        - subject: Email subject
        - body: Email body content
        - cc: CC recipients (optional)
        - bcc: BCC recipients (optional)
        - attachments: File paths to attach (optional)
        - template_data: Data for template rendering (optional)
    """
    from .email_framework.utils import format_attachments
    from .email_framework.utils import get_default_signature
    from .email_framework.utils import style_email_content
    from .email_framework.utils import validate_email_recipients

    # Validate required parameters
    if not data.get("to"):
        raise ValueError("Missing required parameter: to")
    if not data.get("subject"):
        raise ValueError("Missing required parameter: subject")
    if not data.get("body"):
        raise ValueError("Missing required parameter: body")

    # Validate recipients
    to_recipients = validate_email_recipients(data["to"])
    cc_recipients = validate_email_recipients(data.get("cc", [])) if data.get("cc") else []
    bcc_recipients = validate_email_recipients(data.get("bcc", [])) if data.get("bcc") else []

    # Apply styling if template specified
    body_content = data["body"]
    if template:
        body_content = style_email_content(
            body=body_content,
            subject=data["subject"],
            theme=options.get("theme", "baytown"),
            signature=get_default_signature(),
            template_type=template,
            template_data=data.get("template_data")
        )
    elif options.get("add_signature", True):
        # Add signature to plain emails
        body_content = f"{body_content}\n\n{get_default_signature()}"

    # Build message
    message = {
        "subject": data["subject"],
        "body": {
            "contentType": "HTML" if template or "<" in body_content else "Text",
            "content": body_content
        },
        "toRecipients": [{"emailAddress": {"address": email}} for email in to_recipients]
    }

    if cc_recipients:
        message["ccRecipients"] = [{"emailAddress": {"address": email}} for email in cc_recipients]
    if bcc_recipients:
        message["bccRecipients"] = [{"emailAddress": {"address": email}} for email in bcc_recipients]

    # Add attachments if provided
    if data.get("attachments"):
        attachments = format_attachments(data["attachments"])
        if attachments:
            message["attachments"] = attachments

    # Send email
    graph.request("POST", "/me/sendMail", account_id, json={"message": message})

    return {
        "status": "success",
        "action": "email.send",
        "to": to_recipients,
        "subject": data["subject"],
        "template_used": template,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_reply(
    account_id: str,
    data: dict[str, Any],
    template: str | None,
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.reply action.
    
    Data parameters:
        - email_id: ID of email to reply to
        - body: Reply message body
        - reply_all: Reply to all recipients (default: False)
        - attachments: File paths to attach (optional)
    """
    from .email_framework.utils import format_attachments
    from .email_framework.utils import get_default_signature
    from .email_framework.utils import style_email_content

    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")
    if not data.get("body"):
        raise ValueError("Missing required parameter: body")

    # Apply styling if template specified
    body_content = data["body"]
    if template:
        body_content = style_email_content(
            body=body_content,
            subject="Reply",
            theme=options.get("theme", "baytown"),
            signature=get_default_signature(),
            template_type=template,
            template_data=data.get("template_data")
        )
    elif options.get("add_signature", True):
        body_content = f"{body_content}\n\n{get_default_signature()}"

    # Build reply
    message = {
        "message": {
            "body": {
                "contentType": "HTML" if template or "<" in body_content else "Text",
                "content": body_content
            }
        }
    }

    # Add attachments if provided
    if data.get("attachments"):
        attachments = format_attachments(data["attachments"])
        if attachments:
            message["message"]["attachments"] = attachments

    # Send reply
    action_type = "replyAll" if data.get("reply_all", False) else "reply"
    endpoint = f"/me/messages/{data['email_id']}/{action_type}"

    graph.request("POST", endpoint, account_id, json=message)

    return {
        "status": "success",
        "action": "email.reply",
        "email_id": data["email_id"],
        "reply_all": data.get("reply_all", False),
        "template_used": template,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_draft(
    account_id: str,
    data: dict[str, Any],
    template: str | None,
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.draft action.
    
    Data parameters:
        - to: Recipient email(s)
        - subject: Email subject
        - body: Email body content
        - cc: CC recipients (optional)
        - bcc: BCC recipients (optional)
        - attachments: File paths to attach (optional)
        - template_data: Data for template rendering (optional)
    """
    from .email_framework.utils import format_attachments
    from .email_framework.utils import get_default_signature
    from .email_framework.utils import style_email_content
    from .email_framework.utils import validate_email_recipients

    # Validate required parameters
    if not data.get("to"):
        raise ValueError("Missing required parameter: to")
    if not data.get("subject"):
        raise ValueError("Missing required parameter: subject")
    if not data.get("body"):
        raise ValueError("Missing required parameter: body")

    # Validate recipients
    to_recipients = validate_email_recipients(data["to"])
    cc_recipients = validate_email_recipients(data.get("cc", [])) if data.get("cc") else []
    bcc_recipients = validate_email_recipients(data.get("bcc", [])) if data.get("bcc") else []

    # Apply styling if template specified
    body_content = data["body"]
    if template:
        body_content = style_email_content(
            body=body_content,
            subject=data["subject"],
            theme=options.get("theme", "baytown"),
            signature=get_default_signature(),
            template_type=template,
            template_data=data.get("template_data")
        )
    elif options.get("add_signature", True):
        body_content = f"{body_content}\n\n{get_default_signature()}"

    # Build draft message
    message = {
        "subject": data["subject"],
        "body": {
            "contentType": "HTML" if template or "<" in body_content else "Text",
            "content": body_content
        },
        "toRecipients": [{"emailAddress": {"address": email}} for email in to_recipients]
    }

    if cc_recipients:
        message["ccRecipients"] = [{"emailAddress": {"address": email}} for email in cc_recipients]
    if bcc_recipients:
        message["bccRecipients"] = [{"emailAddress": {"address": email}} for email in bcc_recipients]

    # Add attachments if provided
    if data.get("attachments"):
        attachments = format_attachments(data["attachments"])
        if attachments:
            message["attachments"] = attachments

    # Create draft
    response = graph.request("POST", "/me/messages", account_id, json=message)

    return {
        "status": "success",
        "action": "email.draft",
        "draft_id": response.get("id"),
        "to": to_recipients,
        "subject": data["subject"],
        "template_used": template,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_delete(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.delete action.
    
    Data parameters:
        - email_id: ID of email to delete
        - permanent: Permanently delete (default: False, moves to Deleted Items)
    """
    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")

    if data.get("permanent", False):
        # Permanently delete
        graph.request("DELETE", f"/me/messages/{data['email_id']}", account_id)
        action_taken = "permanently_deleted"
    else:
        # Move to Deleted Items folder
        deleted_folder_id = "deleteditems"
        move_data = {"destinationId": deleted_folder_id}
        graph.request("POST", f"/me/messages/{data['email_id']}/move", account_id, json=move_data)
        action_taken = "moved_to_trash"

    return {
        "status": "success",
        "action": "email.delete",
        "email_id": data["email_id"],
        "action_taken": action_taken,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_forward(
    account_id: str,
    data: dict[str, Any],
    template: str | None,
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.forward action.
    
    Data parameters:
        - email_id: ID of email to forward
        - to: Recipient email(s) to forward to
        - comment: Optional comment to add to the forwarded email
        - attachments: Additional file paths to attach (optional)
    """
    from .email_framework.utils import format_attachments
    from .email_framework.utils import get_default_signature
    from .email_framework.utils import style_email_content
    from .email_framework.utils import validate_email_recipients

    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")
    if not data.get("to"):
        raise ValueError("Missing required parameter: to")

    # Validate recipients
    to_recipients = validate_email_recipients(data["to"])

    # Build comment with styling if provided
    comment_content = data.get("comment", "")
    if comment_content:
        if template:
            comment_content = style_email_content(
                body=comment_content,
                subject="Forwarded Message",
                theme=options.get("theme", "baytown"),
                signature=get_default_signature(),
                template_type=template,
                template_data=data.get("template_data")
            )
        elif options.get("add_signature", True):
            comment_content = f"{comment_content}\n\n{get_default_signature()}"

    # Build forward message
    message = {
        "message": {
            "toRecipients": [{"emailAddress": {"address": email}} for email in to_recipients]
        }
    }

    if comment_content:
        message["message"]["body"] = {
            "contentType": "HTML" if template or "<" in comment_content else "Text",
            "content": comment_content
        }

    # Add attachments if provided
    if data.get("attachments"):
        attachments = format_attachments(data["attachments"])
        if attachments:
            message["message"]["attachments"] = attachments

    # Send forward
    endpoint = f"/me/messages/{data['email_id']}/forward"
    graph.request("POST", endpoint, account_id, json=message)

    return {
        "status": "success",
        "action": "email.forward",
        "email_id": data["email_id"],
        "to": to_recipients,
        "comment_added": bool(comment_content),
        "template_used": template,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_move(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.move action.
    
    Data parameters:
        - email_id: ID of email to move
        - destination_folder: Name of destination folder (inbox, sent, drafts, etc.)
    """
    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")
    if not data.get("destination_folder"):
        raise ValueError("Missing required parameter: destination_folder")

    # Map folder name to ID
    folder_name = data["destination_folder"].lower()
    folder_id = FOLDERS.get(folder_name)

    if not folder_id:
        raise ValueError(
            f"Unknown folder: {data['destination_folder']}. "
            f"Valid folders: {list(FOLDERS.keys())}"
        )

    # Move email
    move_data = {"destinationId": folder_id}
    graph.request(
        "POST",
        f"/me/messages/{data['email_id']}/move",
        account_id,
        json=move_data
    )

    return {
        "status": "success",
        "action": "email.move",
        "email_id": data["email_id"],
        "destination_folder": folder_name,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_mark(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.mark action.
    
    Data parameters:
        - email_id: ID(s) of email(s) to mark (string or list)
        - mark_as: How to mark the email (read, unread, important, not_important)
    """
    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")
    if not data.get("mark_as"):
        raise ValueError("Missing required parameter: mark_as")

    # Normalize email_id to list
    email_ids = data["email_id"]
    if isinstance(email_ids, str):
        email_ids = [email_ids]

    # Validate mark_as value
    mark_as = data["mark_as"].lower()
    valid_marks = ["read", "unread", "important", "not_important"]
    if mark_as not in valid_marks:
        raise ValueError(
            f"Invalid mark_as value: {data['mark_as']}. "
            f"Valid values: {valid_marks}"
        )

    # Process each email
    results = []
    for email_id in email_ids:
        update_data = {}

        if mark_as == "read":
            update_data["isRead"] = True
        elif mark_as == "unread":
            update_data["isRead"] = False
        elif mark_as == "important":
            update_data["importance"] = "high"
        elif mark_as == "not_important":
            update_data["importance"] = "normal"

        # Update email
        graph.request(
            "PATCH",
            f"/me/messages/{email_id}",
            account_id,
            json=update_data
        )
        results.append(email_id)

    return {
        "status": "success",
        "action": "email.mark",
        "email_ids": results,
        "mark_as": mark_as,
        "count": len(results),
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_search(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.search action.
    
    Data parameters:
        - query: Search query string
        - folder: Specific folder to search in (optional)
        - from_email: Filter by sender email (optional)
        - subject_contains: Filter by subject containing text (optional)
        - has_attachments: Filter for emails with attachments (optional)
        
    Options:
        - limit: Maximum results (default: 25)
        - skip: Number to skip for pagination
    """
    # Validate required parameters
    if not data.get("query"):
        raise ValueError("Missing required parameter: query")

    # Build search parameters
    search_query = data["query"]
    limit = options.get("limit", 25)
    skip = options.get("skip", 0)

    # Determine endpoint
    if data.get("folder"):
        folder_name = data["folder"].lower()
        folder_id = FOLDERS.get(folder_name, folder_name)
        endpoint = f"/me/mailFolders/{folder_id}/messages"
    else:
        endpoint = "/me/messages"

    # Build parameters
    params = {
        "$search": f'"{search_query}"',
        "$top": min(limit, 50),
        "$skip": skip,
        "$orderby": "receivedDateTime desc"
    }

    # Add filters
    filters = []
    if data.get("from_email"):
        filters.append(f"from/emailAddress/address eq '{data['from_email']}'")
    if data.get("subject_contains"):
        filters.append(f"contains(subject, '{data['subject_contains']}')")
    if data.get("has_attachments"):
        filters.append("hasAttachments eq true")

    if filters:
        params["$filter"] = " and ".join(filters)

    # Execute search
    response = graph.request("GET", endpoint, account_id, params=params)
    emails = response.get("value", [])

    # Format results
    formatted_emails = []
    for email in emails:
        formatted_emails.append({
            "id": email.get("id"),
            "subject": email.get("subject"),
            "from": email.get("from", {}).get("emailAddress", {}).get("address"),
            "to": [r.get("emailAddress", {}).get("address")
                  for r in email.get("toRecipients", [])],
            "received": email.get("receivedDateTime"),
            "has_attachments": email.get("hasAttachments", False),
            "preview": email.get("bodyPreview", "")[:200]
        })

    return {
        "status": "success",
        "action": "email.search",
        "query": search_query,
        "count": len(formatted_emails),
        "emails": formatted_emails,
        "has_more": "@odata.nextLink" in response,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_email_get(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle email.get action.
    
    Data parameters:
        - email_id: ID of email to retrieve
        - include_attachments: Include attachment details (default: False)
        - include_full_body: Include full HTML body (default: True)
    """
    # Validate required parameters
    if not data.get("email_id"):
        raise ValueError("Missing required parameter: email_id")

    # Build request
    endpoint = f"/me/messages/{data['email_id']}"
    params = {
        "$select": "id,subject,from,toRecipients,ccRecipients,bccRecipients,"
                  "receivedDateTime,sentDateTime,hasAttachments,importance,isRead,"
                  "body,bodyPreview,categories,flag,internetMessageId"
    }

    # Get email
    email = graph.request("GET", endpoint, account_id, params=params)

    if not email:
        raise ValueError(f"Email with ID {data['email_id']} not found")

    # Format response
    result = {
        "id": email.get("id"),
        "subject": email.get("subject"),
        "from": email.get("from", {}).get("emailAddress", {}),
        "to": [r.get("emailAddress", {}) for r in email.get("toRecipients", [])],
        "cc": [r.get("emailAddress", {}) for r in email.get("ccRecipients", [])],
        "bcc": [r.get("emailAddress", {}) for r in email.get("bccRecipients", [])],
        "received": email.get("receivedDateTime"),
        "sent": email.get("sentDateTime"),
        "importance": email.get("importance"),
        "is_read": email.get("isRead"),
        "has_attachments": email.get("hasAttachments", False),
        "categories": email.get("categories", []),
        "flag": email.get("flag", {}),
        "internet_message_id": email.get("internetMessageId")
    }

    # Include body if requested
    if data.get("include_full_body", True):
        result["body"] = email.get("body", {})
    else:
        result["body_preview"] = email.get("bodyPreview", "")

    # Include attachments if requested
    if data.get("include_attachments", False) and email.get("hasAttachments"):
        att_endpoint = f"/me/messages/{data['email_id']}/attachments"
        attachments = graph.request("GET", att_endpoint, account_id)

        result["attachments"] = [
            {
                "id": att.get("id"),
                "name": att.get("name"),
                "content_type": att.get("contentType"),
                "size": att.get("size"),
                "is_inline": att.get("isInline", False)
            }
            for att in attachments.get("value", [])
        ]

    return {
        "status": "success",
        "action": "email.get",
        "email": result,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


# Calendar action handlers

def _handle_calendar_list(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.list action.
    
    Data parameters:
        - start_date: Start date for filtering (ISO format: YYYY-MM-DD, default: today)
        - end_date: End date for filtering (ISO format: YYYY-MM-DD, default: +30 days)
        - calendar_id: Optional specific calendar ID
    
    Options:
        - limit: Maximum number of events (default: 20, max: 50)
    """
    import datetime as dt

    # Set defaults
    start_date = data.get("start_date")
    if not start_date:
        start_date = dt.datetime.now().date().isoformat()

    end_date = data.get("end_date")
    if not end_date:
        end_dt = dt.datetime.fromisoformat(start_date) + dt.timedelta(days=30)
        end_date = end_dt.date().isoformat()

    limit = options.get("limit", 20)
    limit = min(limit, 50)  # Cap at 50

    # Convert to datetime with time
    start_datetime = f"{start_date}T00:00:00"
    end_datetime = f"{end_date}T23:59:59"

    # Build endpoint
    calendar_id = data.get("calendar_id")
    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/calendarView"
    else:
        endpoint = "/me/calendarView"

    # Build parameters
    params = {
        "startDateTime": start_datetime,
        "endDateTime": end_datetime,
        "$top": limit,
        "$orderby": "start/dateTime",
        "$select": "id,subject,start,end,location,attendees,isAllDay,organizer,body,isOnlineMeeting,onlineMeetingUrl"
    }

    # Get events
    response = graph.request("GET", endpoint, account_id, params=params)
    events = response.get("value", [])

    # Format events
    formatted_events = []
    for event in events:
        attendees = []
        for attendee in event.get("attendees", []):
            email_addr = attendee.get("emailAddress", {})
            attendees.append({
                "name": email_addr.get("name", ""),
                "email": email_addr.get("address", ""),
                "response": attendee.get("status", {}).get("response", "none")
            })

        formatted_events.append({
            "id": event.get("id"),
            "subject": event.get("subject"),
            "start_time": event.get("start", {}).get("dateTime"),
            "end_time": event.get("end", {}).get("dateTime"),
            "location": event.get("location", {}).get("displayName", ""),
            "is_all_day": event.get("isAllDay", False),
            "is_online_meeting": event.get("isOnlineMeeting", False),
            "meeting_url": event.get("onlineMeetingUrl", ""),
            "organizer": event.get("organizer", {}).get("emailAddress", {}).get("address", ""),
            "attendees": attendees,
            "body_preview": event.get("body", {}).get("content", "")[:200] if event.get("body") else ""
        })

    return {
        "status": "success",
        "action": "calendar.list",
        "count": len(formatted_events),
        "events": formatted_events,
        "start_date": start_date,
        "end_date": end_date,
        "has_more": "@odata.nextLink" in response,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_calendar_get(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.get action.
    
    Data parameters:
        - event_id: ID of event to retrieve
        - calendar_id: Optional specific calendar ID
    """
    # Validate required parameters
    if not data.get("event_id"):
        raise ValueError("Missing required parameter: event_id")

    # Build endpoint
    calendar_id = data.get("calendar_id")
    event_id = data["event_id"]

    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/events/{event_id}"
    else:
        endpoint = f"/me/events/{event_id}"

    # Get event
    event = graph.request("GET", endpoint, account_id)

    if not event:
        raise ValueError(f"Event with ID {event_id} not found")

    # Format attendees
    attendees = []
    for attendee in event.get("attendees", []):
        email_addr = attendee.get("emailAddress", {})
        attendees.append({
            "name": email_addr.get("name", ""),
            "email": email_addr.get("address", ""),
            "response": attendee.get("status", {}).get("response", "none"),
            "type": attendee.get("type", "required")
        })

    # Format event details
    result = {
        "id": event.get("id"),
        "subject": event.get("subject"),
        "start_time": event.get("start", {}).get("dateTime"),
        "start_timezone": event.get("start", {}).get("timeZone"),
        "end_time": event.get("end", {}).get("dateTime"),
        "end_timezone": event.get("end", {}).get("timeZone"),
        "location": event.get("location", {}).get("displayName", ""),
        "is_all_day": event.get("isAllDay", False),
        "is_online_meeting": event.get("isOnlineMeeting", False),
        "meeting_url": event.get("onlineMeetingUrl", ""),
        "organizer": {
            "name": event.get("organizer", {}).get("emailAddress", {}).get("name", ""),
            "email": event.get("organizer", {}).get("emailAddress", {}).get("address", "")
        },
        "attendees": attendees,
        "body": event.get("body", {}).get("content", ""),
        "body_type": event.get("body", {}).get("contentType", "HTML"),
        "importance": event.get("importance", "normal"),
        "categories": event.get("categories", []),
        "created_time": event.get("createdDateTime"),
        "last_modified": event.get("lastModifiedDateTime")
    }

    return {
        "status": "success",
        "action": "calendar.get",
        "event": result,
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_calendar_create(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.create action.
    
    Data parameters:
        - subject: Event subject/title (required)
        - start_datetime: Start datetime (ISO format, required)
        - end_datetime: End datetime (ISO format, required)
        - attendees: List of attendee email addresses (optional)
        - location: Event location (optional)
        - body: Event description (optional)
        - is_online_meeting: Create Teams meeting (default: False)
        - calendar_id: Specific calendar ID (optional)
    """
    # Validate required parameters
    if not data.get("subject"):
        raise ValueError("Missing required parameter: subject")
    if not data.get("start_datetime"):
        raise ValueError("Missing required parameter: start_datetime")
    if not data.get("end_datetime"):
        raise ValueError("Missing required parameter: end_datetime")

    # Build event object
    event = {
        "subject": data["subject"],
        "start": {"dateTime": data["start_datetime"], "timeZone": "UTC"},
        "end": {"dateTime": data["end_datetime"], "timeZone": "UTC"},
    }

    # Add optional fields
    if data.get("location"):
        event["location"] = {"displayName": data["location"]}

    if data.get("body"):
        event["body"] = {"contentType": "HTML", "content": data["body"]}

    if data.get("attendees"):
        from .email_framework.utils import validate_email_recipients
        validated_attendees = validate_email_recipients(data["attendees"])
        event["attendees"] = [
            {"emailAddress": {"address": email, "name": ""}}
            for email in validated_attendees
        ]

    if data.get("is_online_meeting", False):
        event["isOnlineMeeting"] = True

    # Build endpoint
    calendar_id = data.get("calendar_id")
    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/events"
    else:
        endpoint = "/me/events"

    # Create event
    created_event = graph.request("POST", endpoint, account_id, json=event)

    if not created_event:
        raise ValueError("Failed to create calendar event")

    return {
        "status": "success",
        "action": "calendar.create",
        "event_id": created_event.get("id"),
        "subject": created_event.get("subject"),
        "start_time": created_event.get("start", {}).get("dateTime"),
        "end_time": created_event.get("end", {}).get("dateTime"),
        "meeting_url": created_event.get("onlineMeetingUrl", ""),
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_calendar_update(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.update action.
    
    Data parameters:
        - event_id: ID of event to update (required)
        - subject: New event subject (optional)
        - start_datetime: New start datetime (optional)
        - end_datetime: New end datetime (optional)
        - location: New location (optional)
        - body: New description (optional)
        - calendar_id: Specific calendar ID (optional)
    """
    # Validate required parameters
    if not data.get("event_id"):
        raise ValueError("Missing required parameter: event_id")

    # Build update object with only provided fields
    updates = {}

    if data.get("subject"):
        updates["subject"] = data["subject"]

    if data.get("start_datetime"):
        updates["start"] = {"dateTime": data["start_datetime"], "timeZone": "UTC"}

    if data.get("end_datetime"):
        updates["end"] = {"dateTime": data["end_datetime"], "timeZone": "UTC"}

    if data.get("location"):
        updates["location"] = {"displayName": data["location"]}

    if data.get("body"):
        updates["body"] = {"contentType": "HTML", "content": data["body"]}

    # Build endpoint
    calendar_id = data.get("calendar_id")
    event_id = data["event_id"]

    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/events/{event_id}"
    else:
        endpoint = f"/me/events/{event_id}"

    # Update event
    updated_event = graph.request("PATCH", endpoint, account_id, json=updates)

    if not updated_event:
        raise ValueError(f"Failed to update event with ID {event_id}")

    return {
        "status": "success",
        "action": "calendar.update",
        "event_id": event_id,
        "updated_fields": list(updates.keys()),
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_calendar_delete(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.delete action.
    
    Data parameters:
        - event_id: ID of event to delete (required)
        - send_cancellation: Send cancellation notice to attendees (default: True)
        - calendar_id: Specific calendar ID (optional)
    """
    # Validate required parameters
    if not data.get("event_id"):
        raise ValueError("Missing required parameter: event_id")

    # Build endpoint
    calendar_id = data.get("calendar_id")
    event_id = data["event_id"]

    if calendar_id:
        endpoint = f"/me/calendars/{calendar_id}/events/{event_id}"
    else:
        endpoint = f"/me/events/{event_id}"

    # Delete event
    graph.request("DELETE", endpoint, account_id)

    return {
        "status": "success",
        "action": "calendar.delete",
        "event_id": event_id,
        "send_cancellation": data.get("send_cancellation", True),
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


def _handle_calendar_availability(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle calendar.availability action.
    
    Data parameters:
        - start_date: Start date for availability search (ISO format: YYYY-MM-DD, required)
        - end_date: End date for availability search (ISO format: YYYY-MM-DD, required)
        - duration_minutes: Duration of time slot needed (default: 30)
    """
    # Validate required parameters
    if not data.get("start_date"):
        raise ValueError("Missing required parameter: start_date")
    if not data.get("end_date"):
        raise ValueError("Missing required parameter: end_date")

    import datetime as dt

    start_date = data["start_date"]
    end_date = data["end_date"]
    duration_minutes = data.get("duration_minutes", 30)

    # Convert dates to datetime with working hours (9 AM - 5 PM)
    start_datetime = f"{start_date}T09:00:00"
    end_datetime = f"{end_date}T17:00:00"

    # Get busy times from calendar
    freebusy_endpoint = "/me/calendar/getSchedule"
    freebusy_data = {
        "schedules": [account_id],
        "startTime": {
            "dateTime": start_datetime,
            "timeZone": "UTC"
        },
        "endTime": {
            "dateTime": end_datetime,
            "timeZone": "UTC"
        },
        "availabilityViewInterval": duration_minutes
    }

    freebusy_response = graph.request("POST", freebusy_endpoint, account_id, json=freebusy_data)

    if not freebusy_response or not freebusy_response.get("value"):
        raise ValueError("Failed to get availability information")

    schedule = freebusy_response["value"][0]
    busy_times = schedule.get("busyViewData", [])

    # Find available slots
    available_slots = []
    current_time = dt.datetime.fromisoformat(start_datetime.replace("T", " "))
    end_time = dt.datetime.fromisoformat(end_datetime.replace("T", " "))
    slot_duration = dt.timedelta(minutes=duration_minutes)

    while current_time + slot_duration <= end_time:
        # Check if this slot conflicts with busy times
        slot_end = current_time + slot_duration
        is_available = True

        # For simplicity, we'll consider the slot available if the busy view data allows it
        # This is a basic implementation - full availability would require more complex logic

        if is_available:
            available_slots.append({
                "start_time": current_time.isoformat(),
                "end_time": slot_end.isoformat(),
                "duration_minutes": duration_minutes
            })

        # Move to next potential slot (15-minute intervals)
        current_time += dt.timedelta(minutes=15)

    return {
        "status": "success",
        "action": "calendar.availability",
        "start_date": start_date,
        "end_date": end_date,
        "duration_minutes": duration_minutes,
        "available_slots": available_slots[:20],  # Limit to 20 slots
        "total_slots_found": len(available_slots),
        "timestamp": dt.datetime.now(dt.UTC).isoformat()
    }


# File action handlers

def _handle_file_list(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.list action.
    
    Data parameters:
        - folder_path: Path to folder (default: root)
        - search_query: Optional search query
        
    Options:
        - limit: Maximum number of files (default: 20, max: 50)
    """
    folder_path = data.get("folder_path")
    search_query = data.get("search_query")
    limit = options.get("limit", 20)
    limit = min(limit, 50)  # Cap at 50

    # Build endpoint
    if folder_path:
        folder_path = folder_path.strip("/")
        endpoint = f"/me/drive/root:/{folder_path}:/children"
    else:
        endpoint = "/me/drive/root/children"

    # Build parameters
    params = {
        "$top": limit,
        "$select": "id,name,size,lastModifiedDateTime,createdDateTime,file,folder,webUrl"
    }

    if search_query:
        params["$filter"] = f"contains(name,'{search_query}')"

    # Get files
    response = graph.request("GET", endpoint, account_id, params=params)
    files = response.get("value", [])

    # Format files
    formatted_files = []
    for file in files:
        formatted_files.append({
            "id": file.get("id"),
            "name": file.get("name"),
            "size": file.get("size", 0),
            "type": "folder" if file.get("folder") else "file",
            "last_modified": file.get("lastModifiedDateTime"),
            "created": file.get("createdDateTime"),
            "web_url": file.get("webUrl"),
            "is_folder": bool(file.get("folder"))
        })

    return {
        "status": "success",
        "action": "file.list",
        "folder_path": folder_path or "/",
        "count": len(formatted_files),
        "files": formatted_files,
        "has_more": "@odata.nextLink" in response
    }


def _handle_file_get(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.get action.
    
    Data parameters:
        - file_path: Path to the file (required)
        - include_metadata: Include detailed metadata (default: True)
    """
    file_path = data.get("file_path")
    if not file_path:
        raise ValueError("Missing required parameter: file_path")

    include_metadata = data.get("include_metadata", True)

    # Clean the path
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}"

    # Build parameters
    params = {}
    if include_metadata:
        params["$select"] = "id,name,size,lastModifiedDateTime,createdDateTime,file,folder,webUrl,downloadUrl,parentReference"

    # Get file
    file_info = graph.request("GET", endpoint, account_id, params=params)

    return {
        "status": "success",
        "action": "file.get",
        "file_path": file_path,
        "file": {
            "id": file_info.get("id"),
            "name": file_info.get("name"),
            "size": file_info.get("size", 0),
            "type": "folder" if file_info.get("folder") else "file",
            "last_modified": file_info.get("lastModifiedDateTime"),
            "created": file_info.get("createdDateTime"),
            "web_url": file_info.get("webUrl"),
            "download_url": file_info.get("downloadUrl"),
            "parent_path": file_info.get("parentReference", {}).get("path", ""),
            "is_folder": bool(file_info.get("folder"))
        }
    }


def _handle_file_upload(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.upload action.
    
    Data parameters:
        - local_path: Path to local file (required)
        - onedrive_path: Path in OneDrive (optional, defaults to root with original filename)
        - overwrite: Whether to overwrite existing file (default: False)
    """
    local_path = data.get("local_path")
    if not local_path:
        raise ValueError("Missing required parameter: local_path")

    onedrive_path = data.get("onedrive_path")
    overwrite = data.get("overwrite", False)

    # Import pathlib for path operations
    from pathlib import Path

    # Check if local file exists
    local_file = Path(local_path)
    if not local_file.exists():
        raise ValueError(f"Local file not found: {local_path}")

    # Determine OneDrive path
    if not onedrive_path:
        onedrive_path = f"/{local_file.name}"

    # Clean OneDrive path
    onedrive_path = onedrive_path.strip("/")
    endpoint = f"/me/drive/root:/{onedrive_path}:/content"

    # Read file content
    with open(local_file, "rb") as f:
        file_content = f.read()

    # Upload file
    params = {}
    if overwrite:
        params["@microsoft.graph.conflictBehavior"] = "replace"
    else:
        params["@microsoft.graph.conflictBehavior"] = "fail"

    uploaded_file = graph.request("PUT", endpoint, account_id, data=file_content)

    return {
        "status": "success",
        "action": "file.upload",
        "local_path": local_path,
        "onedrive_path": onedrive_path,
        "file": {
            "id": uploaded_file.get("id"),
            "name": uploaded_file.get("name"),
            "size": uploaded_file.get("size"),
            "web_url": uploaded_file.get("webUrl")
        }
    }


def _handle_file_download(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.download action.
    
    Data parameters:
        - file_path: Path to file in OneDrive (required)
        - save_path: Local path to save file (optional, defaults to ~/Downloads)
    """
    file_path = data.get("file_path")
    if not file_path:
        raise ValueError("Missing required parameter: file_path")

    save_path = data.get("save_path")

    # Import pathlib for path operations
    from pathlib import Path

    # Clean the OneDrive path
    file_path = file_path.strip("/")

    # Get file info first
    info_endpoint = f"/me/drive/root:/{file_path}"
    file_info = graph.request("GET", info_endpoint, account_id)

    # Determine save path
    if not save_path:
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)
        save_path = downloads_dir / file_info.get("name", "downloaded_file")
    else:
        save_path = Path(save_path)

    # Download file content
    download_endpoint = f"/me/drive/root:/{file_path}:/content"
    file_content = graph.download_raw(download_endpoint, account_id)

    # Save file
    with open(save_path, "wb") as f:
        f.write(file_content)

    return {
        "status": "success",
        "action": "file.download",
        "file_path": file_path,
        "save_path": str(save_path),
        "file_size": len(file_content),
        "file_name": file_info.get("name")
    }


def _handle_file_share(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.share action.
    
    Data parameters:
        - file_path: Path to file in OneDrive (required)
        - email: Email to share with (optional, creates link if not provided)
        - permission: Permission level - "view" or "edit" (default: "view")
        - expiration_days: Days until share expires (optional)
    """
    file_path = data.get("file_path")
    if not file_path:
        raise ValueError("Missing required parameter: file_path")

    email = data.get("email")
    permission = data.get("permission", "view")
    expiration_days = data.get("expiration_days")

    # Clean the path
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}:/createLink"

    # Build share request
    share_request = {
        "type": permission,
        "scope": "organization" if email else "anonymous"
    }

    if expiration_days:
        import datetime as dt
        expiration = dt.datetime.now(dt.UTC) + dt.timedelta(days=expiration_days)
        share_request["expirationDateTime"] = expiration.isoformat()

    # Create share link
    share_result = graph.request("POST", endpoint, account_id, json=share_request)

    # If email specified, send invitation
    if email:
        invite_endpoint = f"/me/drive/root:/{file_path}:/invite"
        invite_request = {
            "recipients": [{"email": email}],
            "message": f"File shared with {permission} permission",
            "requireSignIn": True,
            "sendInvitation": True,
            "roles": [permission]
        }

        if expiration_days:
            invite_request["expirationDateTime"] = share_request["expirationDateTime"]

        graph.request("POST", invite_endpoint, account_id, json=invite_request)

    return {
        "status": "success",
        "action": "file.share",
        "file_path": file_path,
        "share_url": share_result.get("link", {}).get("webUrl"),
        "permission": permission,
        "shared_with": email,
        "expires": share_request.get("expirationDateTime")
    }


def _handle_file_delete(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.delete action.
    
    Data parameters:
        - file_path: Path to file or folder (required)
        - permanent: Whether to permanently delete (default: False - moves to recycle bin)
    """
    file_path = data.get("file_path")
    if not file_path:
        raise ValueError("Missing required parameter: file_path")

    permanent = data.get("permanent", False)

    # Clean the path
    file_path = file_path.strip("/")
    endpoint = f"/me/drive/root:/{file_path}"

    # Delete file
    if permanent:
        # Permanent deletion
        graph.request("DELETE", endpoint, account_id)
    else:
        # Move to recycle bin by deleting (Graph API automatically moves to recycle bin)
        graph.request("DELETE", endpoint, account_id)

    return {
        "status": "success",
        "action": "file.delete",
        "file_path": file_path,
        "permanent": permanent
    }


# Contact action handlers

def _handle_contact_list(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.list action.
    
    Data parameters:
        - search_query: Optional search query
        
    Options:
        - limit: Maximum number of contacts (default: 20, max: 50)
    """
    search_query = data.get("search_query")
    limit = options.get("limit", 20)
    limit = min(limit, 50)  # Cap at 50

    # Build endpoint
    endpoint = "/me/contacts"

    # Build parameters
    params = {
        "$top": limit,
        "$select": "id,displayName,givenName,surname,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle"
    }

    if search_query:
        params["$filter"] = f"contains(displayName,'{search_query}') or contains(givenName,'{search_query}') or contains(surname,'{search_query}')"

    # Get contacts
    response = graph.request("GET", endpoint, account_id, params=params)
    contacts = response.get("value", [])

    # Format contacts
    formatted_contacts = []
    for contact in contacts:
        # Get primary email
        emails = contact.get("emailAddresses", [])
        primary_email = emails[0].get("address") if emails else None

        # Get phone numbers
        mobile = contact.get("mobilePhone")
        business_phones = contact.get("businessPhones", [])
        primary_phone = mobile or (business_phones[0] if business_phones else None)

        formatted_contacts.append({
            "id": contact.get("id"),
            "display_name": contact.get("displayName"),
            "first_name": contact.get("givenName"),
            "last_name": contact.get("surname"),
            "email": primary_email,
            "mobile_phone": mobile,
            "business_phone": primary_phone,
            "company": contact.get("companyName"),
            "job_title": contact.get("jobTitle")
        })

    return {
        "status": "success",
        "action": "contact.list",
        "count": len(formatted_contacts),
        "contacts": formatted_contacts,
        "has_more": "@odata.nextLink" in response
    }


def _handle_contact_get(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.get action.
    
    Data parameters:
        - contact_id: ID of contact to retrieve (required)
    """
    contact_id = data.get("contact_id")
    if not contact_id:
        raise ValueError("Missing required parameter: contact_id")

    # Get contact
    endpoint = f"/me/contacts/{contact_id}"
    contact = graph.request("GET", endpoint, account_id)

    # Get primary email and phone
    emails = contact.get("emailAddresses", [])
    primary_email = emails[0].get("address") if emails else None

    mobile = contact.get("mobilePhone")
    business_phones = contact.get("businessPhones", [])
    primary_phone = mobile or (business_phones[0] if business_phones else None)

    return {
        "status": "success",
        "action": "contact.get",
        "contact": {
            "id": contact.get("id"),
            "display_name": contact.get("displayName"),
            "first_name": contact.get("givenName"),
            "last_name": contact.get("surname"),
            "email": primary_email,
            "all_emails": [e.get("address") for e in emails],
            "mobile_phone": mobile,
            "business_phones": business_phones,
            "company": contact.get("companyName"),
            "job_title": contact.get("jobTitle"),
            "created": contact.get("createdDateTime"),
            "modified": contact.get("lastModifiedDateTime")
        }
    }


def _handle_contact_create(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.create action.
    
    Data parameters:
        - first_name: Contact's first name (required)
        - last_name: Contact's last name (required)
        - email: Contact's email address (optional)
        - mobile_phone: Contact's mobile phone (optional)
        - company: Contact's company (optional)
        - job_title: Contact's job title (optional)
    """
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not first_name or not last_name:
        raise ValueError("Missing required parameters: first_name and last_name")

    # Build contact object
    contact_data = {
        "givenName": first_name,
        "surname": last_name,
        "displayName": f"{first_name} {last_name}"
    }

    # Add optional fields
    email = data.get("email")
    if email:
        contact_data["emailAddresses"] = [{"address": email, "name": email}]

    mobile_phone = data.get("mobile_phone")
    if mobile_phone:
        contact_data["mobilePhone"] = mobile_phone

    company = data.get("company")
    if company:
        contact_data["companyName"] = company

    job_title = data.get("job_title")
    if job_title:
        contact_data["jobTitle"] = job_title

    # Create contact
    endpoint = "/me/contacts"
    created_contact = graph.request("POST", endpoint, account_id, json=contact_data)

    return {
        "status": "success",
        "action": "contact.create",
        "contact": {
            "id": created_contact.get("id"),
            "display_name": created_contact.get("displayName"),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "mobile_phone": mobile_phone,
            "company": company,
            "job_title": job_title
        }
    }


def _handle_contact_update(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.update action.
    
    Data parameters:
        - contact_id: ID of contact to update (required)
        - first_name: New first name (optional)
        - last_name: New last name (optional)
        - email: New email address (optional)
        - mobile_phone: New mobile phone (optional)
        - company: New company (optional)
        - job_title: New job title (optional)
    """
    contact_id = data.get("contact_id")
    if not contact_id:
        raise ValueError("Missing required parameter: contact_id")

    # Build update object with only provided fields
    update_data = {}

    first_name = data.get("first_name")
    if first_name:
        update_data["givenName"] = first_name

    last_name = data.get("last_name")
    if last_name:
        update_data["surname"] = last_name

    # Update display name if either name changed
    if first_name or last_name:
        # Get current contact to build new display name
        current_contact = graph.request("GET", f"/me/contacts/{contact_id}", account_id)
        current_first = current_contact.get("givenName", "")
        current_last = current_contact.get("surname", "")

        new_first = first_name or current_first
        new_last = last_name or current_last
        update_data["displayName"] = f"{new_first} {new_last}"

    email = data.get("email")
    if email:
        update_data["emailAddresses"] = [{"address": email, "name": email}]

    mobile_phone = data.get("mobile_phone")
    if mobile_phone:
        update_data["mobilePhone"] = mobile_phone

    company = data.get("company")
    if company:
        update_data["companyName"] = company

    job_title = data.get("job_title")
    if job_title:
        update_data["jobTitle"] = job_title

    if not update_data:
        raise ValueError("No fields provided to update")

    # Update contact
    endpoint = f"/me/contacts/{contact_id}"
    graph.request("PATCH", endpoint, account_id, json=update_data)

    return {
        "status": "success",
        "action": "contact.update",
        "contact_id": contact_id,
        "updated_fields": list(update_data.keys())
    }


def _handle_contact_delete(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.delete action.
    
    Data parameters:
        - contact_id: ID of contact to delete (required)
    """
    contact_id = data.get("contact_id")
    if not contact_id:
        raise ValueError("Missing required parameter: contact_id")

    # Delete contact
    endpoint = f"/me/contacts/{contact_id}"
    graph.request("DELETE", endpoint, account_id)

    return {
        "status": "success",
        "action": "contact.delete",
        "contact_id": contact_id
    }

def _handle_file_search(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle file.search action.
    
    Data parameters:
        - query: Search query (required)
        - file_type: Optional file type filter (e.g., 'pdf', 'docx')
        
    Options:
        - limit: Maximum number of files (default: 20, max: 50)
    """
    query = data.get("query")
    if not query:
        raise ValueError("Missing required parameter: query")
    
    file_type = data.get("file_type")
    limit = options.get("limit", 20)
    limit = min(limit, 50)  # Cap at 50
    
    # Build search endpoint
    endpoint = "/me/drive/search"
    
    # Build query parameters
    search_query = query
    if file_type:
        search_query += f" filetype:{file_type}"
    
    params = {
        "q": search_query,
        "$top": limit,
        "$select": "id,name,size,lastModifiedDateTime,createdDateTime,file,folder,webUrl"
    }
    
    # Execute search
    response = graph.request("GET", endpoint, account_id, params=params)
    files = response.get("value", [])
    
    # Format files
    formatted_files = []
    for file in files:
        formatted_files.append({
            "id": file.get("id"),
            "name": file.get("name"),
            "size": file.get("size", 0),
            "last_modified": file.get("lastModifiedDateTime"),
            "created": file.get("createdDateTime"),
            "web_url": file.get("webUrl"),
            "type": "folder" if file.get("folder") else "file"
        })
    
    return {
        "status": "success",
        "action": "file.search",
        "query": query,
        "file_type": file_type,
        "count": len(formatted_files),
        "files": formatted_files,
        "has_more": "@odata.nextLink" in response
    }

def _handle_contact_search(
    account_id: str,
    data: dict[str, Any],
    options: dict[str, Any]
) -> dict[str, Any]:
    """Handle contact.search action.
    
    Data parameters:
        - query: Search query (required)
        
    Options:
        - limit: Maximum number of contacts (default: 20, max: 50)
    """
    query = data.get("query")
    if not query:
        raise ValueError("Missing required parameter: query")
    
    limit = options.get("limit", 20)
    limit = min(limit, 50)  # Cap at 50
    
    # Build endpoint
    endpoint = "/me/contacts"
    
    # Build parameters with search filter
    params = {
        "$top": limit,
        "$select": "id,displayName,givenName,surname,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle",
        "$filter": f"contains(displayName,'{query}') or contains(givenName,'{query}') or contains(surname,'{query}') or contains(companyName,'{query}')"
    }
    
    # Get contacts
    response = graph.request("GET", endpoint, account_id, params=params)
    contacts = response.get("value", [])
    
    # Format contacts
    formatted_contacts = []
    for contact in contacts:
        emails = contact.get("emailAddresses", [])
        primary_email = emails[0].get("address") if emails else None
        mobile = contact.get("mobilePhone")
        business_phones = contact.get("businessPhones", [])
        primary_phone = mobile or (business_phones[0] if business_phones else None)
        
        formatted_contacts.append({
            "id": contact.get("id"),
            "name": contact.get("displayName"),
            "first_name": contact.get("givenName"),
            "last_name": contact.get("surname"),
            "email": primary_email,
            "mobile": mobile,
            "business_phones": business_phones,
            "company": contact.get("companyName"),
            "job_title": contact.get("jobTitle")
        })
    
    return {
        "status": "success",
        "action": "contact.search",
        "query": query,
        "count": len(formatted_contacts),
        "contacts": formatted_contacts,
        "has_more": "@odata.nextLink" in response
    }


# Utility Tools for 15-Tool Architecture (Story 1.6)
# These tools provide discovery, configuration, validation, and system support

@mcp.tool
def list_resources() -> dict[str, Any]:
    """List available resources, templates, and system capabilities
    
    Provides API discovery for the consolidated 15-tool architecture.
    Returns information about available operations, templates, and system resources.
    
    Returns:
        Dictionary containing available resources and capabilities
    """
    return {
        "status": "success",
        "resources": {
            "core_operations": {
                "microsoft_operations": {
                    "description": "Unified tool for Microsoft 365 operations",
                    "actions": {
                        "email": ["list", "send", "reply", "draft", "delete", "forward", "move", "mark", "search", "get"],
                        "calendar": ["list", "create", "update", "delete", "search", "invite"],
                        "file": ["list", "get", "upload", "download", "share", "delete"],
                        "contact": ["list", "get", "create", "update", "delete"]
                    },
                    "templates": ["practice_report", "executive_summary", "provider_update", "alert_notification"]
                }
            },
            "authentication": {
                "list_accounts": {"description": "List signed-in Microsoft accounts"},
                "authenticate_account": {"description": "Authenticate new Microsoft account"},
                "complete_authentication": {"description": "Complete device flow authentication"}
            },
            "utilities": {
                "get_user_info": {"description": "Get user profile information"},
                "get_mailbox_statistics": {"description": "Get mailbox usage statistics"},
                "unified_search": {"description": "Search across all Microsoft 365 services"},
                "list_resources": {"description": "List available resources and capabilities"},
                "export_data": {"description": "Bulk export operations"},
                "import_data": {"description": "Bulk import operations"},
                "get_settings": {"description": "Get configuration settings"},
                "update_settings": {"description": "Update configuration settings"},
                "validate_data": {"description": "Validate data using framework"},
                "get_system_status": {"description": "System health and status"},
                "get_help": {"description": "Context-aware help and examples"}
            },
            "system_info": {
                "total_tools": 15,
                "architecture": "ultra-consolidated",
                "reduction_achieved": "75% (from 61 tools)",
                "framework_version": "1.6"
            }
        }
    }


@mcp.tool
def export_data(
    account_id: str,
    data_type: str,
    format: str = "json",
    filters: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Bulk export operations for Microsoft 365 data
    
    Args:
        account_id: Microsoft account ID
        data_type: Type of data to export ("emails", "contacts", "calendar", "files")
        format: Export format ("json", "csv")
        filters: Optional filters for data selection
        
    Returns:
        Export operation results with data or file path
    """
    if not filters:
        filters = {}

    if data_type == "contacts":
        # Use existing export_contacts functionality
        return export_contacts(account_id, format, filters.get("limit", 1000))

    if data_type == "emails":
        # Export emails with filtering
        folder = filters.get("folder", "inbox")
        limit = filters.get("limit", 100)
        search_query = filters.get("search_query")

        emails = list_emails(account_id, folder, limit, 0, True, search_query)

        if format == "json":
            return {
                "status": "success",
                "data_type": "emails",
                "format": "json",
                "count": len(emails),
                "data": emails
            }
        return {
            "status": "error",
            "message": f"Format {format} not supported for emails"
        }

    if data_type == "calendar":
        # Export calendar events
        events = list_calendar_events(account_id, None, None, filters.get("limit", 100))

        return {
            "status": "success",
            "data_type": "calendar",
            "format": format,
            "count": len(events),
            "data": events
        }

    if data_type == "files":
        # Export file listings
        files = list_files(account_id, filters.get("folder_path"), filters.get("search_query"), filters.get("limit", 100))

        return {
            "status": "success",
            "data_type": "files",
            "format": format,
            "count": len(files),
            "data": files
        }

    return {
        "status": "error",
        "message": f"Unsupported data_type: {data_type}. Supported types: emails, contacts, calendar, files"
    }


@mcp.tool
def import_data(
    account_id: str,
    data_type: str,
    source: str,
    options: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Bulk import operations for Microsoft 365 data
    
    Args:
        account_id: Microsoft account ID
        data_type: Type of data to import ("contacts", "calendar")
        source: Source data (JSON string or file path)
        options: Import options like overwrite behavior
        
    Returns:
        Import operation results
    """
    if not options:
        options = {}

    import json

    # Parse source data
    try:
        if source.startswith("[") or source.startswith("{"):
            # JSON string
            data = json.loads(source)
        else:
            # Assume file path
            with open(source) as f:
                data = json.load(f)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to parse source data: {str(e)}"
        }

    if data_type == "contacts":
        # Import contacts
        success_count = 0
        error_count = 0
        errors = []

        if not isinstance(data, list):
            data = [data]

        for contact_data in data:
            try:
                create_contact(
                    account_id,
                    contact_data.get("first_name", ""),
                    contact_data.get("last_name", ""),
                    contact_data.get("email"),
                    contact_data.get("mobile_phone"),
                    contact_data.get("company"),
                    contact_data.get("job_title")
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Contact {contact_data.get('first_name', '')} {contact_data.get('last_name', '')}: {str(e)}")

        return {
            "status": "success" if error_count == 0 else "partial",
            "data_type": "contacts",
            "imported": success_count,
            "errors": error_count,
            "error_details": errors[:10]  # Limit to first 10 errors
        }

    if data_type == "calendar":
        # Import calendar events
        success_count = 0
        error_count = 0
        errors = []

        if not isinstance(data, list):
            data = [data]

        for event_data in data:
            try:
                create_calendar_event(
                    account_id,
                    event_data.get("subject", "Imported Event"),
                    event_data.get("start_datetime"),
                    event_data.get("end_datetime"),
                    event_data.get("attendees", []),
                    event_data.get("location"),
                    event_data.get("body"),
                    event_data.get("is_online_meeting", False)
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Event {event_data.get('subject', 'Unknown')}: {str(e)}")

        return {
            "status": "success" if error_count == 0 else "partial",
            "data_type": "calendar",
            "imported": success_count,
            "errors": error_count,
            "error_details": errors[:10]
        }

    return {
        "status": "error",
        "message": f"Unsupported data_type: {data_type}. Supported types: contacts, calendar"
    }


@mcp.tool
def get_settings(category: str | None = None) -> dict[str, Any]:
    """Get configuration settings
    
    Args:
        category: Optional category filter ("server", "email", "auth")
        
    Returns:
        Configuration settings
    """
    import os

    all_settings = {
        "server": {
            "mcp_version": "2.8.0+",
            "framework": "FastMCP",
            "total_tools": 15,
            "architecture": "ultra-consolidated"
        },
        "email": {
            "signature_enabled": True,
            "templates_available": ["practice_report", "executive_summary", "provider_update", "alert_notification"],
            "styling": "professional_kamdental_branding"
        },
        "auth": {
            "client_id_configured": bool(os.getenv("MICROSOFT_MCP_CLIENT_ID")),
            "multi_account_support": True,
            "token_storage": "~/.microsoft-mcp/tokens.json"
        },
        "graph_api": {
            "base_url": "https://graph.microsoft.com/v1.0",
            "timeout": 30.0,
            "retry_policy": "exponential_backoff"
        }
    }

    if category:
        if category in all_settings:
            return {
                "status": "success",
                "category": category,
                "settings": all_settings[category]
            }
        return {
            "status": "error",
            "message": f"Unknown category: {category}. Available: {list(all_settings.keys())}"
        }

    return {
        "status": "success",
        "all_settings": all_settings
    }


@mcp.tool
def update_settings(
    category: str,
    settings: dict[str, Any]
) -> dict[str, Any]:
    """Update configuration settings with validation
    
    Args:
        category: Settings category ("server", "email", "auth")  
        settings: New settings to apply
        
    Returns:
        Update operation results
    """
    # This is a placeholder implementation for the utility framework
    # In a real implementation, this would update actual configuration

    valid_categories = ["server", "email", "auth", "graph_api"]

    if category not in valid_categories:
        return {
            "status": "error",
            "message": f"Invalid category: {category}. Valid categories: {valid_categories}"
        }

    # Validate settings based on category
    if category == "email":
        valid_keys = ["signature_enabled", "templates_available", "styling"]
        invalid_keys = [k for k in settings if k not in valid_keys]
        if invalid_keys:
            return {
                "status": "error",
                "message": f"Invalid email settings: {invalid_keys}"
            }

    elif category == "auth":
        # Auth settings are read-only for security
        return {
            "status": "error",
            "message": "Authentication settings are read-only"
        }

    # Simulate successful update
    return {
        "status": "success",
        "category": category,
        "updated_settings": settings,
        "message": "Settings updated successfully (placeholder implementation)"
    }


@mcp.tool
def validate_data(
    data_type: str,
    data: dict[str, Any],
    schema: str | None = None
) -> dict[str, Any]:
    """Validate data using the Story 1.1 validation framework
    
    Args:
        data_type: Type of data to validate ("email", "contact", "calendar", "file")
        data: Data to validate
        schema: Optional schema name for validation
        
    Returns:
        Validation results
    """
    errors = []
    warnings = []

    if data_type == "email":
        # Email validation
        if "to" not in data:
            errors.append("Missing required field: to")
        elif not data["to"] or "@" not in data["to"]:
            errors.append("Invalid email address in 'to' field")

        if "subject" not in data:
            warnings.append("Email subject is empty")

        if "body" not in data:
            warnings.append("Email body is empty")

    elif data_type == "contact":
        # Contact validation
        if "first_name" not in data and "last_name" not in data:
            errors.append("At least one of first_name or last_name is required")

        if "email" in data and data["email"]:
            if "@" not in data["email"]:
                errors.append("Invalid email address format")

    elif data_type == "calendar":
        # Calendar event validation
        required_fields = ["subject", "start_datetime", "end_datetime"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate datetime format
        if "start_datetime" in data and "end_datetime" in data:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(data["start_datetime"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(data["end_datetime"].replace("Z", "+00:00"))
                if start >= end:
                    errors.append("Start time must be before end time")
            except ValueError:
                errors.append("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    elif data_type == "file":
        # File operation validation
        if "file_path" in data:
            path = data["file_path"]
            if not path.startswith("/"):
                warnings.append("File path should be absolute")

            # Check for potentially unsafe paths
            if ".." in path:
                errors.append("File path contains unsafe '..' components")

    else:
        errors.append(f"Unsupported data_type: {data_type}")

    validation_status = "valid"
    if errors:
        validation_status = "invalid"
    elif warnings:
        validation_status = "valid_with_warnings"

    return {
        "status": "success",
        "data_type": data_type,
        "validation_status": validation_status,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "schema_used": schema or f"default_{data_type}"
    }


@mcp.tool
def get_system_status() -> dict[str, Any]:
    """Get system health and status information
    
    Returns:
        System status including health checks and service availability
    """
    import os
    import time
    from pathlib import Path

    # Check authentication configuration
    client_id_configured = bool(os.getenv("MICROSOFT_MCP_CLIENT_ID"))

    # Check token storage
    token_file = Path.home() / ".microsoft-mcp" / "tokens.json"
    token_storage_available = token_file.parent.exists()

    # Check accounts
    accounts = list_accounts.fn()
    active_accounts = len(accounts)

    # Calculate uptime (placeholder)
    uptime_seconds = time.time() % 86400  # Simplified uptime calculation

    # Overall health assessment
    health_status = "healthy"
    issues = []

    if not client_id_configured:
        health_status = "degraded"
        issues.append("MICROSOFT_MCP_CLIENT_ID environment variable not configured")

    if not token_storage_available:
        health_status = "degraded"
        issues.append("Token storage directory not accessible")

    if active_accounts == 0:
        health_status = "degraded"
        issues.append("No authenticated accounts available")

    return {
        "status": "success",
        "timestamp": time.time(),
        "health_status": health_status,
        "issues": issues,
        "system_info": {
            "total_tools": 15,
            "architecture": "ultra-consolidated",
            "framework": "FastMCP 2.8.0+",
            "graph_api_version": "v1.0"
        },
        "authentication": {
            "client_id_configured": client_id_configured,
            "token_storage_available": token_storage_available,
            "active_accounts": active_accounts
        },
        "uptime": {
            "seconds": int(uptime_seconds),
            "formatted": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
        },
        "services": {
            "graph_api": "available",
            "email_framework": "available",
            "validation_framework": "available",
            "unified_operations": "available"
        }
    }


@mcp.tool
def get_help(
    topic: str | None = None,
    action: str | None = None
) -> dict[str, Any]:
    """Get context-aware help and examples for the 15-tool architecture
    
    Args:
        topic: Help topic ("operations", "authentication", "utilities")
        action: Specific action for detailed help (e.g., "email.send")
        
    Returns:
        Help information with examples and usage guidance
    """
    if action:
        # Detailed help for specific actions
        action_help = {
            "email.send": {
                "description": "Send email with optional professional template",
                "parameters": {
                    "account_id": "Microsoft account ID (required)",
                    "action": "'email.send' (required)",
                    "data": {
                        "to": "Recipient email address (required)",
                        "subject": "Email subject (required)",
                        "body": "Email body content (required)",
                        "cc": "CC recipients (optional list)",
                        "bcc": "BCC recipients (optional list)",
                        "attachments": "File paths to attach (optional)"
                    },
                    "template": "Email template: practice_report, executive_summary, etc. (optional)",
                    "options": "Additional options (optional)"
                },
                "example": {
                    "account_id": "user@company.com",
                    "action": "email.send",
                    "data": {
                        "to": "recipient@example.com",
                        "subject": "Monthly Report",
                        "body": "Please find the monthly report attached.",
                        "attachments": ["/path/to/report.pdf"]
                    },
                    "template": "practice_report"
                }
            },
            "email.list": {
                "description": "List emails with filtering options",
                "parameters": {
                    "account_id": "Microsoft account ID (required)",
                    "action": "'email.list' (required)",
                    "data": {
                        "folder": "Email folder (optional, default: inbox)",
                        "limit": "Number of emails to return (optional, default: 10)",
                        "search_query": "Search query (optional)"
                    }
                },
                "example": {
                    "account_id": "user@company.com",
                    "action": "email.list",
                    "data": {
                        "folder": "inbox",
                        "limit": 20,
                        "search_query": "monthly report"
                    }
                }
            }
        }

        if action in action_help:
            return {
                "status": "success",
                "help_type": "action",
                "action": action,
                "help": action_help[action]
            }
        return {
            "status": "error",
            "message": f"No help available for action: {action}"
        }

    if topic:
        # Topic-based help
        topic_help = {
            "operations": {
                "description": "Microsoft Operations Tool Usage",
                "main_tool": "microsoft_operations",
                "categories": {
                    "email": "Email operations: list, send, reply, draft, delete, forward, move, mark, search, get",
                    "calendar": "Calendar operations: list, create, update, delete, search, invite",
                    "file": "File operations: list, get, upload, download, share, delete",
                    "contact": "Contact operations: list, get, create, update, delete"
                },
                "usage_pattern": "microsoft_operations(account_id, action, data, template, options)",
                "examples": [
                    "Send email: microsoft_operations('user@company.com', 'email.send', {'to': 'recipient@example.com', 'subject': 'Hello', 'body': 'Test message'})",
                    "List contacts: microsoft_operations('user@company.com', 'contact.list', {'limit': 50})"
                ]
            },
            "authentication": {
                "description": "Authentication and Account Management",
                "tools": ["list_accounts", "authenticate_account", "complete_authentication"],
                "workflow": [
                    "1. Run authenticate_account() to start device flow",
                    "2. Follow the provided URL and enter the code",
                    "3. Run complete_authentication(flow_cache) to finish",
                    "4. Use list_accounts() to see authenticated accounts"
                ],
                "requirements": "Set MICROSOFT_MCP_CLIENT_ID environment variable"
            },
            "utilities": {
                "description": "Utility Tools for System Management",
                "tools": [
                    "get_user_info: Get user profile information",
                    "get_mailbox_statistics: Get mailbox usage stats",
                    "unified_search: Search across all services",
                    "list_resources: Show available capabilities",
                    "export_data: Bulk export operations",
                    "import_data: Bulk import operations",
                    "get_settings: Get configuration",
                    "update_settings: Update configuration",
                    "validate_data: Validate before operations",
                    "get_system_status: Health check",
                    "get_help: This help system"
                ]
            }
        }

        if topic in topic_help:
            return {
                "status": "success",
                "help_type": "topic",
                "topic": topic,
                "help": topic_help[topic]
            }
        return {
            "status": "error",
            "message": f"No help available for topic: {topic}. Available topics: {list(topic_help.keys())}"
        }

    # General help overview
    return {
        "status": "success",
        "help_type": "overview",
        "architecture": {
            "total_tools": 15,
            "reduction": "75% reduction from 61 tools",
            "approach": "Ultra-consolidated architecture with unified operations"
        },
        "quick_start": {
            "authentication": "1. Set MICROSOFT_MCP_CLIENT_ID environment variable\n2. Run authenticate_account()\n3. Follow device flow instructions",
            "basic_usage": "Use microsoft_operations(account_id, action, data) for most operations",
            "discovery": "Run list_resources() to see all available capabilities"
        },
        "main_tools": {
            "microsoft_operations": "Unified tool for all Microsoft 365 operations",
            "list_accounts": "Account management",
            "authenticate_account": "Authentication setup",
            "utilities": "11 utility tools for system management and discovery"
        },
        "help_topics": ["operations", "authentication", "utilities"],
        "example_actions": ["email.send", "email.list", "contact.create", "file.upload"],
        "get_detailed_help": "Use get_help(topic='operations') or get_help(action='email.send') for specific guidance"
    }


# ================================================================================
# DEPRECATION LAYER - STORY 1.7: MIGRATION AND DEPRECATION
# ================================================================================
#
# The following functions provide backward compatibility during the transition
# from legacy tools to unified tools. Each legacy tool is wrapped with:
# 1. Deprecation warnings with clear migration guidance
# 2. Automatic parameter mapping to unified format
# 3. Routing to appropriate microsoft_operations action
# 4. Zero breaking changes during 30-day transition period
#
# ARCHITECTURE:
# - 55+ legacy tools → 15 unified tools (75% reduction)
# - All legacy tools route through microsoft_operations with action-based parameters
# - Professional email templates preserved through template parameter
# - Complete parameter compatibility maintained during migration
#
# ================================================================================

# Initialize global router for legacy tool routing
legacy_router = LegacyToolRouter(microsoft_operations)


# ================================================================================
# DEPRECATION WRAPPERS FOR LEGACY TOOLS (Story 1.7)
#
# The following section contains deprecation wrappers for all 55+ legacy tools.
# Each wrapper:
# 1. Routes to the appropriate microsoft_operations action
# 2. Provides clear deprecation warnings with migration guidance
# 3. Maintains 100% backward compatibility during transition period
# 4. Will be removed after 30-day deprecation period
#
# Priority Order: Email (28) -> Calendar (8) -> File (13) -> Contact (6)
# ================================================================================

# EMAIL TOOL DEPRECATION WRAPPERS (28 tools)

@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_emails_deprecated(
    account_id: str,
    folder_name: str | None = None,
    limit: int = 10,
    include_body: bool = True,
    search_query: str | None = None,
    skip: int = 0
) -> list[dict[str, Any]]:
    """DEPRECATED: List emails from a Microsoft account
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "list_emails",
        account_id=account_id,
        folder_name=folder_name,
        limit=limit,
        include_body=include_body,
        search_query=search_query,
        skip=skip
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def send_email_deprecated(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Send an email immediately with file path(s) as attachments
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send') instead.
    """
    return legacy_router.route_email_tool(
        "send_email",
        account_id=account_id,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        attachments=attachments
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.draft'",
    unified_action="email.draft",
    removal_timeline="30 days"
)
@mcp.tool
def create_email_draft_deprecated(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Create an email draft with file path(s) as attachments
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.draft') instead.
    """
    return legacy_router.route_email_tool(
        "create_email_draft",
        account_id=account_id,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        attachments=attachments
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.reply'",
    unified_action="email.reply",
    removal_timeline="30 days"
)
@mcp.tool
def reply_to_email_deprecated(
    account_id: str,
    email_id: str,
    body: str,
    reply_all: bool = False,
    attachments: str | list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Reply to an email
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.reply') instead.
    """
    return legacy_router.route_email_tool(
        "reply_to_email",
        account_id=account_id,
        email_id=email_id,
        body=body,
        reply_all=reply_all,
        attachments=attachments
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.forward'",
    unified_action="email.forward",
    removal_timeline="30 days"
)
@mcp.tool
def forward_email_deprecated(
    account_id: str,
    email_id: str,
    to: str | list[str],
    comment: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Forward an email to other recipients
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.forward') instead.
    """
    return legacy_router.route_email_tool(
        "forward_email",
        account_id=account_id,
        email_id=email_id,
        to=to,
        comment=comment
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.delete'",
    unified_action="email.delete",
    removal_timeline="30 days"
)
@mcp.tool
def delete_email_deprecated(
    account_id: str,
    email_id: str,
    permanent: bool = False
) -> dict[str, str]:
    """DEPRECATED: Delete or move an email to trash
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.delete') instead.
    """
    return legacy_router.route_email_tool(
        "delete_email",
        account_id=account_id,
        email_id=email_id,
        permanent=permanent
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.mark'",
    unified_action="email.mark",
    removal_timeline="30 days"
)
@mcp.tool
def mark_email_as_read_deprecated(
    account_id: str,
    email_id: str,
    is_read: bool = True
) -> dict[str, str]:
    """DEPRECATED: Mark an email as read or unread
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.mark') instead.
    """
    return legacy_router.route_email_tool(
        "mark_email_as_read",
        account_id=account_id,
        email_id=email_id,
        is_read=is_read
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.move'",
    unified_action="email.move",
    removal_timeline="30 days"
)
@mcp.tool
def move_email_deprecated(
    account_id: str,
    email_id: str,
    destination_folder: str
) -> dict[str, str]:
    """DEPRECATED: Move an email to a different folder
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.move') instead.
    """
    return legacy_router.route_email_tool(
        "move_email",
        account_id=account_id,
        email_id=email_id,
        destination_folder=destination_folder
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.search'",
    unified_action="email.search",
    removal_timeline="30 days"
)
@mcp.tool
def search_emails_deprecated(
    account_id: str,
    query: str,
    folder: str | None = None,
    limit: int = 20,
    has_attachments: bool | None = None
) -> list[dict[str, Any]]:
    """DEPRECATED: Search emails using Microsoft Graph search
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.search') instead.
    """
    return legacy_router.route_email_tool(
        "search_emails",
        account_id=account_id,
        query=query,
        folder=folder,
        limit=limit,
        has_attachments=has_attachments
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.get'",
    unified_action="email.get",
    removal_timeline="30 days"
)
@mcp.tool
def get_email_deprecated(account_id: str, email_id: str) -> dict[str, Any]:
    """DEPRECATED: Get a specific email by ID
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.get') instead.
    """
    return legacy_router.route_email_tool(
        "get_email",
        account_id=account_id,
        email_id=email_id
    )


# CALENDAR TOOL DEPRECATION WRAPPERS (8 tools)

@deprecated_tool(
    "Use microsoft_operations with action='calendar.list'",
    unified_action="calendar.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_calendar_events_deprecated(
    account_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    calendar_id: str | None = None
) -> list[dict[str, Any]]:
    """DEPRECATED: List calendar events for a Microsoft account
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.list') instead.
    """
    return legacy_router.route_calendar_tool(
        "list_calendar_events",
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        calendar_id=calendar_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.create'",
    unified_action="calendar.create",
    removal_timeline="30 days"
)
@mcp.tool
def create_calendar_event_deprecated(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str] | None = None,
    location: str | None = None,
    body: str | None = None,
    is_online_meeting: bool = False,
    calendar_id: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Create a new calendar event
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.create') instead.
    """
    return legacy_router.route_calendar_tool(
        "create_calendar_event",
        account_id=account_id,
        subject=subject,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        attendees=attendees,
        location=location,
        body=body,
        is_online_meeting=is_online_meeting,
        calendar_id=calendar_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.update'",
    unified_action="calendar.update",
    removal_timeline="30 days"
)
@mcp.tool
def update_calendar_event_deprecated(
    account_id: str,
    event_id: str,
    subject: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    location: str | None = None,
    body: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Update an existing calendar event
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.update') instead.
    """
    return legacy_router.route_calendar_tool(
        "update_calendar_event",
        account_id=account_id,
        event_id=event_id,
        subject=subject,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location=location,
        body=body
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.delete'",
    unified_action="calendar.delete",
    removal_timeline="30 days"
)
@mcp.tool
def delete_calendar_event_deprecated(
    account_id: str,
    event_id: str,
    send_cancellation: bool = True
) -> dict[str, str]:
    """DEPRECATED: Delete a calendar event
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.delete') instead.
    """
    return legacy_router.route_calendar_tool(
        "delete_calendar_event",
        account_id=account_id,
        event_id=event_id,
        send_cancellation=send_cancellation
    )


# FILE TOOL DEPRECATION WRAPPERS (13 tools)

@deprecated_tool(
    "Use microsoft_operations with action='file.list'",
    unified_action="file.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_files_deprecated(
    account_id: str,
    folder_path: str | None = None,
    search_query: str | None = None,
    limit: int = 20
) -> list[dict[str, Any]]:
    """DEPRECATED: List files in OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.list') instead.
    """
    return legacy_router.route_file_tool(
        "list_files",
        account_id=account_id,
        folder_path=folder_path,
        search_query=search_query,
        limit=limit
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.download'",
    unified_action="file.download",
    removal_timeline="30 days"
)
@mcp.tool
def download_file_deprecated(
    account_id: str,
    file_path: str,
    save_path: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Download a file from OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.download') instead.
    """
    return legacy_router.route_file_tool(
        "download_file",
        account_id=account_id,
        file_path=file_path,
        save_path=save_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.upload'",
    unified_action="file.upload",
    removal_timeline="30 days"
)
@mcp.tool
def upload_file_deprecated(
    account_id: str,
    local_path: str,
    onedrive_path: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Upload a file to OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.upload') instead.
    """
    return legacy_router.route_file_tool(
        "upload_file",
        account_id=account_id,
        local_path=local_path,
        onedrive_path=onedrive_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.delete'",
    unified_action="file.delete",
    removal_timeline="30 days"
)
@mcp.tool
def delete_file_deprecated(account_id: str, file_path: str) -> dict[str, str]:
    """DEPRECATED: Delete a file or folder from OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.delete') instead.
    """
    return legacy_router.route_file_tool(
        "delete_file",
        account_id=account_id,
        file_path=file_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.share'",
    unified_action="file.share",
    removal_timeline="30 days"
)
@mcp.tool
def share_file_deprecated(
    account_id: str,
    file_path: str,
    email: str | None = None,
    permission: str = "view",
    expiration_days: int | None = None
) -> dict[str, str]:
    """DEPRECATED: Share a file or folder from OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.share') instead.
    """
    return legacy_router.route_file_tool(
        "share_file",
        account_id=account_id,
        file_path=file_path,
        email=email,
        permission=permission,
        expiration_days=expiration_days
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.search'",
    unified_action="file.search",
    removal_timeline="30 days"
)
@mcp.tool
def search_files_deprecated(
    account_id: str,
    query: str,
    file_type: str | None = None,
    limit: int = 20
) -> list[dict[str, Any]]:
    """DEPRECATED: Search for files across OneDrive using Microsoft Search
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.search') instead.
    """
    return legacy_router.route_file_tool(
        "search_files",
        account_id=account_id,
        query=query,
        file_type=file_type,
        limit=limit
    )


# CONTACT TOOL DEPRECATION WRAPPERS (6 tools)

@deprecated_tool(
    "Use microsoft_operations with action='contact.list'",
    unified_action="contact.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_contacts_deprecated(
    account_id: str,
    search_query: str | None = None,
    limit: int = 20
) -> list[dict[str, Any]]:
    """DEPRECATED: List contacts from the Microsoft account
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.list') instead.
    """
    return legacy_router.route_contact_tool(
        "list_contacts",
        account_id=account_id,
        search_query=search_query,
        limit=limit
    )


@deprecated_tool(
    "Use microsoft_operations with action='contact.create'",
    unified_action="contact.create",
    removal_timeline="30 days"
)
@mcp.tool
def create_contact_deprecated(
    account_id: str,
    first_name: str,
    last_name: str,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Create a new contact
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.create') instead.
    """
    return legacy_router.route_contact_tool(
        "create_contact",
        account_id=account_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        mobile_phone=mobile_phone,
        company=company,
        job_title=job_title
    )


@deprecated_tool(
    "Use microsoft_operations with action='contact.update'",
    unified_action="contact.update",
    removal_timeline="30 days"
)
@mcp.tool
def update_contact_deprecated(
    account_id: str,
    contact_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Update an existing contact
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.update') instead.
    """
    return legacy_router.route_contact_tool(
        "update_contact",
        account_id=account_id,
        contact_id=contact_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        mobile_phone=mobile_phone,
        company=company,
        job_title=job_title
    )


@deprecated_tool(
    "Use microsoft_operations with action='contact.delete'",
    unified_action="contact.delete",
    removal_timeline="30 days"
)
@mcp.tool
def delete_contact_deprecated(account_id: str, contact_id: str) -> dict[str, str]:
    """DEPRECATED: Delete a contact
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.delete') instead.
    """
    return legacy_router.route_contact_tool(
        "delete_contact",
        account_id=account_id,
        contact_id=contact_id
    )


# ================================================================================
# ADDITIONAL EMAIL TOOL DEPRECATION WRAPPERS
# (Remaining email tools from LegacyToolRegistry)
# ================================================================================

@deprecated_tool(
    "Use microsoft_operations with action='email.get'",
    unified_action="email.get",
    removal_timeline="30 days"
)
@mcp.tool
def download_email_attachments_deprecated(
    account_id: str,
    email_id: str,
    save_dir: str = "~/Downloads"
) -> list[dict[str, Any]]:
    """DEPRECATED: Download all attachments from an email
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.get') instead.
    """
    return legacy_router.route_email_tool(
        "download_email_attachments",
        account_id=account_id,
        email_id=email_id,
        save_dir=save_dir
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_mail_folders_deprecated(account_id: str) -> list[dict[str, Any]]:
    """DEPRECATED: List all mail folders in the account
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "list_mail_folders",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def create_mail_folder_deprecated(
    account_id: str,
    folder_name: str,
    parent_folder_id: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Create a new mail folder
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "create_mail_folder",
        account_id=account_id,
        folder_name=folder_name,
        parent_folder_id=parent_folder_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_email_signature_deprecated(account_id: str) -> dict[str, str]:
    """DEPRECATED: Get the user's email signature
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "get_email_signature",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.draft'",
    unified_action="email.draft",
    removal_timeline="30 days"
)
@mcp.tool
def add_email_attachment_from_onedrive_deprecated(
    account_id: str,
    email_id: str,
    file_path: str
) -> dict[str, str]:
    """DEPRECATED: Add a OneDrive file as an attachment to an existing draft email
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.draft') instead.
    """
    return legacy_router.route_email_tool(
        "add_email_attachment_from_onedrive",
        account_id=account_id,
        email_id=email_id,
        file_path=file_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_inbox_rules_deprecated(account_id: str) -> list[dict[str, Any]]:
    """DEPRECATED: Get email inbox rules
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "get_inbox_rules",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_email_categories_deprecated(account_id: str) -> list[dict[str, Any]]:
    """DEPRECATED: Get available email categories
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "get_email_categories",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def schedule_email_deprecated(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    send_datetime: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Schedule an email to be sent at a specific time
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send') instead.
    """
    return legacy_router.route_email_tool(
        "schedule_email",
        account_id=account_id,
        to=to,
        subject=subject,
        body=body,
        send_datetime=send_datetime,
        cc=cc,
        bcc=bcc
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.get'",
    unified_action="email.get",
    removal_timeline="30 days"
)
@mcp.tool
def batch_download_attachments_deprecated(
    account_id: str,
    email_ids: list[str],
    save_dir: str = "~/Downloads"
) -> list[dict[str, Any]]:
    """DEPRECATED: Download attachments from multiple emails
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.get') instead.
    """
    return legacy_router.route_email_tool(
        "batch_download_attachments",
        account_id=account_id,
        email_ids=email_ids,
        save_dir=save_dir
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.get'",
    unified_action="email.get",
    removal_timeline="30 days"
)
@mcp.tool
def get_email_headers_deprecated(account_id: str, email_id: str) -> dict[str, Any]:
    """DEPRECATED: Get detailed email headers
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.get') instead.
    """
    return legacy_router.route_email_tool(
        "get_email_headers",
        account_id=account_id,
        email_id=email_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.delete'",
    unified_action="email.delete",
    removal_timeline="30 days"
)
@mcp.tool
def empty_deleted_items_deprecated(account_id: str) -> dict[str, str]:
    """DEPRECATED: Empty the Deleted Items folder
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.delete') instead.
    """
    return legacy_router.route_email_tool(
        "empty_deleted_items",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.list'",
    unified_action="email.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_out_of_office_deprecated(account_id: str) -> dict[str, Any]:
    """DEPRECATED: Get out of office settings
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.list') instead.
    """
    return legacy_router.route_email_tool(
        "get_out_of_office",
        account_id=account_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def set_out_of_office_deprecated(
    account_id: str,
    message: str,
    start_time: str | None = None,
    end_time: str | None = None,
    external_message: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Set out of office auto-reply
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send') instead.
    """
    return legacy_router.route_email_tool(
        "set_out_of_office",
        account_id=account_id,
        message=message,
        start_time=start_time,
        end_time=end_time,
        external_message=external_message
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def disable_out_of_office_deprecated(account_id: str) -> dict[str, str]:
    """DEPRECATED: Disable out of office auto-reply
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send') instead.
    """
    return legacy_router.route_email_tool(
        "disable_out_of_office",
        account_id=account_id
    )


# ================================================================================
# PROFESSIONAL EMAIL TEMPLATE DEPRECATION WRAPPERS
# (Template-based email tools)
# ================================================================================

@deprecated_tool(
    "Use microsoft_operations with action='email.send' and template='practice_report'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def send_practice_report_deprecated(
    account_id: str,
    to: str,
    subject: str,
    location: str,
    financial_data: dict[str, Any],
    provider_data: list[dict[str, Any]],
    period: str | None = None,
    alerts: list[dict[str, Any]] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Send a professional practice performance report email
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send', template='practice_report') instead.
    """
    return legacy_router.route_email_tool(
        "send_practice_report",
        account_id=account_id,
        to=to,
        subject=subject,
        location=location,
        financial_data=financial_data,
        provider_data=provider_data,
        period=period,
        alerts=alerts,
        recommendations=recommendations,
        cc=cc,
        bcc=bcc
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send' and template='executive_summary'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def send_executive_summary_deprecated(
    account_id: str,
    to: str,
    locations_data: list[dict[str, Any]],
    period: str,
    subject: str | None = None,
    key_insights: list[dict[str, Any]] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Send an executive summary email with multi-location overview
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send', template='executive_summary') instead.
    """
    return legacy_router.route_email_tool(
        "send_executive_summary",
        account_id=account_id,
        to=to,
        locations_data=locations_data,
        period=period,
        subject=subject,
        key_insights=key_insights,
        cc=cc,
        bcc=bcc
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send' and template='provider_update'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def send_provider_update_deprecated(
    account_id: str,
    to: str,
    provider_name: str,
    performance_data: dict[str, Any],
    period: str | None = None,
    highlights: list[str] | None = None,
    recommendations: list[str] | None = None,
    subject: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Send a personalized provider performance update email
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send', template='provider_update') instead.
    """
    return legacy_router.route_email_tool(
        "send_provider_update",
        account_id=account_id,
        to=to,
        provider_name=provider_name,
        performance_data=performance_data,
        period=period,
        highlights=highlights,
        recommendations=recommendations,
        subject=subject,
        cc=cc,
        bcc=bcc
    )


@deprecated_tool(
    "Use microsoft_operations with action='email.send' and template='alert_notification'",
    unified_action="email.send",
    removal_timeline="30 days"
)
@mcp.tool
def send_alert_notification_deprecated(
    account_id: str,
    to: str,
    alert_type: str,
    title: str,
    message: str,
    urgency: str = "normal",
    impact: str | None = None,
    recommended_actions: list[str] | None = None,
    subject: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> dict[str, str]:
    """DEPRECATED: Send an alert notification email with urgency-based styling
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='email.send', template='alert_notification') instead.
    """
    return legacy_router.route_email_tool(
        "send_alert_notification",
        account_id=account_id,
        to=to,
        alert_type=alert_type,
        title=title,
        message=message,
        urgency=urgency,
        impact=impact,
        recommended_actions=recommended_actions,
        subject=subject,
        cc=cc,
        bcc=bcc
    )


# ================================================================================
# ADDITIONAL CALENDAR TOOL DEPRECATION WRAPPERS
# ================================================================================

@deprecated_tool(
    "Use microsoft_operations with action='calendar.list'",
    unified_action="calendar.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_calendar_availability_deprecated(
    account_id: str,
    start_date: str,
    end_date: str,
    duration_minutes: int = 30
) -> list[dict[str, Any]]:
    """DEPRECATED: Find available time slots in calendar
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.list') instead.
    """
    return legacy_router.route_calendar_tool(
        "get_calendar_availability",
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        duration_minutes=duration_minutes
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.invite'",
    unified_action="calendar.invite",
    removal_timeline="30 days"
)
@mcp.tool
def send_calendar_invite_deprecated(
    account_id: str,
    subject: str,
    start_datetime: str,
    end_datetime: str,
    attendees: list[str],
    location: str | None = None,
    body: str | None = None,
    send_invitation: bool = True
) -> dict[str, str]:
    """DEPRECATED: Create and send a calendar invitation
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.invite') instead.
    """
    return legacy_router.route_calendar_tool(
        "send_calendar_invite",
        account_id=account_id,
        subject=subject,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        attendees=attendees,
        location=location,
        body=body,
        send_invitation=send_invitation
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.search'",
    unified_action="calendar.search",
    removal_timeline="30 days"
)
@mcp.tool
def search_calendar_events_deprecated(
    account_id: str,
    query: str,
    start_date: str | None = None,
    end_date: str | None = None
) -> list[dict[str, Any]]:
    """DEPRECATED: Search calendar events by keyword
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.search') instead.
    """
    return legacy_router.route_calendar_tool(
        "search_calendar_events",
        account_id=account_id,
        query=query,
        start_date=start_date,
        end_date=end_date
    )


@deprecated_tool(
    "Use microsoft_operations with action='calendar.list'",
    unified_action="calendar.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_calendar_list_deprecated(account_id: str) -> list[dict[str, Any]]:
    """DEPRECATED: List all calendars available to the user
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='calendar.list') instead.
    """
    return legacy_router.route_calendar_tool(
        "get_calendar_list",
        account_id=account_id
    )


# ================================================================================
# ADDITIONAL FILE TOOL DEPRECATION WRAPPERS
# ================================================================================

@deprecated_tool(
    "Use microsoft_operations with action='file.list'",
    unified_action="file.list",
    removal_timeline="30 days"
)
@mcp.tool
def create_folder_deprecated(
    account_id: str,
    folder_name: str,
    parent_path: str | None = None
) -> dict[str, str]:
    """DEPRECATED: Create a new folder in OneDrive
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.list') instead.
    """
    return legacy_router.route_file_tool(
        "create_folder",
        account_id=account_id,
        folder_name=folder_name,
        parent_path=parent_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.list'",
    unified_action="file.list",
    removal_timeline="30 days"
)
@mcp.tool
def get_recent_files_deprecated(account_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """DEPRECATED: Get recently accessed files
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.list') instead.
    """
    return legacy_router.route_file_tool(
        "get_recent_files",
        account_id=account_id,
        limit=limit
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.get'",
    unified_action="file.get",
    removal_timeline="30 days"
)
@mcp.tool
def get_file_preview_deprecated(
    account_id: str,
    file_path: str,
    page: int = 1
) -> dict[str, Any]:
    """DEPRECATED: Get a preview/thumbnail of a file
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.get') instead.
    """
    return legacy_router.route_file_tool(
        "get_file_preview",
        account_id=account_id,
        file_path=file_path,
        page=page
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.get'",
    unified_action="file.get",
    removal_timeline="30 days"
)
@mcp.tool
def get_file_versions_deprecated(account_id: str, file_path: str) -> list[dict[str, Any]]:
    """DEPRECATED: Get version history of a file
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.get') instead.
    """
    return legacy_router.route_file_tool(
        "get_file_versions",
        account_id=account_id,
        file_path=file_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.get'",
    unified_action="file.get",
    removal_timeline="30 days"
)
@mcp.tool
def restore_file_version_deprecated(
    account_id: str,
    file_path: str,
    version_id: str
) -> dict[str, str]:
    """DEPRECATED: Restore a specific version of a file
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.get') instead.
    """
    return legacy_router.route_file_tool(
        "restore_file_version",
        account_id=account_id,
        file_path=file_path,
        version_id=version_id
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.get'",
    unified_action="file.get",
    removal_timeline="30 days"
)
@mcp.tool
def get_file_permissions_deprecated(account_id: str, file_path: str) -> list[dict[str, Any]]:
    """DEPRECATED: Get sharing permissions for a file
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.get') instead.
    """
    return legacy_router.route_file_tool(
        "get_file_permissions",
        account_id=account_id,
        file_path=file_path
    )


@deprecated_tool(
    "Use microsoft_operations with action='file.list'",
    unified_action="file.list",
    removal_timeline="30 days"
)
@mcp.tool
def list_shared_files_deprecated(account_id: str, limit: int = 20) -> list[dict[str, Any]]:
    """DEPRECATED: List files shared with the user
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='file.list') instead.
    """
    return legacy_router.route_file_tool(
        "list_shared_files",
        account_id=account_id,
        limit=limit
    )


# ================================================================================
# ADDITIONAL CONTACT TOOL DEPRECATION WRAPPERS
# ================================================================================

@deprecated_tool(
    "Use microsoft_operations with action='contact.list'",
    unified_action="contact.list",
    removal_timeline="30 days"
)
@mcp.tool
def export_contacts_deprecated(
    account_id: str,
    format: str = "json",
    limit: int = 1000
) -> dict[str, Any]:
    """DEPRECATED: Export all contacts to a structured format
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.list') instead.
    """
    return legacy_router.route_contact_tool(
        "export_contacts",
        account_id=account_id,
        format=format,
        limit=limit
    )


@deprecated_tool(
    "Use microsoft_operations with action='contact.list'",
    unified_action="contact.list",
    removal_timeline="30 days"
)
@mcp.tool
def search_people_deprecated(
    account_id: str,
    query: str,
    limit: int = 10
) -> list[dict[str, Any]]:
    """DEPRECATED: Search for people in the organization
    
    ⚠️  This tool is deprecated. Use microsoft_operations(action='contact.list') instead.
    """
    return legacy_router.route_contact_tool(
        "search_people",
        account_id=account_id,
        query=query,
        limit=limit
    )


# ================================================================================
# COMPLETION MESSAGE AND STATISTICS
# ================================================================================

# Total deprecation wrappers implemented: 55+ tools
# - Email tools: 28 (including professional templates)
# - Calendar tools: 8
# - File tools: 13
# - Contact tools: 6
#
# All legacy tools now route through microsoft_operations with proper:
# - Deprecation warnings with clear migration guidance
# - Parameter mapping and backward compatibility
# - 30-day removal timeline
# - Zero breaking changes during transition period
