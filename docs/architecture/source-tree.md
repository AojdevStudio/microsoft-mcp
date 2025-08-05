# Source Tree Structure

## Overview

This document defines the project structure for the Microsoft MCP server, including directory organization, file naming conventions, and architectural boundaries.

## Directory Structure

```
microsoft-mcp/
├── .github/                      # GitHub configuration
│   └── workflows/               # CI/CD workflows
│       ├── test.yml            # Run tests on PR
│       └── release.yml         # Release automation
├── docs/                        # Documentation root
│   ├── architecture/           # Architecture documents
│   │   ├── coding-standards.md
│   │   ├── tech-stack.md
│   │   ├── source-tree.md
│   │   ├── email-consolidation-architecture.md
│   │   └── email-consolidation-implementation.md
│   ├── prds/                   # Product Requirements Documents
│   │   └── MSFT-701-ultra-consolidation-email.md
│   ├── stories/                # Development stories
│   │   └── 1.1.story.md
│   └── brief.md               # Project brief
├── src/                        # Source code root
│   └── microsoft_mcp/         # Main package
│       ├── __init__.py        # Package initialization
│       ├── server.py          # MCP server entry point
│       ├── tools.py           # Tool definitions (to be refactored)
│       ├── auth.py            # Authentication handling
│       ├── graph.py           # Microsoft Graph API wrapper
│       ├── email_params.py    # Email parameter models (NEW)
│       ├── email_operations.py # Email operation handlers (NEW)
│       ├── validation.py      # Validation utilities (NEW)
│       ├── constants.py       # Project constants (NEW)
│       └── email_framework/   # Email template framework
│           ├── __init__.py
│           ├── base.py        # Base email components
│           ├── themes.py      # Theme definitions
│           ├── templates.py   # Email templates
│           └── test_runner.py # Template test runner
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── test_email_params.py  # Parameter validation tests (NEW)
│   ├── test_email_operations.py # Operation handler tests (NEW)
│   ├── test_auth.py          # Authentication tests
│   ├── test_graph.py         # Graph API tests
│   └── email_framework/      # Template framework tests
│       └── test_templates.py
├── scripts/                    # Utility scripts
│   ├── authenticate.py        # Manual authentication script
│   └── validate_config.py     # Configuration validator
├── .bmad-core/                # BMad Method configuration
│   ├── agents/               # Agent definitions
│   ├── tasks/                # Task definitions
│   ├── templates/            # Document templates
│   ├── checklists/           # Validation checklists
│   └── core-config.yaml      # Core configuration
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
├── README.md                  # Project documentation
├── LICENSE                    # License file
└── .gitignore                # Git ignore rules
```

## File Organization Guidelines

### Source Code (`src/microsoft_mcp/`)

#### Core Modules
- **server.py** - MCP server initialization and configuration
- **tools.py** - Tool registration (being replaced by email_operations.py)
- **auth.py** - MSAL authentication and token management
- **graph.py** - Microsoft Graph API client wrapper

#### New Consolidation Modules
- **email_params.py** - All Pydantic parameter models for email operations
- **email_operations.py** - Unified email operations implementation
- **validation.py** - Error formatting and validation utilities
- **constants.py** - API endpoints, regex patterns, enums

#### Email Framework (`email_framework/`)
- **base.py** - Base CSS components and styling utilities
- **themes.py** - Theme definitions (Baytown, Humble, Executive)
- **templates.py** - Professional email templates
- **test_runner.py** - Template testing and preview generation

### Tests (`tests/`)

#### Test File Naming
- Test files must start with `test_` prefix
- Match source file names: `email_params.py` → `test_email_params.py`
- Group related tests in subdirectories matching source structure

#### Test Organization
```python
# tests/test_email_params.py
class TestBaseEmailParams:
    """Test base parameter model."""
    pass

class TestSendEmailParams:
    """Test send email parameters."""
    pass

class TestListEmailParams:
    """Test list email parameters."""
    pass
```

