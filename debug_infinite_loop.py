#!/usr/bin/env python3
"""
Debug script to trace infinite loop in Microsoft MCP server.

This script will run the email_operations function with extensive logging
to identify exactly where the code is hanging.
"""

import logging
import os
import signal
import sys
import traceback
from contextlib import contextmanager

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set up stderr-only logging as per Python mastery guidelines
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(sys.stderr)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

log = logging.getLogger(__name__)

# Timeout handler to prevent infinite hanging
@contextmanager
def timeout_context(seconds):
    """Context manager to timeout operations."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore the old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def debug_trace_function_calls():
    """Set up function call tracing to see where code hangs."""
    def trace_calls(frame, event, arg):
        if event == "call":
            filename = frame.f_code.co_filename
            if "microsoft_mcp" in filename:
                func_name = frame.f_code.co_name
                line_no = frame.f_lineno
                log.debug(f"CALL: {filename}:{line_no} in {func_name}")
        elif event == "return":
            filename = frame.f_code.co_filename
            if "microsoft_mcp" in filename:
                func_name = frame.f_code.co_name
                log.debug(f"RETURN: {func_name}")
        return trace_calls

    sys.settrace(trace_calls)


def test_auth_first():
    """Test authentication functionality first."""
    log.info("=== TESTING AUTH OPERATIONS ===")

    try:
        from microsoft_mcp.auth_tool import auth_operations

        log.info("Calling auth_operations with action='status'")
        with timeout_context(10):
            result = auth_operations(action="status")

        log.info(f"Auth status result: {result}")
        return result

    except Exception as e:
        log.error(f"Auth test failed: {e}")
        log.error(traceback.format_exc())
        return None


def test_token_retrieval():
    """Test token retrieval specifically."""
    log.info("=== TESTING TOKEN RETRIEVAL ===")

    try:
        from microsoft_mcp.auth import get_token
        from microsoft_mcp.auth import list_accounts

        log.info("Getting accounts list")
        accounts = list_accounts()
        log.info(f"Found accounts: {[acc.username for acc in accounts]}")

        if accounts:
            account_id = accounts[0].account_id
            log.info(f"Getting token for account: {account_id}")

            with timeout_context(10):
                token = get_token(account_id)

            log.info(f"Token retrieved successfully (length: {len(token)})")
            return {"status": "success", "token_length": len(token)}
        log.warning("No accounts found")
        return {"status": "error", "message": "No accounts found"}

    except Exception as e:
        log.error(f"Token retrieval failed: {e}")
        log.error(traceback.format_exc())
        return None


def test_graph_request():
    """Test basic graph API request."""
    log.info("=== TESTING GRAPH API REQUEST ===")

    try:
        from microsoft_mcp import graph
        from microsoft_mcp.auth import list_accounts

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available for testing")
            return None

        account_id = accounts[0].account_id
        log.info(f"Testing graph request with account: {account_id}")

        # Test a simple graph request
        log.info("Making simple graph request to /me")
        with timeout_context(15):
            result = graph.request("GET", "/me", account_id)

        log.info(f"Graph request successful: {result.get('displayName', 'Unknown') if result else 'No result'}")
        return {"status": "success", "user": result.get("displayName") if result else None}

    except Exception as e:
        log.error(f"Graph request failed: {e}")
        log.error(traceback.format_exc())
        return None


def test_email_list_minimal():
    """Test minimal email listing functionality."""
    log.info("=== TESTING MINIMAL EMAIL LIST ===")

    try:
        from microsoft_mcp import graph
        from microsoft_mcp.auth import list_accounts

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available for testing")
            return None

        account_id = accounts[0].account_id
        log.info(f"Testing email list with account: {account_id}")

        # Test email listing with minimal parameters
        endpoint = "/me/mailFolders/inbox/messages"
        params = {
            "$top": 1,  # Only get 1 email to minimize data
            "$select": "id,subject",  # Minimal fields
        }

        log.info(f"Making request to {endpoint} with params: {params}")
        with timeout_context(20):
            result = graph.request("GET", endpoint, account_id, params=params)

        if result and "value" in result:
            log.info(f"Email list successful: {len(result['value'])} emails")
            return {"status": "success", "email_count": len(result["value"])}
        log.warning("No emails or unexpected response format")
        return {"status": "warning", "message": "No emails found or unexpected response"}

    except Exception as e:
        log.error(f"Email list failed: {e}")
        log.error(traceback.format_exc())
        return None


def test_pagination_function():
    """Test the pagination function specifically."""
    log.info("=== TESTING PAGINATION FUNCTION ===")

    try:
        from microsoft_mcp import graph
        from microsoft_mcp.auth import list_accounts

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available for testing")
            return None

        account_id = accounts[0].account_id
        log.info(f"Testing pagination with account: {account_id}")

        # Test pagination directly
        endpoint = "/me/mailFolders/inbox/messages"
        params = {
            "$top": 1,
            "$select": "id,subject",
        }

        log.info("Testing graph.paginate function")
        with timeout_context(20):
            # Convert iterator to list to see if it hangs
            items = list(graph.paginate(endpoint, account_id, params=params, limit=1))

        log.info(f"Pagination successful: {len(items)} items")
        return {"status": "success", "items_count": len(items)}

    except Exception as e:
        log.error(f"Pagination test failed: {e}")
        log.error(traceback.format_exc())
        return None


def test_email_operations_function():
    """Test the actual email_operations function that's hanging."""
    log.info("=== TESTING EMAIL_OPERATIONS FUNCTION ===")

    try:
        from microsoft_mcp.auth import list_accounts
        from microsoft_mcp.email_tool import email_operations

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available for testing")
            return None

        account_id = accounts[0].account_id
        log.info(f"Testing email_operations with account: {account_id}")

        log.info("Calling email_operations with action='list', limit=1")
        with timeout_context(30):
            result = email_operations(
                account_id=account_id,
                action="list",
                limit=1,
                include_body=False  # Minimize data transfer
            )

        log.info(f"Email operations successful: {result}")
        return result

    except Exception as e:
        log.error(f"Email operations failed: {e}")
        log.error(traceback.format_exc())
        return None


