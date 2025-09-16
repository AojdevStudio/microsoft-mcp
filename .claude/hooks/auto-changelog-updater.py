#!/usr/bin/env python3
"""
Auto Changelog Updater Hook

This hook automatically updates the changelog after git commits are made.
It runs the update-changelog.py script in automatic mode to analyze recent
commits and update the CHANGELOG.md file accordingly.

Hook Type: post_tool_use
Triggers On: git commit commands
"""

import json
import subprocess
import sys
from pathlib import Path


def main():
    # Read the tool use data from stdin
    tool_data = json.load(sys.stdin)
    
    # Check if this is a git commit command
    tool_name = tool_data.get("tool", "")
    
    # We're looking for Bash tool with git commit commands
    if tool_name != "Bash":
        # Not a bash command, skip
        return 0
    
    # Check if the command contains git commit
    command = tool_data.get("arguments", {}).get("command", "")
    if not command:
        return 0
    
    # Check for various forms of git commit commands
    git_commit_patterns = [
        "git commit",
        "git commit -m",
        "git commit --message",
        "git commit -am",
        "git commit --amend"
    ]
    
    is_git_commit = any(pattern in command for pattern in git_commit_patterns)
    
    if not is_git_commit:
        # Not a git commit command, skip
        return 0
    
    # Check if the command was successful
    result = tool_data.get("result", {})
    if isinstance(result, dict):
        exit_code = result.get("exitCode", 0)
        if exit_code != 0:
            # Git commit failed, don't update changelog
            return 0
    
    # Find the update-changelog.py script
    script_path = Path(__file__).parent.parent.parent / "scripts" / "changelog" / "update-changelog.py"
    
    if not script_path.exists():
        print(f"Warning: Changelog update script not found at {script_path}", file=sys.stderr)
        return 0
    
    # Run the changelog update script in auto mode
    try:
        print("\n🔄 Automatically updating changelog after git commit...", file=sys.stderr)
        
        # Run the script with --auto flag
        result = subprocess.run(
            ["python", str(script_path), "--auto"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent  # Run from project root
        )
        
        if result.returncode == 0:
            print("✅ Changelog updated successfully!", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
        else:
            print(f"⚠️  Changelog update completed with warnings (exit code: {result.returncode})", file=sys.stderr)
            if result.stderr:
                print(f"Error output: {result.stderr}", file=sys.stderr)
    
    except Exception as e:
        print(f"❌ Error updating changelog: {e}", file=sys.stderr)
        # Don't fail the hook even if changelog update fails
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())