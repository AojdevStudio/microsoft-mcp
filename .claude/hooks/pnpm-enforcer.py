#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class PnpmEnforcer:
    def __init__(self, input_data: Dict[str, Any]):
        self.input = input_data

    def detect_npm_usage(self, command: str) -> Optional[Dict[str, Any]]:
        """Check if command contains npm or npx usage"""
        if not command or not isinstance(command, str):
            return None

        # Common npm/npx patterns to block
        npm_patterns = [
            r'(?:^|\s|;|&&|\|\|)npm\s+',
            r'(?:^|\s|;|&&|\|\|)npx\s+',
            r'(?:^|\s|;|&&|\|\|)npm$',
            r'(?:^|\s|;|&&|\|\|)npx$'
        ]

        for pattern in npm_patterns:
            match = re.search(pattern, command)
            if match:
                return {
                    'detected': True,
                    'original': command.strip(),
                    'suggestion': self.generate_pnpm_alternative(command)
                }

        return None

    def generate_pnpm_alternative(self, command: str) -> str:
        """Generate pnpm alternative for npm/npx commands"""
        # Common npm -> pnpm conversions
        conversions = [
            # Basic package management
            (r'npm install(?:\s|$)', 'pnpm install'),
            (r'npm i(?:\s|$)', 'pnpm install'),
            (r'npm install\s+(.+)', r'pnpm add \1'),
            (r'npm i\s+(.+)', r'pnpm add \1'),
            (r'npm install\s+--save-dev\s+(.+)', r'pnpm add -D \1'),
            (r'npm install\s+-D\s+(.+)', r'pnpm add -D \1'),
            # Global installs are project-specific in CDEV
            (r'npm install\s+--global\s+(.+)', r'# Global installs not supported - use npx or install as dev dependency'),
            (r'npm install\s+-g\s+(.+)', r'# Global installs not supported - use npx or install as dev dependency'),
            
            # Uninstall
            (r'npm uninstall\s+(.+)', r'pnpm remove \1'),
            (r'npm remove\s+(.+)', r'pnpm remove \1'),
            (r'npm rm\s+(.+)', r'pnpm remove \1'),
            
            # Scripts
            (r'npm run\s+(.+)', r'pnpm run \1'),
            (r'npm start', 'pnpm start'),
            (r'npm test', 'pnpm test'),
            (r'npm build', 'pnpm build'),
            (r'npm dev', 'pnpm dev'),
            
            # Other commands
            (r'npm list', 'pnpm list'),
            (r'npm ls', 'pnpm list'),
            (r'npm outdated', 'pnpm outdated'),
            (r'npm update', 'pnpm update'),
            (r'npm audit', 'pnpm audit'),
            (r'npm ci', 'pnpm install --frozen-lockfile'),
            
            # npx commands
            (r'npx\s+(.+)', r'pnpm dlx \1'),
            (r'npx', 'pnpm dlx')
        ]

        suggestion = command
        
        for pattern, replacement in conversions:
            if re.search(pattern, command):
                suggestion = re.sub(pattern, replacement, command)
                break

        # If no specific conversion found, do basic substitution
        if suggestion == command:
            suggestion = re.sub(r'(?:^|\s)npm(?:\s|$)', ' pnpm ', command)
            suggestion = re.sub(r'(?:^|\s)npx(?:\s|$)', ' pnpm dlx ', suggestion)
            suggestion = suggestion.strip()

        return suggestion

    def validate(self) -> Dict[str, Any]:
        """Validate and process the bash command"""
        try:
            # Parse Claude Code hook input format
            tool_name = self.input.get('tool_name')
            
            if tool_name != 'Bash':
                return self.approve()

            tool_input = self.input.get('tool_input', {})
            command = tool_input.get('command')
            
            if not command:
                return self.approve()

            # Check for npm/npx usage
            npm_usage = self.detect_npm_usage(command)
            
            if npm_usage:
                return self.block(npm_usage)

            return self.approve()
            
        except Exception as error:
            return self.approve(f'PNPM enforcer error: {error}')

    def approve(self, custom_message: Optional[str] = None) -> Dict[str, Any]:
        """Approve the command"""
        return {
            'approve': True,
            'message': custom_message or '✅ Command approved'
        }

    def block(self, npm_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Block npm/npx command and suggest pnpm alternative"""
        message = [
            '🚫 NPM/NPX Usage Blocked',
            '',
            f'❌ Blocked command: {npm_usage["original"]}',
            f'✅ Use this instead: {npm_usage["suggestion"]}',
            '',
            '📋 Why pnpm?',
            '  • Faster installation and better disk efficiency',
            '  • More reliable dependency resolution',
            '  • Better monorepo support',
            '  • Consistent with project standards',
            '',
            '💡 Quick pnpm reference:',
            '  • pnpm install     → Install dependencies',
            '  • pnpm add <pkg>   → Add package',
            '  • pnpm add -D <pkg> → Add dev dependency',
            '  • pnpm run <script> → Run package script',
            '  • pnpm dlx <cmd>   → Execute package (like npx)',
            '',
            'Please use the suggested pnpm command instead.'
        ]

        return {
            'approve': False,
            'message': '\n'.join(message)
        }


def main():
    """Main execution"""
    try:
        input_data = json.load(sys.stdin)
        
        # Ensure log directory exists
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'pnpm_enforcer.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Add timestamp to the log entry
        timestamp = datetime.now().strftime("%b %d, %I:%M%p").lower()
        input_data['timestamp'] = timestamp
        
        # Process enforcement logic
        enforcer = PnpmEnforcer(input_data)
        result = enforcer.validate()
        
        # Add result to log entry
        input_data['enforcement_result'] = result
        
        # Append new data to log
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(json.dumps(result))
    except Exception as error:
        print(json.dumps({
            'approve': True,
            'message': f'PNPM enforcer error: {error}'
        }))


if __name__ == '__main__':
    main()