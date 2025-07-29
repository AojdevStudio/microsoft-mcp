# FEATURE KamDental Email Framework

## Metadata
- **Priority:** High
- **Status:** Todo
- **Assignee:** AI Agent
- **Estimate:** 8 weeks / 32 story points
- **Issue ID:** ENG-001
- **Labels:** 
  - type:feature
  - priority:high
  - agent-ready
  - backend
  - email-framework

## Problem Statement

### What
Transform the Microsoft MCP server into a comprehensive email styling framework that produces consistently professional, branded reports for KamDental practice analytics with sub-30-second generation times.

### Why
Current email generation requires 30+ minutes of manual formatting, lacks brand consistency, and produces inconsistent professional appearance across different practice locations and report types. This inefficiency results in:
- 98% time waste on manual formatting
- Inconsistent brand representation
- Delayed communications to stakeholders
- Poor user experience for operations team

### Context
KamDental operates multiple practice locations (Baytown, Humble) requiring regular analytics reports to executives and operations teams. The existing Microsoft MCP server handles email delivery but lacks professional styling capabilities. A component-based CSS email framework will automate styling while maintaining brand consistency across all communications.

> **📋 Live Preview**: Working prototypes of all components and themes are available in [`docs/visual-mocks.html`](../visual-mocks.html)

## Acceptance Criteria
- [ ] **AC1:** CSS framework loads in <2 seconds with 95%+ email client compatibility
- [ ] **AC2:** Template system automatically selects appropriate theme based on recipient and content type with >95% accuracy
- [ ] **AC3:** All new MCP tools integrate seamlessly while maintaining backward compatibility
- [ ] **AC4:** Framework reduces email creation time from 30+ minutes to <30 seconds (98% improvement)
- [ ] **AC5:** 100% mobile responsiveness across iOS/Android email apps
- [ ] **AC6:** WCAG 2.1 AA accessibility compliance verified
- [ ] **AC7:** Framework size remains under 100KB total
- [ ] **AC8:** Executive signature integration works consistently across all templates

## Technical Requirements

### Implementation Notes
- Component-based CSS architecture with modular organization
- Template inheritance system supporting base classes and specialized implementations
- Integration with existing Microsoft MCP infrastructure and MSAL authentication
- Framework must maintain <100KB size with <2s render time
- Email client optimization for Outlook, Gmail, Apple Mail (95%+ compatibility)
- Three theme system: Baytown (blue), Humble (purple), Executive (dark/minimal)

### Core Features

#### 1. CSS Framework Foundation
**Framework Structure:**
```
src/microsoft_mcp/email_framework/
├── core/
│   ├── variables.css      # CSS custom properties
│   ├── base.css          # Reset and base styles
│   └── utilities.css     # Helper classes
├── components/
│   ├── metrics.css       # Metric cards and grids
│   ├── providers.css     # Provider performance lists
│   ├── alerts.css        # Alert banners
│   └── recommendations.css # Action item cards
├── themes/
│   ├── baytown.css       # Baytown theme
│   ├── humble.css        # Humble theme
│   └── executive.css     # Executive theme
└── templates/
    ├── practice-report.html
    ├── executive-summary.html
    └── provider-update.html
```

#### 2. Template System
**Template Classes:**
```python
class EmailTemplate:
    def __init__(self, theme: str = "baytown")
    def render(self, data: dict) -> str

class PracticeReportTemplate(EmailTemplate):
    def render(self, metrics: dict, providers: list, alerts: list) -> str

class ExecutiveSummaryTemplate(EmailTemplate):
    def render(self, locations: list, key_insights: list) -> str
```

**Data Structure:**
```json
{
  "email_type": "practice-report",
  "theme": "baytown", 
  "summary": "Performance summary text",
  "metrics": [{"label": "MTD Production", "value": "$143,343", "status": "behind"}],
  "alerts": [{"type": "critical", "icon": "🚨", "message": "Alert message"}],
  "recommendations": [{"priority": "IMMEDIATE", "title": "Action item"}],
  "providers": [{"name": "Dr. Name", "role": "Role", "production": "$Amount"}]
}
```

