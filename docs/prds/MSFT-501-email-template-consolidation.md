# [FEATURE] Consolidate Email Template Tools into Generic Email API

## Metadata
- **Priority:** High
- **Status:** Backlog
- **Assignee:** AI Agent
- **Estimate:** 8 Story Points
- **Issue ID:** MSFT-501
- **Labels:** 
  - type:feature
  - priority:high
  - agent-ready
  - api-consolidation
  - email-framework
  - backward-compatibility

## Problem Statement

### What
Consolidate the four specialized email template tools (`send_practice_report`, `send_executive_summary`, `send_provider_update`, `send_alert_notification`) into the existing generic email tools (`create_email_draft`, `send_email`) while preserving all template functionality and maintaining backward compatibility.

### Why
**Current Issues:**
- **API Bloat:** 6 email tools when 2 would suffice, creating confusion for users
- **Maintenance Burden:** Multiple tools with overlapping functionality require more maintenance
- **Discovery Problem:** Users may not discover the sophisticated template framework capabilities
- **Code Duplication:** Template tools are thin wrappers around `send_email()`, creating unnecessary indirection

**Business Impact:**
- Simplified developer experience reduces onboarding time by ~30%
- Reduced API surface area improves maintainability
- Better discoverability of professional email templates increases usage
- Unified approach enables future template expansion without API proliferation

### Context
The Microsoft MCP server currently has a sophisticated email template framework with:
- Professional themes (baytown, humble, executive) with CSS styling
- CSS inlining and minification for email client compatibility
- Template-specific data validation and rendering
- Signature automation and professional formatting

Analysis shows template tools already use `send_email()` internally, making consolidation architecturally straightforward. The email framework infrastructure is well-designed and just needs exposure through the generic API.

## Acceptance Criteria

- [ ] **AC1:** `create_email_draft()` and `send_email()` support optional `template_name` parameter that triggers template rendering when provided
- [ ] **AC2:** All existing template functionality preserved: themes, CSS inlining, professional styling, data validation
- [ ] **AC3:** New `list_email_templates()` tool provides template discovery with descriptions and required data schemas
- [ ] **AC4:** Template mode validates input data and provides clear error messages for missing/invalid fields
- [ ] **AC5:** Backward compatibility maintained - existing template tools continue working with deprecation warnings
- [ ] **AC6:** Template themes automatically selected based on `location` parameter when provided
- [ ] **AC7:** Both simple HTML emails and template-based emails work seamlessly through same API
- [ ] **AC8:** Template mode preserves signature automation and professional formatting
- [ ] **AC9:** Error handling provides actionable guidance for template data requirements
- [ ] **AC10:** Documentation updated with template usage examples and migration guidance

## Technical Requirements

### Implementation Notes
- **Template Registry:** Create mapping of template names to template classes for dynamic instantiation
- **Parameter Validation:** Implement robust validation for template-specific data requirements
- **Theme Auto-Selection:** Use `location` parameter to auto-select appropriate theme (baytown/humble)
- **Graceful Fallback:** If template rendering fails, fall back to simple HTML mode with warning
- **CSS Framework Integration:** Maintain existing CSS inlining and email compatibility features
- **Signature Preservation:** Ensure signature automation works in both template and simple modes

### API Design Specification

#### Enhanced send_email() Signature
```python
@mcp.tool
def send_email(
    account_id: str,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: str | list[str] | None = None,
    # NEW PARAMETERS
    template_name: str | None = None,
    template_data: dict[str, Any] | None = None,
    theme: str | None = None,
    location: str | None = None,  # Auto-theme selection
) -> dict[str, str]:
```

#### New Template Discovery Tool
```python
@mcp.tool  
def list_email_templates() -> dict[str, Any]:
    """List available email templates with schemas and examples"""
```

#### Template Registry Structure
```python
TEMPLATE_REGISTRY = {
    "practice_report": {
        "class": PracticeReportTemplate,
        "description": "Professional practice performance report",
        "required_fields": ["location", "financial_data", "provider_data"],
        "optional_fields": ["period", "alerts", "recommendations"],
        "example_data": {...}
    },
    # ... other templates
}
```

### Testing Requirements
- [ ] **Unit Tests** - Framework: pytest, Coverage: 90%, Location: `tests/email_framework/test_consolidated_api.py`
- [ ] **Integration Tests** - Framework: pytest, Location: `tests/email_framework/test_template_integration.py`
- [ ] **Backward Compatibility Tests** - Framework: pytest, Location: `tests/email_framework/test_backward_compatibility.py`

### Dependencies
- **Files to Modify:**
  - `src/microsoft_mcp/tools.py` - Enhanced email functions
  - `src/microsoft_mcp/email_framework/templates/__init__.py` - Template registry
  - `src/microsoft_mcp/email_framework/template_registry.py` - New registry module
- **Related:** Email framework security audit (MSFT-487) provides XSS protection
- **Blockers:** None - can implement immediately

