"""
CSS Inliner for email client compatibility
Converts CSS classes to inline styles for better email client support
"""

import re
from typing import Dict, Optional
from xml.etree import ElementTree as ET


def parse_css(css: str) -> Dict[str, Dict[str, str]]:
    """Parse CSS string into a dictionary of selectors and their properties"""
    css_rules = {}
    
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Remove media queries (they'll be handled separately)
    css = re.sub(r'@media[^{]+{[^{}]*{[^}]*}[^}]*}', '', css, flags=re.DOTALL)
    
    # Parse CSS rules
    pattern = r'([^{]+)\s*{\s*([^}]+)\s*}'
    matches = re.findall(pattern, css)
    
    for selector, properties in matches:
        selector = selector.strip()
        prop_dict = {}
        
        # Parse properties
        props = properties.strip().split(';')
        for prop in props:
            if ':' in prop:
                key, value = prop.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Remove !important as it's not needed in inline styles
                value = value.replace('!important', '').strip()
                prop_dict[key] = value
        
        if prop_dict:
            css_rules[selector] = prop_dict
    
    return css_rules


def apply_css_to_element(element: ET.Element, css_rules: Dict[str, Dict[str, str]], theme_vars: Optional[Dict[str, str]] = None):
    """Apply CSS rules to an element based on its classes"""
    classes = element.get('class', '').split()
    existing_style = element.get('style', '')
    
    # Parse existing inline styles
    existing_props = {}
    if existing_style:
        for prop in existing_style.split(';'):
            if ':' in prop:
                key, value = prop.split(':', 1)
                existing_props[key.strip()] = value.strip()
    
    # Apply CSS rules for each class
    new_props = existing_props.copy()
    for class_name in classes:
        class_selector = f'.{class_name}'
        if class_selector in css_rules:
            for prop, value in css_rules[class_selector].items():
                # Replace CSS variables with theme values
                if theme_vars and 'var(' in value:
                    for var_name, var_value in theme_vars.items():
                        value = value.replace(f'var({var_name})', var_value)
                new_props[prop] = value
    
    # Filter out incompatible properties for email clients
    incompatible_props = [
        'display: flex', 'display: grid', 'position: fixed', 'position: absolute',
        'transform', 'animation', 'transition'
    ]
    
    filtered_props = {}
    for prop, value in new_props.items():
        full_prop = f'{prop}: {value}'
        if not any(incompat in full_prop for incompat in incompatible_props):
            filtered_props[prop] = value
    
    # Build new style string
    if filtered_props:
        style_parts = [f'{k}: {v}' for k, v in filtered_props.items()]
        element.set('style', '; '.join(style_parts))
    
    # Remove class attribute
    if 'class' in element.attrib:
        del element.attrib['class']


def inline_css(html: str, css: str, theme_vars: Optional[Dict[str, str]] = None) -> str:
    """
    Convert CSS classes to inline styles in HTML
    
    Args:
        html: HTML content with class attributes
        css: CSS rules to apply
        theme_vars: Optional theme variables to replace
    
    Returns:
        HTML with inline styles and no class attributes
    """
    # Parse CSS
    css_rules = parse_css(css)
    
    # Parse HTML (wrap in root element if needed)
    if not html.strip().startswith('<html'):
        html = f'<html><body>{html}</body></html>'
    
    try:
        # Parse as HTML-like XML
        # First, fix common HTML issues for XML parsing
        html = html.replace('<br>', '<br/>')
        html = html.replace('<hr>', '<hr/>')
        html = html.replace('<img ', '<img ')  # Images should be self-closing
        html = re.sub(r'<img([^>]+)(?<!/)>', r'<img\1/>', html)
        
        root = ET.fromstring(html)
    except ET.ParseError:
        # If parsing fails, return original HTML
        return html
    
    # Apply styles to all elements with classes
    for element in root.iter():
        if element.get('class'):
            apply_css_to_element(element, css_rules, theme_vars)
    
    # Convert back to string
    result = ET.tostring(root, encoding='unicode', method='html')
    
    # Clean up the output
    result = result.replace('&lt;', '<').replace('&gt;', '>')
    
    return result


def process_media_queries(css: str) -> str:
    """Extract and preserve media queries in a style tag"""
    media_queries = re.findall(r'(@media[^{]+{[^{}]*{[^}]*}[^}]*})', css, flags=re.DOTALL)
    
    if media_queries:
        return '<style>' + '\n'.join(media_queries) + '</style>'
    return ''


def minify_css(css: str) -> str:
    """Minify CSS by removing unnecessary whitespace"""
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Remove excessive whitespace
    css = re.sub(r'\s+', ' ', css)
    # Remove spaces around punctuation
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    return css.strip()


def remove_unused_css(html: str, css: str) -> str:
    """Remove CSS rules that don't match any elements in the HTML"""
    used_classes = set()
    
    # Find all classes used in HTML
    class_pattern = r'class=["\']([^"\']+)["\']'
    matches = re.findall(class_pattern, html)
    for match in matches:
        used_classes.update(match.split())
    
    # Parse CSS and keep only used rules
    css_rules = parse_css(css)
    filtered_css = []
    
    for selector, properties in css_rules.items():
        # Check if selector is used
        if selector.startswith('.'):
            class_name = selector[1:].split(':')[0].split(' ')[0]
            if class_name in used_classes:
                props_str = '; '.join([f'{k}: {v}' for k, v in properties.items()])
                filtered_css.append(f'{selector} {{ {props_str} }}')
    
    return '\n'.join(filtered_css)


def get_css_size(css: str) -> int:
    """Get the size of CSS in bytes"""
    return len(css.encode('utf-8'))

def optimize_css_size(css: str, max_size: int = 50000) -> str:
    """Optimize CSS to fit within size limits"""
    # First try to minify
    minified = minify_css(css)
    
    if len(minified.encode('utf-8')) <= max_size:
        return minified
    
    # If still too large, remove non-essential properties
    # This is a simple implementation - can be made more sophisticated
    lines = minified.split('\n')
    essential_lines = []
    
    for line in lines:
        # Keep critical styling
        if any(prop in line.lower() for prop in ['color:', 'background:', 'font-size:', 'display:', 'width:', 'height:']):
            essential_lines.append(line)
    
    optimized = '\n'.join(essential_lines)
    
    # If still too large, truncate
    if len(optimized.encode('utf-8')) > max_size:
        optimized = optimized[:max_size]
    
    return optimized