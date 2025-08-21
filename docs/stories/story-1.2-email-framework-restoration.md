# Story 1.2: Implement Microsoft Operations Unified Tool

## User Story

As a **Microsoft MCP developer**,  
I want **to implement the unified `microsoft_operations` tool with action-based parameters**,  
So that **we can begin consolidating from 61 tools to 15 tools while preserving all functionality**.

## Story Context

**Strategic Pivot - Ultra-Consolidation:**
- **From:** 61 individual MCP tools causing discovery paralysis
- **To:** 15 unified tools with action-based parameters
- **Target Timeline:** TODAY (immediate implementation)
- **Integration:** Utilizes Story 1.1's parameter validation framework
- **Approach:** Start with email actions, expand systematically
- **Styling:** Email templates as utility functions, not separate tools

**Touch Points:**
- `src/microsoft_mcp/tools.py` - Add `microsoft_operations` tool definition
- `src/microsoft_mcp/email_framework/utils.py` - Email styling utilities
- `src/microsoft_mcp/graph.py` - Existing Graph API client (unchanged)
- Story 1.1 validation framework - **FULLY UTILIZED**

## Acceptance Criteria

**Core Implementation (TODAY):**
1. Create `microsoft_operations` tool in `tools.py` with action-based routing
2. Implement email actions: `email.list`, `email.send`, `email.reply`, `email.draft`, `email.delete`
3. Integrate Story 1.1's parameter validation framework for all operations
4. Create email styling utilities in `src/microsoft_mcp/email_framework/utils.py`

**Parameter Structure:**
5. Tool accepts: `account_id` (required), `action` (required), `data` (dict), `template` (optional), `options` (optional)
6. Action routing validates parameters specific to each action type
7. Template parameter triggers professional email styling via utilities
8. Options parameter handles pagination, filtering, and additional flags

**Integration Requirements:**
9. All existing email tools remain functional (backward compatibility)
10. New tool follows existing authentication and error handling patterns
11. Email styling preserves KamDental branding (Baytown blue, Humble green, Executive themes)
12. Multi-account support via `account_id` parameter maintained

**Quality Requirements:**
13. Zero regression in existing functionality during implementation
14. Email actions thoroughly tested with existing Graph API patterns
15. Performance: Action routing < 100ms, email operations maintain current speed
16. Clear migration path documented for future tool consolidation

## Technical Notes

**Action-Based Architecture:**
- Single `microsoft_operations` tool routes to specific Graph API operations
- Action parameter (e.g., "email.send") determines operation type and validation rules
- Data parameter contains action-specific inputs (to, subject, body for email.send)
- Template parameter triggers professional styling via utility functions
- Options parameter provides common functionality (pagination, filters, flags)

**Email Styling Integration:**
- Utilities in `email_framework/utils.py` handle HTML generation and CSS inlining
- Professional themes (Baytown, Humble, Executive) applied via template parameter
- CSS-to-inline conversion for email client compatibility maintained
- KamDental signature and branding preserved through utility functions

**Key Design Principles:**
- Leverage Story 1.1's parameter validation for consistent error handling
- Maintain existing Graph API authentication and error patterns
- Preserve backward compatibility - existing tools work unchanged
- Action routing enables future expansion to calendar, file, contact operations

## Implementation Scope

