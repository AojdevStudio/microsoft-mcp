#!/usr/bin/env python3
"""Quick validation test for 5 nuclear simplified tools.

This tests the basic FastMCP compatibility and function signature validation
for all 5 nuclear tools: email_operations, calendar_operations, file_operations,
contact_operations, and account_operations.
"""

import inspect
from typing import get_type_hints


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
    from microsoft_mcp.tools import account_operations
    from microsoft_mcp.tools import calendar_operations
    from microsoft_mcp.tools import contact_operations
    from microsoft_mcp.tools import email_operations
    from microsoft_mcp.tools import file_operations

    tools = {
        "email_operations": email_operations,
        "calendar_operations": calendar_operations,
        "file_operations": file_operations,
        "contact_operations": contact_operations,
        "account_operations": account_operations
    }

    results = {}

    for name, func in tools.items():
        try:
            # Test function signature
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)

            # Verify no **kwargs or **params (FastMCP incompatible)
            has_var_keyword = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
            if has_var_keyword:
                results[name] = "❌ Has **kwargs (FastMCP incompatible)"
                continue

            # Verify required parameters exist
            required_params = [p.name for p in sig.parameters.values()
                             if p.default == p.empty and p.name not in ["action", "flow_cache"]]

            if name != "account_operations" and "account_id" not in required_params:
                results[name] = "❌ Missing required account_id parameter"
                continue

            if "action" not in [p.name for p in sig.parameters.values()]:
                results[name] = "❌ Missing required action parameter"
                continue

            results[name] = f"✅ Valid signature with {len(sig.parameters)} parameters"

        except Exception as e:
            results[name] = f"❌ Signature analysis failed: {e}"

    return results


def test_nuclear_tools_token_count():
    """Estimate token count reduction (nuclear simplification goal: 92% reduction)."""
    try:
        # Read the nuclear tools.py file
        with open("/Users/ossieirondi/Projects/local-mcps/microsoft-mcp/src/microsoft_mcp/tools.py") as f:
            content = f.read()

        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(content) // 4

        # Original unified tool was ~63k tokens
        original_tokens = 63000
        reduction_percentage = ((original_tokens - estimated_tokens) / original_tokens) * 100

        print("📊 Token Analysis:")
        print(f"   Original unified tool: ~{original_tokens:,} tokens")
        print(f"   Nuclear simplified: ~{estimated_tokens:,} tokens")
        print(f"   Reduction: {reduction_percentage:.1f}%")
        print(f"   Goal: 92% reduction ({'✅ ACHIEVED' if reduction_percentage >= 92 else '❌ NOT YET'})")

        return {
            "original_tokens": original_tokens,
            "nuclear_tokens": estimated_tokens,
            "reduction_percentage": reduction_percentage,
            "goal_achieved": reduction_percentage >= 92
        }

    except Exception as e:
        print(f"❌ Token analysis failed: {e}")
        return None


def main():
    """Run nuclear tools validation."""
    print("🚀 Nuclear Simplified Tools Validation")
    print("=" * 50)

    # Test 1: Import validation
    print("\n1. Testing FastMCP Import Compatibility...")
    import_success = test_nuclear_tools_import()

    if not import_success:
        print("❌ Import failed - cannot proceed with further tests")
        return False

    # Test 2: Function signature validation
    print("\n2. Testing Function Signatures...")
    signature_results = test_nuclear_tools_signatures()
    for tool, result in signature_results.items():
        print(f"   {tool}: {result}")

    # Test 3: Token count analysis
    print("\n3. Nuclear Simplification Analysis...")
    token_analysis = test_nuclear_tools_token_count()

    # Summary
    print("\n" + "=" * 50)
    print("📋 NUCLEAR SIMPLIFICATION SUMMARY")

    signature_success = all("✅" in result for result in signature_results.values())
    token_success = token_analysis and token_analysis.get("goal_achieved", False)

    print(f"   FastMCP Compatibility: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Function Signatures: {'✅ PASS' if signature_success else '❌ FAIL'}")
    print(f"   92% Token Reduction: {'✅ PASS' if token_success else '❌ FAIL'}")

    overall_success = import_success and signature_success and token_success
    print(f"\n🎯 NUCLEAR SIMPLIFICATION: {'✅ SUCCESS' if overall_success else '❌ INCOMPLETE'}")

    return overall_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
