# Story 1.6: Implement Utility Tools to Reach 15 Total

## User Story

As a **Microsoft MCP developer**,  
I want **to implement the remaining 11 utility tools to reach the target of 15 total tools**,  
So that **the ultra-consolidation from 61 tools to 15 tools is complete**.

## Story Context

**Final Tool Implementation Phase:**
- **From:** 4 tools implemented (microsoft_operations + authenticate_account + list_accounts + complete_authentication)
- **To:** 15 total tools as specified in UNIFIED PRD
- **Target Timeline:** 2 hours (TODAY completion)
- **Architecture:** Complete the 15-tool target from UNIFIED PRD
- **Foundation:** `microsoft_operations` tool handles all 27 core actions

**Current Tool Status:**
1. ✅ `microsoft_operations` - 27 core actions (Stories 1.2-1.5)
2. ✅ `authenticate_account` - Already exists in tools.py
3. ✅ `list_accounts` - Already exists in tools.py  
4. ✅ `complete_authentication` - Already exists in tools.py

**Tools to Implement (11 remaining):**
5. `get_user_info` - User profile information
6. `get_mailbox_statistics` - Usage statistics
7. `unified_search` - Search across all services
8. `list_resources` - Available resources/templates
9. `export_data` - Bulk export operations
10. `import_data` - Bulk import operations
11. `get_settings` - Configuration settings
12. `update_settings` - Update configuration
13. `validate_data` - Data validation before operations
14. `get_system_status` - Health check and status
15. `get_help` - Context-aware help and examples

## Acceptance Criteria

**User & Profile Tools (2 tools):**
1. Implement `get_user_info` tool: retrieve user profile, settings, and account details
2. Implement `get_mailbox_statistics` tool: storage usage, message counts, folder sizes

**Search & Discovery Tools (2 tools):**
3. Implement `unified_search` tool: search across emails, files, events, contacts with filtering
4. Implement `list_resources` tool: list available templates, settings, and system resources

**Data Management Tools (2 tools):**
5. Implement `export_data` tool: bulk export of emails, contacts, calendar events to standard formats
6. Implement `import_data` tool: bulk import from CSV, JSON, or other standard formats

**Configuration Tools (2 tools):**
7. Implement `get_settings` tool: retrieve MCP server and user configuration settings
8. Implement `update_settings` tool: update configuration with validation

**System Tools (3 tools):**
9. Implement `validate_data` tool: validate data before operations using Story 1.1's framework
10. Implement `get_system_status` tool: health check, connection status, service availability
11. Implement `get_help` tool: context-aware help, examples, and usage guidance

**Quality Requirements:**
12. All 11 tools follow consistent parameter patterns (account_id where applicable)
13. Error handling and response formats consistent with existing tools
14. Performance: each utility tool responds in <500ms
15. Integration with existing authentication and Graph API patterns

**Test Migration Strategy:**
16. Move related legacy utility tests to `tests/legacy/` subdirectory
17. Create consolidated tests in new utility-focused test files
18. Mark old tests with `@pytest.mark.legacy` to exclude from CI
19. Create 8 utility tests, replacing dozens of scattered legacy tests
20. Focus on testing utility functionality, not reimplementing individual tool tests

## Technical Notes

**Tool Implementation Strategy:**
- Leverage existing Graph API patterns from current tools
- Reuse authentication and error handling from existing codebase
- Focus on utility functions that complement `microsoft_operations` core actions
- Maintain consistent parameter and response patterns

**Key Implementation Details:**

**Search & Discovery:**
- `unified_search` aggregates results from Graph API's unified search endpoint
- `list_resources` provides metadata about available operations and templates
- Both tools provide discovery capabilities for the consolidated API

**Data Management:**
- `export_data` leverages existing list operations with bulk processing
- `import_data` uses `microsoft_operations` actions for bulk creation
- Support standard formats (CSV, JSON) for interoperability

**Configuration & System:**
- `get_settings`/`update_settings` manage MCP server configuration
- `validate_data` exposes Story 1.1's validation framework as standalone tool
- `get_system_status` provides health monitoring for the consolidated system
- `get_help` provides contextual guidance for the new 15-tool architecture

## Implementation Scope

**Core Components (2-Hour Focus):**
1. Implement 11 utility tools in `tools.py` following existing patterns
2. Create parameter validation for tools that require complex inputs
3. Integrate with existing Graph API client and authentication system
4. Maintain consistent error handling and response formatting

**Files to Modify:**
- `src/microsoft_mcp/tools.py` - Add 11 utility tools (primary change)
- `src/microsoft_mcp/validation.py` - Extend for utility tool validation
- `tests/test_utility_tools.py` - Add consolidated utility tool tests (NEW FILE)
- `tests/legacy/` - Move scattered utility tests here for migration tracking