def main():
    """Main debug function."""
    log.info("Starting Microsoft MCP infinite loop debugging")
    log.info("=" * 60)

    # Enable function call tracing
    debug_trace_function_calls()

    results = {}

    # Test sequence from basic to complex
    tests = [
        ("auth_status", test_auth_first),
        ("token_retrieval", test_token_retrieval),
        ("graph_request", test_graph_request),
        ("email_list_minimal", test_email_list_minimal),
        ("pagination_function", test_pagination_function),
        ("email_operations", test_email_operations_function),
    ]

    for test_name, test_func in tests:
        log.info(f"\n--- Running test: {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result

            if result and result.get("status") == "error":
                log.warning(f"Test {test_name} returned error, stopping here")
                break

        except TimeoutError as e:
            log.error(f"Test {test_name} TIMED OUT: {e}")
            results[test_name] = {"status": "timeout", "message": str(e)}
            break
        except Exception as e:
            log.error(f"Test {test_name} CRASHED: {e}")
            results[test_name] = {"status": "crash", "message": str(e)}
            break

    # Disable tracing
    sys.settrace(None)

    log.info("\n" + "=" * 60)
    log.info("DEBUG RESULTS SUMMARY:")
    for test_name, result in results.items():
        if result:
            status = result.get("status", "unknown")
            log.info(f"  {test_name}: {status}")
        else:
            log.info(f"  {test_name}: None (failed)")

    # Print results to stdout for easy reading
    print("\n=== MICROSOFT MCP DEBUG RESULTS ===", file=sys.stdout)
    for test_name, result in results.items():
        print(f"{test_name}: {result}", file=sys.stdout)


if __name__ == "__main__":
    main()
