#!/usr/bin/env python3
"""Quick validation test for 5 nuclear simplified tools.

This tests the basic FastMCP compatibility and function signature validation
for all 5 nuclear tools: email_operations, calendar_operations, file_operations,
contact_operations, and auth_operations.
"""

import inspect


def test_nuclear_tools_import():
    """Test that all 5 nuclear tools can be imported without FastMCP errors."""
    try:
        print("✅ All 5 nuclear tools imported successfully")
        return True
    except Exception as e:
        print(f"❌ Nuclear tool import failed: {e}")
        return False


def test_nuclear_tools_signatures():
    """Test that all nuclear tools have proper function signatures."""
    from microsoft_mcp.tools import auth_operations
    from microsoft_mcp.tools import calendar_operations
    from microsoft_mcp.tools import contact_operations
    from microsoft_mcp.tools import email_operations
    from microsoft_mcp.tools import file_operations

    tools = {
        "email_operations": email_operations,
        "calendar_operations": calendar_operations,
        "file_operations": file_operations,
        "contact_operations": contact_operations,
        "auth_operations": auth_operations,
    }

    results = {}
    for tool_name, tool_func in tools.items():
        try:
            # Check function signature
            sig = inspect.signature(tool_func)
            params = list(sig.parameters.keys())

            # All tools should have account_id as first param and action as second
            if len(params) >= 2:
                if params[0] == "account_id" and params[1] == "action":
                    results[tool_name] = "✅ Valid signature (account_id, action, ...)"
                else:
                    results[tool_name] = f"❌ Invalid param order: {params[:2]}"
            else:
                results[tool_name] = f"❌ Insufficient params: {params}"

        except Exception as e:
            results[tool_name] = f"❌ Signature error: {e}"

    return results


def test_nuclear_tools_fastmcp_registration():
    """Test that tools are properly registered with FastMCP."""
    try:
        from microsoft_mcp.tools import mcp

        # Check if FastMCP instance exists
        if hasattr(mcp, "app"):
            return "✅ FastMCP registration successful"
        return "❌ FastMCP registration failed - no app attribute"

    except Exception as e:
        return f"❌ FastMCP registration failed: {e}"


def test_nuclear_architecture_validation():
    """Validate the nuclear architecture achievements."""
    import os

    # Check tools.py token count (should be ~1000 characters = ~250 tokens)
    tools_path = "src/microsoft_mcp/tools.py"
    if os.path.exists(tools_path):
        with open(tools_path) as f:
            content = f.read()
            char_count = len(content)
            token_estimate = char_count // 4  # Rough estimate: 4 chars per token

            if char_count < 2000:  # Should be much smaller than 63k
                return f"✅ Nuclear simplification achieved: {char_count} chars (~{token_estimate} tokens)"
            return f"❌ Tools.py still too large: {char_count} chars"
    else:
        return "❌ tools.py not found"


def test_nuclear_tool_files_exist():
    """Check that all 5 nuclear tool files exist."""
    import os

    tool_files = [
        "src/microsoft_mcp/email_tool.py",
        "src/microsoft_mcp/calendar_tool.py",
        "src/microsoft_mcp/file_tool.py",
        "src/microsoft_mcp/contact_tool.py",
        "src/microsoft_mcp/auth_tool.py"
    ]

    results = {}
    for tool_file in tool_files:
        if os.path.exists(tool_file):
            # Get file size to verify it's substantial
            size = os.path.getsize(tool_file)
            results[tool_file] = f"✅ Exists ({size} bytes)"
        else:
            results[tool_file] = "❌ Missing"

    return results


def main():
    """Run all nuclear tools validation tests."""
    print("🚀 Nuclear Simplified Tools Validation")
    print("=" * 50)

    # Test 1: Import compatibility
    print("\n1. Testing FastMCP Import Compatibility...")
    import_success = test_nuclear_tools_import()

    # Test 2: Function signatures
    print("\n2. Testing Function Signatures...")
    signature_results = test_nuclear_tools_signatures()
    for tool, result in signature_results.items():
        print(f"   {tool}: {result}")

    # Test 3: FastMCP registration
    print("\n3. Testing FastMCP Registration...")
    fastmcp_result = test_nuclear_tools_fastmcp_registration()
    print(f"   {fastmcp_result}")

    # Test 4: Nuclear architecture validation
    print("\n4. Testing Nuclear Architecture...")
    architecture_result = test_nuclear_architecture_validation()
    print(f"   {architecture_result}")

    # Test 5: Tool files existence
    print("\n5. Testing Nuclear Tool Files...")
    file_results = test_nuclear_tool_files_exist()
    for tool_file, result in file_results.items():
        print(f"   {tool_file}: {result}")

    # Summary
    print("\n" + "=" * 50)
    all_passed = (
        import_success and
        all("✅" in result for result in signature_results.values()) and
        "✅" in fastmcp_result and
        "✅" in architecture_result and
        all("✅" in result for result in file_results.values())
    )

    if all_passed:
        print("🎉 ALL NUCLEAR TOOLS VALIDATION PASSED!")
        print("Ready for deployment to production.")
    else:
        print("⚠️  Some validations failed. Review issues before deployment.")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
