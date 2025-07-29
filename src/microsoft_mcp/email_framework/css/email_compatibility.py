"""
Email client compatibility fixes and optimizations
Ensures CSS works across all major email clients
"""

from typing import Dict, List, Tuple


def apply_email_compatibility_fixes(css: str) -> str:
    """
    Apply email client compatibility fixes to CSS
    
    Args:
        css: Original CSS string
        
    Returns:
        Email-client compatible CSS
    """
    # Apply all compatibility transformations
    css = fix_outlook_specific_issues(css)
    css = fix_gmail_specific_issues(css)
    css = fix_apple_mail_issues(css)
    css = add_vendor_prefixes(css)
    css = convert_modern_css_to_legacy(css)
    css = add_important_flags(css)
    
    return css


def fix_outlook_specific_issues(css: str) -> str:
    """Fix CSS issues specific to Outlook"""
    # Outlook doesn't support max-width properly
    css = css.replace('max-width:', 'width:')
    
    # Add Outlook conditional CSS
    outlook_fixes = """
    /* Outlook Specific Fixes */
    .outlook-spacing {
        mso-line-height-rule: exactly;
    }
    
    table {
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
    }
    
    img {
        -ms-interpolation-mode: bicubic;
    }
    
    .outlook-hide {
        mso-hide: all;
    }
    """
    
    return css + outlook_fixes


def fix_gmail_specific_issues(css: str) -> str:
    """Fix CSS issues specific to Gmail"""
    # Gmail strips out <style> tags in some cases, so we need inline styles
    # This is handled by the CSS inliner
    
    # Gmail specific fixes
    gmail_fixes = """
    /* Gmail Specific Fixes */
    u ~ div .gmail-hide {
        display: none !important;
    }
    
    /* Force Gmail to display emails at full width */
    .gmail-width {
        min-width: 100vw;
    }
    """
    
    return css + gmail_fixes


def fix_apple_mail_issues(css: str) -> str:
    """Fix CSS issues specific to Apple Mail"""
    apple_fixes = """
    /* Apple Mail Specific Fixes */
    @media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
        .apple-mail-full-width {
            width: 100% !important;
        }
    }
    
    /* Fix auto-scaling in iOS Mail */
    body[yahoo] {
        width: 100% !important;
        min-width: 100% !important;
    }
    """
    
    return css + apple_fixes


def add_vendor_prefixes(css: str) -> str:
    """Add vendor prefixes for better compatibility"""
    prefixes = {
        'border-radius': ['-webkit-border-radius', '-moz-border-radius'],
        'box-shadow': ['-webkit-box-shadow', '-moz-box-shadow'],
        'transform': ['-webkit-transform', '-ms-transform', '-moz-transform'],
        'transition': ['-webkit-transition', '-moz-transition', '-o-transition'],
    }
    
    for property_name, vendor_prefixes in prefixes.items():
        if property_name in css:
            # Find all instances of the property
            import re
            pattern = rf'({property_name}:\s*[^;]+;)'
            matches = re.findall(pattern, css)
            
            for match in matches:
                # Create vendor-prefixed versions
                prefixed_props = []
                for prefix in vendor_prefixes:
                    prefixed_props.append(match.replace(property_name, prefix))
                
                # Add prefixed properties before the standard property
                replacement = '\n    '.join(prefixed_props) + '\n    ' + match
                css = css.replace(match, replacement)
    
    return css


def convert_modern_css_to_legacy(css: str) -> str:
    """Convert modern CSS to legacy equivalents"""
    conversions = {
        # Flexbox to table
        'display: flex': 'display: table',
        'flex-direction: row': 'display: table-row',
        'flex-direction: column': 'display: table',
        'justify-content: center': 'text-align: center',
        'align-items: center': 'vertical-align: middle',
        
        # Grid to table
        'display: grid': 'display: table',
        
        # Modern units to legacy
        'rem': 'px',
        'vh': '%',
        'vw': '%',
        
        # CSS variables (handled separately by theme system)
        'var(--': 'var(--',  # Keep as-is, will be replaced by inliner
    }
    
    for modern, legacy in conversions.items():
        css = css.replace(modern, legacy)
    
    return css


def add_important_flags(css: str) -> str:
    """Add !important flags to critical properties"""
    critical_properties = [
        'width',
        'max-width',
        'min-width',
        'height',
        'margin',
        'padding',
        'border',
        'background-color',
        'color',
        'font-size',
        'line-height',
        'text-align',
    ]
    
    import re
    
    for prop in critical_properties:
        # Find properties that don't already have !important
        pattern = rf'({prop}:\s*[^;!]+)(;)'
        css = re.sub(pattern, r'\1 !important\2', css)
    
    return css


def get_email_client_compatibility_report() -> Dict[str, List[str]]:
    """Get compatibility report for major email clients"""
    return {
        "outlook": [
            "✅ Table-based layouts",
            "✅ Inline styles",
            "✅ Basic CSS properties",
            "⚠️ Limited max-width support",
            "⚠️ No CSS3 support",
            "❌ No media queries"
        ],
        "gmail": [
            "✅ Most CSS2 properties",
            "✅ Inline styles",
            "✅ Media queries (mobile app)",
            "⚠️ Strips some <style> tags",
            "⚠️ Limited pseudo-selector support",
            "❌ No negative margins"
        ],
        "apple_mail": [
            "✅ Full CSS2 support",
            "✅ Most CSS3 properties",
            "✅ Media queries",
            "✅ <style> tags",
            "⚠️ Auto-scaling on iOS",
            "✅ Dark mode support"
        ],
        "yahoo_mail": [
            "✅ Basic CSS support",
            "✅ Inline styles",
            "⚠️ Limited <style> support",
            "⚠️ Adds default styles",
            "❌ No CSS3 animations",
            "❌ Limited pseudo-selectors"
        ],
        "android_mail": [
            "✅ Good CSS support",
            "✅ Media queries",
            "✅ Most CSS3 properties",
            "⚠️ Varies by app version",
            "⚠️ Some rendering quirks",
            "✅ Dark mode support"
        ]
    }


def get_safe_css_properties() -> List[str]:
    """Get list of CSS properties safe for all email clients"""
    return [
        # Typography
        "font-family",
        "font-size",
        "font-weight",
        "font-style",
        "line-height",
        "text-align",
        "text-decoration",
        "color",
        
        # Box Model
        "width",
        "height",
        "margin",
        "padding",
        "border",
        "border-radius",  # With vendor prefixes
        
        # Background
        "background-color",
        "background-image",
        "background-repeat",
        "background-position",
        
        # Display
        "display",
        "visibility",
        "vertical-align",
        
        # Tables
        "border-collapse",
        "border-spacing",
        "table-layout",
        
        # Basic positioning
        "float",
        "clear",
        
        # Lists
        "list-style",
        "list-style-type",
    ]


def get_unsupported_properties() -> List[str]:
    """Get list of CSS properties to avoid in emails"""
    return [
        # Modern layout
        "display: flex",
        "display: grid",
        "position: fixed",
        "position: sticky",
        
        # Animations
        "animation",
        "transition",
        "transform",
        
        # Advanced selectors
        ":before",
        ":after",
        ":nth-child",
        ":not",
        
        # Modern properties
        "box-shadow",  # Limited support
        "text-shadow",  # Limited support
        "opacity",  # Use background-color instead
        "filter",
        
        # CSS variables (use theme system instead)
        "--custom-property",
    ]