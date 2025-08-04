---
allowed-tools: Bash, Read, Eza
description: Load essential project context by analyzing codebase structure and core docs
---

# Prime Specific

This command provides a lean, focused overview of the project by examining the codebase structure and core documentation for efficient context loading.

**Usage Examples:**

- `/prime` - Load project context and provide overview

**variables:**  
Directory-to-read: $ARGUMENTS 

```yaml
# Task definition for analyzing a software project codebase
task_definition:
  # Specific steps to be executed for the analysis
  instructions:
    - 1. 'Run `eza --tree` to understand the codebase structure and file organization.'
      command: 'eza --tree'
    - 2. 'Run `eza -l --group-directories-first` to understand the codebase structure and file organization.'
      command: 'eza -l --group-directories-first'
    - 3. 'Run `eza -la --git` to show hidden files with git status'
      command: 'eza -la --git'
    - 4. 'IMPORTANT: Read $ARGUMENTS to understand users request' 

  # The primary focus of the analysis report
  analysis_focus:
    - 'Focus on what the codebase contains rather than how to work with it (CLAUDE.md handles that).'

  # Input sources providing context for the analysis task
  context_sources:
    - type: 'Codebase Structure'
      source_command: '!`eza --tree`'
    - type: 'User Instructions'
      source_file: '@CLAUDE.md'
    - type: 'Recent Changes'
      source_command: '!`eza -l --sort=modified`'

  # Important notes regarding the operational workflow
  workflow_notes:
    - 'Claude AI is the main developer of this project, while the user is the stakeholder.'
```
