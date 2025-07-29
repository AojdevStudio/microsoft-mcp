"""
Component styles for KamDental email templates
Reusable UI components optimized for email clients
"""


def get_component_styles() -> str:
    """
    Get CSS styles for all email components
    """
    return f"""
    {get_metric_card_styles()}
    {get_alert_styles()}
    {get_button_styles()}
    {get_table_styles()}
    {get_provider_card_styles()}
    {get_recommendation_styles()}
    {get_signature_styles()}
    """


def get_metric_card_styles() -> str:
    """Styles for metric display cards"""
    return """
    /* Metric Cards */
    .metric-card {
        background: #F7FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #718096;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    
    .metric-subtitle {
        font-size: 14px;
        color: #718096;
        margin-top: 4px;
    }
    
    .metric-trend {
        display: inline-block;
        font-size: 14px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-top: 8px;
    }
    
    .metric-trend.positive {
        background-color: #F0FFF4;
        color: #38A169;
    }
    
    .metric-trend.negative {
        background-color: #FFF5F5;
        color: #E53E3E;
    }
    
    /* Metric Grid */
    .metric-grid {
        width: 100%;
        margin-bottom: 30px;
    }
    
    .metric-row {
        display: table;
        width: 100%;
        margin-bottom: 15px;
    }
    
    .metric-col {
        display: table-cell;
        width: 48%;
        vertical-align: top;
    }
    
    .metric-col:first-child {
        padding-right: 2%;
    }
    
    @media only screen and (max-width: 600px) {
        .metric-row {
            display: block;
        }
        
        .metric-col {
            display: block;
            width: 100%;
            padding-right: 0 !important;
            margin-bottom: 15px;
        }
        
        .metric-value {
            font-size: 24px;
        }
    }
    """


def get_alert_styles() -> str:
    """Styles for alert notifications"""
    return """
    /* Alerts */
    .alert {
        padding: 16px 20px;
        margin-bottom: 20px;
        border-radius: 6px;
        border-left: 4px solid #D69E2E;
        background-color: #FFFAF0;
    }
    
    .alert-header {
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 16px;
    }
    
    .alert-body {
        font-size: 14px;
        line-height: 1.5;
        color: #4A5568;
    }
    
    .alert-danger {
        border-left-color: #E53E3E;
        background-color: #FFF5F5;
    }
    
    .alert-danger .alert-header {
        color: #E53E3E;
    }
    
    .alert-warning {
        border-left-color: #D69E2E;
        background-color: #FFFAF0;
    }
    
    .alert-warning .alert-header {
        color: #D69E2E;
    }
    
    .alert-success {
        border-left-color: #38A169;
        background-color: #F0FFF4;
    }
    
    .alert-success .alert-header {
        color: #38A169;
    }
    
    .alert-info {
        border-left-color: #4299E1;
        background-color: #EBF8FF;
    }
    
    .alert-info .alert-header {
        color: #4299E1;
    }
    """


def get_button_styles() -> str:
    """Styles for buttons and CTAs"""
    return """
    /* Buttons */
    .button {
        display: inline-block;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        border-radius: 6px;
        transition: background-color 0.2s;
        cursor: pointer;
    }
    
    .button-primary {
        background-color: #2B6CB0;
        color: #ffffff !important;
    }
    
    .button-secondary {
        background-color: #4A90E2;
        color: #ffffff !important;
    }
    
    .button-success {
        background-color: #38A169;
        color: #ffffff !important;
    }
    
    .button-outline {
        background-color: transparent;
        border: 2px solid #2B6CB0;
        color: #2B6CB0 !important;
    }
    
    .button-full {
        display: block;
        width: 100%;
        box-sizing: border-box;
    }
    
    .button-small {
        padding: 8px 16px;
        font-size: 14px;
    }
    
    .button-large {
        padding: 16px 32px;
        font-size: 18px;
    }
    
    /* Button Container */
    .button-container {
        text-align: center;
        margin: 30px 0;
    }
    """


