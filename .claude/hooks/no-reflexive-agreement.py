#!/usr/bin/env -S uv run --script

"""
Claude Code Hook: No Reflexive Agreement

This Tier 1 hook prevents Claude from using reflexive agreement phrases like 
"you're right", "absolutely correct", etc. It enforces analytical rigor by 
requiring substantive technical analysis instead of empty validation.

Installation:
1. Save this script to .claude/hooks/no-reflexive-agreement.py
2. Make it executable: chmod +x no-reflexive-agreement.py
3. Add as UserPromptSubmit hook in Claude Code

How it works:
- Analyzes the last 5 assistant messages in the transcript
- Detects reflexive agreement patterns using regex
- Supports multilingual detection (English, Korean)
- Appends system reminder when triggered
- Logs all activity for debugging and analysis

Author: CDEV System
Type: Tier 1 Critical Hook
Category: Behavioral Constraint
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ReflexiveAgreementDetector:
    """
    Detects and prevents reflexive agreement patterns in Claude responses.
    
    This class analyzes assistant messages for common agreement phrases
    that lack substantive analysis, promoting more rigorous responses.
    """
    
    # Regex patterns for detecting reflexive agreement
    AGREEMENT_PATTERNS = [
        # English patterns
        r'[Yy]ou.*(?:are\s+)?(?:right|correct)',
        r'[Aa]bsolutely(?:\s+correct|\s+right)?',
        r'[Tt]hat\'?s\s+(?:exactly\s+)?right',
        r'[Pp]erfectly\s+correct',
        r'[Ee]xactly(?:\s+right)?',
        
        # Korean patterns
        r'사용자가.*맞다',  # "user is right"
        r'맞습니다',        # "that's correct"
        r'정확합니다',      # "that's accurate"
        r'옳습니다',        # "that's right"
    ]
    
    def __init__(self, log_path: Path):
        """
        Initialize the detector with logging capability.
        
        Args:
            log_path: Path to the log file for recording events
        """
        self.log_path = log_path
        self.compiled_patterns = [re.compile(pattern) for pattern in self.AGREEMENT_PATTERNS]
    
    def analyze_message_content(self, message: Dict[str, Any]) -> bool:
        """
        Analyze a single message for reflexive agreement patterns.
        
        Args:
            message: Assistant message from transcript
            
        Returns:
            True if reflexive agreement detected, False otherwise
        """
        try:
            # Extract text content from message structure
            if not message.get('message', {}).get('content'):
                return False
                
            content = message['message']['content']
            if not isinstance(content, list) or not content:
                return False
                
            # Check first content block for text
            first_content = content[0]
            if first_content.get('type') != 'text':
                return False
                
            text = first_content.get('text', '')
            if not text:
                return False
            
            # Analyze first 80 characters for reflexive agreement
            # (matching bash script behavior)
            text_sample = text[:80]
            
            # Check against all compiled patterns
            for pattern in self.compiled_patterns:
                if pattern.search(text_sample):
                    return True
                    
            return False
            
        except (KeyError, TypeError, IndexError) as e:
            self.log_event({
                'event': 'message_analysis_error',
                'error': str(e),
                'message_structure': str(type(message))
            })
            return False
    
    def analyze_recent_messages(self, transcript_path: Path) -> bool:
        """
        Analyze the last 5 assistant messages for reflexive agreement.
        
        Args:
            transcript_path: Path to the transcript file
            
        Returns:
            True if reflexive agreement detected, False otherwise
        """
        try:
            if not transcript_path.exists():
                self.log_event({
                    'event': 'transcript_not_found',
                    'path': str(transcript_path)
                })
                return False
            
            # Read and parse transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            # Extract assistant messages (last 5)
            assistant_messages = self._extract_assistant_messages(transcript_content)
            recent_messages = assistant_messages[-5:] if len(assistant_messages) >= 5 else assistant_messages
            
            # Analyze each recent message
            detected_patterns = []
            for i, message in enumerate(recent_messages):
                if self.analyze_message_content(message):
                    detected_patterns.append({
                        'message_index': i,
                        'preview': self._get_message_preview(message)
                    })
            
            # Log analysis results
            self.log_event({
                'event': 'transcript_analysis',
                'messages_analyzed': len(recent_messages),
                'patterns_detected': len(detected_patterns),
                'detected_patterns': detected_patterns
            })
            
            return len(detected_patterns) > 0
            
        except Exception as e:
            self.log_event({
                'event': 'analysis_error',
                'error': str(e),
                'transcript_path': str(transcript_path)
            })
            return False
    
    def _extract_assistant_messages(self, transcript_content: str) -> List[Dict[str, Any]]:
        """
        Extract assistant messages from transcript content.
        
        Args:
            transcript_content: Raw transcript file content
            
        Returns:
            List of assistant message dictionaries
        """
        assistant_messages = []
        
        # Split transcript into lines and process each
        for line in transcript_content.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            try:
                # Parse JSON line
                message = json.loads(line)
                
                # Filter for assistant messages with text content
                if (message.get('role') == 'assistant' and 
                    message.get('type') == 'assistant' and
                    message.get('message', {}).get('content')):
                    assistant_messages.append(message)
                    
            except json.JSONDecodeError:
                # Skip malformed JSON lines
                continue
                
        return assistant_messages
    
    def _get_message_preview(self, message: Dict[str, Any]) -> str:
        """
        Get a preview of the message content for logging.
        
        Args:
            message: Assistant message dictionary
            
        Returns:
            Preview string (first 80 characters)
        """
        try:
            content = message['message']['content'][0]
            text = content.get('text', '')
            return text[:80] + ('...' if len(text) > 80 else '')
        except (KeyError, IndexError, TypeError):
            return '<unable to extract preview>'
    
    def log_event(self, event_data: Dict[str, Any]) -> None:
        """
        Log an event to the hook's log file following CDEV standards.
        
        Args:
            event_data: Dictionary containing event information
        """
        try:
            # Ensure log directory exists
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing log data or initialize empty list
            if self.log_path.exists():
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    try:
                        log_data = json.load(f)
                    except (json.JSONDecodeError, ValueError):
                        log_data = []
            else:
                log_data = []
            
            # Add timestamp to the log entry
            timestamp = datetime.now().strftime("%b %d, %I:%M%p").lower()
            event_data['timestamp'] = timestamp
            event_data['hook'] = 'no-reflexive-agreement'
            
            # Append new data
            log_data.append(event_data)
            
            # Write back to file with formatting
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Fallback: write to stderr if logging fails
            print(f"Logging failed: {e}", file=sys.stderr)


def generate_system_reminder() -> str:
    """
    Generate the system reminder text to append when reflexive agreement is detected.
    
    Returns:
        System reminder text with examples and guidelines
    """
    return """<system-reminder>
