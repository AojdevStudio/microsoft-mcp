import os
import msal
import pathlib as pl
from typing import NamedTuple
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = pl.Path.home() / ".microsoft_mcp_token_cache.json"
SCOPES = ["https://graph.microsoft.com/.default"]


class Account(NamedTuple):
    username: str
    account_id: str


def _read_cache() -> str | None:
    try:
        return CACHE_FILE.read_text()
    except FileNotFoundError:
        return None


def _write_cache(content: str) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(content)


def get_app() -> msal.PublicClientApplication:
    client_id = os.getenv("MICROSOFT_MCP_CLIENT_ID")
    if not client_id:
        raise ValueError("MICROSOFT_MCP_CLIENT_ID environment variable is required")

    tenant_id = os.getenv("MICROSOFT_MCP_TENANT_ID", "common")
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    cache = msal.SerializableTokenCache()
    cache_content = _read_cache()
    if cache_content:
        cache.deserialize(cache_content)

    app = msal.PublicClientApplication(
        client_id, authority=authority, token_cache=cache
    )

    return app


def get_token(account_id: str | None = None) -> str:
    app = get_app()

    accounts = app.get_accounts()
    account = None

    if account_id:
        account = next(
            (a for a in accounts if a["home_account_id"] == account_id), None
        )
    elif accounts:
        account = accounts[0]

    result = app.acquire_token_silent(SCOPES, account=account)

    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise Exception(
                f"Failed to get device code: {flow.get('error_description', 'Unknown error')}"
            )
        verification_uri = flow.get(
            "verification_uri",
            flow.get("verification_url", "https://microsoft.com/devicelogin"),
        )
        print(
            f"\nTo authenticate:\n1. Visit {verification_uri}\n2. Enter code: {flow['user_code']}"
        )
        result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        raise Exception(
            f"Auth failed: {result.get('error_description', result['error'])}"
        )

    cache = app.token_cache
    if isinstance(cache, msal.SerializableTokenCache) and cache.has_state_changed:
        _write_cache(cache.serialize())

    return result["access_token"]


def list_accounts() -> list[Account]:
    app = get_app()
    return [
        Account(username=a["username"], account_id=a["home_account_id"])
        for a in app.get_accounts()
    ]


def authenticate_new_account() -> Account | None:
    """Authenticate a new account interactively"""
    app = get_app()

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception(
            f"Failed to get device code: {flow.get('error_description', 'Unknown error')}"
        )

    print("\nTo authenticate:")
    print(
        f"1. Visit: {flow.get('verification_uri', flow.get('verification_url', 'https://microsoft.com/devicelogin'))}"
    )
    print(f"2. Enter code: {flow['user_code']}")
    print("3. Sign in with your Microsoft account")
    print("\nWaiting for authentication...")

    result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        raise Exception(
            f"Auth failed: {result.get('error_description', result['error'])}"
        )

    cache = app.token_cache
    if isinstance(cache, msal.SerializableTokenCache) and cache.has_state_changed:
        _write_cache(cache.serialize())

    # Get the newly added account
    accounts = app.get_accounts()
    if accounts:
        # Find the account that matches the token we just got
        for account in accounts:
            if (
                account.get("username", "").lower()
                == result.get("id_token_claims", {})
                .get("preferred_username", "")
                .lower()
            ):
                return Account(
                    username=account["username"], account_id=account["home_account_id"]
                )
        # If exact match not found, return the last account
        account = accounts[-1]
        return Account(
            username=account["username"], account_id=account["home_account_id"]
        )

    return None


def refresh_token(account_id: str) -> dict[str, str]:
    """Refresh access token for a specific account"""
    app = get_app()
    
    # Find the account
    accounts = app.get_accounts()
    account = None
    for acc in accounts:
        if acc["home_account_id"] == account_id:
            account = acc
            break
    
    if not account:
        raise ValueError(f"Account {account_id} not found")
    
    # Try to get token silently (refresh if needed)
    result = app.acquire_token_silent(SCOPES, account=account)
    
    if "error" in result:
        raise Exception(f"Token refresh failed: {result.get('error_description', result['error'])}")
    
    # Save updated cache
    cache = app.token_cache
    if isinstance(cache, msal.SerializableTokenCache) and cache.has_state_changed:
        _write_cache(cache.serialize())
    
    return {
        "status": "success",
        "message": "Token refreshed successfully",
        "expires_in": result.get("expires_in", 0),
        "token_type": result.get("token_type", "Bearer")
    }


def logout_account(account_id: str) -> dict[str, str]:
    """Logout and remove a specific account from the cache"""
    app = get_app()
    
    # Find the account
    accounts = app.get_accounts()
    account = None
    for acc in accounts:
        if acc["home_account_id"] == account_id:
            account = acc
            break
    
    if not account:
        return {"status": "error", "message": f"Account {account_id} not found"}
    
    # Remove the account from cache
    app.remove_account(account)
    
    # Save updated cache
    cache = app.token_cache
    if isinstance(cache, msal.SerializableTokenCache) and cache.has_state_changed:
        _write_cache(cache.serialize())
    
    return {
        "status": "success",
        "message": f"Account {account['username']} logged out successfully"
    }


def get_auth_status() -> dict[str, any]:
    """Get authentication status for all accounts"""
    app = get_app()
    accounts = app.get_accounts()
    
    account_statuses = []
    for account in accounts:
        # Check if we can get a token silently (indicates valid refresh token)
        result = app.acquire_token_silent(SCOPES, account=account)
        
        status = {
            "account_id": account["home_account_id"],
            "username": account["username"],
            "authenticated": "error" not in result,
        }
        
        if "error" not in result:
            status["expires_in"] = result.get("expires_in", 0)
            status["token_type"] = result.get("token_type", "Bearer")
        else:
            status["error"] = result.get("error_description", result.get("error"))
        
        account_statuses.append(status)
    
    return {
        "status": "success",
        "total_accounts": len(accounts),
        "authenticated_accounts": len([s for s in account_statuses if s["authenticated"]]),
        "accounts": account_statuses
    }


def authenticate_account() -> dict[str, any]:
    """Start device flow authentication for new account"""
    app = get_app()
    
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        return {
            "status": "error",
            "message": f"Failed to get device code: {flow.get('error_description', 'Unknown error')}"
        }
    
    return {
        "status": "success",
        "verification_uri": flow.get("verification_uri", flow.get("verification_url", "https://microsoft.com/devicelogin")),
        "user_code": flow["user_code"],
        "expires_in": flow.get("expires_in", 900),
        "message": "Visit the verification URI and enter the user code to complete authentication",
        "flow_cache": app.token_cache.serialize() if hasattr(app.token_cache, 'serialize') else "{}"
    }


def complete_authentication(flow_cache: str) -> dict[str, any]:
    """Complete authentication using cached flow data"""
    app = get_app()
    
    # Restore cache state
    if isinstance(app.token_cache, msal.SerializableTokenCache):
        app.token_cache.deserialize(flow_cache)
    
    # Get accounts to see if authentication completed
    accounts = app.get_accounts()
    
    if not accounts:
        return {
            "status": "error",
            "message": "Authentication not completed or timed out"
        }
    
    # Find the newest account (most recently authenticated)
    newest_account = accounts[-1]
    
    # Save cache
    cache = app.token_cache
    if isinstance(cache, msal.SerializableTokenCache) and cache.has_state_changed:
        _write_cache(cache.serialize())
    
    return {
        "status": "success",
        "message": "Authentication completed successfully",
        "account": {
            "username": newest_account["username"],
            "account_id": newest_account["home_account_id"]
        }
    }
