# Story 1.5: Add File & Contact Actions to Complete Core Operations

## User Story

As a **Microsoft MCP developer**,  
I want **to add file and contact actions to the `microsoft_operations` tool**,  
So that **all core Microsoft 365 operations are consolidated into a single unified tool**.

## Story Context

**Core Operations Completion Phase:**
- **From:** Email (10) + Calendar (6) = 16 actions in `microsoft_operations` tool
- **To:** Email + Calendar + File (6) + Contact (5) = 27 core actions in unified tool  
- **Target Timeline:** 2 hours (TODAY completion)
- **Integration:** Final extension of proven action routing architecture
- **Foundation:** Complete core operations before implementing utility tools

**Touch Points:**
- `src/microsoft_mcp/tools.py` - Complete `microsoft_operations` tool with all core actions
- `src/microsoft_mcp/graph.py` - Existing Graph API client (unchanged)
- Story 1.1 validation framework - **EXTEND TO FILE/CONTACT PARAMS**
- Story 1.2-1.4 action router - **COMPLETE CORE ACTION COVERAGE**

## Acceptance Criteria

**File Action Implementation (TODAY):**
1. Add 6 file actions to `microsoft_operations` tool: `file.list`, `file.get`, `file.upload`, `file.download`, `file.share`, `file.delete`
2. Create file parameter validation models with path, size, and permission validation
3. Implement file action handlers with proper error handling for large files
4. Support file operations across OneDrive personal and business accounts

**Contact Action Implementation (TODAY):**
5. Add 5 contact actions to `microsoft_operations` tool: `contact.list`, `contact.get`, `contact.create`, `contact.update`, `contact.delete`
6. Create contact parameter validation models with email and phone validation
7. Implement contact action handlers with proper field validation
8. Support contact operations with comprehensive address book integration

**Parameter Structure (File Actions):**
9. List: `account_id`, `action: "file.list"`, `data: {folder_path, search_query, limit}`
10. Get: `account_id`, `action: "file.get"`, `data: {file_path, include_metadata}`
11. Upload: `account_id`, `action: "file.upload"`, `data: {local_path, onedrive_path, overwrite}`
12. Download: `account_id`, `action: "file.download"`, `data: {file_path, save_path}`
13. Share: `account_id`, `action: "file.share"`, `data: {file_path, email, permission, expiration_days}`
14. Delete: `account_id`, `action: "file.delete"`, `data: {file_path, permanent}`

**Parameter Structure (Contact Actions):**
15. List: `account_id`, `action: "contact.list"`, `data: {search_query, limit}`
16. Get: `account_id`, `action: "contact.get"`, `data: {contact_id}`
17. Create: `account_id`, `action: "contact.create"`, `data: {first_name, last_name, email, mobile_phone, company, job_title}`
18. Update: `account_id`, `action: "contact.update"`, `data: {contact_id, first_name, last_name, email, mobile_phone, company, job_title}`
19. Delete: `account_id`, `action: "contact.delete"`, `data: {contact_id}`

**Quality & Integration:**
20. Zero regression in existing 16 email and calendar actions
21. All 11 new actions work seamlessly through unified tool
22. Parameter validation comprehensive for file paths, sizes, and contact data
23. Performance maintained: file operations handle large files efficiently

**Test Migration Strategy:**
24. Move related legacy file and contact tests to `tests/legacy/` subdirectory
25. Create consolidated tests in `test_microsoft_operations.py` for file/contact actions
26. Mark old tests with `@pytest.mark.legacy` to exclude from CI
27. Replace 18 file/contact tests with 2 comprehensive action tests (files + contacts)
28. Focus on testing unified parameter validation and action routing patterns

## Technical Notes

**File Action Considerations:**
- Path validation for OneDrive file operations (Windows/Unix compatibility)
- File size limits and chunked upload for large files
- Permission validation for share operations (view/edit permissions)
- Error handling for file not found, access denied, storage quota exceeded
- Support for both personal and business OneDrive accounts

**Contact Action Considerations:**
- Email validation reusing patterns from Story 1.1's email parameter validation
- Phone number format validation for international numbers
- Optional field handling (not all contact fields are required)
- Duplicate contact detection and handling
- Contact group operations (future extension point)

**Parameter Validation Extensions:**
- Create `FileParams` and `ContactParams` base classes following established patterns
- Implement path validation for file operations (security and format checks)
- Add contact field validation (name, email, phone number formats)
- Maintain consistent error formatting across all 4 operation types

## Implementation Scope

**Core Components (2-Hour Focus):**
1. Create file and contact parameter models in validation framework
2. Extend `microsoft_operations` action router with file and contact handlers
3. Implement 11 new actions (6 file + 5 contact) with Graph API integration
4. Add comprehensive parameter validation for file and contact operations

