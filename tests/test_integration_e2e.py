"""End-to-End (E2E) Integration Tests.

These tests require REAL Microsoft Graph authentication and should only be run:
1. Manually by developers with authenticated accounts
2. In a dedicated E2E test environment with test accounts
3. NOT in CI/CD pipelines

To run these tests:
1. Ensure MICROSOFT_MCP_CLIENT_ID is set
2. Run: uv run python authenticate.py (to authenticate)
3. Run: pytest tests/test_integration_e2e.py -m e2e

These tests will be skipped in CI unless explicitly enabled.
"""

import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

# Skip all E2E tests if not in E2E mode
E2E_MODE = os.getenv("RUN_E2E_TESTS", "false").lower() == "true"

if not E2E_MODE:
    pytest.skip("E2E tests skipped - set RUN_E2E_TESTS=true to enable", allow_module_level=True)

if not os.getenv("MICROSOFT_MCP_CLIENT_ID"):
    pytest.skip("MICROSOFT_MCP_CLIENT_ID environment variable is required for E2E tests", allow_module_level=True)


def parse_result(result, tool_name=None):
    """Helper to parse MCP tool results consistently"""
    if result.content and hasattr(result.content[0], "text"):
        text = result.content[0].text
        if text == "[]":
            return []
        data = json.loads(text)
        # FastMCP seems to unwrap single-element lists, so rewrap for consistency
        list_tools = {
            "list_accounts",
            "list_emails",
            "list_events", 
            "list_contacts",
            "list_files",
        }
        if tool_name in list_tools and isinstance(data, dict):
            return [data]
        return data
    return []