def get_table_styles() -> str:
    """Enhanced table styles for email"""
    return """
    /* Enhanced Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 30px;
        font-size: 14px;
    }
    
    .data-table th {
        background-color: #F7FAFC;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        color: #4A5568;
        border-bottom: 2px solid #E2E8F0;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.05em;
    }
    
    .data-table td {
        padding: 12px;
        border-bottom: 1px solid #E2E8F0;
        vertical-align: middle;
    }
    
    .data-table tr:last-child td {
        border-bottom: none;
    }
    
    .data-table tr:hover {
        background-color: #F7FAFC;
    }
    
    .table-responsive {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 30px;
    }
    
    /* Mobile Tables */
    @media only screen and (max-width: 600px) {
        .data-table {
            font-size: 12px;
        }
        
        .data-table th,
        .data-table td {
            padding: 8px;
        }
    }
    """


def get_provider_card_styles() -> str:
    """Styles for provider performance cards"""
    return """
    /* Provider Cards */
    .provider-card {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #FFFFFF;
    }
    
    .provider-header {
        display: table;
        width: 100%;
        margin-bottom: 15px;
    }
    
    .provider-name {
        display: table-cell;
        font-size: 18px;
        font-weight: 600;
        color: #2D3748;
        vertical-align: middle;
    }
    
    .provider-badge {
        display: table-cell;
        text-align: right;
        vertical-align: middle;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-excellent {
        background-color: #F0FFF4;
        color: #38A169;
    }
    
    .badge-good {
        background-color: #EBF8FF;
        color: #4299E1;
    }
    
    .badge-needs-attention {
        background-color: #FFFAF0;
        color: #D69E2E;
    }
    
    .provider-metrics {
        display: table;
        width: 100%;
        margin-top: 15px;
    }
    
    .provider-metric {
        display: table-cell;
        width: 33.33%;
        text-align: center;
        padding: 10px;
        border-right: 1px solid #E2E8F0;
    }
    
    .provider-metric:last-child {
        border-right: none;
    }
    
    .provider-metric-label {
        font-size: 12px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .provider-metric-value {
        font-size: 20px;
        font-weight: 700;
        color: #2D3748;
    }
    """


def get_recommendation_styles() -> str:
    """Styles for recommendation sections"""
    return """
    /* Recommendations */
    .recommendations {
        background-color: #F7FAFC;
        border-radius: 8px;
        padding: 25px;
        margin: 30px 0;
    }
    
    .recommendations-header {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #2D3748;
    }
    
    .recommendation-item {
        margin-bottom: 16px;
        padding-left: 30px;
        position: relative;
    }
    
    .recommendation-item:before {
        content: "→";
        position: absolute;
        left: 0;
        top: 0;
        color: #4A90E2;
        font-weight: 700;
        font-size: 18px;
    }
    
    .recommendation-priority {
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-left: 8px;
    }
    
    .priority-high {
        background-color: #FFF5F5;
        color: #E53E3E;
    }
    
    .priority-medium {
        background-color: #FFFAF0;
        color: #D69E2E;
    }
    
    .priority-low {
        background-color: #EBF8FF;
        color: #4299E1;
    }
    """


def get_signature_styles() -> str:
    """Styles for email signatures"""
    return """
    /* Signature */
    .signature {
        margin-top: 40px;
        padding-top: 30px;
        border-top: 1px solid #E2E8F0;
    }
    
    .signature-name {
        font-size: 18px;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 4px;
    }
    
    .signature-title {
        font-size: 14px;
        color: #718096;
        margin-bottom: 2px;
    }
    
    .signature-company {
        font-size: 14px;
        color: #4A5568;
        font-weight: 600;
    }
    
    .signature-contact {
        margin-top: 12px;
        font-size: 14px;
        color: #718096;
    }
    
    .signature-logo {
        margin-top: 20px;
        max-width: 150px;
        height: auto;
    }
    """