**Files to Create/Modify:**
- `src/microsoft_mcp/file_params.py` - File parameter models (NEW FILE)
- `src/microsoft_mcp/contact_params.py` - Contact parameter models (NEW FILE)
- `src/microsoft_mcp/tools.py` - Complete microsoft_operations tool (primary change)
- `src/microsoft_mcp/validation.py` - Extend error formatting for all action types
- `tests/test_microsoft_operations.py` - Add consolidated file/contact action tests
- `tests/legacy/` - Move existing file/contact tests here for migration tracking

**File Actions to Implement:**
- `file.list` - List files and folders with search and filtering
- `file.get` - Retrieve file metadata and content information
- `file.upload` - Upload local files to OneDrive with path management
- `file.download` - Download OneDrive files to local storage
- `file.share` - Create sharing links with permission and expiration control
- `file.delete` - Delete files and folders with optional permanent deletion

**Contact Actions to Implement:**
- `contact.list` - List contacts with search and pagination
- `contact.get` - Retrieve detailed contact information
- `contact.create` - Create new contact with validation
- `contact.update` - Update existing contact fields
- `contact.delete` - Delete contact from address book

## Definition of Done

**Implementation Complete:**
- [ ] All 6 file actions implemented in `microsoft_operations` tool
- [ ] All 5 contact actions implemented in `microsoft_operations` tool
- [ ] File and contact parameter validation models created
- [ ] Action router handles all 27 core actions (email + calendar + file + contact)

**Quality Assurance:**
- [ ] Zero regression in existing 16 email and calendar actions
- [ ] All 11 new actions thoroughly tested with representative operations
- [ ] File operations handle large files and path validation correctly
- [ ] Contact operations validate email and phone number formats properly
- [ ] Performance benchmarks met for all operation types

**Documentation & Testing:**
- [ ] File and contact parameter models documented with field descriptions
- [ ] Action parameter documentation complete for all 27 actions
- [ ] Legacy file/contact tests moved to `tests/legacy/` with `@pytest.mark.legacy`
- [ ] Consolidated file and contact action tests created in unified test suite
- [ ] Complete migration examples with all core operation types

## Success Metrics

**Immediate Success (TODAY):**
1. `microsoft_operations` tool handles all 27 core actions across 4 service types
2. File operations work correctly with OneDrive personal and business accounts
3. Contact operations integrate seamlessly with Microsoft address book
4. Action routing architecture scales to handle diverse operation complexity
5. Parameter validation framework proven across all Microsoft 365 core services

**Strategic Success:**
- Core Microsoft 365 operations fully consolidated (27/27 target actions)
- Single unified tool replaces majority of existing 61 individual tools
- Action routing architecture validated for production use at scale
- Foundation complete for utility tools and final consolidation phase

## Dependencies

**Required for Start:**
- [x] Story 1.1: Parameter validation framework (DONE)
- [x] Story 1.2: microsoft_operations tool with email actions (DONE)
- [x] Story 1.3: Complete email actions (DONE)
- [x] Story 1.4: Add calendar actions (DONE - prerequisite)

**Enables:**
- Story 1.6: Implement utility tools to reach 15 total tools
- Story 1.7: Migration and deprecation layer
- Story 1.8: Final cleanup and launch

## Risk Assessment

**Primary Risk:** File upload/download complexity within 2-hour timeline**  
**Mitigation:** Focus on basic file operations first, leverage existing Graph API patterns  
**Fallback:** Implement list, get, delete first; upload/download if time permits

**Technical Risk:** OneDrive path handling across personal/business accounts  
**Mitigation:** Use existing OneDrive tool implementations as reference  
**Validation:** Test with both personal and business Microsoft accounts

**Integration Risk:** 27 actions in single tool may impact performance  
**Mitigation:** Maintain lightweight action routing, delegate heavy work to Graph API  
**Monitoring:** Track action routing overhead throughout implementation

## Next Steps

**After Story 1.5 Complete:**
- **Story 1.6**: "Implement Utility Tools to Reach 15 Total Tools"
- **Story 1.7**: "Migration and Deprecation Layer"  
- **Story 1.8**: "Final Cleanup and Launch"

## Communication Points

**Strategic Updates:**
1. **CORE OPERATIONS COMPLETE**: All 27 Microsoft 365 core actions unified
2. **SINGLE TOOL MILESTONE**: One tool now handles majority of user operations
3. **ARCHITECTURE PROVEN**: Action routing scales to 4 service types seamlessly
4. **VALIDATION COMPREHENSIVE**: Parameter framework handles all operation complexity

**Implementation Notes:**
- Complete action router with file and contact handlers
- Create parameter models following proven validation patterns
- Maintain performance and error handling consistency across all actions
- Preserve backward compatibility with all existing individual tools

## Notes

This story completes the core operation consolidation by adding file and contact actions to the `microsoft_operations` tool. With 27 actions covering email, calendar, file, and contact operations, this single tool will handle the vast majority of user interactions with Microsoft 365 services. The completion validates the action routing architecture at scale and establishes the foundation for implementing the remaining utility tools to reach the target of 15 total tools.