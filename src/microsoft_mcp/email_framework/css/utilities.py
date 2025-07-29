"""
Utility CSS classes for email templates
Common utility classes for spacing, alignment, visibility, etc.
"""


def get_utility_styles() -> str:
    """
    Get all utility CSS styles
    """
    return f"""
    {get_text_utilities()}
    {get_spacing_utilities()}
    {get_alignment_utilities()}
    {get_display_utilities()}
    {get_color_utilities()}
    {get_border_utilities()}
    """


def get_text_utilities() -> str:
    """Text formatting utilities"""
    return """
    /* Text Utilities */
    .text-left { text-align: left !important; }
    .text-center { text-align: center !important; }
    .text-right { text-align: right !important; }
    
    .text-xs { font-size: 12px !important; }
    .text-sm { font-size: 14px !important; }
    .text-base { font-size: 16px !important; }
    .text-lg { font-size: 18px !important; }
    .text-xl { font-size: 20px !important; }
    .text-2xl { font-size: 24px !important; }
    .text-3xl { font-size: 30px !important; }
    
    .font-normal { font-weight: 400 !important; }
    .font-medium { font-weight: 500 !important; }
    .font-semibold { font-weight: 600 !important; }
    .font-bold { font-weight: 700 !important; }
    
    .uppercase { text-transform: uppercase !important; }
    .lowercase { text-transform: lowercase !important; }
    .capitalize { text-transform: capitalize !important; }
    
    .italic { font-style: italic !important; }
    .underline { text-decoration: underline !important; }
    .no-underline { text-decoration: none !important; }
    
    .tracking-tight { letter-spacing: -0.05em !important; }
    .tracking-normal { letter-spacing: 0 !important; }
    .tracking-wide { letter-spacing: 0.05em !important; }
    
    .leading-none { line-height: 1 !important; }
    .leading-tight { line-height: 1.25 !important; }
    .leading-normal { line-height: 1.5 !important; }
    .leading-relaxed { line-height: 1.75 !important; }
    """


def get_spacing_utilities() -> str:
    """Spacing utilities for margin and padding"""
    return """
    /* Margin Utilities */
    .m-0 { margin: 0 !important; }
    .m-1 { margin: 4px !important; }
    .m-2 { margin: 8px !important; }
    .m-3 { margin: 12px !important; }
    .m-4 { margin: 16px !important; }
    .m-5 { margin: 20px !important; }
    .m-6 { margin: 24px !important; }
    .m-8 { margin: 32px !important; }
    .m-10 { margin: 40px !important; }
    
    .mx-0 { margin-left: 0 !important; margin-right: 0 !important; }
    .mx-1 { margin-left: 4px !important; margin-right: 4px !important; }
    .mx-2 { margin-left: 8px !important; margin-right: 8px !important; }
    .mx-3 { margin-left: 12px !important; margin-right: 12px !important; }
    .mx-4 { margin-left: 16px !important; margin-right: 16px !important; }
    .mx-5 { margin-left: 20px !important; margin-right: 20px !important; }
    .mx-auto { margin-left: auto !important; margin-right: auto !important; }
    
    .my-0 { margin-top: 0 !important; margin-bottom: 0 !important; }
    .my-1 { margin-top: 4px !important; margin-bottom: 4px !important; }
    .my-2 { margin-top: 8px !important; margin-bottom: 8px !important; }
    .my-3 { margin-top: 12px !important; margin-bottom: 12px !important; }
    .my-4 { margin-top: 16px !important; margin-bottom: 16px !important; }
    .my-5 { margin-top: 20px !important; margin-bottom: 20px !important; }
    
    .mt-0 { margin-top: 0 !important; }
    .mt-1 { margin-top: 4px !important; }
    .mt-2 { margin-top: 8px !important; }
    .mt-3 { margin-top: 12px !important; }
    .mt-4 { margin-top: 16px !important; }
    .mt-5 { margin-top: 20px !important; }
    .mt-6 { margin-top: 24px !important; }
    .mt-8 { margin-top: 32px !important; }
    
    .mb-0 { margin-bottom: 0 !important; }
    .mb-1 { margin-bottom: 4px !important; }
    .mb-2 { margin-bottom: 8px !important; }
    .mb-3 { margin-bottom: 12px !important; }
    .mb-4 { margin-bottom: 16px !important; }
    .mb-5 { margin-bottom: 20px !important; }
    .mb-6 { margin-bottom: 24px !important; }
    .mb-8 { margin-bottom: 32px !important; }
    
    .ml-0 { margin-left: 0 !important; }
    .ml-1 { margin-left: 4px !important; }
    .ml-2 { margin-left: 8px !important; }
    .ml-3 { margin-left: 12px !important; }
    .ml-4 { margin-left: 16px !important; }
    
    .mr-0 { margin-right: 0 !important; }
    .mr-1 { margin-right: 4px !important; }
    .mr-2 { margin-right: 8px !important; }
    .mr-3 { margin-right: 12px !important; }
    .mr-4 { margin-right: 16px !important; }
    
    /* Padding Utilities */
    .p-0 { padding: 0 !important; }
    .p-1 { padding: 4px !important; }
    .p-2 { padding: 8px !important; }
    .p-3 { padding: 12px !important; }
    .p-4 { padding: 16px !important; }
    .p-5 { padding: 20px !important; }
    .p-6 { padding: 24px !important; }
    .p-8 { padding: 32px !important; }
    
    .px-0 { padding-left: 0 !important; padding-right: 0 !important; }
    .px-1 { padding-left: 4px !important; padding-right: 4px !important; }
    .px-2 { padding-left: 8px !important; padding-right: 8px !important; }
    .px-3 { padding-left: 12px !important; padding-right: 12px !important; }
    .px-4 { padding-left: 16px !important; padding-right: 16px !important; }
    .px-5 { padding-left: 20px !important; padding-right: 20px !important; }
    
    .py-0 { padding-top: 0 !important; padding-bottom: 0 !important; }
    .py-1 { padding-top: 4px !important; padding-bottom: 4px !important; }
    .py-2 { padding-top: 8px !important; padding-bottom: 8px !important; }
    .py-3 { padding-top: 12px !important; padding-bottom: 12px !important; }
    .py-4 { padding-top: 16px !important; padding-bottom: 16px !important; }
    .py-5 { padding-top: 20px !important; padding-bottom: 20px !important; }
    
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
    
    .pl-0 { padding-left: 0 !important; }
    .pl-1 { padding-left: 4px !important; }
    .pl-2 { padding-left: 8px !important; }
    .pl-3 { padding-left: 12px !important; }
    .pl-4 { padding-left: 16px !important; }
    
    .pr-0 { padding-right: 0 !important; }
    .pr-1 { padding-right: 4px !important; }
    .pr-2 { padding-right: 8px !important; }
    .pr-3 { padding-right: 12px !important; }
    .pr-4 { padding-right: 16px !important; }
    """