## Definition of Done
- [ ] All acceptance criteria met and validated
- [ ] Code reviewed and approved by senior developer
- [ ] Unit tests achieve 90% coverage for email consolidation logic
- [ ] Integration tests verify all template types work through generic API
- [ ] Backward compatibility tests ensure existing tools work unchanged
- [ ] API documentation updated with template examples
- [ ] Migration guide created for users of specialized tools
- [ ] Deployed to staging and production environments
- [ ] Manual verification of all template types completed
- [ ] Performance impact assessed (should be neutral/positive)

## Agent Context

### Reference Materials
- Email Framework Documentation: `src/microsoft_mcp/email_framework/`
- Template Base Class: `src/microsoft_mcp/email_framework/templates/base.py`
- Theme System: `src/microsoft_mcp/email_framework/css/themes.py`
- CSS Framework: `src/microsoft_mcp/email_framework/css/`
- Existing Templates: `src/microsoft_mcp/email_framework/templates/`

### Integration Points
- **Email Framework:** Must preserve all existing template rendering capabilities
- **Theme System:** Integrate automatic theme selection based on location
- **CSS Inlining:** Maintain email client compatibility through CSS processing
- **Signature System:** Preserve automatic signature appending
- **Validation Framework:** Leverage existing template data validation
- **Error Handling:** Provide clear, actionable error messages for template issues

### Template System Architecture
```
Generic Email Tools (send_email, create_email_draft)
    ↓ (when template_name provided)
Template Registry → Template Class → CSS Framework → HTML Output
    ↓                    ↓              ↓
Validation          Rendering      Inlining/Minification
```

## Validation Steps

### Automated Verification
- [ ] Build pipeline passes with new consolidated API
- [ ] Unit tests achieve 90%+ coverage for email consolidation
- [ ] Integration tests verify all 4 template types work through generic API
- [ ] Backward compatibility tests confirm existing tools unchanged
- [ ] Code quality checks pass (linting, type checking)
- [ ] Security scans clean (no new vulnerabilities)

### Manual Verification
1. **Template Discovery:** Run `list_email_templates()` and verify all templates listed with correct schemas
2. **Template Rendering:** Send emails using each template type through `send_email()` with `template_name` parameter
3. **Theme Selection:** Verify `location="baytown"` applies baytown theme, `location="humble"` applies humble theme
4. **Backward Compatibility:** Test existing `send_practice_report()` still works and shows deprecation warning
5. **Error Handling:** Test invalid template data and verify helpful error messages
6. **Fallback Behavior:** Test template failures gracefully fall back to simple HTML mode
7. **Performance:** Verify template rendering performance is equivalent to existing tools
8. **Email Client Compatibility:** Test rendered emails in major email clients (Outlook, Gmail, Apple Mail)

## Agent Execution Record

### Branch Strategy
- **Name Format:** feature/MSFT-501-email-template-consolidation
- **Linear Example:** feature/MSFT-501-consolidate-email-templates

### PR Strategy  
Link to this issue using magic words in PR description: "Fixes MSFT-501"

### Implementation Approach

**Phase 1: Core Infrastructure**
1. Create template registry system in `email_framework/template_registry.py`
2. Add template support parameters to `send_email()` and `create_email_draft()`
3. Implement template name → template class resolution logic
4. Add template data validation and error handling

**Phase 2: Template Integration**
1. Integrate existing template classes into registry
2. Add theme auto-selection based on location parameter
3. Implement template discovery tool `list_email_templates()`
4. Add comprehensive error messages for template failures

**Phase 3: Backward Compatibility**
1. Add deprecation warnings to existing template tools
2. Ensure existing tools continue working unchanged
3. Create migration documentation and examples
4. Add backward compatibility test suite

**Phase 4: Validation & Documentation**
1. Comprehensive testing of all template types through generic API
2. Performance testing and optimization
3. Documentation updates with template usage examples
4. Migration guide for existing users

### Success Metrics
- **API Simplification:** Reduce email-related tools from 6 to 3 (50% reduction)
- **Template Usage:** Increase template usage by 40% through better discoverability
- **Developer Experience:** Reduce email API learning time by 30% 
- **Maintenance Efficiency:** Reduce email tool maintenance overhead by 60%
- **Backward Compatibility:** 100% of existing template tool functionality preserved

### PR Integration
- **Linear Magic Words:** Fixes MSFT-501
- **Auto Close Trigger:** PR merge to main branch
- **Status Automation:** Issue will auto-move from 'In Progress' to 'Done'

## Bot Automation Integration

### Branch Naming for Auto-Linking
- feature/MSFT-501-email-template-consolidation

### PR Description Template
```markdown
## Description
Consolidates the 4 specialized email template tools into the generic email API while preserving all template functionality and maintaining backward compatibility.

**Key Changes:**
- Enhanced `send_email()` and `create_email_draft()` with template support
- Added `list_email_templates()` for template discovery
- Created template registry system for dynamic template resolution
- Maintained 100% backward compatibility with deprecation warnings
- Added comprehensive error handling and validation

**Linked Issues:**
- Fixes MSFT-501

## Testing
- [ ] Unit tests pass (90%+ coverage)
- [ ] Integration tests verify all template types
- [ ] Backward compatibility tests confirm existing tools work
- [ ] Manual verification in multiple email clients completed
```