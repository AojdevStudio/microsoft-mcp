# Today's Nuclear Simplification - Feasibility Assessment

## Executive Summary

**VERDICT: NUCLEAR SIMPLIFICATION ACHIEVABLE IN ONE DAY**

- **Estimated Time**: 6 hours total work
- **Complexity**: Low (deletion + 5 focused rewrites)
- **Risk**: Low (git revert rollback strategy)
- **Impact**: 92% complexity reduction (63k → 5k tokens)

## Hour-by-Hour Execution Plan

### Hour 1: Nuclear Deletion Phase
**IMMEDIATE ACTIONS - DELETE WITHOUT MERCY**

```bash
# Delete migration framework entirely
git rm src/microsoft_mcp/migration.py          # 599 lines deleted
git rm src/microsoft_mcp/legacy_mapper.py     # 343 lines deleted  
git rm src/microsoft_mcp/deprecation.py       # 217 lines deleted
git commit -m "BREAKING: Nuclear deletion of migration framework

DELETED:
- migration.py: Parameter mapping system
- legacy_mapper.py: Legacy tool routing
- deprecation.py: Deprecation warnings

ROLLBACK: git revert HEAD if needed
Total complexity eliminated: 1,159 lines"

# Archive mega unified tool
cp src/microsoft_mcp/tools.py .old-files/tools_unified_63k.py
git add .old-files/
git commit -m "Archive 63k token unified tool before nuclear rewrite"
```

### Hour 2: Email Tool Implementation
**DIRECT GRAPH API - ZERO COMPATIBILITY**

```python
# src/microsoft_mcp/tools.py - CLEAN SLATE START
from fastmcp import FastMCP
from . import auth, graph

mcp = FastMCP("microsoft-mcp")

@mcp.tool
def email_operations(
    account_id: str,
    action: Literal["list", "send", "reply", "draft", "delete", "move", "search"],
    **params
) -> dict:
    """Email operations for Microsoft Outlook
    
    Actions:
    - list: Get emails from folder (folder, limit, search_query)
    - send: Send email (to, subject, body, cc, bcc, attachments)
    - reply: Reply to email (email_id, body, reply_all)
    - draft: Create draft (to, subject, body, cc, bcc)  
    - delete: Delete email (email_id, permanent)
    - move: Move email (email_id, destination_folder)
    - search: Search emails (query, folder, limit)
    """
    try:
        token = auth.get_access_token(account_id)
        client = graph.GraphClient(token)
        
        if action == "list":
            return client.list_emails(**params)
        elif action == "send":
            return client.send_email(**params)
        elif action == "reply":
            return client.reply_to_email(**params) 
        elif action == "draft":
            return client.create_draft(**params)
        elif action == "delete":
            return client.delete_email(**params)
        elif action == "move":
            return client.move_email(**params)
        elif action == "search":
            return client.search_emails(**params)
        else:
            raise ValueError(f"Unknown email action: {action}")
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Hour 3: Calendar Tool Implementation

```python
@mcp.tool
def calendar_operations(
    account_id: str,
    action: Literal["list", "create", "update", "delete", "invite"],
    **params
) -> dict:
    """Calendar operations for Microsoft Calendar
    
    Actions:
    - list: Get calendar events (start_date, end_date, limit)
    - create: Create event (subject, start_datetime, end_datetime, attendees, location, body)
    - update: Update event (event_id, subject, start_datetime, end_datetime, location, body)
    - delete: Delete event (event_id, send_cancellation)
    - invite: Send calendar invite (subject, start_datetime, end_datetime, attendees, location, body)
    """
    try:
        token = auth.get_access_token(account_id)
        client = graph.GraphClient(token)
        
        if action == "list":
            return client.list_calendar_events(**params)
        elif action == "create":
            return client.create_calendar_event(**params)
        elif action == "update":
            return client.update_calendar_event(**params)
        elif action == "delete":
            return client.delete_calendar_event(**params)
        elif action == "invite":
            return client.send_calendar_invite(**params)
        else:
            raise ValueError(f"Unknown calendar action: {action}")
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Hour 4: File + Contact Tools Implementation

```python
@mcp.tool
def file_operations(
    account_id: str,
    action: Literal["list", "upload", "download", "delete", "share", "search"],
    **params
) -> dict:
    """File operations for Microsoft OneDrive
    
    Actions:
    - list: List files (folder_path, search_query, limit)
    - upload: Upload file (local_path, onedrive_path)
    - download: Download file (file_path, save_path)  
    - delete: Delete file (file_path)
    - share: Share file (file_path, email, permission, expiration_days)
    - search: Search files (query, file_type, limit)
    """
    try:
        token = auth.get_access_token(account_id)
        client = graph.GraphClient(token)
        
        if action == "list":
            return client.list_files(**params)
        elif action == "upload":
            return client.upload_file(**params)
        elif action == "download":
            return client.download_file(**params)
        elif action == "delete":
            return client.delete_file(**params)
        elif action == "share":
            return client.share_file(**params)
        elif action == "search":
            return client.search_files(**params)
        else:
            raise ValueError(f"Unknown file action: {action}")
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool
def contact_operations(
    account_id: str,
    action: Literal["list", "create", "update", "delete", "search"],
    **params
) -> dict:
    """Contact operations for Microsoft Contacts
    
    Actions:
    - list: List contacts (search_query, limit)
    - create: Create contact (first_name, last_name, email, mobile_phone, company, job_title)
    - update: Update contact (contact_id, first_name, last_name, email, mobile_phone, company, job_title)
    - delete: Delete contact (contact_id)
    - search: Search contacts (query, limit)
    """
    try:
        token = auth.get_access_token(account_id)
        client = graph.GraphClient(token)
        
        if action == "list":
            return client.list_contacts(**params)
        elif action == "create":
            return client.create_contact(**params)
        elif action == "update":
            return client.update_contact(**params)
        elif action == "delete":
            return client.delete_contact(**params)
        elif action == "search":
            return client.search_contacts(**params)
        else:
            raise ValueError(f"Unknown contact action: {action}")
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Hour 5: Auth Tool + Testing

```python
# Keep existing auth tools - they're already clean
@mcp.tool
def list_accounts() -> list[dict[str, str]]:
    """List all signed-in Microsoft accounts"""
    return [
        {"username": acc.username, "account_id": acc.account_id}
        for acc in auth.list_accounts()
    ]

