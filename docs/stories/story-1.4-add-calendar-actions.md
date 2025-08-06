# Story 1.4: Add Calendar Actions to Microsoft Operations Tool

## User Story

As a **Microsoft MCP developer**,  
I want **to add all 6 calendar actions to the `microsoft_operations` tool**,  
So that **calendar functionality is consolidated into the unified tool architecture**.

## Story Context

**Calendar Consolidation Phase:**
- **From:** Completed email actions (10/10) in `microsoft_operations` tool
- **To:** Email + Calendar actions (16 total) in unified tool
- **Target Timeline:** 2 hours (TODAY completion)
- **Integration:** Leverages Story 1.1's parameter validation and Story 1.2's action routing
- **Foundation:** Proven action router architecture from email consolidation

**Touch Points:**
- `src/microsoft_mcp/tools.py` - Extend `microsoft_operations` tool with calendar actions
- `src/microsoft_mcp/graph.py` - Existing Graph API client (unchanged)
- Story 1.1 validation framework - **EXTEND TO CALENDAR PARAMS**
- Story 1.2/1.3 action router - **ADD CALENDAR ACTION ROUTING**

## Acceptance Criteria

**Calendar Action Implementation (TODAY):**
1. Add 6 calendar actions to `microsoft_operations` tool: `calendar.list`, `calendar.get`, `calendar.create`, `calendar.update`, `calendar.delete`, `calendar.availability`
2. Create calendar parameter validation models extending Story 1.1's framework
3. Implement calendar action routing following Story 1.2's established patterns
4. Maintain consistent error handling and response formats

**Parameter Structure (Calendar Actions):**
5. List: `account_id`, `action: "calendar.list"`, `data: {start_date, end_date, limit, calendar_id}`
6. Get: `account_id`, `action: "calendar.get"`, `data: {event_id, calendar_id}`
7. Create: `account_id`, `action: "calendar.create"`, `data: {subject, start_datetime, end_datetime, attendees, location, body}`
8. Update: `account_id`, `action: "calendar.update"`, `data: {event_id, subject, start_datetime, end_datetime, location, body}`
9. Delete: `account_id`, `action: "calendar.delete"`, `data: {event_id, send_cancellation}`
10. Availability: `account_id`, `action: "calendar.availability"`, `data: {start_date, end_date, duration_minutes}`

**Quality & Integration:**
11. Zero regression in existing 10 email actions
12. All 6 calendar actions work seamlessly through unified tool
13. Parameter validation comprehensive for all calendar operations
14. Performance maintained: action routing + operation < 300ms total

**Backward Compatibility:**
15. All existing individual calendar tools remain functional
16. Authentication and error handling patterns consistent with email actions
17. Multi-account support maintained across all calendar operations

**Test Migration Strategy:**
18. Move related legacy calendar tests to `tests/legacy/` subdirectory
19. Create consolidated tests in `test_microsoft_operations.py` for calendar actions
20. Mark old tests with `@pytest.mark.legacy` to exclude from CI
21. Replace 8 calendar tool tests with 1 comprehensive calendar action test
22. Focus on testing unified parameter validation and action routing

## Technical Notes

**Parameter Validation Extensions:**
- Create `CalendarParams` base class following Story 1.1's `BaseEmailParams` pattern
- Implement validation for datetime formats, attendee lists, duration constraints
- Add enum validation for calendar-specific fields (time zones, meeting types)
- Maintain consistent error formatting across email and calendar actions

**Action Router Extensions:**
- Add calendar action handlers to existing action router from Story 1.2
- Implement calendar-specific Graph API call patterns
- Maintain consistent response format between email and calendar operations
- Handle calendar-specific errors (conflicts, permission issues, invalid dates)

**Calendar-Specific Considerations:**
- DateTime validation and timezone handling
- Attendee email validation (reuse email validation from Story 1.1)
- Duration and availability calculation logic
- Meeting conflict detection and resolution
- Recurring event support (future extension point)

## Implementation Scope

**Core Components (2-Hour Focus):**
1. Create calendar parameter models in validation framework
2. Extend `microsoft_operations` action router with calendar handlers
3. Implement 6 calendar actions with Graph API integration
4. Add comprehensive parameter validation for calendar operations

**Files to Create/Modify:**
- `src/microsoft_mcp/calendar_params.py` - Calendar parameter models (NEW FILE)
- `src/microsoft_mcp/tools.py` - Extend microsoft_operations tool (primary change)  
- `src/microsoft_mcp/validation.py` - Extend error formatting for calendar actions
- `tests/test_microsoft_operations.py` - Add consolidated calendar action tests
- `tests/legacy/` - Move existing calendar tests here for migration tracking

