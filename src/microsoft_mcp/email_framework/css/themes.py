"""
Theme system for KamDental email templates
Provides color schemes and visual styles for different practice locations
"""

from typing import Dict


THEME_REGISTRY: Dict[str, Dict[str, str]] = {
    "baytown": {
        "primary": "#2B6CB0",
        "secondary": "#4A90E2",
        "accent": "#667eea",
        "success": "#38A169",
        "warning": "#D69E2E",
        "danger": "#E53E3E",
        "text": "#333333",
        "text-light": "#718096",
        "bg": "#FFFFFF",
        "bg-light": "#F7FAFC",
        "bg-accent": "#EBF4FF",
        "border": "#E2E8F0",
        "border-light": "#EDF2F7",
    },
    "humble": {
        "primary": "#48BB78",
        "secondary": "#68D391",
        "accent": "#38A169",
        "success": "#22543D",
        "warning": "#D69E2E",
        "danger": "#E53E3E",
        "text": "#2D3748",
        "text-light": "#4A5568",
        "bg": "#FFFFFF",
        "bg-light": "#F0FFF4",
        "bg-accent": "#E6FFFA",
        "border": "#9AE6B4",
        "border-light": "#C6F6D5",
    },
    "executive": {
        "primary": "#2D3748",
        "secondary": "#4A5568",
        "accent": "#805AD5",
        "success": "#38A169",
        "warning": "#D69E2E",
        "danger": "#E53E3E",
        "text": "#1A202C",
        "text-light": "#4A5568",
        "bg": "#FFFFFF",
        "bg-light": "#F7FAFC",
        "bg-accent": "#FAF5FF",
        "border": "#CBD5E0",
        "border-light": "#E2E8F0",
    },
}


def get_theme_styles(theme_name: str = "baytown") -> str:
    """
    Get CSS styles for a specific theme
    
    Args:
        theme_name: Name of the theme (baytown, humble, executive)
        
    Returns:
        CSS string with theme-specific styles
    """
    if theme_name not in THEME_REGISTRY:
        theme_name = "baytown"
        
    theme = THEME_REGISTRY[theme_name]
    
    return f"""
    /* Theme: {theme_name.title()} */
    
    /* Text Colors */
    .text-primary {{ color: {theme['primary']} !important; }}
    .text-secondary {{ color: {theme['secondary']} !important; }}
    .text-accent {{ color: {theme['accent']} !important; }}
    .text-success {{ color: {theme['success']} !important; }}
    .text-warning {{ color: {theme['warning']} !important; }}
    .text-danger {{ color: {theme['danger']} !important; }}
    .text-light {{ color: {theme['text-light']} !important; }}
    
    /* Background Colors */
    .bg-primary {{ background-color: {theme['primary']} !important; }}
    .bg-secondary {{ background-color: {theme['secondary']} !important; }}
    .bg-accent {{ background-color: {theme['accent']} !important; }}
    .bg-success {{ background-color: {theme['success']} !important; }}
    .bg-warning {{ background-color: {theme['warning']} !important; }}
    .bg-danger {{ background-color: {theme['danger']} !important; }}
    .bg-light {{ background-color: {theme['bg-light']} !important; }}
    .bg-accent-light {{ background-color: {theme['bg-accent']} !important; }}
    
    /* Border Colors */
    .border-primary {{ border-color: {theme['primary']} !important; }}
    .border-secondary {{ border-color: {theme['secondary']} !important; }}
    .border-light {{ border-color: {theme['border-light']} !important; }}
    
    /* Component Theme Overrides */
    .header {{
        border-bottom: 3px solid {theme['primary']};
        padding-bottom: 20px;
        margin-bottom: 30px;
    }}
    
    .header h1 {{
        color: {theme['primary']};
    }}
    
    .metric-card {{
        background-color: {theme['bg-light']};
        border: 1px solid {theme['border']};
    }}
    
    .metric-value {{
        color: {theme['text']};
    }}
    
    .metric-label {{
        color: {theme['text-light']};
    }}
    
    .alert {{
        border-left: 4px solid {theme['warning']};
        background-color: {theme['bg-light']};
    }}
    
    .alert-danger {{
        border-left-color: {theme['danger']};
        background-color: #FFF5F5;
    }}
    
    .alert-success {{
        border-left-color: {theme['success']};
        background-color: #F0FFF4;
    }}
    
    .button-primary {{
        background-color: {theme['primary']};
        color: #ffffff;
    }}
    
    .button-secondary {{
        background-color: {theme['secondary']};
        color: #ffffff;
    }}
    
    .section-header {{
        color: {theme['primary']};
        border-bottom: 2px solid {theme['border']};
    }}
    
    .footer {{
        border-top: 1px solid {theme['border']};
        color: {theme['text-light']};
    }}
    
    /* Status Colors */
    .status-behind {{ color: {theme['danger']} !important; }}
    .status-warning {{ color: {theme['warning']} !important; }}
    .status-ahead {{ color: {theme['success']} !important; }}
    .status-normal {{ color: {theme['text']} !important; }}
    """


def get_theme_variables(theme_name: str = "baytown") -> Dict[str, str]:
    """
    Get theme variables as a dictionary for CSS variable replacement
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        Dictionary of CSS variable names to values
    """
    if theme_name not in THEME_REGISTRY:
        theme_name = "baytown"
        
    theme = THEME_REGISTRY[theme_name]
    
    # Convert to CSS variable format
    variables = {}
    for key, value in theme.items():
        var_name = f"--{key}"
        variables[var_name] = value
        
    return variables