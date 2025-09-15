#!/usr/bin/env python3
"""
Focused debug script for pagination infinite loop issue.

Based on analysis, the most likely culprit is in the graph.py pagination logic.
This script will specifically test the pagination function with detailed logging.
"""

import logging
import os
import signal
import sys
from contextlib import contextmanager

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(sys.stderr)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
)

log = logging.getLogger(__name__)

@contextmanager
def timeout_context(seconds):
    """Context manager to timeout operations."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def patch_graph_module_for_debugging():
    """Patch the graph module to add extensive debugging."""
    from microsoft_mcp import graph

    # Store original functions
    original_request = graph.request
    original_paginate = graph.request_paginated

    def debug_request(method, path, account_id=None, params=None, json=None, data=None, max_retries=3):
        log.debug(f"GRAPH REQUEST: {method} {path}")
        log.debug(f"  account_id: {account_id}")
        log.debug(f"  params: {params}")
        log.debug(f"  max_retries: {max_retries}")

        try:
            result = original_request(method, path, account_id, params, json, data, max_retries)
            log.debug(f"GRAPH RESPONSE: {type(result)} - {len(str(result)) if result else 0} chars")

            # Log important response fields
            if result and isinstance(result, dict):
                if "value" in result:
                    log.debug(f"  Response has 'value' with {len(result['value'])} items")
                if "@odata.nextLink" in result:
                    log.debug(f"  Response has nextLink: {result['@odata.nextLink'][:100]}...")
                else:
                    log.debug("  Response has NO nextLink")

            return result
        except Exception as e:
            log.error(f"GRAPH REQUEST FAILED: {e}")
            raise

    def debug_paginate(path, account_id=None, params=None, limit=None):
        log.debug(f"PAGINATION START: {path}")
        log.debug(f"  account_id: {account_id}")
        log.debug(f"  params: {params}")
        log.debug(f"  limit: {limit}")

        items_returned = 0
        next_link = None
        iteration_count = 0

        while True:
            iteration_count += 1
            log.debug(f"PAGINATION ITERATION {iteration_count}")

            if iteration_count > 100:  # Safety brake
                log.error("PAGINATION: Breaking infinite loop after 100 iterations!")
                break

            if next_link:
                log.debug(f"  Using nextLink: {next_link[:100]}...")
                result = debug_request("GET", next_link.replace(graph.BASE_URL, ""), account_id)
            else:
                log.debug(f"  Initial request to: {path}")
                result = debug_request("GET", path, account_id, params=params)

            if not result:
                log.debug("PAGINATION: No result, breaking")
                break

            if "value" in result:
                log.debug(f"PAGINATION: Processing {len(result['value'])} items")
                for item in result["value"]:
                    if limit and items_returned >= limit:
                        log.debug(f"PAGINATION: Limit reached ({limit}), returning")
                        return
                    yield item
                    items_returned += 1
                    log.debug(f"PAGINATION: Yielded item {items_returned}")
            else:
                log.debug("PAGINATION: No 'value' in result")

            next_link = result.get("@odata.nextLink")
            if not next_link:
                log.debug("PAGINATION: No nextLink, breaking")
                break
            else:
                log.debug("PAGINATION: Got nextLink for next iteration")

    # Apply patches
    graph.request = debug_request
    graph.request_paginated = debug_paginate
    graph.paginate = debug_paginate  # This is the alias


def test_pagination_detailed():
    """Test pagination with detailed debugging."""
    log.info("=== DETAILED PAGINATION TEST ===")

    try:
        # Patch the graph module first
        patch_graph_module_for_debugging()

        from microsoft_mcp import graph
        from microsoft_mcp.auth import list_accounts

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available")
            return None

        account_id = accounts[0].account_id
        log.info(f"Using account: {account_id}")

        # Test pagination with very conservative settings
        endpoint = "/me/mailFolders/inbox/messages"
        params = {
            "$top": 1,  # Request only 1 item per page
            "$select": "id,subject",  # Minimal fields
        }

        log.info("Starting pagination test...")
        with timeout_context(30):
            items = list(graph.paginate(endpoint, account_id, params=params, limit=2))

        log.info(f"Pagination completed successfully: {len(items)} items")
        return {"status": "success", "items_count": len(items)}

    except TimeoutError as e:
        log.error(f"Pagination timed out: {e}")
        return {"status": "timeout", "message": str(e)}
    except Exception as e:
        log.error(f"Pagination failed: {e}")
        import traceback
        log.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}


def test_simple_email_list():
    """Test the _list_emails function specifically."""
    log.info("=== TESTING _list_emails FUNCTION ===")

    try:
        patch_graph_module_for_debugging()

        from microsoft_mcp.auth import list_accounts
        from microsoft_mcp.email_tool import _list_emails

        accounts = list_accounts()
        if not accounts:
            log.error("No accounts available")
            return None

        account_id = accounts[0].account_id
        log.info(f"Testing _list_emails with account: {account_id}")

        log.info("Calling _list_emails with minimal parameters...")
        with timeout_context(30):
            result = _list_emails(
                account_id=account_id,
                folder_name="inbox",
                limit=1,  # Very small limit
                include_body=False,
                search_query=None,
                skip=0
            )

        log.info(f"_list_emails completed: {result}")
        return result

    except TimeoutError as e:
        log.error(f"_list_emails timed out: {e}")
        return {"status": "timeout", "message": str(e)}
    except Exception as e:
        log.error(f"_list_emails failed: {e}")
        import traceback
        log.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}


def main():
    """Main debugging function."""
    log.info("Starting focused pagination debugging")
    log.info("=" * 60)

    # Test sequence
    tests = [
        ("pagination_detailed", test_pagination_detailed),
        ("list_emails_function", test_simple_email_list),
    ]

    results = {}

    for test_name, test_func in tests:
        log.info(f"\n--- Running test: {test_name} ---")
        try:
            result = test_func()
            results[test_name] = result

            if result and result.get("status") in ["timeout", "error"]:
                log.warning(f"Test {test_name} failed, stopping here")
                break

        except Exception as e:
            log.error(f"Test {test_name} crashed: {e}")
            results[test_name] = {"status": "crash", "message": str(e)}
            break

    log.info("\n" + "=" * 60)
    log.info("PAGINATION DEBUG RESULTS:")
    for test_name, result in results.items():
        if result:
            status = result.get("status", "unknown")
            log.info(f"  {test_name}: {status}")
        else:
            log.info(f"  {test_name}: None (failed)")

    # Print results to stdout
    print("\n=== PAGINATION DEBUG RESULTS ===", file=sys.stdout)
    for test_name, result in results.items():
        print(f"{test_name}: {result}", file=sys.stdout)


if __name__ == "__main__":
    main()
