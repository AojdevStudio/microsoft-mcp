# Story 1.7: Nuclear Migration - LEGACY STORY (COMPLETED)

## User Story

**⚠️ NUCLEAR OVERRIDE**: This story was superseded by nuclear simplification approach.
Migration frameworks were **DELETED** as part of nuclear strategy - no compatibility layers.

**Nuclear Implementation Status**: ✅ COMPLETE
- Migration frameworks deleted (no backward compatibility)
- 5 focused tools implemented with action-based routing
- Git revert strategy provides rollback capability
- 92% token reduction achieved

## Legacy Story Context (ARCHIVED)

**Original Migration Phase - SUPERSEDED BY NUCLEAR:**
- **Original Plan:** 61 original tools + 15 new unified tools (76 total) + 184+ tests
- **Nuclear Reality:** 5 focused tools with zero compatibility layers
- **Nuclear Timeline:** 6 hours total (delete → build → deploy)
- **Nuclear Strategy:** Delete migration frameworks, implement clean architecture
- **Nuclear Result:** 92% complexity reduction, zero maintenance overhead

**Current Architecture State:**
- ✅ 15 unified tools implemented (Stories 1.1-1.6)
- ✅ `microsoft_operations` handles 27 core actions
- ✅ 11 utility tools provide comprehensive support
- ✅ Legacy tests moved to `tests/legacy/` from Stories 1.3-1.6
- 🔄 46 legacy tools still active (need deprecation layer)
- 🔄 184+ legacy tests need consolidation into ~30 migration tests

**Touch Points:**
- `src/microsoft_mcp/tools.py` - Add deprecation wrapper functions
- `src/microsoft_mcp/migration.py` - NEW FILE: Migration utilities
- `src/microsoft_mcp/legacy_mapper.py` - NEW FILE: Legacy tool routing
- `tests/legacy/` - All legacy tests archived and marked (from Stories 1.3-1.6)
- `tests/test_migration_validation.py` - NEW FILE: ~30 consolidated tests
- `pytest.ini` - Configure to skip legacy tests in CI

## Acceptance Criteria

**Deprecation Layer Implementation (TODAY):**
1. Create deprecation wrapper functions for all 46 legacy tools in `tools.py`
2. Implement automatic routing from legacy tools to appropriate unified tools
3. Add clear deprecation warnings with migration guidance for each legacy tool
4. Create migration utility functions to map legacy parameters to unified tool parameters

**Test Consolidation (PRIMARY FOCUS):**
5. Consolidate 184+ legacy tests into ~30 migration tests in `test_migration_validation.py`
6. Stop running legacy tests in CI by configuring pytest to skip `@pytest.mark.legacy`
7. Create comprehensive migration tests that verify equivalence without duplicating logic
8. Focus on testing parameter mapping, routing logic, and backward compatibility
9. Ensure consolidated tests provide sufficient coverage without maintaining legacy test complexity

**Parameter Mapping & Validation:**
10. Map legacy tool parameters to `microsoft_operations` action-based parameters
11. Handle parameter transformation for complex cases (email templates, bulk operations)
12. Preserve all existing functionality through the deprecation layer
13. Validate legacy parameters and provide upgrade guidance for invalid usage

**User Experience:**
14. Legacy tools continue to work exactly as before (zero breaking changes)
15. Clear deprecation messages provide specific migration examples for each tool
16. Migration warnings include timeline information (30-day notice period)
17. Help system provides legacy-to-unified mapping documentation

**Quality & Performance:**
18. Deprecation layer adds <50ms overhead per legacy tool call
19. Migration tests validate backward compatibility without maintaining 184+ test files
20. Migration mapper handles all legacy parameter patterns correctly
21. Error messages for legacy tools include both legacy and unified formats

## Technical Notes

**Deprecation Architecture:**
- Legacy tools become wrapper functions that route to unified tools
- Parameter transformation handles differences between legacy and unified APIs
- Deprecation warnings logged but don't break existing workflows
- Migration mapper provides automatic parameter translation

**Legacy Tool Categories:**

**Email Tools (25 tools) → `microsoft_operations` with email actions:**
- `send_email` → `microsoft_operations(action="email.send")`
- `list_emails` → `microsoft_operations(action="email.list")`
- `send_practice_report` → `microsoft_operations(action="email.send", template="practice_report")`
- `send_executive_summary` → `microsoft_operations(action="email.send", template="executive_summary")`
- Plus 21 other email operations

**Calendar Tools (8 tools) → `microsoft_operations` with calendar actions:**
- `list_calendar_events` → `microsoft_operations(action="calendar.list")`
- `create_calendar_event` → `microsoft_operations(action="calendar.create")`
- Plus 6 other calendar operations

**File Tools (7 tools) → `microsoft_operations` with file actions:**
- `list_files` → `microsoft_operations(action="file.list")`
- `upload_file` → `microsoft_operations(action="file.upload")`
- Plus 5 other file operations

**Contact Tools (6 tools) → `microsoft_operations` with contact actions:**
- `list_contacts` → `microsoft_operations(action="contact.list")`
- `create_contact` → `microsoft_operations(action="contact.create")`
- Plus 4 other contact operations

## Implementation Scope

**Core Components (2-Hour Focus):**
1. Create deprecation wrapper functions for all 46 legacy tools
2. Implement parameter mapping from legacy format to unified format
3. Add deprecation warnings with specific migration guidance
4. Create migration utilities for complex parameter transformations

