"""File operations tool for Microsoft OneDrive integration.

Focused tool providing 6 file actions through action-based interface:
- list, upload, download, delete, share, search

Part of nuclear simplification architecture replacing 63k token unified tool.
"""

import pathlib as pl
from typing import Any
from typing import Literal

from . import graph


def format_file_item(item: dict[str, Any]) -> dict[str, Any]:
    """Format file item data for output"""
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "size": item.get("size"),
        "type": "folder" if "folder" in item else "file",
        "web_url": item.get("webUrl"),
        "download_url": item.get("@microsoft.graph.downloadUrl"),
        "created_datetime": item.get("createdDateTime"),
        "modified_datetime": item.get("lastModifiedDateTime"),
        "created_by": item.get("createdBy", {}).get("user", {}).get("displayName"),
        "modified_by": item.get("lastModifiedBy", {}).get("user", {}).get("displayName"),
        "mime_type": item.get("file", {}).get("mimeType"),
        "parent_path": item.get("parentReference", {}).get("path", "").replace("/drive/root:", "")
    }


def file_operations(
    account_id: str,
    action: Literal["list", "upload", "download", "delete", "share", "search"],
    # List action parameters
    folder_path: str | None = None,
    limit: int = 20,
    search_query: str | None = None,
    # Upload action parameters
    local_path: str | None = None,
    onedrive_path: str | None = None,
    # Download/Delete action parameters
    file_path: str | None = None,
    # Download action parameters
    save_path: str | None = None,
    # Share action parameters
    email: str | None = None,
    permission: str = "view",
    expiration_days: int | None = None,
    # Search action parameters
    query: str | None = None,
    file_type: str | None = None
) -> dict[str, Any]:
    """File operations for Microsoft OneDrive
    
    Actions:
    - list: List files in OneDrive (folder_path, limit, search_query)
    - upload: Upload file to OneDrive (local_path, onedrive_path)
    - download: Download file from OneDrive (file_path, save_path)
    - delete: Delete file or folder (file_path)
    - share: Share file or folder (file_path, email, permission, expiration_days)
    - search: Search files across OneDrive (query, file_type, limit)
    """
    try:
        if action == "list":
            return _list_files(account_id, folder_path, limit, search_query)
        if action == "upload":
            return _upload_file(account_id, local_path, onedrive_path)
        if action == "download":
            return _download_file(account_id, file_path, save_path)
        if action == "delete":
            return _delete_file(account_id, file_path)
        if action == "share":
            return _share_file(account_id, file_path, email, permission, expiration_days)
        if action == "search":
            return _search_files(account_id, query, file_type, limit)
        return {"status": "error", "message": f"Unknown file action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _list_files(
    account_id: str,
    folder_path: str | None = None,
    limit: int = 20,
    search_query: str | None = None
) -> dict[str, Any]:
    """List files in OneDrive"""
    if folder_path:
        # Clean up the folder path
        folder_path = folder_path.strip("/")
        if folder_path:
            endpoint = f"/me/drive/root:/{folder_path}:/children"
        else:
            endpoint = "/me/drive/root/children"
    else:
        endpoint = "/me/drive/root/children"

    params = {
        "$top": min(limit, 50),
        "$orderby": "lastModifiedDateTime desc",
        "$select": "id,name,size,webUrl,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,file,folder,parentReference,@microsoft.graph.downloadUrl"
    }

    if search_query:
        # Use search endpoint for queries
        endpoint = "/me/drive/search(q='{0}')".format(search_query.replace("'", "''"))

    items = list(graph.paginate(endpoint, account_id, params=params, limit=limit))
    return {
        "status": "success",
        "files": [format_file_item(item) for item in items],
        "count": len(items)
    }


def _upload_file(
    account_id: str,
    local_path: str,
    onedrive_path: str | None = None
) -> dict[str, Any]:
    """Upload a file to OneDrive"""

    local_file = pl.Path(local_path).expanduser().resolve()
    if not local_file.exists():
        return {"status": "error", "message": f"Local file not found: {local_path}"}

    # Determine upload path
    if onedrive_path:
        upload_path = onedrive_path.strip("/")
        if not upload_path.endswith(local_file.name):
            upload_path = f"{upload_path}/{local_file.name}"
    else:
        upload_path = local_file.name

    # Read file content
    file_content = local_file.read_bytes()
    file_size = len(file_content)

    if file_size < 4 * 1024 * 1024:  # < 4MB - use simple upload
        endpoint = f"/me/drive/root:/{upload_path}:/content"
        headers = {
            "Content-Type": "application/octet-stream"
        }

        response = graph.request("PUT", endpoint, account_id, data=file_content, headers=headers)

        return {
            "status": "success",
            "file": format_file_item(response),
            "message": f"File uploaded successfully to {upload_path}"
        }
    # Large file - would need upload session (simplified for now)
    return {"status": "error", "message": "File too large (>4MB). Large file upload not implemented in this simplified version."}