**Utility Tools by Category:**

**User & Profile (2 tools):**
- `get_user_info(account_id)` - User profile and account information
- `get_mailbox_statistics(account_id)` - Storage and usage statistics

**Search & Discovery (2 tools):**
- `unified_search(account_id, query, types, filters)` - Cross-service search
- `list_resources()` - Available templates, actions, and system resources

**Data Management (2 tools):**
- `export_data(account_id, data_type, format, filters)` - Bulk export operations
- `import_data(account_id, data_type, source, options)` - Bulk import operations

**Configuration (2 tools):**
- `get_settings(category)` - Retrieve configuration settings
- `update_settings(category, settings)` - Update configuration with validation

**System (3 tools):**
- `validate_data(data_type, data, schema)` - Validate data using framework
- `get_system_status()` - Health check and service status
- `get_help(topic, action)` - Context-aware help and examples

## Definition of Done

**Implementation Complete:**
- [ ] All 11 utility tools implemented following consistent patterns
- [ ] Parameter validation for complex tools (unified_search, export_data, import_data)
- [ ] Integration with existing authentication and Graph API systems
- [ ] Consistent error handling and response formats across all tools

**Quality Assurance:**
- [ ] All 15 tools working correctly (4 existing + 11 new)
- [ ] Performance benchmarks met (utility tools < 500ms response time)
- [ ] Zero regression in existing `microsoft_operations` tool functionality
- [ ] Authentication and multi-account support maintained

**Documentation & Architecture:**
- [ ] All 15 tools documented with clear parameter descriptions
- [ ] Help system provides guidance for new 15-tool architecture
- [ ] Resource listing provides complete API discovery
- [ ] System status provides operational visibility
- [ ] Legacy utility tests moved to `tests/legacy/` with proper categorization
- [ ] New consolidated utility test suite created with comprehensive coverage

## Success Metrics

**Immediate Success (TODAY):**
1. Exactly 15 tools implemented as specified in UNIFIED PRD
2. All utility tools complement `microsoft_operations` core functionality
3. System provides complete API discovery through `list_resources`
4. Help system guides users through consolidated architecture
5. 75% tool reduction achieved (61 → 15 tools)

**Strategic Success:**
- Ultra-consolidation target achieved (15 total tools)
- Complete utility ecosystem supports core operations
- System provides self-service discovery and help
- Foundation ready for migration and deprecation phase

## Dependencies

**Required for Start:**
- [x] Story 1.1: Parameter validation framework (DONE)
- [x] Story 1.2: microsoft_operations tool (DONE)
- [x] Story 1.3: Complete email actions (DONE)
- [x] Story 1.4: Add calendar actions (DONE)
- [x] Story 1.5: Add file & contact actions (DONE - prerequisite)

**Enables:**
- Story 1.7: Migration and deprecation layer
- Story 1.8: Final cleanup and launch

## Risk Assessment

**Primary Risk:** 11 tools in 2 hours may be too aggressive  
**Mitigation:** Focus on simpler utility tools first, implement complex ones (export/import) last  
**Fallback:** Deliver essential tools (help, status, settings) first, complete others if time permits

**Technical Risk:** Utility tools may require new Graph API patterns  
**Mitigation:** Start with tools that leverage existing patterns, research complex ones  
**Validation:** Test with existing authentication and error handling systems

**Scope Risk:** Some tools may require more complexity than anticipated  
**Mitigation:** Keep initial implementations simple, mark extension points for future enhancement  
**Quality Gate:** Ensure basic functionality works before adding advanced features

## Next Steps

**After Story 1.6 Complete:**
- **Story 1.7**: "Migration and Deprecation Layer" 
- **Story 1.8**: "Final Cleanup and Launch"

## Communication Points

**Strategic Updates:**
1. **TARGET ACHIEVED**: 15 tools implemented, 75% reduction from 61 tools
2. **UTILITY ECOSYSTEM**: Complete support system for core operations
3. **SELF-SERVICE**: Help and discovery tools guide users through new architecture
4. **FOUNDATION READY**: All tools implemented, ready for migration phase

**Implementation Notes:**
- Focus on utility functions that complement core operations
- Maintain consistency with existing authentication and error patterns
- Provide comprehensive help and discovery capabilities
- Keep implementations simple and extensible

## Notes

This story completes the tool implementation phase by adding the remaining 11 utility tools to reach the UNIFIED PRD's target of 15 total tools. These utilities provide essential support functions including search, data management, configuration, and help systems. The completion represents a 75% reduction from the original 61 tools while maintaining full functionality through the consolidated architecture. The next phase will focus on migration and deprecation of the old tool set.