async def get_session():
    """Get MCP session"""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "microsoft-mcp"],
        env={
            "MICROSOFT_MCP_CLIENT_ID": os.getenv("MICROSOFT_MCP_CLIENT_ID", ""),
            "MICROSOFT_MCP_TENANT_ID": os.getenv("MICROSOFT_MCP_TENANT_ID", "common"),
        },
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def get_account_info(session):
    """Get account info"""
    result = await session.call_tool("list_accounts", {})
    assert not result.isError, f"Failed to list accounts: {result.content}"
    accounts = parse_result(result, "list_accounts")
    assert accounts and len(accounts) > 0, (
        "No accounts found - please run 'uv run python authenticate.py' first"
    )

    return {"email": accounts[0]["username"], "account_id": accounts[0]["account_id"]}


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_list_accounts():
    """E2E test for list_accounts tool"""
    async for session in get_session():
        result = await session.call_tool("list_accounts", {})
        assert not result.isError
        accounts = parse_result(result, "list_accounts")
        assert accounts is not None
        assert len(accounts) > 0
        assert "username" in accounts[0]
        assert "account_id" in accounts[0]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_email_operations():
    """E2E test for email operations"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Test list emails
        result = await session.call_tool(
            "list_emails",
            {
                "account_id": account_info["account_id"],
                "limit": 3,
                "include_body": True,
            },
        )
        assert not result.isError
        emails = parse_result(result, "list_emails")
        assert emails is not None
        
        if len(emails) > 0:
            assert "id" in emails[0]
            assert "subject" in emails[0]
            assert "body" in emails[0]
            
            # Test get specific email
            email_id = emails[0].get("id")
            get_result = await session.call_tool(
                "get_email",
                {"email_id": email_id, "account_id": account_info["account_id"]},
            )
            assert not get_result.isError
            email_detail = parse_result(get_result)
            assert email_detail is not None
            assert "id" in email_detail


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_calendar_operations():
    """E2E test for calendar operations"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Test list events
        result = await session.call_tool(
            "list_events",
            {
                "account_id": account_info["account_id"],
                "days_ahead": 14,
                "include_details": True,
            },
        )
        assert not result.isError
        events = parse_result(result, "list_events")
        assert events is not None
        
        # Test create and delete event
        start_time = datetime.now(timezone.utc) + timedelta(days=7)
        end_time = start_time + timedelta(hours=1)
        
        create_result = await session.call_tool(
            "create_event",
            {
                "account_id": account_info["account_id"],
                "subject": "E2E Test Event",
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "location": "Test Location",
                "body": "This is an E2E test event",
            },
        )
        assert not create_result.isError
        event_data = parse_result(create_result)
        assert event_data is not None
        assert "id" in event_data
        
        # Clean up - delete the test event
        event_id = event_data.get("id")
        delete_result = await session.call_tool(
            "delete_event",
            {
                "account_id": account_info["account_id"],
                "event_id": event_id,
                "send_cancellation": False,
            },
        )
        assert not delete_result.isError


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_contact_operations():
    """E2E test for contact operations"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Test list contacts
        result = await session.call_tool(
            "list_contacts", {"account_id": account_info["account_id"], "limit": 10}
        )
        assert not result.isError
        contacts = parse_result(result, "list_contacts")
        assert contacts is not None
        
        # Test create and delete contact
        create_result = await session.call_tool(
            "create_contact",
            {
                "account_id": account_info["account_id"],
                "first_name": "E2E",
                "last_name": "TestContact",
                "email_addresses": ["e2e.test@example.com"],
            },
        )
        assert not create_result.isError
        new_contact = parse_result(create_result)
        assert new_contact is not None
        assert "id" in new_contact
        
        # Clean up - delete the test contact
        contact_id = new_contact.get("id")
        delete_result = await session.call_tool(
            "delete_contact",
            {"contact_id": contact_id, "account_id": account_info["account_id"]},
        )
        assert not delete_result.isError


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_file_operations():
    """E2E test for file operations"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Test list files
        result = await session.call_tool(
            "list_files", {"account_id": account_info["account_id"]}
        )
        assert not result.isError
        files = parse_result(result)
        assert files is not None
        
        # Test search files
        search_result = await session.call_tool(
            "search_files",
            {"account_id": account_info["account_id"], "query": "test", "limit": 5},
        )
        assert not search_result.isError
        search_results = parse_result(search_result)
        assert search_results is not None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_search_operations():
    """E2E test for search operations"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Test unified search
        result = await session.call_tool(
            "unified_search",
            {
                "account_id": account_info["account_id"],
                "query": "test",
                "entity_types": ["message"],
                "limit": 10,
            },
        )
        assert not result.isError
        search_results = parse_result(result)
        assert search_results is not None
        assert isinstance(search_results, dict)
        
        # Test email search
        email_search_result = await session.call_tool(
            "search_emails",
            {"account_id": account_info["account_id"], "query": "test", "limit": 5},
        )
        assert not email_search_result.isError
        email_results = parse_result(email_search_result)
        assert email_results is not None


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_e2e_email_draft_workflow():
    """E2E test for complete email draft workflow"""
    async for session in get_session():
        account_info = await get_account_info(session)
        
        # Create draft
        draft_result = await session.call_tool(
            "create_email_draft",
            {
                "account_id": account_info["account_id"],
                "to": account_info["email"],
                "subject": "E2E Test Draft",
                "body": "This is an E2E test draft email",
            },
        )
        assert not draft_result.isError
        draft_data = parse_result(draft_result)
        assert draft_data is not None
        assert "id" in draft_data
        
        draft_id = draft_data.get("id")
        
        # Update draft
        update_result = await session.call_tool(
            "update_email",
            {
                "email_id": draft_id,
                "account_id": account_info["account_id"],
                "updates": {"subject": "E2E Test Draft (Updated)"},
            },
        )
        assert not update_result.isError
        
        # Clean up - delete the draft
        delete_result = await session.call_tool(
            "delete_email",
            {"email_id": draft_id, "account_id": account_info["account_id"]},
        )
        assert not delete_result.isError


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio 
async def test_e2e_multi_account_support():
    """E2E test for multi-account functionality"""
    async for session in get_session():
        # List all accounts
        accounts_result = await session.call_tool("list_accounts", {})
        assert not accounts_result.isError
        accounts = parse_result(accounts_result, "list_accounts")
        assert accounts is not None
        
        if len(accounts) > 1:
            # Test operations with different accounts
            for account in accounts[:2]:  # Test first two accounts
                account_id = account["account_id"]
                
                # Test email listing for this account
                email_result = await session.call_tool(
                    "list_emails",
                    {"account_id": account_id, "limit": 1},
                )
                assert not email_result.isError
                
                # Test calendar listing for this account
                calendar_result = await session.call_tool(
                    "list_events",
                    {"account_id": account_id, "days_ahead": 7},
                )
                assert not calendar_result.isError
        else:
            pytest.skip("Multi-account test requires multiple authenticated accounts")


if __name__ == "__main__":
    # Instructions for running E2E tests manually
    print("""E2E Test Instructions:
    
    1. Set environment variable: export RUN_E2E_TESTS=true
    2. Authenticate: uv run python authenticate.py
    3. Run tests: pytest tests/test_integration_e2e.py -v -m e2e
    
    Optional: Run slow tests too: pytest tests/test_integration_e2e.py -v -m "e2e or slow"
    """)
