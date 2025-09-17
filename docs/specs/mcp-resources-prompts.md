# MCP Resource & Prompt Expansion Ideas

## Context

The Microsoft MCP server already exposes a focused tool surface (`email_operations`, `calendar_operations`, `file_operations`, `contact_operations`, `auth_operations`). To unlock richer autonous behavior from LLM clients we should add the missing MCP primitives:

- **Resources** – share reusable contextual data (records, schemas, enumerations, instructions).
- **Prompts** – offer reusable conversation blueprints that steer the model toward calling the right tools with the right arguments.

This doc captures candidate resources/prompts and how they could integrate with the existing codebase.

## Resource Concepts

### 1. Email Template Catalog (`email_templates`)
- **Source**: `src/microsoft_mcp/email_framework/templates` + validator requirements.
- **Purpose**: Give LLMs structured knowledge of available templates, required fields, optional fields, defaults, and theme guidance.
- **Shape**: JSON tree keyed by `template_id` with description, mandatory keys, example payload, and rendering notes.
- **Implementation Notes**:
  - Build metadata from lightweight dataclasses or static dicts alongside the template classes to avoid tight coupling.
  - Expose via `@mcp.resource("email-templates")` in `tools.py` so clients can `read_resource(...)` before calling `email_operations`.
  - Include version info and last-update timestamp so agents can cache responsibly.

### 2. Account Insight (`account_context/<account_id>`)
- **Source**: Aggregated from `auth.list_accounts`, `email_tool.FOLDERS`, `file_tool` root.
- **Purpose**: Let the LLM inspect which Microsoft account is `default`, what aliases exist, and which folders/drives it can target.
- **Shape**: Hierarchical JSON listing `account_summary`, `mail_folders`, `recent_calendars`, `onedrive_roots`.
- **Implementation Notes**:
  - Generate on read using existing Graph pagination helpers with conservative limits.
  - Cache per-account results briefly (e.g., in-memory with timestamp) to avoid rate limits.
  - Guard with explicit error messaging when account token is stale.

### 3. Compliance & Branding Guide (`branding_guide`)
- **Source**: `docs/email-framework-guide.md`, template CSS, tone guidelines from product briefs.
- **Purpose**: Provide quick reference on voice & tone, signature conventions, theme selection, subject-line rules.
- **Shape**: Markdown resource summarizing do/don't bullets plus references to the template IDs.
- **Implementation Notes**:
  - Assemble from existing docs to avoid duplication; consider programmatically pulling sections during build time.
  - Useful as a fallback when template data is incomplete—the LLM can still craft bespoke mails while staying on brand.

### 4. Graph API Capability Matrix (`graph_capabilities`)
- **Source**: `graph.py`, docs on supported scopes, rate limits.
- **Purpose**: Educate the LLM on which Graph endpoints are wired through each tool, available fields, and notable constraints (e.g., `list_emails` max page size).
- **Shape**: JSON table keyed by tool action (`email.list`, `calendar.create`, etc.) with Graph endpoint, default select fields, pagination behavior, known errors.
- **Implementation Notes**:
  - Auto-generate by introspecting helper functions to stay in sync (e.g., docstring parser or decorators).
  - Expose for debugging/chain-of-thought: helps agents reason about why an action failed and suggest alternatives.

### 5. Template Data Library (`sample_payloads/<template_id>`)
- **Source**: Curated examples from real workflows.
- **Purpose**: Give the model ready-to-use payloads it can tweak instead of inventing structure from scratch.
- **Shape**: Resource family (dynamic IDs) returning JSON sample objects plus commentary on when to use them.
- **Implementation Notes**:
  - Store sample payloads in `docs/templates/examples/*.json` and load on demand.
  - Provide multiple variations per template (e.g., monthly report, urgent alert) to cover tone/urgency changes.

## Prompt Concepts

### 1. `compose_practice_report`
- **Goal**: Guide the LLM to gather necessary inputs (location, period, KPI metrics) and then call `email_operations` with `template="practice_report"`.
- **Structure**:
  - System: “You are KamDental's operations assistant... ensure all numeric metrics are present.”
  - User: placeholder instructions for the human's request.
  - Additional: checklist enumerating template fields and reminding to `style_email_content` gets invoked automatically.
- **Implementation**: Add to `tools.py` (or new `prompts.py`) using `@mcp.prompt(...)` and returning `fastmcp.prompts.base.SystemMessage/UserMessage` list.

### 2. `compose_executive_summary`
- **Goal**: Ensure multi-location data is compiled, highlight cross-location comparisons, then call template.
- **Structure**: Emphasize verifying each location has production/collections and key insights array populated.

### 3. `compose_provider_update`
- **Goal**: Tailor to provider performance with positive/negative feedback guardrails.
- **Structure**: Provide branch instructions when metrics are below goal (suggest callouts) vs above goal (celebrate wins).

### 4. `send_manual_email`
- **Goal**: For bespoke emails (no template), prompt should remind the agent to pull the branding resource and apply `style_email_content` with appropriate theme.
- **Structure**: Steps for collecting tone, greeting, CTA, attachments.

### 5. `plan_calendared_followup`
- **Goal**: Multi-step prompt that first drafts the email (via resource+template or manual), then schedules a follow-up meeting using `calendar_operations.create`.
- **Structure**: Encourage verifying attendee availability via `check_availability` before scheduling.

## Implementation Sequencing

1. **Metadata groundwork** – add static metadata modules describing templates, tools, account schema to avoid duplication.
2. **Resource scaffolding** – implement `@mcp.resource` functions for template catalog + branding guide as phase 1 (lowest risk, pure read operations).
3. **Prompt library** – once template metadata is exposed, create prompt definitions referencing the new resources so LLMs know where to look.
4. **Client onboarding** – document in README how Claude/other clients should `list_resources`, read the catalog, then use prompts before calling tools.
5. **Testing/validation** – add unit tests ensuring resources return valid JSON/Markdown and prompts list registers correctly.

## Open Questions

- How frequently should dynamic resources (e.g., account insight) refresh, and do we need server-side caching semantics?
- Should resources support query parameters (e.g., `/resources/email-templates?template=practice_report`) for narrower payloads?
- Do we want to allow prompts to trigger multi-tool flows (email + calendar) automatically, or keep them as guidance only?
- How will we version resources/prompts so clients detect breaking changes?

## Next Steps

- Review this list, tag high-priority resources/prompts.
- Design lightweight metadata structs for templates to generate catalog + validation rules.
- Prototype the `email-templates` resource and a single prompt to validate ergonomics.
- Update product docs once the new primitives ship so internal users know how to leverage them.