def _download_file(
    account_id: str,
    file_path: str,
    save_path: str | None = None
) -> dict[str, Any]:
    """Download a file from OneDrive"""

    # Clean up the file path
    file_path = file_path.strip("/")

    # Get file metadata first
    try:
        file_info = graph.request("GET", f"/me/drive/root:/{file_path}", account_id)
    except Exception:
        return {"status": "error", "message": f"File not found: {file_path}"}

    # Get download URL
    download_url = file_info.get("@microsoft.graph.downloadUrl")
    if not download_url:
        return {"status": "error", "message": "File download URL not available"}

    # Determine save path
    if save_path:
        save_file = pl.Path(save_path).expanduser().resolve()
    else:
        downloads_dir = pl.Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)
        save_file = downloads_dir / file_info["name"]

    # Download file content
    import requests
    response = requests.get(download_url)
    response.raise_for_status()

    save_file.write_bytes(response.content)

    return {
        "status": "success",
        "file_info": format_file_item(file_info),
        "saved_to": str(save_file),
        "message": f"File downloaded successfully to {save_file}"
    }


def _delete_file(account_id: str, file_path: str) -> dict[str, Any]:
    """Delete a file or folder from OneDrive"""
    file_path = file_path.strip("/")

    # Delete the file/folder
    graph.request("DELETE", f"/me/drive/root:/{file_path}", account_id)

    return {
        "status": "success",
        "message": f"File/folder deleted successfully: {file_path}"
    }


def _share_file(
    account_id: str,
    file_path: str,
    email: str | None = None,
    permission: str = "view",
    expiration_days: int | None = None
) -> dict[str, Any]:
    """Share a file or folder from OneDrive"""
    file_path = file_path.strip("/")

    if email:
        # Share with specific email
        share_data = {
            "recipients": [{"email": email}],
            "message": "Shared via Microsoft MCP",
            "requireSignIn": True,
            "sendInvitation": True,
            "roles": ["read" if permission == "view" else "write"]
        }

        if expiration_days:
            import datetime as dt
            expiry_date = dt.datetime.now() + dt.timedelta(days=expiration_days)
            share_data["expirationDateTime"] = expiry_date.isoformat()

        response = graph.request("POST", f"/me/drive/root:/{file_path}:/invite", account_id, json=share_data)
    else:
        # Create shareable link
        link_data = {
            "type": permission,  # "view" or "edit"
            "scope": "anonymous"
        }

        if expiration_days:
            import datetime as dt
            expiry_date = dt.datetime.now() + dt.timedelta(days=expiration_days)
            link_data["expirationDateTime"] = expiry_date.isoformat()

        response = graph.request("POST", f"/me/drive/root:/{file_path}:/createLink", account_id, json=link_data)

    return {
        "status": "success",
        "share_info": response,
        "message": f"File shared successfully: {file_path}"
    }


def _search_files(
    account_id: str,
    query: str,
    file_type: str | None = None,
    limit: int = 20
) -> dict[str, Any]:
    """Search for files across OneDrive using Microsoft Search"""
    # Escape single quotes in query
    escaped_query = query.replace("'", "''")
    endpoint = f"/me/drive/search(q='{escaped_query}')"

    params = {
        "$top": min(limit, 50),
        "$select": "id,name,size,webUrl,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,file,folder,parentReference,@microsoft.graph.downloadUrl"
    }

    # Add file type filter if specified
    if file_type:
        file_type = file_type.lower()
        if not file_type.startswith("."):
            file_type = f".{file_type}"
        params["$filter"] = f"endswith(name,'{file_type}')"

    items = list(graph.paginate(endpoint, account_id, params=params, limit=limit))
    return {
        "status": "success",
        "files": [format_file_item(item) for item in items],
        "count": len(items)
    }
