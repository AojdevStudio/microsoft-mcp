# Story 1.2: Test Strategy Addendum

## Test Implementation Approach

### 1. Maintain Existing Tests (Zero Regression)
**DO NOT modify existing tests for the 61 tools**
- All existing tests in `tests/` must continue passing unchanged
- This proves backward compatibility is maintained
- Run: `pytest tests/ -k "not test_microsoft_operations"`

### 2. Create New Test File for Unified Tool
**Create: `tests/test_microsoft_operations.py`**

```python
import pytest
from microsoft_mcp.tools import microsoft_operations
from microsoft_mcp.email_params import (
    BaseEmailParams,
    ListEmailParams,
    SendEmailParams,
    ReplyEmailParams,
    DraftEmailParams,
    DeleteEmailParams
)

class TestMicrosoftOperations:
    """Test suite for unified microsoft_operations tool"""
    
    def test_email_list_action(self, mock_graph_client):
        """Test email.list action matches list_emails behavior"""
        # Test that microsoft_operations with action="email.list"
        # produces same result as list_emails tool
        
    def test_email_send_action(self, mock_graph_client):
        """Test email.send action matches send_email behavior"""
        # Verify parameter validation from Story 1.1
        # Verify email styling utilities are called
        
    def test_email_reply_action(self, mock_graph_client):
        """Test email.reply action matches reply_to_email behavior"""
        
    def test_email_draft_action(self, mock_graph_client):
        """Test email.draft action matches create_email_draft behavior"""
        
    def test_email_delete_action(self, mock_graph_client):
        """Test email.delete action matches delete_email behavior"""
        
    def test_invalid_action_handling(self):
        """Test proper error for invalid actions"""
        
    def test_parameter_validation_integration(self):
        """Test Story 1.1 validation framework is properly integrated"""
        
    def test_template_parameter_triggers_styling(self):
        """Test that template parameter calls email styling utilities"""
```

### 3. Create Parallel Testing Strategy

**Approach: Test Equivalence**
```python
# tests/test_equivalence.py
class TestToolEquivalence:
    """Verify unified tool produces same results as legacy tools"""
    
    @pytest.mark.parametrize("test_case", [
        # Each test case runs BOTH implementations
        {"legacy": "list_emails", "unified": "email.list"},
        {"legacy": "send_email", "unified": "email.send"},
        {"legacy": "reply_to_email", "unified": "email.reply"},
    ])
    def test_legacy_unified_equivalence(self, test_case):
        # Run legacy tool
        legacy_result = call_legacy_tool(test_case["legacy"], params)
        
        # Run unified tool
        unified_result = microsoft_operations(
            action=test_case["unified"],
            data=params
        )
        
        # Assert results are identical
        assert legacy_result == unified_result
```

### 4. Test Email Styling Utilities

**Create: `tests/test_email_utilities.py`**
```python
from microsoft_mcp.email_framework.utils import (
    ensure_html_structure,
    apply_template,
    inline_css
)

class TestEmailUtilities:
    """Test email styling utilities (not tools)"""
    
    def test_ensure_html_structure(self):
        """Test HTML structure generation"""
        # These replace the quarantined tests
        # But test utilities, not tools
        
    def test_apply_template_baytown(self):
        """Test Baytown theme application"""
        
    def test_inline_css_conversion(self):
        """Test CSS to inline conversion"""
```

### 5. Quarantined Test Strategy

**For the 21+ quarantined tests:**
- **DO NOT restore them as-is** (they test non-existent tools)
- **CREATE new utility tests** that validate the same functionality
- **Example transformation:**

```python
# OLD (Quarantined) - Tests a tool that doesn't exist
def test_send_practice_report_tool():
    result = send_practice_report(data)  # This tool doesn't exist
    
# NEW - Tests the utility function
def test_practice_report_template_utility():
    html = apply_template("practice_report", data)
    assert "Baytown" in html  # Verify theming
    assert inline_css(html)  # Verify CSS inlining
```

### 6. Test Execution Plan

```bash
# Phase 1: Verify no regression (existing tools work)
pytest tests/ -v --tb=short

# Phase 2: Test new unified tool
pytest tests/test_microsoft_operations.py -v

# Phase 3: Test equivalence between old and new
pytest tests/test_equivalence.py -v

# Phase 4: Test email utilities
pytest tests/test_email_utilities.py -v

# Phase 5: Performance benchmarks
pytest tests/test_microsoft_operations.py -v -k "performance"
```

### 7. Continuous Integration Updates

**Update `.github/workflows/test.yml`:**
```yaml
- name: Test Backward Compatibility
  run: pytest tests/ -k "not microsoft_operations"
  
- name: Test Unified Tool
  run: pytest tests/test_microsoft_operations.py
  
- name: Test Tool Equivalence
  run: pytest tests/test_equivalence.py
```

## Success Criteria for Testing

1. ✅ All 163+ existing tests pass unchanged
2. ✅ New microsoft_operations tests cover all 5 email actions
3. ✅ Equivalence tests prove identical behavior
4. ✅ Email utility tests replace quarantined test functionality
5. ✅ Performance benchmarks met (< 100ms routing)

## Key Principle

**Test the implementation, not the interface:**
- Old interface (61 tools) → Keep tests unchanged
- New interface (unified tool) → Create new tests
- Utilities (not tools) → Test as utilities
- Equivalence → Prove both paths work identically

This approach ensures zero regression while building confidence in the new unified architecture.