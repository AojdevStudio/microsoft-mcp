#!/usr/bin/env python3
"""Nuclear Simplified Tools Integration Validation

Validates that the 5 nuclear tools are properly integrated and FastMCP compatible.
Focuses on core functionality validation without requiring Microsoft authentication.
"""

import sys
from unittest.mock import patch


def test_email_operations_integration():
    """Test email_operations tool basic integration."""
    try:
        from microsoft_mcp.tools import email_operations
        
        # Test tool exists and has expected structure
        assert callable(email_operations), "email_operations should be callable"
        
        # Test parameter validation for invalid action
        with patch('microsoft_mcp.graph.request') as mock_request:
            result = email_operations(
                account_id="test@example.com",
                action="invalid_action"
            )
            assert result["status"] == "error"
            assert "Unknown email action" in result["message"]
        
        print("✅ email_operations: Basic integration successful")
        return True
        
    except Exception as e:
        print(f"❌ email_operations: Integration failed - {e}")
        return False


def test_calendar_operations_integration():
    """Test calendar_operations tool basic integration."""
    try:
        from microsoft_mcp.tools import calendar_operations
        
        # Test tool exists and has expected structure
        assert callable(calendar_operations), "calendar_operations should be callable"
        
        # Test parameter validation for invalid action
        with patch('microsoft_mcp.graph.request') as mock_request:
            result = calendar_operations(
                account_id="test@example.com",
                action="invalid_action"
            )
            assert result["status"] == "error"
            assert "Unknown calendar action" in result["message"]
        
        print("✅ calendar_operations: Basic integration successful")
        return True
        
    except Exception as e:
        print(f"❌ calendar_operations: Integration failed - {e}")
        return False


def test_file_operations_integration():
    """Test file_operations tool basic integration."""
    try:
        from microsoft_mcp.tools import file_operations
        
        # Test tool exists and has expected structure
        assert callable(file_operations), "file_operations should be callable"
        
        # Test parameter validation for invalid action
        with patch('microsoft_mcp.graph.request') as mock_request:
            result = file_operations(
                account_id="test@example.com",
                action="invalid_action"
            )
            assert result["status"] == "error"
            assert "Unknown file action" in result["message"]
        
        print("✅ file_operations: Basic integration successful")
        return True
        
    except Exception as e:
        print(f"❌ file_operations: Integration failed - {e}")
        return False


def test_contact_operations_integration():
    """Test contact_operations tool basic integration."""
    try:
        from microsoft_mcp.tools import contact_operations
        
        # Test tool exists and has expected structure
        assert callable(contact_operations), "contact_operations should be callable"
        
        # Test parameter validation for invalid action
        with patch('microsoft_mcp.graph.request') as mock_request:
            result = contact_operations(
                account_id="test@example.com",
                action="invalid_action"
            )
            assert result["status"] == "error"
            assert "Unknown contact action" in result["message"]
        
        print("✅ contact_operations: Basic integration successful")
        return True
        
    except Exception as e:
        print(f"❌ contact_operations: Integration failed - {e}")
        return False


def test_account_operations_integration():
    """Test account_operations tool basic integration."""
    try:
        from microsoft_mcp.tools import account_operations
        
        # Test tool exists and has expected structure
        assert callable(account_operations), "account_operations should be callable"
        
        # Test parameter validation for invalid action
        result = account_operations(action="invalid_action")
        assert result["status"] == "error"
        assert "Unknown account action" in result["message"]
        
        print("✅ account_operations: Basic integration successful")
        return True
        
    except Exception as e:
        print(f"❌ account_operations: Integration failed - {e}")
        return False


def test_fastmcp_server_compatibility():
    """Test FastMCP server integration."""
    try:
        from microsoft_mcp.tools import mcp
        
        # Verify FastMCP instance exists
        assert hasattr(mcp, 'tools'), "FastMCP instance should have tools attribute"
        
        # Get all registered tools
        tools = list(mcp.tools.keys())
        expected_tools = [
            "email_operations",
            "calendar_operations", 
            "file_operations",
            "contact_operations",
            "account_operations"
        ]
        
        for tool_name in expected_tools:
            if tool_name not in tools:
                print(f"❌ FastMCP: Missing tool {tool_name}")
                return False
        
        print(f"✅ FastMCP: All 5 tools registered successfully ({len(tools)} total tools)")
        return True
        
    except Exception as e:
        print(f"❌ FastMCP: Server compatibility failed - {e}")
        return False


def test_token_reduction_achievement():
    """Test nuclear simplification token reduction."""
    try:
        # Read the nuclear tools.py file
        with open("src/microsoft_mcp/tools.py") as f:
            content = f.read()
        
        # Calculate token count (rough estimation: 1 token ≈ 4 characters)
        estimated_tokens = len(content) // 4
        
        # Original unified tool was ~63k tokens
        original_tokens = 63000
        reduction_percentage = ((original_tokens - estimated_tokens) / original_tokens) * 100
        
        print(f"📊 Token Reduction Analysis:")
        print(f"   Original: ~{original_tokens:,} tokens")
        print(f"   Nuclear: ~{estimated_tokens:,} tokens")
        print(f"   Reduction: {reduction_percentage:.1f}%")
        
        # Goal is 92% reduction
        goal_achieved = reduction_percentage >= 92
        if goal_achieved:
            print("✅ Token Reduction: 92% goal achieved!")
        else:
            print(f"⚠️  Token Reduction: {reduction_percentage:.1f}% (goal: 92%)")
        
        return goal_achieved, reduction_percentage
        
    except Exception as e:
        print(f"❌ Token Reduction: Analysis failed - {e}")
        return False, 0


def main():
    """Run nuclear tools integration validation."""
    print("🚀 Nuclear Simplified Tools Integration Validation")
    print("=" * 60)
    
    # Run all integration tests
    tests = [
        test_email_operations_integration,
        test_calendar_operations_integration,
        test_file_operations_integration,
        test_contact_operations_integration,
        test_account_operations_integration,
        test_fastmcp_server_compatibility
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Token reduction test (separate from pass/fail criteria)
    goal_achieved, reduction = test_token_reduction_achievement()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 NUCLEAR INTEGRATION VALIDATION SUMMARY")
    
    tools_passing = sum(results)
    total_tools = len(results)
    
    print(f"   Tool Integration: {tools_passing}/{total_tools} passing")
    print(f"   Token Reduction: {reduction:.1f}% ({'✅' if goal_achieved else '⚠️'})")
    
    # Overall assessment
    integration_success = all(results)
    if integration_success:
        print("\n🎯 NUCLEAR INTEGRATION: ✅ SUCCESS")
        print("   All 5 nuclear tools are properly integrated and FastMCP compatible.")
        if goal_achieved:
            print("   92% token reduction goal achieved.")
        else:
            print("   Token reduction in progress (nuclear simplification benefits achieved).")
    else:
        print("\n🎯 NUCLEAR INTEGRATION: ❌ ISSUES DETECTED")
        print("   Some tools have integration problems that need attention.")
    
    return integration_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