**Files to Create/Modify:**
- `src/microsoft_mcp/tools.py` - Add deprecation wrappers (primary change)
- `src/microsoft_mcp/migration.py` - NEW FILE: Migration utilities and parameter mappers
- `src/microsoft_mcp/legacy_mapper.py` - NEW FILE: Legacy-to-unified routing logic
- `src/microsoft_mcp/deprecation.py` - NEW FILE: Deprecation warning system
- `tests/test_migration_validation.py` - NEW FILE: ~30 consolidated migration tests
- `pytest.ini` - Configure to skip `@pytest.mark.legacy` tests in CI
- `tests/legacy/` - Contains all archived legacy tests (already moved in Stories 1.3-1.6)

**Legacy Tool Migration Strategy:**

**Simple 1:1 Mapping:**
```python
@deprecated_tool("Use microsoft_operations with action='email.list'")
def list_emails(account_id: str, folder: str = "inbox", limit: int = 10):
    return microsoft_operations(
        account_id=account_id,
        action="email.list",
        data={"folder": folder, "limit": limit}
    )
```

**Complex Template Mapping:**
```python
@deprecated_tool("Use microsoft_operations with template parameter")
def send_practice_report(account_id: str, to: str, data: dict):
    return microsoft_operations(
        account_id=account_id,
        action="email.send",
        template="practice_report",
        data={"to": to, **data}
    )
```

## Definition of Done

**Migration Layer Complete:**
- [ ] All 46 legacy tools have deprecation wrapper functions
- [ ] Parameter mapping correctly transforms legacy calls to unified format
- [ ] Deprecation warnings provide clear migration guidance with examples
- [ ] Legacy tools continue to work without breaking changes

**Test Consolidation Complete:**
- [ ] 184+ legacy tests consolidated into ~30 migration tests
- [ ] Legacy tests marked with `@pytest.mark.legacy` and excluded from CI
- [ ] Migration tests verify equivalence without duplicating individual test logic
- [ ] CI runs only ~30 migration tests instead of 184+ legacy tests
- [ ] Test maintenance burden reduced by 85%

**Quality Assurance:**
- [ ] Migration tests provide sufficient coverage for backward compatibility validation
- [ ] Performance overhead from deprecation layer < 50ms per call
- [ ] Migration mapper handles all parameter transformation edge cases
- [ ] Deprecation warnings are informative but non-blocking

**Documentation & User Support:**
- [ ] Migration guide documents legacy-to-unified mapping for all 46 tools
- [ ] Help system provides specific migration examples for each legacy tool
- [ ] Deprecation timeline communicated clearly (30-day transition period)
- [ ] Error messages include both legacy and unified usage examples

## Success Metrics

**Immediate Success (TODAY):**
1. All 46 legacy tools continue to work exactly as before
2. Clear deprecation warnings guide users toward unified tools
3. Parameter mapping handles 100% of legacy usage patterns
4. Zero breaking changes during implementation
5. 184+ legacy tests consolidated into ~30 migration tests
6. CI test execution time dramatically reduced (85% fewer tests)
7. Test maintenance burden eliminated for legacy functionality

**Strategic Success:**
- Smooth transition path established for all existing users
- Deprecation layer enables phased migration over 30-day period
- Legacy tool complexity fully abstracted through unified tools
- Test maintenance burden reduced by 85% (184+ → ~30 tests)
- Foundation set for final cleanup phase (Story 1.8)

## Dependencies

**Required for Start:**
- [x] Story 1.1: Parameter validation framework (DONE)
- [x] Story 1.2-1.5: `microsoft_operations` tool with all 27 actions (DONE)
- [x] Story 1.6: All 15 unified tools implemented (DONE - prerequisite)

**Enables:**
- Story 1.8: Final cleanup and launch (removal of legacy tools)

## Risk Assessment

**Primary Risk:** Parameter mapping complexity may cause subtle bugs  
**Mitigation:** Comprehensive testing with existing legacy tool test suites  
**Validation:** Run full test suite before and after deprecation layer implementation

**User Experience Risk:** Deprecation warnings may cause confusion  
**Mitigation:** Clear, actionable migration guidance with specific examples  
**Support:** Provide migration assistance through help system

**Performance Risk:** Deprecation layer overhead may impact response times  
**Mitigation:** Optimize parameter mapping, cache transformation logic  
**Benchmark:** Measure performance impact and optimize critical paths

## Migration Timeline Communication

**Phase 1 (Today):** Deprecation layer active, warnings begin
**Phase 2 (Week 1):** Migration guidance and support active
**Phase 3 (Week 2-3):** Encourage active migration, provide assistance
**Phase 4 (Week 4):** Final migration reminders
**Phase 5 (Story 1.8):** Legacy tools removed, unified tools only

## Next Steps

**After Story 1.7 Complete:**
- **Story 1.8**: "Final Cleanup and Launch" - Remove legacy tools and complete consolidation

## Communication Points

**Strategic Updates:**
1. **MIGRATION READY**: All 46 legacy tools have deprecation wrappers
2. **ZERO BREAKAGE**: Complete backward compatibility during transition
3. **CLEAR GUIDANCE**: Every legacy tool has specific migration examples
4. **30-DAY TIMELINE**: Structured transition period for all users

**Implementation Notes:**
- Focus on preserving exact legacy behavior through unified tools
- Provide clear, actionable migration guidance in every deprecation warning
- Handle complex parameter transformations through dedicated mapping functions
- Maintain performance while adding deprecation layer functionality

## Notes

This story implements the critical migration and deprecation layer that enables a smooth transition from 61 tools to 15 tools without breaking existing integrations. By providing wrapper functions with clear deprecation warnings and automatic parameter mapping, users can continue using familiar tools while being guided toward the new unified architecture. This approach ensures zero breaking changes while establishing a clear path for final consolidation in Story 1.8.