#### 3. MCP Tool Integration
**New Tools:**
```python
@mcp.tool
def send_practice_report(
    account_id: str, to: str, subject: str,
    financial_data: dict, theme: str = "auto"
) -> dict[str, str]

@mcp.tool  
def send_executive_summary(
    account_id: str, to: str,
    locations_data: list[dict], period: str = "MTD"
) -> dict[str, str]

@mcp.tool
def send_provider_update(
    account_id: str, to: str,
    provider_name: str, performance_data: dict
) -> dict[str, str]

@mcp.tool
def send_alert_notification(
    account_id: str, to: str,
    alert_type: str, message: str, urgency: str = "normal"
) -> dict[str, str]
```

#### 4. Advanced Features (Optional)
- Smart recommendations with AI-generated action items
- Performance trends using CSS/SVG visualizations  
- Customization system for brand elements
- Analytics integration for email performance tracking

### Integration Points
- **Microsoft Graph API**: Continue using existing endpoints for email delivery
- **MSAL Authentication**: Leverage existing authentication system
- **Multi-Account Support**: Maintain current account management
- **Data Flow**: Claude Analysis → Structured Data → MCP Tool → Framework → Email

### Performance Constraints
- Framework size: <100KB total
- Render time: <2 seconds
- Compilation time: <5 seconds
- Memory usage: <50MB during operation

### Testing Requirements
- [ ] **Unit Tests** - Framework: pytest, Coverage: 90%, Location: tests/email_framework/
- [ ] **Integration Tests** - Framework: pytest, Location: tests/integration/
- [ ] **E2E Tests** - Framework: Playwright, Location: tests/e2e/
- [ ] **Email Sending Robustness Tests** - Comprehensive testing of Microsoft Graph send_email functionality across multiple scenarios:
  - [ ] **Multi-Account Testing**: Verify email sending works across all authenticated Microsoft accounts
  - [ ] **Attachment Handling**: Test email sending with various attachment types and sizes (<3MB direct, >3MB chunked)
  - [ ] **Email Client Compatibility**: Verify sent emails render correctly in Outlook, Gmail, Apple Mail, Yahoo Mail
  - [ ] **Network Resilience**: Test email sending with network interruptions and retry logic
  - [ ] **Error Handling**: Validate proper error handling for invalid recipients, token expiration, rate limiting
  - [ ] **Bulk Email Testing**: Test sending multiple emails in sequence without failures
  - [ ] **HTML/Rich Content**: Verify complex HTML emails with styling render correctly when sent
  - [ ] **Authentication Edge Cases**: Test behavior with expired tokens, invalid accounts, permission changes
  - [ ] **Performance Testing**: Measure email sending latency and success rates under load
  - [ ] **Draft vs Direct Send**: Compare behavior between send_email (direct) and create_email_draft + send workflow

### Dependencies
- **Blockers:** Microsoft MCP server infrastructure must be operational
- **Related:** Visual mockups in docs/visual-mocks.html contain design specifications
- **Files to Modify:** 
  - src/microsoft_mcp/tools.py (add new MCP tools)
  - src/microsoft_mcp/ (add email_framework/ directory)
  - tests/ (add comprehensive test suite)

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Tests written and passing (per testing requirements)
- [ ] Documentation updated (README, API docs)
- [ ] Deployed to development environment
- [ ] Manual verification completed by operations team

## Agent Context

