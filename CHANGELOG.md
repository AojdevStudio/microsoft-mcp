# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.2.0] - 2025-08-04

### Added

- ✨ feat: introduce foundational documentation and task framework
- Add KamDental Professional Email Framework with Templates and Themes (#4) [#4]
- 🔧 feat(hooks): add post-tool use hook for workflow completion
- ✨ feat(mcp): enhance Microsoft Graph API integration
- 🏗️ feat(claude): add comprehensive agent infrastructure
- 🚀 feat(claude): major command framework enhancement
- ⚡ feat(hooks): enhance code quality and notification systems
- 📋 docs: add KamDental Email Framework PRD with comprehensive testing requirements
- 📄 chore: add .env.example template for environment configuration

### Changed

- ⚙️ config: update Claude settings and gitignore rules
- 🙈 chore: update .gitignore with project-specific ignores

### Removed

- 🗑️ chore: remove obsolete hook files

### Fixed

- 🧹 style: fix linting errors in Claude hooks
- 🐛 fix: force HTML formatting for all email functions to ensure professional styling

### Fixed
- 🐛 Force HTML formatting for all email functions to ensure professional styling is always applied
- 🐛 Remove content detection logic that was causing emails to be sent as plain text instead of formatted HTML
- 🐛 Ensure executive signature and professional styling appear in all emails regardless of input content type

## [0.1.0] - 2025-01-18

### Added
- ✨ Complete Microsoft MCP server implementation with FastMCP framework
- 🔧 Claude Code infrastructure including commands, hooks, and settings
- ✨ Professional email signature with booking link integration
- ✨ Enhanced email functionality with HTML formatting and rich styling
- 🔧 Comprehensive validation and notification hooks for development workflow
- ✨ Core Microsoft Graph API integration for email, calendar, files, and contacts
- 📝 AI documentation and protocol templates for development guidance
- ✨ Comprehensive test suite including email styling tests
- 🔧 Project configuration with pyproject.toml and dependency management
- ✨ Authentication system with device flow support
- ✨ Multi-account management capabilities
- ✨ Unified search across Microsoft 365 resources
- ✨ Calendar event management with recurring events support
- ✨ Contact management functionality
- ✨ OneDrive file operations
- ✨ Email attachment handling

### Changed
- 🔀 Unified dev and master branches with consistent Claude Code infrastructure
- ♻️ Improved API structure and consolidated functionality
- 📝 Enhanced documentation with clear setup and usage instructions

### Fixed
- 🐛 HTML email rendering and recipient formatting issues
- 🐛 Authentication script environment loading
- 🐛 MSAL field name variations handling
- 🐛 Integration test robustness improvements
- 🐛 Include_body parameter in read_emails tool
- 🐛 Various API endpoint and authentication issues

### Removed
- 🔥 Obsolete configuration files
- 🔥 Legacy API endpoints and deprecated code
- 🔥 Redundant AI documentation files from initial structure

### Security
- 🔒 Secure token caching implementation
- 🔒 Environment-based client ID configuration
- 🔒 OAuth2 device flow authentication

[Unreleased]: https://github.com/org/repo/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/org/repo/releases/tag/v0.2.0
[0.1.0]: https://github.com/AojdevStudio/microsoft-mcp/releases/tag/v0.1.0