def get_alignment_utilities() -> str:
    """Alignment utilities"""
    return """
    /* Alignment Utilities */
    .align-top { vertical-align: top !important; }
    .align-middle { vertical-align: middle !important; }
    .align-bottom { vertical-align: bottom !important; }
    .align-text-top { vertical-align: text-top !important; }
    .align-text-bottom { vertical-align: text-bottom !important; }
    """


def get_display_utilities() -> str:
    """Display and visibility utilities"""
    return """
    /* Display Utilities */
    .block { display: block !important; }
    .inline-block { display: inline-block !important; }
    .inline { display: inline !important; }
    .table { display: table !important; }
    .table-cell { display: table-cell !important; }
    .table-row { display: table-row !important; }
    .hidden { display: none !important; }
    
    /* Width Utilities */
    .w-full { width: 100% !important; }
    .w-auto { width: auto !important; }
    .w-1-2 { width: 50% !important; }
    .w-1-3 { width: 33.333333% !important; }
    .w-2-3 { width: 66.666667% !important; }
    .w-1-4 { width: 25% !important; }
    .w-3-4 { width: 75% !important; }
    
    .max-w-none { max-width: none !important; }
    .max-w-full { max-width: 100% !important; }
    .max-w-sm { max-width: 300px !important; }
    .max-w-md { max-width: 400px !important; }
    .max-w-lg { max-width: 500px !important; }
    .max-w-xl { max-width: 600px !important; }
    
    /* Mobile Visibility */
    @media only screen and (max-width: 600px) {
        .hide-mobile { display: none !important; }
        .show-mobile { display: block !important; }
    }
    
    @media only screen and (min-width: 601px) {
        .hide-desktop { display: none !important; }
        .show-desktop { display: block !important; }
    }
    """


def get_color_utilities() -> str:
    """Color utilities for quick styling"""
    return """
    /* Color Utilities */
    .text-white { color: #ffffff !important; }
    .text-black { color: #000000 !important; }
    .text-gray { color: #718096 !important; }
    .text-gray-dark { color: #4A5568 !important; }
    .text-gray-light { color: #CBD5E0 !important; }
    
    .bg-white { background-color: #ffffff !important; }
    .bg-gray-light { background-color: #F7FAFC !important; }
    .bg-gray { background-color: #E2E8F0 !important; }
    .bg-transparent { background-color: transparent !important; }
    """


def get_border_utilities() -> str:
    """Border utilities"""
    return """
    /* Border Utilities */
    .border { border: 1px solid #E2E8F0 !important; }
    .border-0 { border: 0 !important; }
    .border-t { border-top: 1px solid #E2E8F0 !important; }
    .border-r { border-right: 1px solid #E2E8F0 !important; }
    .border-b { border-bottom: 1px solid #E2E8F0 !important; }
    .border-l { border-left: 1px solid #E2E8F0 !important; }
    
    .border-2 { border-width: 2px !important; }
    .border-4 { border-width: 4px !important; }
    
    .rounded { border-radius: 4px !important; }
    .rounded-md { border-radius: 6px !important; }
    .rounded-lg { border-radius: 8px !important; }
    .rounded-xl { border-radius: 12px !important; }
    .rounded-full { border-radius: 9999px !important; }
    .rounded-none { border-radius: 0 !important; }
    """