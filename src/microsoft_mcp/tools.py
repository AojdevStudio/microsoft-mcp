"""Microsoft MCP Tools - Nuclear Simplified Architecture

5 focused tools replacing 63k token unified monster:
- email_operations: Email management  
- calendar_operations: Calendar management
- file_operations: OneDrive file management  
- contact_operations: Contact management
- auth_operations: Authentication management

Each tool provides action-based interface with direct Graph API integration.
No compatibility layers, no migration framework - pure nuclear simplification.
"""

from fastmcp import FastMCP

# Import focused tool functions
from .email_tool import email_operations
from .calendar_tool import calendar_operations
from .file_tool import file_operations
from .contact_tool import contact_operations
from .auth_tool import auth_operations

mcp = FastMCP("microsoft-mcp")

# Register 5 focused tools with FastMCP
mcp.tool(email_operations)
mcp.tool(calendar_operations)
mcp.tool(file_operations)
mcp.tool(contact_operations)
mcp.tool(auth_operations)

