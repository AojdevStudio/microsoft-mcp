"""Contact operations tool for Microsoft Graph API integration.

Focused tool providing 5 contact actions through action-based interface:
- list, create, update, delete, search

Part of nuclear simplification architecture replacing 63k token unified tool.
"""

from typing import Any
from typing import Literal

from . import graph


def format_contact(contact: dict[str, Any]) -> dict[str, Any]:
    """Format contact data for output"""
    # Get email addresses
    emails = contact.get("emailAddresses", [])
    primary_email = emails[0].get("address") if emails else None

    # Get phone numbers
    phones = contact.get("mobilePhone") or contact.get("businessPhones", [])
    mobile_phone = phones[0] if isinstance(phones, list) and phones else phones

    return {
        "id": contact.get("id"),
        "first_name": contact.get("givenName"),
        "last_name": contact.get("surname"),
        "display_name": contact.get("displayName"),
        "email": primary_email,
        "emails": [email.get("address") for email in emails],
        "mobile_phone": mobile_phone,
        "business_phones": contact.get("businessPhones", []),
        "company": contact.get("companyName"),
        "job_title": contact.get("jobTitle"),
        "department": contact.get("department"),
        "office_location": contact.get("officeLocation"),
        "created_datetime": contact.get("createdDateTime"),
        "modified_datetime": contact.get("lastModifiedDateTime"),
    }


def contact_operations(
    account_id: str,
    action: Literal["list", "create", "update", "delete", "search"],
    # List/Search action parameters
    limit: int = 20,
    search_query: str | None = None,
    # Create/Update action parameters
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None,
    # Update/Delete action parameters
    contact_id: str | None = None,
    # Search action parameters
    query: str | None = None
) -> dict[str, Any]:
    """Contact operations for Microsoft Outlook
    
    Actions:
    - list: List contacts from account (limit, search_query)
    - create: Create new contact (first_name, last_name, email, mobile_phone, company, job_title)
    - update: Update existing contact (contact_id, first_name, last_name, email, mobile_phone, company, job_title)
    - delete: Delete contact (contact_id)
    - search: Search contacts (query, limit)
    """
    try:
        if action == "list":
            return _list_contacts(account_id, limit, search_query)
        if action == "create":
            return _create_contact(account_id, first_name, last_name, email, mobile_phone, company, job_title)
        if action == "update":
            return _update_contact(account_id, contact_id, first_name, last_name, email, mobile_phone, company, job_title)
        if action == "delete":
            return _delete_contact(account_id, contact_id)
        if action == "search":
            return _search_contacts(account_id, query, limit)
        return {"status": "error", "message": f"Unknown contact action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _list_contacts(
    account_id: str,
    limit: int = 20,
    search_query: str | None = None
) -> dict[str, Any]:
    """List contacts from the Microsoft account"""
    endpoint = "/me/contacts"

    params = {
        "$top": min(limit, 50),
        "$orderby": "displayName",
        "$select": "id,givenName,surname,displayName,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle,department,officeLocation,createdDateTime,lastModifiedDateTime"
    }

    if search_query:
        params["$search"] = f'"{search_query}"'

    contacts = list(graph.paginate(endpoint, account_id, params=params, limit=limit))
    return {
        "status": "success",
        "contacts": [format_contact(contact) for contact in contacts],
        "count": len(contacts)
    }


def _create_contact(
    account_id: str,
    first_name: str,
    last_name: str,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None
) -> dict[str, Any]:
    """Create a new contact"""
    contact_data = {
        "givenName": first_name,
        "surname": last_name,
        "displayName": f"{first_name} {last_name}".strip()
    }

    if email:
        contact_data["emailAddresses"] = [{"address": email, "name": f"{first_name} {last_name}"}]

    if mobile_phone:
        contact_data["mobilePhone"] = mobile_phone

    if company:
        contact_data["companyName"] = company

    if job_title:
        contact_data["jobTitle"] = job_title

    response = graph.request("POST", "/me/contacts", account_id, json=contact_data)

    return {
        "status": "success",
        "contact": format_contact(response),
        "message": "Contact created successfully"
    }


def _update_contact(
    account_id: str,
    contact_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    mobile_phone: str | None = None,
    company: str | None = None,
    job_title: str | None = None
) -> dict[str, Any]:
    """Update an existing contact"""
    update_data = {}

    if first_name is not None:
        update_data["givenName"] = first_name
    if last_name is not None:
        update_data["surname"] = last_name

    # Update display name if first or last name changed
    if first_name is not None or last_name is not None:
        # Get current contact to construct display name
        current = graph.request("GET", f"/me/contacts/{contact_id}", account_id,
                               params={"$select": "givenName,surname"})
        fname = first_name if first_name is not None else current.get("givenName", "")
        lname = last_name if last_name is not None else current.get("surname", "")
        update_data["displayName"] = f"{fname} {lname}".strip()

    if email is not None:
        display_name = update_data.get("displayName", f"{first_name or ''} {last_name or ''}").strip()
        update_data["emailAddresses"] = [{"address": email, "name": display_name}]

    if mobile_phone is not None:
        update_data["mobilePhone"] = mobile_phone

    if company is not None:
        update_data["companyName"] = company

    if job_title is not None:
        update_data["jobTitle"] = job_title

    if not update_data:
        return {"status": "error", "message": "No update fields provided"}

    graph.request("PATCH", f"/me/contacts/{contact_id}", account_id, json=update_data)
    return {"status": "success", "message": "Contact updated successfully"}


def _delete_contact(account_id: str, contact_id: str) -> dict[str, Any]:
    """Delete a contact"""
    graph.request("DELETE", f"/me/contacts/{contact_id}", account_id)
    return {"status": "success", "message": "Contact deleted successfully"}


def _search_contacts(
    account_id: str,
    query: str,
    limit: int = 20
) -> dict[str, Any]:
    """Search contacts using Microsoft Graph search"""
    endpoint = "/me/contacts"

    params = {
        "$search": f'"{query}"',
        "$top": min(limit, 50),
        "$orderby": "displayName",
        "$select": "id,givenName,surname,displayName,emailAddresses,mobilePhone,businessPhones,companyName,jobTitle,department,officeLocation"
    }

    contacts = list(graph.paginate(endpoint, account_id, params=params, limit=limit))
    return {
        "status": "success",
        "contacts": [format_contact(contact) for contact in contacts],
        "count": len(contacts)
    }
