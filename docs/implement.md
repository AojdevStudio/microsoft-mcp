## Email Formatting Fix for Microsoft MCP Tool

### **Objective**
Fix the email draft creation functionality in the Microsoft MCP tool where CSS gradients and certain styles are not rendering properly in Outlook, causing white text to appear on white backgrounds and making content invisible.

### **Problem Description**
The current email generation creates HTML emails with CSS styles that don't render correctly in Microsoft Outlook. Specifically:
- CSS gradients in headers are not supported
- White text becomes invisible when background colors don't render
- Some CSS properties are being ignored by email clients

### **Files to Modify**
Look for the Microsoft MCP email creation functionality, likely in:
- `microsoft-mcp:create_email_draft` function
- `microsoft-mcp:send_email` function
- Any email template or HTML generation code

### **Required Changes**

#### 1. **Replace CSS Gradients with Solid Colors**
Change this:
```css
.header { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    color: white; 
}
```

To this:
```css
.header { 
    background-color: #667eea; 
    color: white; 
}
```

#### 2. **Convert Critical Styles to Inline Styles**
For email client compatibility, convert CSS classes to inline styles for these elements:
- `.header` sections
- `.section` backgrounds
- `.highlight` boxes
- Any element with background colors

Example conversion:
```html
<!-- From this -->
<div class="header">

<!-- To this -->
<div style="background-color: #667eea; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
```

#### 3. **Add Fallback Colors**
For any remaining CSS classes, add fallback background colors:
```css
.section { 
    background-color: #f8f9fa; /* Fallback solid color */
    background: #f8f9fa; /* Keep existing if it works */
}
```

#### 4. **Email-Safe Color Combinations**
Ensure all text has sufficient contrast:
- Dark text (#333) on light backgrounds (#f8f9fa, #e3f2fd)
- White text (#ffffff) only on dark backgrounds (#667eea, #28a745)
- Never rely on gradients for text readability

#### 5. **Table-Based Layout Option** (If needed)
Consider converting div-based layouts to table-based for maximum email client compatibility:
```html
<table width="100%" cellpadding="0" cellspacing="0">
    <tr>
        <td style="background-color: #667eea; color: white; padding: 20px;">
            Header content
        </td>
    </tr>
</table>
```

### **Testing Requirements**
After making changes:
1. Test email draft creation generates properly formatted HTML
2. Verify all text is visible (no white-on-white issues)
3. Ensure styling works across different email clients
4. Maintain professional appearance and readability

### **Specific Style Mappings**
Replace these problematic styles:

| Current Class | New Inline Style |
|---------------|------------------|
| `.header` | `style="background-color: #667eea; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;"` |
| `.section` | `style="background-color: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea;"` |
| `.highlight` | `style="background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin: 10px 0;"` |
| `.strong-yes` | `style="background-color: #28a745; color: white; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 18px;"` |

### **Priority**
High - This affects email readability and professional communication.

### **Expected Outcome**
Email drafts should render correctly in all major email clients, especially Microsoft Outlook, with all text clearly visible and styling preserved.

---