### Reference Materials
- **Design Specifications**: [`docs/visual-mocks.html`](../visual-mocks.html) - Complete visual mockups and component examples
- **Microsoft Graph API**: [Email API Documentation](https://docs.microsoft.com/en-us/graph/api/resources/message)
- **CSS Email Best Practices**: Email client compatibility patterns
- **Current MCP Tools**: src/microsoft_mcp/tools.py for integration patterns

### Visual Design System
**Themes:**
- **Baytown**: Professional Blue (#1B365D), structured layout
- **Humble**: Professional Purple (#6A1B9A), friendly presentation  
- **Executive**: Dark Professional (#212121), minimal design

**Components:**
- **Metric Cards**: Responsive grid, status colors (red/yellow/green/blue)
- **Alert Banners**: Full-width, colored borders, prominent typography
- **Provider Lists**: Card-based, color-coded status badges

### Integration Points
- **Database**: Practice analytics data structure (JSON format)
- **API Endpoints**: Microsoft Graph /sendMail endpoint
- **UI Components**: Email templates with CSS framework
- **External Services**: Microsoft Graph API, MSAL authentication

## Validation Steps

### Automated Verification
- [ ] Build pipeline passes (CSS compilation, Python linting)
- [ ] All tests green (unit, integration, e2e)
- [ ] Code quality checks pass (ruff, pyright)
- [ ] Security scans clean (no XSS vulnerabilities)

### Manual Verification
1. **Framework Loading**: Verify CSS framework loads in <2 seconds across email clients
2. **Template Rendering**: Test template selection accuracy with sample practice data
3. **Mobile Responsiveness**: Confirm email display on iOS/Android email apps
4. **Brand Compliance**: Validate theme application matches KamDental branding
5. **Integration Testing**: Verify MCP tools work with existing authentication
6. **Performance Testing**: Confirm <30 second email generation end-to-end

## Agent Execution Record

### Branch Strategy
- **Name Format:** feature/ENG-001-kamdental-email-framework
- **Implementation Phases:**
  - feature/ENG-001-css-foundation (Weeks 1-2)
  - feature/ENG-001-template-system (Weeks 3-4)
  - feature/ENG-001-mcp-integration (Weeks 5-6)
  - feature/ENG-001-advanced-features (Weeks 7-8)

### PR Strategy
Link to this issue using "Fixes ENG-001" in PR description

### Implementation Approach
Phased implementation starting with CSS framework foundation, then template system, MCP integration, and finally advanced features. Each phase includes comprehensive testing and validation.

### Completion Notes
[To be filled during implementation]

### PR Integration
- **Magic Words:** Fixes ENG-001
- **Auto Close Trigger:** PR merge to main branch
- **Status Automation:** Issue will auto-move from 'In Progress' to 'Done'

### Debug References
[To be populated during implementation]

### Change Log
[Track changes made during implementation]

## Bot Automation Integration

### Branch Naming for Auto-Linking
- feature/ENG-001-css-framework-foundation
- feature/ENG-001-template-system-implementation
- feature/ENG-001-mcp-tool-integration

### PR Description Template
```markdown
## Description
Implement KamDental Email Framework phase [X]

**Linked Issues:**
- Fixes ENG-001

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Email client compatibility verified
```

---

## Additional Context

### Implementation Timeline
**Phase 1: CSS Framework Foundation (Week 1-2)**
- Create framework directory structure
- Implement core CSS architecture
- Build component CSS (metrics, providers, alerts)
- Create theme CSS files (Baytown, Humble, Executive)

**Phase 2: Template System (Week 3-4)**
- Design template base classes and inheritance
- Implement data processing pipeline
- Create template selection logic
- Build HTML template files

**Phase 3: MCP Tool Integration (Week 5-6)**
- Update existing email functions
- Implement new specialized MCP tools
- Integrate framework with MCP infrastructure
- Add automatic signature handling

**Phase 4: Advanced Features (Week 7-8)**
- Implement smart recommendations
- Add performance visualization
- Create customization system
- Performance optimization

### Risk Mitigation
**High Risk - Email Client Compatibility:**
- Mitigation: Comprehensive testing and fallback strategies

**Medium Risk - Performance Impact:**
- Mitigation: Size optimization and performance monitoring

**Medium Risk - User Adoption:**
- Mitigation: Training, gradual rollout, feedback integration

### Success Metrics
- 98% reduction in email creation time (30+ min → 30 sec)
- 95%+ email client compatibility
- 100% mobile responsiveness
- 90%+ code coverage
- 100% framework adoption by operations team

### Technical Architecture
```
Claude Analysis → Structured Data → MCP Tool → Framework Processing → Professional Email
```

### Component Specifications
**Metric Cards**: Responsive grid, status colors (red/yellow/green/blue)
**Alert Banners**: Full-width, colored borders, prominent typography  
**Provider Lists**: Card-based, color-coded status badges

### Email Client Support Matrix
| Client | Desktop | Mobile | Notes |
|--------|---------|--------|---------|
| Outlook 2016+ | ✅ Full | ✅ Full | Primary target |
| Gmail | ✅ Full | ✅ Full | Web and app |
| Apple Mail | ✅ Full | ✅ Full | macOS and iOS |
| Yahoo Mail | ✅ Limited | ✅ Limited | CSS limitations |

### Data Schema Example
```json
{
  "report_type": "practice-monthly",
  "location": "baytown",
  "period": "July 2025 MTD",
  "financial_metrics": {
    "production": {"value": 143343, "goal": 160000, "status": "behind"}
  },
  "alerts": [{
    "type": "critical",
    "title": "Phone Coverage Critical",
    "message": "Answer rate at 69.3% vs 85% goal"
  }]
}
```