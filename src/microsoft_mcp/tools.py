import base64
import datetime as dt
import pathlib as pl
from typing import Any
from fastmcp import FastMCP
from . import graph, auth

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
    elif has_large_attachments:
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
    else:
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
    else:
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
    elif format == "csv":
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
    else:
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
        return '<html><body></body></html>'
    
    # If content doesn't have html tags, wrap it
    if not content.strip().startswith('<html'):
        content = f'<html><body>{content}</body></html>'
    
    return content