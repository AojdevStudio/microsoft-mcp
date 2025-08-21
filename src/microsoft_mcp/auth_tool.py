"""Authentication operations tool for Microsoft MCP.

Focused tool providing 3 auth actions through action-based interface:
- list, authenticate, complete_auth

Part of nuclear simplification architecture (~1,000 tokens).
Handles multi-account management efficiently.
"""

from typing import Any, Literal

from .auth import list_accounts as auth_list_accounts


def auth_operations(
    action: Literal["list", "authenticate", "complete_auth"],
    flow_cache: str | None = None
) -> dict[str, Any]:
    """Authentication operations for Microsoft accounts
    
    Actions:
    - list: List all signed-in Microsoft accounts
    - authenticate: Start device flow authentication for new account  
    - complete_auth: Complete authentication with flow cache data
    """
    try:
        if action == "list":
            accounts = auth_list_accounts()
            return {
                "status": "success",
                "accounts": [{"username": acc.username, "account_id": acc.account_id} for acc in accounts]
            }
        if action == "authenticate":
            from .auth import authenticate_account
            return authenticate_account()
        if action == "complete_auth":
            if not flow_cache:
                return {"status": "error", "message": "flow_cache parameter required"}
            from .auth import complete_authentication
            return complete_authentication(flow_cache)
        return {"status": "error", "message": f"Unknown auth action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
