"""
Base CSS styles for email templates
Foundation styles that work across all email clients
"""



def get_base_styles() -> str:
    """
    Get base CSS styles that form the foundation of all email templates.
    These styles are optimized for maximum email client compatibility.
    """
    return """
    /* Reset and Base Styles */
    body {
        margin: 0;
        padding: 0;
        width: 100% !important;
        min-width: 100%;
        -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #333333;
        background-color: #f5f5f5;
    }
    
    table {
        border-collapse: collapse;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
    }
    
    td {
        padding: 0;
    }
    
    img {
        border: 0;
        height: auto;
        line-height: 100%;
        outline: none;
        text-decoration: none;
        -ms-interpolation-mode: bicubic;
        display: block;
    }
    
    p, h1, h2, h3, h4, h5, h6 {
        margin: 0;
        padding: 0;
    }
    
    a {
        color: inherit;
        text-decoration: none;
    }
    
    /* Container Styles */
    .email-wrapper {
        width: 100%;
        background-color: #f5f5f5;
        padding: 20px 0;
    }
    
    .email-container {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .email-content {
        padding: 40px;
    }
    
    /* Typography Base */
    h1 {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 16px;
    }
    
    h2 {
        font-size: 24px;
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 12px;
    }
    
    h3 {
        font-size: 20px;
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 10px;
    }
    
    p {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    
    /* Responsive Base */
    @media only screen and (max-width: 600px) {
        .email-wrapper {
            padding: 10px 0;
        }
        
        .email-content {
            padding: 20px;
        }
        
        h1 {
            font-size: 24px;
        }
        
        h2 {
            font-size: 20px;
        }
        
        h3 {
            font-size: 18px;
        }
    }
    """


def get_table_base_styles() -> str:
    """Get base styles for tables that work in all email clients"""
    return """
    /* Table Base Styles */
    table {
        width: 100%;
        border-spacing: 0;
        border-collapse: collapse;
    }
    
    th, td {
        text-align: left;
        padding: 12px;
    }
    
    th {
        font-weight: 600;
        border-bottom: 2px solid #e2e8f0;
    }
    
    td {
        border-bottom: 1px solid #e2e8f0;
    }
    
    tr:last-child td {
        border-bottom: none;
    }
    
    /* Responsive Tables */
    @media only screen and (max-width: 600px) {
        table {
            font-size: 14px;
        }
        
        th, td {
            padding: 8px;
        }
    }
    """


def get_spacing_styles() -> str:
    """Get spacing utility styles"""
    return """
    /* Spacing Utilities */
    .mt-0 { margin-top: 0 !important; }
    .mt-1 { margin-top: 4px !important; }
    .mt-2 { margin-top: 8px !important; }
    .mt-3 { margin-top: 12px !important; }
    .mt-4 { margin-top: 16px !important; }
    .mt-5 { margin-top: 20px !important; }
    
    .mb-0 { margin-bottom: 0 !important; }
    .mb-1 { margin-bottom: 4px !important; }
    .mb-2 { margin-bottom: 8px !important; }
    .mb-3 { margin-bottom: 12px !important; }
    .mb-4 { margin-bottom: 16px !important; }
    .mb-5 { margin-bottom: 20px !important; }
    
    .pt-0 { padding-top: 0 !important; }
    .pt-1 { padding-top: 4px !important; }
    .pt-2 { padding-top: 8px !important; }
    .pt-3 { padding-top: 12px !important; }
    .pt-4 { padding-top: 16px !important; }
    .pt-5 { padding-top: 20px !important; }
    
    .pb-0 { padding-bottom: 0 !important; }
    .pb-1 { padding-bottom: 4px !important; }
    .pb-2 { padding-bottom: 8px !important; }
    .pb-3 { padding-bottom: 12px !important; }
    .pb-4 { padding-bottom: 16px !important; }
    .pb-5 { padding-bottom: 20px !important; }
    """