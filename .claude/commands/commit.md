---
allowed-tools: Bash, Read, Write
description: Create well-formatted commits with conventional messages and emoji
---

# Commit

Use the git-flow-manager sub-agent to create well-formatted Git commits with conventional messages and emoji. Parse $ARGUMENTS for commit options and --no-verify flag, run pre-commit checks (lint, build, tests) unless skipped, validate .gitignore configuration, auto-stage modified files if none staged, analyze changes for atomic commit splitting, generate conventional commit messages with appropriate emoji from ai-docs/emoji-commit-ref.yaml, execute commits, and display summary.
