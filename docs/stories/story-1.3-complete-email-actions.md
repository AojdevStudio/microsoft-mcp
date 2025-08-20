# Story 1.3: Complete Email Actions in Microsoft Operations Tool

## User Story

As a **Microsoft MCP developer**,  
I want **to complete all 10 email actions in the `microsoft_operations` tool**,  
So that **all email functionality is consolidated into the unified tool architecture**.

## Story Context

**Completing Email Consolidation:**
- **From:** Story 1.2's 5 email actions (list, send, reply, draft, delete)
- **To:** Complete set of 10 email actions in `microsoft_operations` tool
- **Target Timeline:** 2 hours (TODAY completion)
- **Integration:** Leverages existing parameter validation from Story 1.1
- **Foundation:** Builds on Story 1.2's action routing architecture

**Touch Points:**
- `src/microsoft_mcp/tools.py` - Extend `microsoft_operations` tool with 5 additional email actions
- `src/microsoft_mcp/email_framework/utils.py` - Enhance utilities for new actions
- `src/microsoft_mcp/graph.py` - Existing Graph API client (unchanged)
- Story 1.1 validation framework - **CONTINUE USAGE**
- Story 1.2 action router - **EXTEND FUNCTIONALITY**

## Acceptance Criteria

**Email Action Completion (TODAY):**
1. Add 5 remaining email actions to `microsoft_operations` tool: `email.forward`, `email.move`, `email.mark`, `email.search`, `email.get`
2. Integrate all actions with Story 1.1's parameter validation framework
3. Ensure email styling utilities support forward and reply-like operations
4. Maintain consistent action routing pattern from Story 1.2

**Parameter Structure Enhancement:**
5. Forward action: `account_id`, `action: "email.forward"`, `data: {email_id, to, comment}`
6. Move action: `account_id`, `action: "email.move"`, `data: {email_id, destination_folder}`
7. Mark action: `account_id`, `action: "email.mark"`, `data: {email_id, mark_as: read|unread|important}`
8. Search action: `account_id`, `action: "email.search"`, `data: {query, folder, limit}`
9. Get action: `account_id`, `action: "email.get"`, `data: {email_id, include_attachments}`

**Quality & Integration:**
10. Zero regression in existing 5 email actions from Story 1.2
11. All 10 email actions work seamlessly through unified `microsoft_operations` tool
12. Performance maintained: action routing + operation < 200ms total
13. Email styling utilities enhanced for forward operations with professional templates

**Backward Compatibility:**
14. All existing individual email tools remain functional (no breaking changes)
15. New actions follow identical authentication and error handling patterns
16. Multi-account support via `account_id` parameter maintained across all actions

**Test Migration Strategy:**
17. Move related legacy email tests to `tests/legacy/` subdirectory
18. Create consolidated tests in `test_microsoft_operations.py` for all 10 email actions
19. Mark old tests with `@pytest.mark.legacy` to exclude from CI
20. Consolidate 25+ email tests into 5 comprehensive action tests
21. Focus on testing action routing and parameter validation, not individual operations

## Technical Notes

**Action Implementation Strategy:**
- Extend Story 1.2's action router with 5 additional email action handlers
- Reuse existing Graph API patterns from current individual tools
- Apply Story 1.1's parameter validation for each new action type
- Maintain consistent response format across all 10 email actions

**Specific Graph API Methods (Microsoft Graph v1.0):**
- `email.forward`: POST `/me/messages/{message-id}/forward` - Forward message immediately
- `email.move`: POST `/me/messages/{message-id}/move` - Move message to folder
- `email.mark`: PATCH `/me/messages/{message-id}` - Update message properties (isRead, importance)
- `email.search`: GET `/me/messages?$search="{query}"` - Search messages with query
- `email.get`: GET `/me/messages/{message-id}` - Retrieve specific message with details

**Email Styling Integration:**
- Forward action integrates with professional email templates
- Maintain KamDental branding consistency across all styled operations
- Email utilities handle comment formatting for forward operations
- CSS inlining preserved for all template-based actions

**Performance Considerations:**
- Action routing overhead: <50ms (already achieved in Story 1.2)
- Email operations: maintain current speed (varies by Graph API)
- Search operations: leverage existing pagination patterns
- Get operations: preserve attachment handling efficiency

## Implementation Scope

**Core Components (2-Hour Focus):**
1. Extend `microsoft_operations` action router with 5 new email handlers
2. Implement forward, move, mark, search, get email actions
3. Integrate Story 1.1 parameter validation for all new actions
4. Enhance email styling utilities for forward operations

**Files to Modify:**
- `src/microsoft_mcp/tools.py` - Extend microsoft_operations tool (primary change)
- `src/microsoft_mcp/email_framework/utils.py` - Enhance for forward styling
- `tests/test_microsoft_operations.py` - Add consolidated email action tests
- `tests/legacy/` - Move existing email tests here for migration tracking

**New Email Actions to Implement:**
- `email.forward` - Forward email with comment and styling support
- `email.move` - Move email between folders with validation
- `email.mark` - Mark email as read/unread/important with batch support
- `email.search` - Search emails with advanced filtering options
- `email.get` - Retrieve specific email with attachment options

