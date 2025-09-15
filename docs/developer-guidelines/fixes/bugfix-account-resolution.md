Bugfix: Account Resolution Hang in MCP Tools
Date: 2025-09-15

Summary
- Fixes a hang in MCP tool calls (notably email operations) when `account_id` did not match an existing authenticated account.
- Adds smarter account resolution and clearer errors; updates docs for missing `Mail.Send` permission that caused 403 on send.

Symptoms
- MCP tool calls appeared to "do nothing" or hang when an email address was passed as `account_id`.
- Logs showed device flow starting unexpectedly during tool execution.
- Sending mail sometimes returned HTTP 403 on `/me/sendMail` due to missing `Mail.Send` permission.

Root Cause
- `get_token()` only matched accounts by `home_account_id`. When a username (email) was passed, no match was found and MSAL device flow was initiated inside the tool call, blocking the server.

What Changed
- Smarter account resolution in `get_token(account_id)`:
  - Accepts: `home_account_id` (original), username/email (case‑insensitive), or `'default'`/`'me'`/`'primary'` (first account).
  - If accounts exist but `account_id` is invalid, immediately raises a clear error that lists available accounts and suggests using `'default'`.
  - Only enters device flow when there are no cached accounts.
- Documentation updates:
  - Call out the required `Mail.Send` delegated permission for sending mail.
  - Clarify how to pass `account_id` (`home_account_id`, email, or `'default'`).

Files Touched
- `src/microsoft_mcp/auth.py`
  - `get_token()` now resolves accounts by ID or email and returns a helpful error instead of entering device flow on invalid IDs.
- `README.md`
  - Multi‑account usage clarified; troubleshooting updated to mention `Mail.Send` for 403s.
- `CHANGELOG.md`
  - Added entry under Unreleased → Fixed.

Before vs After
- Before: Passing `admin@example.com` as `account_id` triggered device flow and the tool call hung.
- After: The same input resolves to the correct account (or returns a clear error listing available accounts). No hanging.

How To Use
- Pass one of:
  - Exact `home_account_id`
  - Account email (case‑insensitive)
  - `'default'` to use the first authenticated account

Notes
- Ensure Azure App Registration includes `Mail.Send` in addition to `Mail.ReadWrite` to avoid 403 on `/me/sendMail`.

