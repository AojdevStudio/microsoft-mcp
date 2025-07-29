# KamDental Email Framework - Implementation Plan

## Phase 2: Design & Architecture (Current Phase)

### CSS Framework Architecture

#### Directory Structure
```
src/microsoft_mcp/email_framework/
├── __init__.py
├── core/
│   ├── variables.css      # Design tokens
│   ├── base.css          # Reset and foundational styles
│   └── utilities.css     # Helper classes
├── components/
│   ├── metrics.css       # Metric cards and grids
│   ├── providers.css     # Provider performance lists
│   ├── alerts.css        # Alert banners
│   └── recommendations.css # Action item cards
├── themes/
│   ├── baytown.css       # Blue theme (#2B6CB0)
│   ├── humble.css        # Purple theme (#6B46C1)
│   └── executive.css     # Dark theme (#1A202C)
└── kamdental-email.css   # Compiled framework
```

#### CSS Variables Design
```css
:root {
  /* Colors */
  --primary: #2B6CB0;
  --success: #38A169;
  --warning: #D69E2E;
  --danger: #E53E3E;
  --neutral: #4A5568;
  --light-bg: #F7FAFC;
  --border: #E2E8F0;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-base: 16px;
  --line-height: 1.6;
  
  /* Spacing */
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Borders */
  --radius: 8px;
  --border-width: 1px;
}
```

### Template System Architecture

#### Base Template Class
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import jinja2
from .css_inliner import inline_css
from .validator import validate_email_data

class EmailTemplate(ABC):
    def __init__(self, theme: str = "baytown"):
        self.theme = theme
        self.jinja_env = self._setup_jinja_env()
        
    def _setup_jinja_env(self) -> jinja2.Environment:
        """Set up Jinja2 environment with custom filters"""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates/html'),
            autoescape=True
        )
        env.filters['currency'] = self._format_currency
        env.filters['percentage'] = self._format_percentage
        return env
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Return the HTML template filename"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate input data for the template"""
        pass
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render the email with inline CSS"""
        self.validate_data(data)
        
        # Load theme CSS
        theme_css = self._load_theme_css()
        
        # Render HTML template
        template = self.jinja_env.get_template(self.get_template_name())
        html = template.render(data=data, theme=self.theme)
        
        # Inline CSS for email compatibility
        return inline_css(html, theme_css)
```

#### Specialized Templates
1. **PracticeReportTemplate**: Monthly/weekly practice performance
2. **ExecutiveSummaryTemplate**: Multi-location overview
3. **ProviderUpdateTemplate**: Individual provider performance
4. **AlertNotificationTemplate**: Critical alerts and notifications

### MCP Tool Integration Plan

#### New Tools Structure
```python
@mcp.tool
def send_practice_report(
    account_id: str,
    to: str,
    subject: str,
    location: str,  # "baytown" or "humble"
    financial_data: dict,
    provider_data: list[dict],
    alerts: list[dict] = None,
    recommendations: list[dict] = None,
    cc: list[str] = None,
    bcc: list[str] = None
) -> dict[str, str]:
    """Send a professional practice report email with KamDental styling"""
    
    # Select theme based on location
    theme = location.lower() if location.lower() in ["baytown", "humble"] else "baytown"
    
    # Create template instance
    template = PracticeReportTemplate(theme=theme)
    
    # Prepare data
    data = {
        "location": location,
        "financial_data": financial_data,
        "providers": provider_data,
        "alerts": alerts or [],
        "recommendations": recommendations or []
    }
    
    # Render email body
    body = template.render(data)
    
    # Use existing send_email with rendered HTML
    return send_email(
        account_id=account_id,
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc
    )
```

### CSS Inliner Design

The CSS inliner will:
1. Parse CSS files and extract rules
2. Apply styles inline to HTML elements
3. Handle pseudo-classes and media queries appropriately
4. Optimize for email client compatibility

### Performance Optimization Strategy

1. **CSS Compilation**: Pre-compile theme CSS to reduce runtime processing
2. **Template Caching**: Cache compiled Jinja2 templates
3. **Lazy Loading**: Load CSS only when needed
4. **Size Optimization**: Minify CSS and remove unused styles

### Testing Strategy

#### Unit Tests
- Template rendering with various data inputs
- CSS inlining accuracy
- Theme selection logic
- Data validation

#### Integration Tests
- MCP tool functionality
- Email sending with styled content
- Multi-account support

#### Compatibility Tests
- Outlook 2016+ (desktop/mobile)
- Gmail (web/app)
- Apple Mail (macOS/iOS)
- Yahoo Mail

#### Performance Tests
- Render time < 2 seconds
- Framework size < 100KB
- Memory usage < 50MB

### Migration Plan

1. **Phase 1**: Add new tools alongside existing send_email
2. **Phase 2**: Update documentation with examples
3. **Phase 3**: Gradual adoption by operations team
4. **Phase 4**: Deprecate manual styling in favor of framework

### Risk Mitigation

1. **Email Client Compatibility**
   - Use table-based layouts for Outlook
   - Avoid unsupported CSS properties
   - Test extensively across clients

2. **Performance Impact**
   - Pre-compile CSS where possible
   - Implement caching strategies
   - Monitor render times

3. **Backward Compatibility**
   - Keep existing send_email function
   - Add new tools without breaking changes
   - Provide migration guide