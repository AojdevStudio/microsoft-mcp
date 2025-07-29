# KamDental Email Framework Guide

## Overview

The KamDental Email Framework is a professional email styling system designed to create consistent, beautiful, and responsive emails across all KamDental practices. It provides a comprehensive solution for automated email communications with built-in themes, templates, and Microsoft Graph integration.

## Key Features

- **Professional Templates**: Pre-built templates for practice reports, executive summaries, provider updates, and alerts
- **Multi-Theme Support**: Location-specific themes (Baytown, Humble) and executive styling
- **Email Client Compatibility**: Optimized for 95%+ email clients including Outlook, Gmail, Apple Mail
- **Performance Optimized**: Sub-2 second rendering with <100KB total size
- **WCAG 2.1 AA Compliant**: Accessible design with proper contrast and semantic HTML
- **Mobile Responsive**: Fully responsive design for iOS and Android email apps
- **Microsoft Graph Integration**: Seamless integration with Office 365 email sending

## Quick Start

### Basic Usage

```python
from microsoft_mcp.email_framework import render_email

# Send a practice report
html = render_email(
    "practice_report",
    {
        "location": "Baytown",
        "period": "January 2024",
        "financial_data": {
            "production": {"value": 285000, "goal": 300000},
            "collections": {"value": 270000, "ratio": 0.947},
            "case_acceptance": {"value": 0.72, "goal": 0.75},
            "call_answer_rate": {"value": 0.91, "goal": 0.95}
        },
        "providers": [
            {
                "name": "Dr. Sarah Johnson",
                "role": "General Dentist",
                "production": 125000,
                "goal_percentage": 1.04
            }
        ]
    }
)
```

### Using MCP Tools

```python
# Send practice report via MCP
result = await send_practice_report(
    account_id="default",
    to="manager@kamdental.com",
    subject="Baytown Practice Report - January 2024",
    location="Baytown",
    financial_data={...},
    provider_data=[...],
    period="January 2024",
    alerts=[...],
    recommendations=[...]
)
```

## Template Types

### 1. Practice Report Template
Monthly performance reports for individual practice locations.

**Required Data:**
- `location`: Practice location name
- `financial_data`: Production, collections, case acceptance, call answer rate
- `providers`: List of provider performance data

**Optional Data:**
- `period`: Reporting period
- `alerts`: Performance alerts
- `recommendations`: Action items

### 2. Executive Summary Template
Multi-location overview for executive team.

**Required Data:**
- `locations_data`: List of location performance metrics
- `period`: Reporting period

**Optional Data:**
- `key_insights`: Executive-level insights
- `subject`: Custom subject line

### 3. Provider Update Template
Individual provider performance updates.

**Required Data:**
- `provider_name`: Provider's name
- `performance_data`: Performance metrics

**Optional Data:**
- `period`: Reporting period
- `highlights`: Achievement highlights
- `recommendations`: Improvement suggestions

### 4. Alert Notification Template
Urgent notifications and alerts.

**Required Data:**
- `alert_type`: Type of alert (info, warning, danger, critical)
- `title`: Alert title
- `message`: Alert message

**Optional Data:**
- `urgency`: Urgency level
- `impact`: Business impact
- `recommended_actions`: Action items

## Theme System

### Automatic Theme Selection

The framework automatically selects the appropriate theme based on:

1. **Location**: "Baytown" or "Humble" in location field
2. **Recipient**: Executive email addresses get executive theme
3. **Level**: `recipient_level: "executive"` triggers executive theme
4. **Explicit**: `theme` field in data overrides automatic selection

### Available Themes