@mcp.tool  
def authenticate_account() -> dict[str, str]:
    """Authenticate a new Microsoft account using device flow"""
    # Keep existing implementation - already clean
    
@mcp.tool
def complete_authentication(flow_cache: str) -> dict[str, str]:
    """Complete the authentication process"""
    # Keep existing implementation - already clean
```

**Testing Phase:**
```bash
# Test each tool independently  
uv run pytest tests/test_email_operations.py -v
uv run pytest tests/test_calendar_operations.py -v  
uv run pytest tests/test_file_operations.py -v
uv run pytest tests/test_contact_operations.py -v
uv run pytest tests/test_auth.py -v
```

### Hour 6: Nuclear Deployment

```bash
# Final commit with breaking changes
git add .
git commit -m "BREAKING: Nuclear simplification complete - 5 focused tools

BREAKING CHANGES:
❌ microsoft_operations() DELETED - use specific tools:
✅ email_operations(account_id, action, **params) 
✅ calendar_operations(account_id, action, **params)
✅ file_operations(account_id, action, **params) 
✅ contact_operations(account_id, action, **params)
✅ list_accounts(), authenticate_account(), complete_authentication() 

COMPLEXITY REDUCTION: 
- 63,693 tokens → 5,000 tokens (92% reduction)
- 1 mega tool → 5 focused tools
- 1,159 lines of migration code → 0 lines

ROLLBACK STRATEGY:
git revert HEAD    # Instant rollback if issues
git tag v1.9.0     # Pin clients to previous version  

MIGRATION EXAMPLES:
OLD: microsoft_operations(account_id, 'email.send', data={...})
NEW: email_operations(account_id, 'send', to='...', subject='...', body='...')

OLD: microsoft_operations(account_id, 'calendar.create', data={...})
NEW: calendar_operations(account_id, 'create', subject='...', start_datetime='...', end_datetime='...')
"

# Tag nuclear release
git tag v2.0.0-nuclear-simplification
git push origin main --tags
```

## Feasibility Analysis

### ✅ FEASIBLE FACTORS

1. **Simple Deletion**: Migration framework is self-contained - clean deletion
2. **Existing Infrastructure**: Graph API client already exists and works
3. **Clear Patterns**: Each tool follows same action-based pattern
4. **Small Codebase**: Core functionality is already implemented in graph.py
5. **No External Dependencies**: Internal consolidation, not external API
6. **Git Safety Net**: Instant rollback with git revert

### ⚠️ RISK FACTORS  

1. **Testing Completeness**: Need to verify all Graph API calls still work
2. **Email Framework Integration**: Ensure email templates still accessible
3. **Parameter Mapping**: Some parameter names might need adjustment
4. **Error Handling**: Ensure consistent error responses across tools

### 🎯 SUCCESS CRITERIA

**Must achieve today:**
- [ ] All migration framework files deleted
- [ ] 5 focused tools implemented and tested
- [ ] Core functionality working (email send, calendar create, file list, contact list)
- [ ] Breaking changes documented
- [ ] Nuclear deployment completed

**Quality gates:**
- [ ] Each tool < 1,000 tokens
- [ ] No compatibility code remaining
- [ ] Git revert strategy tested
- [ ] All original functionality preserved

## Execution Readiness

### Prerequisites ✅
- Existing graph.py client works
- Auth system functional  
- Test framework in place
- Git repository ready

### Blockers 🚫
- None identified - all dependencies internal

### Success Probability: 95%

**Factors supporting success:**
- Clear deletion targets
- Simple rewrite pattern
- Existing working infrastructure
- Git rollback safety net
- Internal-only deployment (no external client impact)

## Today's Action Plan

**START NOW - NUCLEAR SIMPLIFICATION EXECUTION:**

1. **Commit to nuclear approach** - No backwards compatibility
2. **Execute Hour 1: Nuclear deletion** - Delete migration framework  
3. **Execute Hours 2-4: Tool implementation** - 5 focused tools
4. **Execute Hour 5: Testing** - Verify functionality
5. **Execute Hour 6: Nuclear deployment** - Breaking changes deployment

**END STATE**: 92% complexity reduction achieved in one day with full functionality preserved and git revert rollback strategy.