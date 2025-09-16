# Tier 1 - Critical Hooks

This directory contains critical security and validation hooks that are essential for project integrity.

## Hooks in this tier:

- **notification.py**: Sends notifications for various events
- **stop.py**: Handles stop events
- **subagent_stop.py**: Handles subagent stop events
- **pre_tool_use.py**: Runs before tool usage
- **post_tool_use.py**: Runs after tool usage
- **user_prompt_sumbit.py**: Runs when the user submits a prompt
- **pre_compact.py**: Runs before compacting
- **session_start.py**: Runs when the session starts

## Characteristics:

- Security-focused
- Validation and enforcement
- Required for all projects
- Cannot be disabled without explicit override

## Usage:

These hooks are automatically included in all project setups unless explicitly excluded.
