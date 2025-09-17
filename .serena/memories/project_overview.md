# Microsoft MCP Project Overview

## Purpose
The Microsoft MCP (Model Context Protocol) server is a comprehensive AI assistant toolkit that provides access to Microsoft Graph API for Outlook, Calendar, OneDrive, and Contacts. It enables natural language automation of Microsoft 365 services through conversational interfaces.

## Key Features
- **Email Management**: Read, send, reply, manage attachments, organize folders
- **Professional Email Templates**: KamDental-branded templates with automatic theme selection
- **Calendar Intelligence**: Create, update, check availability, respond to invitations
- **OneDrive Files**: Upload, download, browse with pagination
- **Contacts**: Search and list contacts from address book
- **Multi-Account Support**: Support for multiple Microsoft accounts (personal, work, school)
- **Unified Search**: Search across emails, files, events, and people

## Architecture
Nuclear-simplified architecture with 5 focused tools:
- `email_tool.py` - Email operations (list, send, reply, draft, delete)
- `calendar_tool.py` - Calendar operations 
- `contact_tool.py` - Contact management
- `file_tool.py` - OneDrive file operations
- `auth_tool.py` - Authentication management

Action-based routing pattern: `tool(account_id, action, data, options)`

## Current Status
- Version 0.2.1 (Beta)
- Nuclear simplification completed (reduced from 63k tokens to 5 focused tools)
- Critical pagination bugs fixed (Dec 2024)
- Professional email framework preserved as utilities
- Multi-account support functional across all Microsoft 365 services