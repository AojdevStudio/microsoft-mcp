#!/usr/bin/env python3
import json
import sys
import re

# Dangerous command patterns
DANGEROUS_PATTERNS = [
    (r'\brm\s+-rf\s+/', 'Dangerous rm -rf command detected'),
    (r'\b(sudo|su)\b', 'Sudo/su commands require manual execution'),
    (r':\s*\(\s*\)\s*\{.*\}\s*;\s*:', 'Fork bomb pattern detected'),
    (r'\b(chmod|chown)\s+777', 'Overly permissive file permissions'),
]

try:
    input_data = json.load(sys.stdin)
    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')
    
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(message, file=sys.stderr)
            sys.exit(2)  # Block the command
            
except Exception as e:
    print(f"Hook error: {e}", file=sys.stderr)
    sys.exit(1)