**Calendar Actions to Implement:**
- `calendar.list` - List calendar events with date filtering and pagination
- `calendar.get` - Retrieve specific calendar event with full details
- `calendar.create` - Create new calendar event with attendee invitations
- `calendar.update` - Update existing calendar event properties
- `calendar.delete` - Delete calendar event with optional cancellation notice
- `calendar.availability` - Find available time slots for scheduling

## Definition of Done

**Implementation Complete:**
- [ ] All 6 calendar actions implemented in `microsoft_operations` tool
- [ ] Calendar parameter validation models created following Story 1.1 patterns
- [ ] Action router extended to handle both email and calendar actions
- [ ] Comprehensive error handling for calendar-specific operations

**Quality Assurance:**
- [ ] Zero regression in existing 10 email actions
- [ ] All 6 calendar actions thoroughly tested with representative operations
- [ ] Parameter validation comprehensive for datetime, attendees, and constraints
- [ ] Performance benchmarks met (total operation time < 300ms)

**Documentation & Testing:**
- [ ] Calendar parameter models documented with field descriptions
- [ ] Action parameter documentation complete for all 6 calendar actions
- [ ] Legacy calendar tests moved to `tests/legacy/` with `@pytest.mark.legacy`
- [ ] Consolidated calendar action test created in unified test suite
- [ ] Migration examples updated with calendar action usage

## Success Metrics

**Immediate Success (TODAY):**
1. `microsoft_operations` tool handles all 16 actions (10 email + 6 calendar)
2. Calendar parameter validation works flawlessly with detailed error messages
3. Action routing seamlessly handles both email and calendar operations
4. Zero regression in existing email functionality during calendar addition
5. Calendar operations perform within acceptable time limits

**Strategic Success:**
- Email and calendar operations fully consolidated (16/27 target actions)
- Action routing architecture proven scalable across different Microsoft services
- Parameter validation framework validated for diverse operation types
- Foundation established for file and contact action consolidation

## Dependencies

**Required for Start:**
- [x] Story 1.1: Parameter validation framework (DONE)
- [x] Story 1.2: microsoft_operations tool with email actions (DONE)  
- [x] Story 1.3: Complete email actions (DONE - prerequisite)

**Enables:**
- Story 1.5: Add file and contact actions to complete core operations
- Story 1.6: Implement utility tools to reach 15 total tools
- Story 1.7: Migration and deprecation layer

## Risk Assessment

**Primary Risk:** DateTime and timezone complexity  
**Mitigation:** Leverage existing calendar tool implementations, focus on UTC standardization  
**Fallback:** Implement basic calendar actions first, enhance datetime handling iteratively

**Technical Risk:** Calendar action complexity vs. 2-hour timeline  
**Mitigation:** Prioritize most-used actions (list, create, get), implement others if time permits  
**Validation:** Start with simpler actions (list, get) before complex ones (create, update)

**Integration Risk:** Calendar parameter validation complexity  
**Mitigation:** Follow proven patterns from Story 1.1's email validation  
**Rollback:** Implement basic validation first, enhance with detailed constraints

## Next Steps

**After Story 1.4 Complete:**
- **Story 1.5**: "Add File & Contact Actions to Complete Core Operations"
- **Story 1.6**: "Implement Utility Tools to Reach 15 Total Tools"
- **Story 1.7**: "Migration and Deprecation Layer"

## Communication Points

**Strategic Updates:**
1. **CALENDAR CONSOLIDATION COMPLETE**: All 6 calendar actions unified in microsoft_operations
2. **ACTION ROUTING SCALES**: Architecture handles 16 actions across 2 service types
3. **VALIDATION FRAMEWORK PROVEN**: Story 1.1's approach works for diverse parameter types
4. **UNIFIED TOOL MATURING**: Single tool now handles most common Microsoft 365 operations

**Implementation Notes:**
- Extend action router patterns from email consolidation
- Create calendar parameter models following email validation patterns
- Maintain consistent error handling and response formats
- Preserve all backward compatibility with existing tools

## Notes

This story extends the `microsoft_operations` tool with calendar functionality, demonstrating the scalability of the action routing architecture. By adding 6 calendar actions, the unified tool will handle 16 of the most common Microsoft 365 operations. The implementation validates that Story 1.1's parameter validation framework can handle diverse operation types beyond email, establishing the foundation for completing the consolidation with file and contact operations.