#### Baytown Theme
- Primary: Professional blue (#2B6CB0)
- Clean, modern design
- Default theme for Baytown location

#### Humble Theme
- Primary: Fresh green (#48BB78)
- Natural, approachable design
- Default theme for Humble location

#### Executive Theme
- Primary: Sophisticated dark (#2D3748)
- Elegant, minimal design
- Automatic for executive recipients

## CSS Framework Architecture

### Modular Structure
```
email_framework/
├── css/
│   ├── base.py          # Foundation styles
│   ├── components.py    # UI components
│   ├── themes.py        # Theme definitions
│   ├── utilities.py     # Utility classes
│   └── email_compatibility.py  # Client fixes
├── templates/
│   ├── base.py          # Base template class
│   ├── practice_report.py
│   ├── executive_summary.py
│   ├── provider_update.py
│   └── alert_notification.py
├── css_inliner.py       # CSS inlining engine
├── renderer.py          # Template renderer
└── validators.py        # Data validation
```

### Component Library

- **Metric Cards**: Visual KPI displays
- **Data Tables**: Responsive tables
- **Alerts**: Notification components
- **Buttons**: Call-to-action elements
- **Provider Cards**: Performance summaries
- **Recommendations**: Action item displays

## Email Client Compatibility

### Supported Clients (95%+)
- ✅ Outlook (2013, 2016, 2019, 365)
- ✅ Gmail (Web, iOS, Android)
- ✅ Apple Mail (macOS, iOS)
- ✅ Yahoo Mail
- ✅ Outlook.com
- ✅ Android Mail
- ✅ Samsung Mail

### Compatibility Features
- Table-based layouts for Outlook
- Inline CSS for Gmail
- Media queries for mobile
- Vendor prefixes for older clients
- Fallback fonts and colors

## Performance Optimization

### Rendering Performance
- Average render time: <0.5 seconds
- Max render time: <2 seconds
- Template caching enabled
- CSS minification

### Email Size
- CSS framework: ~30KB
- Average email: 60-80KB
- Maximum size: <100KB
- Optimized images

## Accessibility Features

### WCAG 2.1 AA Compliance
- Proper color contrast ratios
- Semantic HTML structure
- Alt text for images
- Readable font sizes
- Logical heading hierarchy

### Screen Reader Support
- Descriptive link text
- Table headers properly associated
- ARIA labels where needed
- Skip navigation links

## Data Validation

### Built-in Validators
- Email address validation
- Required field checking
- Data type validation
- Range validation for metrics
- Currency formatting
- Percentage handling

### Error Handling
```python
from microsoft_mcp.email_framework import EmailRenderer

renderer = EmailRenderer()
result = renderer.validate_template_data("practice_report", data)

if not result["valid"]:
    print("Validation errors:", result["errors"])
    print("Warnings:", result["warnings"])
```

## Best Practices

### 1. Data Preparation
- Always validate data before rendering
- Use consistent date formats
- Provide meaningful default values
- Include period information

### 2. Theme Selection
- Let automatic theme selection work
- Override only when necessary
- Test all themes during development
- Consider recipient preferences

### 3. Performance
- Cache rendered templates when possible
- Batch email sending operations
- Monitor rendering times
- Optimize data queries

### 4. Testing
- Test in multiple email clients
- Verify mobile responsiveness
- Check accessibility compliance
- Validate all data paths

## Troubleshooting

### Common Issues

**1. Template Not Rendering**
- Check required fields are present
- Validate data structure
- Ensure template name is correct

**2. Wrong Theme Applied**
- Check location field spelling
- Verify recipient email domain
- Look for explicit theme override

**3. Performance Issues**
- Check data size
- Enable template caching
- Profile rendering time
- Optimize data queries

**4. Email Client Issues**
- Test with inline styles enabled
- Check CSS compatibility
- Verify HTML structure
- Test actual email delivery

### Debug Mode

```python
# Enable detailed error messages
renderer = EmailRenderer()
stats = renderer.get_email_stats("practice_report", data)
print(f"Render stats: {stats}")

# Preview without sending
preview = renderer.preview_template("practice_report", theme="baytown")
```

## Migration Guide

### From Old Email System

1. **Update MCP tool calls**:
   ```python
   # Old
   await send_email(to, subject, body)
   
   # New
   await send_practice_report(
       account_id, to, subject, location,
       financial_data, provider_data
   )
   ```

2. **Data structure changes**:
   - Financial metrics now require `value` field
   - Providers need `name` and `production`
   - Alerts use `type`, `title`, `message`

3. **Theme handling**:
   - No need to specify theme manually
   - Location-based selection automatic
   - Executive detection built-in

## Advanced Usage

### Custom Styling

```python
# Get CSS for customization
template = PracticeReportTemplate()
css = template.get_css()

# Check email size
size_info = template.get_email_size()
print(f"CSS size: {size_info['css_size_kb']}KB")
```

### Template Extension

```python
from microsoft_mcp.email_framework.templates.base import EmailTemplate

class CustomTemplate(EmailTemplate):
    def get_template_name(self):
        return "Custom Report"
    
    def validate_data(self, data):
        # Custom validation
        pass
    
    def _get_template_html(self, data):
        # Custom HTML generation
        return self.build_metric_card(
            "Custom Metric",
            self.format_currency(data["value"])
        )
```

### Batch Processing

```python
# Process multiple emails efficiently
renderer = EmailRenderer()

for location in locations:
    data = prepare_data(location)
    html = renderer.render("practice_report", data)
    # Send email...
```

## Support

For questions or issues:
1. Check this guide first
2. Review error messages carefully
3. Test with sample data
4. Contact the development team

## Version History

- **v1.0.0** - Initial release with 4 templates
- **v1.1.0** - Added mobile responsiveness
- **v1.2.0** - Enhanced accessibility features
- **v1.3.0** - Performance optimizations