**Core Components (TODAY's Focus):**
1. `microsoft_operations` tool definition in `tools.py`
2. Action router function with parameter validation integration
3. Email action handlers: list, send, reply, draft, delete
4. Email styling utilities in `utils.py`

**Files to Create/Modify:**
- `src/microsoft_mcp/tools.py` - Add microsoft_operations tool (primary change)
- `src/microsoft_mcp/email_framework/utils.py` - Create utility functions (NEW FILE)
- `src/microsoft_mcp/email_framework/css_inliner.py` - Enhance for utilities
- `src/microsoft_mcp/email_framework/renderer.py` - Refactor for utilities

**Email Actions to Implement:**
- `email.list` - List emails with filtering options
- `email.send` - Send email with optional template styling
- `email.reply` - Reply to email with styling support  
- `email.draft` - Create draft with template support
- `email.delete` - Delete email operations

## Definition of Done

**Implementation Complete:**
- [x] `microsoft_operations` tool added to `tools.py` with full action routing
- [x] Email actions (list, send, reply, draft, delete) implemented and tested
- [x] Story 1.1 parameter validation integrated for all operations
- [x] Email styling utilities created in `email_framework/utils.py`

**Quality Assurance:**
- [x] Zero regression in existing 163+ tests
- [x] New tool thoroughly tested with representative email operations
- [x] Performance benchmarks met (action routing < 100ms)
- [x] Backward compatibility verified - existing email tools unchanged

**Documentation & Migration Readiness:**
- [x] CLAUDE.md updated with unified tool documentation
- [x] Clear migration examples for future consolidation work
- [x] Action parameter documentation complete
- [x] Email styling utility usage documented

## Risk and Compatibility Check

**Primary Risk:** Adding complexity while trying to simplify the API surface  
**Mitigation:** Start with email actions only, maintain existing tool functionality unchanged  
**Rollback:** Remove `microsoft_operations` tool, all existing functionality remains intact

**Strategic Risk:** Today's timeline may be too aggressive  
**Mitigation:** Focus on core email actions first, expand systematically  
**Fallback:** Deliver working foundation today, complete remaining actions in follow-up

**Compatibility Verification:**
- [x] No breaking changes to existing APIs (new tool is additive)
- [x] Existing authentication patterns preserved
- [x] Current Graph API integration unchanged
- [x] Email styling functionality enhanced, not replaced

## Validation Checklist

**Strategic Alignment:**
- [x] Supports 61 → 15 tool consolidation goal
- [x] Utilizes Story 1.1's parameter validation framework
- [x] Email styling preserved as utilities, not tools
- [x] Enables future calendar, file, contact action expansion

**Implementation Readiness:**
- [x] Clear scope limited to email actions
- [x] Existing patterns and infrastructure leveraged
- [x] Integration points clearly specified
- [x] Success criteria measurable and testable

## Success Metrics

**Immediate Success (TODAY):**
1. `microsoft_operations` tool successfully handles all 5 email actions
2. Action routing with parameter validation works flawlessly
3. Email styling utilities produce professional HTML output
4. Zero regression in existing functionality during implementation
5. Clear migration path established for future tool consolidation

**Strategic Success (Long-term):**
- Foundation laid for 61 → 15 tool consolidation
- Story 1.1's validation framework proven in production use
- Email styling capabilities preserved and enhanced
- Development team aligned on unified tool approach

## Next Steps - Revised Strategy

**After Story 1.2 Complete:**
- **Story 1.3**: "Implement Calendar Actions in microsoft_operations tool"
- **Story 1.4**: "Implement File & Contact Actions, Complete Unified Tool"
- **Story 1.5**: "Create Migration Layer and Deprecate Old Tools"
- **Story 1.6**: "Complete Ultra-Consolidation to 15 Tools"

## Communication Points for Development Team

**Critical Strategic Updates:**
1. **PIVOT COMPLETE**: We're no longer building 61 individual tools
2. **NEW TARGET**: 15 unified tools with action-based parameters
3. **TIMELINE**: TODAY implementation, not 6-week project
4. **FOUNDATION**: Story 1.1's validation work is our cornerstone
5. **STYLING**: Professional email templates are utilities, not separate tools

**Implementation Priorities:**
- Start with email actions today
- Leverage existing Graph API patterns
- Maintain backward compatibility throughout
- Use Story 1.1's validation for all parameters
- Document migration path for future work

## Notes

This story represents the strategic pivot to ultra-consolidation. By implementing the `microsoft_operations` tool with email actions first, we establish the foundation for transforming 61 tools into 15 unified tools. The approach preserves all functionality while dramatically simplifying the API surface. Story 1.1's parameter validation framework becomes the cornerstone of this new architecture, proving its value immediately in production use.