### Documentation (`docs/`)

#### Architecture Documents (`architecture/`)
- Technical specifications and design decisions
- Must be kept in sync with implementation
- Use clear section headers and examples

#### Stories (`stories/`)
- Named as `{epic}.{story}.story.md`
- Follow story template structure
- Include all context needed for implementation

#### PRDs (`prds/`)
- Feature specifications and requirements
- Named with issue ID: `MSFT-{number}-{feature}.md`
- Include acceptance criteria and success metrics

## Import Organization

### Standard Import Order
```python
# 1. Standard library imports
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Union

# 2. Third-party imports
import aiohttp
from pydantic import BaseModel, Field, validator
from fastmcp import FastMCP

# 3. Local application imports
from .auth import get_authenticated_client
from .graph import GraphClient
from .constants import GRAPH_API_BASE_URL
from .validation import format_error_response
```

### Relative vs Absolute Imports
```python
# Within package: use relative imports
from .auth import authenticate
from .graph import GraphClient
from ..email_framework.base import apply_styling

# From tests: use absolute imports
from microsoft_mcp.email_params import SendEmailParams
from microsoft_mcp.validation import format_error_response
```

## Module Boundaries

### Clean Architecture Layers

#### 1. API Layer (`server.py`, `tools.py`)
- MCP protocol handling
- Tool registration
- Request/response formatting
- No business logic

#### 2. Business Layer (`email_operations.py`)
- Operation handlers
- Business logic
- Template processing
- Error handling

#### 3. Data Layer (`email_params.py`)
- Parameter models
- Validation rules
- Type definitions
- No API dependencies

#### 4. Infrastructure Layer (`auth.py`, `graph.py`)
- External service integration
- Authentication
- HTTP client management
- Token storage

### Dependency Rules
- Dependencies flow inward (API → Business → Data)
- Infrastructure can be used by any layer
- No circular dependencies
- Interfaces over implementations

## File Naming Conventions

### Python Files
- Use `snake_case.py` for all Python files
- Be descriptive: `email_operations.py` not `ops.py`
- Group related functionality: `email_params.py` for all email parameters

### Test Files
- Prefix with `test_`: `test_email_operations.py`
- Match source file structure
- Can have multiple test files per source file if needed

### Documentation Files
- Use `kebab-case.md` for documentation
- Be specific: `email-consolidation-architecture.md`
- Include file type in name when relevant

## Configuration Files

### Project Configuration
- **pyproject.toml** - Project metadata, dependencies, tool configuration
- **uv.lock** - Locked dependency versions
- **.env** - Local environment variables (never commit)
- **.env.example** - Example environment configuration

### Development Configuration
- **.gitignore** - Git ignore patterns
- **.prettierrc** - Markdown formatting
- **pytest.ini** - Test configuration
- **.coverage** - Coverage settings

## Security Considerations

### Sensitive Files
```
# Never commit these files
.env                    # Environment variables
*.pem                   # Certificates
*_secret*              # Files with secrets
~/.microsoft-mcp/      # Token storage directory
```

### File Permissions
- Token storage: 600 (user read/write only)
- Configuration: 644 (user write, others read)
- Scripts: 755 (executable)

## Migration Notes

### Legacy Structure (To Be Removed)
```
# Old structure with 61 tools
src/microsoft_mcp/tools/
├── list_emails.py
├── send_email.py
├── reply_to_email.py
└── ... (58 more files)
```

### New Consolidated Structure
```
# New structure with unified operations
src/microsoft_mcp/
├── email_operations.py  # Single file for all operations
├── email_params.py      # All parameter models
└── validation.py        # Shared validation logic
```

## Best Practices

1. **Keep files focused** - One concern per file
2. **Use clear names** - File name should indicate contents
3. **Maintain symmetry** - Test structure mirrors source structure
4. **Document changes** - Update this file when structure changes
5. **Follow conventions** - Consistency over personal preference