You MUST NEVER use the phrase 'you are right' or similar.

Avoid reflexive agreement. Instead, provide substantive technical analysis.

You must always look for flaws, bugs, loopholes, counter-examples,
invalid assumptions in what the user writes. If you find none,
and find that the user is correct, you must state that dispassionately
and with a concrete specific reason for why you agree, before
continuing with your work.

<example>
user: It's failing on empty inputs, so we should add a null-check.
assistant: That approach seems to avoid the immediate issue.
However it's not idiomatic, and hasn't considered the edge case
of an empty string. A more general approach would be to check
for falsy values.
</example>
<example>
user: I'm concerned that we haven't handled connection failure.
assistant: [thinks hard] I do indeed spot a connection failure
edge case: if the connection attempt on line 42 fails, then
the catch handler on line 49 won't catch it.
[ultrathinks] The most elegant and rigorous solution would be
to move failure handling up to the caller.
</example>
</system-reminder>"""


def main() -> None:
    """
    Main hook execution function.
    
    Reads input from stdin, analyzes transcript for reflexive agreement,
    and outputs system reminder if patterns are detected.
    """
    try:
        # Read input from stdin
        stdin_data = sys.stdin.read().strip()
        if not stdin_data:
            sys.exit(0)
        
        # Parse JSON input
        input_data = json.loads(stdin_data)
        transcript_path_str = input_data.get('transcript_path')
        
        if not transcript_path_str:
            sys.exit(0)
        
        transcript_path = Path(transcript_path_str)
        
        # Initialize detector with logging
        log_path = Path.cwd() / 'logs' / 'no-reflexive-agreement.json'
        detector = ReflexiveAgreementDetector(log_path)
        
        # Log hook execution
        detector.log_event({
            'event': 'hook_execution',
            'transcript_path': str(transcript_path),
            'input_data': input_data
        })
        
        # Analyze transcript for reflexive agreement
        needs_reminder = detector.analyze_recent_messages(transcript_path)
        
        if needs_reminder:
            # Output system reminder (Claude Code will append to context)
            print(generate_system_reminder())
            detector.log_event({
                'event': 'reminder_triggered',
                'action': 'system_reminder_output'
            })
        else:
            detector.log_event({
                'event': 'analysis_complete',
                'action': 'no_reminder_needed'
            })
        
        # Exit successfully (allows Claude Code to proceed)
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        # Log parsing error and exit
        log_path = Path.cwd() / 'logs' / 'no-reflexive-agreement.json'
        detector = ReflexiveAgreementDetector(log_path)
        detector.log_event({
            'event': 'input_parsing_error',
            'error': str(e),
            'stdin_data': stdin_data[:100] if 'stdin_data' in locals() else 'N/A'
        })
        sys.exit(0)
        
    except Exception as e:
        # Log unexpected error and exit
        log_path = Path.cwd() / 'logs' / 'no-reflexive-agreement.json'
        detector = ReflexiveAgreementDetector(log_path)
        detector.log_event({
            'event': 'unexpected_error',
            'error': str(e),
            'error_type': type(e).__name__
        })
        sys.exit(0)


if __name__ == '__main__':
    main()