**Implementation Examples (Graph API Calls):**
```python
# email.forward - POST /me/messages/{id}/forward
def handle_forward(graph, email_id, to_recipients, comment=None):
    body = {
        "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_recipients]
    }
    if comment:
        body["comment"] = apply_email_styling(comment)  # Use Story 1.2 utilities
    return graph.post(f"/me/messages/{email_id}/forward", json=body)

# email.move - POST /me/messages/{id}/move
def handle_move(graph, email_id, destination_folder):
    # Map folder names to IDs (inbox, sent, drafts, deleteditems, etc.)
    folder_id = resolve_folder_id(destination_folder)
    body = {"destinationId": folder_id}
    return graph.post(f"/me/messages/{email_id}/move", json=body)

# email.mark - PATCH /me/messages/{id}
def handle_mark(graph, email_id, mark_as):
    body = {}
    if mark_as == "read":
        body["isRead"] = True
    elif mark_as == "unread":
        body["isRead"] = False
    elif mark_as == "important":
        body["importance"] = "high"
    return graph.patch(f"/me/messages/{email_id}", json=body)

# email.search - GET /me/messages with $search parameter
def handle_search(graph, query, folder=None, limit=20):
    params = {
        "$search": f'"{query}"',
        "$top": limit,
        "$select": "id,subject,from,receivedDateTime,bodyPreview"
    }
    if folder:
        endpoint = f"/me/mailFolders/{folder}/messages"
    else:
        endpoint = "/me/messages"
    return graph.get(endpoint, params=params)

# email.get - GET /me/messages/{id} with optional expansion
def handle_get(graph, email_id, include_attachments=False):
    params = {"$select": "id,subject,body,from,to,cc,receivedDateTime,hasAttachments"}
    if include_attachments:
        params["$expand"] = "attachments"
    return graph.get(f"/me/messages/{email_id}", params=params)
```

## Definition of Done

**Implementation Complete:**
- [ ] All 5 additional email actions implemented in `microsoft_operations` tool
- [ ] Story 1.1 parameter validation integrated for new actions
- [ ] Email styling utilities enhanced for forward operations
- [ ] Action routing handles all 10 email actions seamlessly

**Quality Assurance:**
- [ ] Zero regression in Story 1.2's 5 existing email actions
- [ ] All 10 email actions thoroughly tested with representative operations
- [ ] Performance benchmarks met (total operation time < 200ms)
- [ ] Backward compatibility verified - existing individual tools unchanged

**Documentation & Testing:**
- [ ] Action parameter documentation complete for all 10 email actions
- [ ] Legacy email tests moved to `tests/legacy/` with `@pytest.mark.legacy`
- [ ] Consolidated test suite created with 5 comprehensive email action tests
- [ ] Email styling utility enhancements documented
- [ ] Migration examples updated with complete email action set

## Success Metrics

**Immediate Success (TODAY):**
1. `microsoft_operations` tool successfully handles all 10 email actions
2. Action routing with parameter validation works flawlessly for new actions
3. Email styling utilities produce professional output for forward operations
4. Zero regression in existing functionality during extension
5. Complete email consolidation achieved in unified tool

**Strategic Success:**
- Email operations fully consolidated (10/10 actions in unified tool)
- Foundation proven for calendar, file, and contact action consolidation
- Story 1.1's validation framework proven across broader action set
- Action routing architecture validated for future tool consolidation

## Dependencies

**Required for Start:**
- [x] Story 1.1: Parameter validation framework (DONE)
- [x] Story 1.2: microsoft_operations tool with 5 email actions (DONE)

**Enables:**
- Story 1.4: Add calendar actions to microsoft_operations
- Story 1.5: Add file and contact actions
- Story 1.6: Implement utility tools

## Risk Assessment

**Primary Risk:** Time constraint (2-hour completion)  
**Mitigation:** Focus on extending existing patterns, reuse Graph API implementations  
**Fallback:** Deliver most critical actions (forward, search) first, complete remainder

**Technical Risk:** Complex forward email styling integration  
**Mitigation:** Leverage existing reply styling patterns, focus on professional output  
**Rollback:** Implement forward without styling initially, enhance in follow-up

**Compatibility Risk:** Regression in Story 1.2's existing actions  
**Mitigation:** Thorough testing of existing actions during extension  
**Validation:** Run existing email action tests before and after implementation

## Next Steps

**After Story 1.3 Complete:**
- **Story 1.4**: "Add Calendar Actions to microsoft_operations tool"
- **Story 1.5**: "Add File & Contact Actions, Complete Unified Tool" 
- **Story 1.6**: "Implement Utility Tools to Reach 15 Total"

## Communication Points

**Strategic Updates:**
1. **EMAIL CONSOLIDATION COMPLETE**: All 10 email actions unified in single tool
2. **VALIDATION PROVEN**: Story 1.1's framework successfully handles diverse action types
3. **ARCHITECTURE VALIDATED**: Action routing scales effectively for multiple operations
4. **PERFORMANCE MAINTAINED**: No degradation despite consolidation complexity

**Implementation Notes:**
- Extend existing action router from Story 1.2
- Reuse proven Graph API patterns from individual tools
- Maintain professional email styling for forward operations
- Preserve all backward compatibility throughout extension

## Notes

This story completes the email consolidation phase by adding the remaining 5 email actions to the `microsoft_operations` tool. Building on Story 1.2's foundation, it demonstrates the scalability of the action routing architecture and validates Story 1.1's parameter validation across a broader set of operations. Completion establishes the pattern for consolidating calendar, file, and contact operations in subsequent stories.