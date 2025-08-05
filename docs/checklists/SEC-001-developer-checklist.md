# Developer Checklist: Email Framework Security & Quality Remediation

**PRD Reference:** [docs/prds/email-framework-security-quality-fixes.md](../prds/email-framework-security-quality-fixes.md)
**Issue ID:** SEC-001
**Priority:** Urgent (Security Critical)
**Estimated Time:** 16 hours

## Pre-Development Setup

- [ ] Review PRD and all acceptance criteria thoroughly
- [ ] Set up development branch: `security/SEC-001-email-framework-xss-fixes`
- [ ] Review existing code and identify all XSS vulnerability locations:
  - [ ] `src/microsoft_mcp/email_framework/templates/base.py:74`
  - [ ] `src/microsoft_mcp/email_framework/templates/practice_report.py:74-75`
  - [ ] All template rendering functions
- [ ] Install security testing dependencies: `uv add --dev bandit safety markupsafe premailer`
- [ ] Run initial security scan: `uv run bandit -r src/`

## Critical Security Fixes (Phase 1 - 4 hours)

### XSS Vulnerability Remediation

- [ ] **CRITICAL:** Install markupsafe for HTML escaping
  ```bash
  uv add markupsafe
  ```

- [ ] **CRITICAL:** Fix XSS in `src/microsoft_mcp/email_framework/templates/base.py:74`
  ```python
  # BEFORE (VULNERABLE):
  # html_content = f"<div class='location'>{data['location']}</div>"
  
  # AFTER (SECURE):
  from markupsafe import escape
  html_content = f"<div class='location'>{escape(data['location'])}</div>"
  ```

- [ ] **CRITICAL:** Fix XSS in `src/microsoft_mcp/email_framework/templates/practice_report.py:74-75`
  ```python
  # Apply HTML escaping to ALL user-provided variables:
  location = escape(data["location"])
  period = escape(data.get("period", ""))
  ```

- [ ] **CRITICAL:** Audit ALL template files for user input insertion:
  - [ ] Search for f-string usage with user data: `grep -r "f.*{.*}" src/microsoft_mcp/email_framework/`
  - [ ] Search for string formatting: `grep -r "\.format\|%" src/microsoft_mcp/email_framework/`
  - [ ] Apply escaping to every instance

### Security Headers Implementation

- [ ] Add Content Security Policy headers to email templates:
  ```python
  def add_security_headers(html_content: str) -> str:
      """Add security headers to prevent content injection"""
      csp_header = "Content-Security-Policy: default-src 'self'; style-src 'unsafe-inline'"
      return f"<!--{csp_header}-->\n{html_content}"
  ```

- [ ] Implement input validation before template rendering:
  ```python
  def validate_email_data(data: dict) -> dict:
      """Validate and sanitize email template data"""
      validated = {}
      for key, value in data.items():
          if isinstance(value, str):
              validated[key] = escape(value)
          else:
              validated[key] = value
      return validated
  ```

### Security Test Suite Creation

- [ ] Create security test directory: `tests/security/`
- [ ] Create XSS prevention test file: `tests/security/test_xss_prevention.py`
  ```python
  import pytest
  from markupsafe import escape
  from microsoft_mcp.email_framework.templates.base import render_template
  
  class TestXSSPrevention:
      def test_script_tag_escaped(self):
          """Test that script tags are properly escaped"""
          malicious_input = "<script>alert('xss')</script>"
          result = render_template("practice_report", {"location": malicious_input})
          assert "<script>" not in result
          assert "&lt;script&gt;" in result
      
      def test_html_entities_escaped(self):
          """Test HTML entities are properly escaped"""
          malicious_input = "\"'<>&"
          result = render_template("practice_report", {"location": malicious_input})
          assert "&quot;" in result or "&#34;" in result
          assert "&#39;" in result or "&apos;" in result
          assert "&lt;" in result
          assert "&gt;" in result
          assert "&amp;" in result
  ```

## Test Suite Remediation (Phase 2 - 6 hours)

### Fix Gmail Compatibility Tests

- [ ] Locate failing Gmail tests: `uv run pytest -v -k "gmail" --tb=short`
- [ ] Fix HTML structure checks in `tests/email_framework/test_gmail_compatibility.py`
  ```python
  # Fix assertion patterns for proper HTML validation
  def test_gmail_html_structure(self):
      result = render_email_template(test_data)
      # Use proper HTML parsing instead of string matching
      from bs4 import BeautifulSoup
      soup = BeautifulSoup(result, 'html.parser')
      assert soup.find('div', class_='email-content')
      assert soup.find('table')  # Gmail requires table-based layout
  ```

### Fix Performance Test Mocking

- [ ] Identify failing performance tests: `uv run pytest -v -k "performance" --tb=short`
- [ ] Fix mocking patterns in `tests/email_framework/test_performance.py`
  ```python
  @patch('microsoft_mcp.email_framework.css_inliner.inline_css')
  def test_template_rendering_performance(self, mock_inline):
      mock_inline.return_value = "mocked css"
      # Proper async mocking for email operations
      with patch('microsoft_mcp.graph.request') as mock_request:
          mock_request.return_value = {"id": "test-email-id"}
  ```

### Fix Template Test Assertions

- [ ] Update template tests with proper assertion patterns:
  ```python
  # Replace string-based assertions with structured validation
  def test_template_content(self):
      result = render_template("practice_report", test_data)
      soup = BeautifulSoup(result, 'html.parser')
      
      # Structured assertions instead of string matching
      assert soup.find('h1', string='Practice Report')
      assert soup.find('div', class_='location-info')
      
      # Security validation
      assert '<script>' not in result
      assert all(tag not in result for tag in ['<script>', '<iframe>', '<object>'])
  ```

### Add Comprehensive Test Coverage

- [ ] Create missing test cases for all template functions
- [ ] Add edge case testing for malformed CSS
- [ ] Add boundary testing for large email data
- [ ] Test error handling in CSS inliner

## Code Quality & Architecture (Phase 3 - 6 hours)

### Remove Unused Imports and Lint Issues

- [ ] Run comprehensive linting check: `uv run ruff check`
- [ ] Fix all unused imports automatically: `uv run ruff check --fix`
- [ ] Manual review for complex unused imports:
  ```bash
  # Identify specific unused imports
  uv run ruff check --select F401
  ```

- [ ] Run type checking: `uv run pyright`
- [ ] Format all code: `uv run ruff format`

### Improve CSS Inliner Robustness

- [ ] Replace regex-based CSS parsing with premailer:
  ```python
  # Replace current implementation in css_inliner.py
  from premailer import Premailer
  
  def inline_css_robust(html_content: str, css_content: str) -> str:
      """Use proper CSS parser instead of regex"""
      p = Premailer(html=html_content, strip_important=False)
      return p.transform()
  ```

- [ ] Add comprehensive error handling:
  ```python
  def inline_css_with_fallback(html_content: str, css_content: str) -> str:
      """CSS inlining with graceful fallback"""
      try:
          return inline_css_robust(html_content, css_content)
      except Exception as e:
          logger.warning(f"CSS inlining failed: {e}, using fallback")
          return html_content  # Return original HTML if CSS fails
  ```

### Architecture Simplification Assessment

- [ ] Review template abstraction layers for over-engineering:
  - [ ] Audit class hierarchy in `templates/base.py`
  - [ ] Identify unnecessary abstraction layers
  - [ ] Document simplification opportunities

- [ ] Evaluate migration to Jinja2 template engine:
  ```python
  # Consider replacing custom template system with Jinja2
  from jinja2 import Environment, FileSystemLoader, select_autoescape
  
  env = Environment(
      loader=FileSystemLoader('templates'),
      autoescape=select_autoescape(['html', 'xml'])  # Built-in XSS protection
  )
  ```

- [ ] Maintain functionality while reducing complexity:
  - [ ] Keep all existing template features working
  - [ ] Ensure theme system compatibility
  - [ ] Preserve location-based styling

### Error Handling Implementation

- [ ] Add comprehensive exception handling to template rendering:
  ```python
  def render_template_safe(template_name: str, data: dict) -> str:
      """Template rendering with comprehensive error handling"""
      try:
          validated_data = validate_email_data(data)
          return render_template(template_name, validated_data)
      except TemplateError as e:
          logger.error(f"Template rendering failed: {e}")
          return render_fallback_template(data)
      except Exception as e:
          logger.critical(f"Unexpected template error: {e}")
          raise
  ```

## Integration and Validation Tasks

### Security Integration

- [ ] Integrate security scanning in CI/CD:
  ```yaml
  # Add to GitHub Actions workflow
  - name: Security Scan
    run: |
      uv run bandit -r src/
      uv run safety check
  ```

- [ ] Add pre-commit hooks for security:
  ```yaml
  # .pre-commit-config.yaml
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
    - id: bandit
      args: ['-r', 'src/']
  ```

### Performance Validation

- [ ] Benchmark template rendering before/after changes:
  ```python
  def benchmark_template_rendering():
      import time
      start = time.time()
      for _ in range(100):
          render_template("practice_report", large_test_data)
      end = time.time()
      return end - start
  ```

- [ ] Verify <5% performance overhead for security measures
- [ ] Test with large datasets (1000+ recipients)

### Cross-Platform Email Testing

- [ ] Test rendered emails in multiple clients:
  - [ ] Gmail web interface
  - [ ] Outlook desktop client
  - [ ] Apple Mail
  - [ ] Mobile email apps

- [ ] Validate HTML structure compatibility:
  - [ ] Table-based layouts for Outlook
  - [ ] CSS support limitations
  - [ ] Image handling across clients

## Testing Tasks

### Unit Tests

- [ ] Write unit tests for all new security functions
- [ ] Test XSS prevention with various payloads:
  ```python
  XSS_PAYLOADS = [
      "<script>alert('xss')</script>",
      "javascript:alert('xss')",
      "<img src=x onerror=alert('xss')>",
      "&#60;script&#62;alert('xss')&#60;/script&#62;",
      "<svg onload=alert('xss')>",
  ]
  ```
- [ ] Test CSS inliner robustness with malformed CSS
- [ ] Achieve 100% code coverage for modified files

### Integration Tests

- [ ] Test complete email sending workflow with security measures
- [ ] Test multi-account scenarios with XSS payloads
- [ ] Test template inheritance with security validation
- [ ] Verify theme system works with escaped content

### End-to-End Tests

- [ ] Test actual email sending with escaped content
- [ ] Verify email rendering in actual email clients
- [ ] Test error recovery scenarios
- [ ] Performance testing under load

### Security-Specific Tests

- [ ] Penetration testing for XSS vulnerabilities
- [ ] Input fuzzing with malicious payloads
- [ ] Content Security Policy validation
- [ ] HTML injection prevention testing

## Documentation Tasks

- [ ] Update security documentation with XSS prevention patterns
- [ ] Document new security functions and their usage
- [ ] Create security guidelines for template development
- [ ] Update API documentation with security considerations
- [ ] Add examples of secure template usage

## Review & Deployment

### Pre-Review Checklist

- [ ] All 72 tests passing: `uv run pytest -v`
- [ ] Security scan clean: `uv run bandit -r src/`
- [ ] No linting issues: `uv run ruff check`
- [ ] Type checking passes: `uv run pyright`
- [ ] Performance benchmarks acceptable

### Security Review Requirements

- [ ] Demonstrate XSS prevention with before/after examples
- [ ] Show security test coverage and results
- [ ] Document all security measures implemented
- [ ] Provide penetration testing results

### Code Review Focus Areas

- [ ] **Security:** All user inputs properly escaped
- [ ] **Testing:** All failing tests now passing
- [ ] **Quality:** Clean, maintainable code
- [ ] **Performance:** Acceptable overhead from security measures
- [ ] **Architecture:** Simplified where over-engineered

### Deployment Strategy

- [ ] Deploy to staging environment first
- [ ] Run security validation in staging
- [ ] Performance monitoring during rollout
- [ ] Monitor error rates and email delivery success

## Post-Deployment

### Monitoring Setup

- [ ] Set up alerts for template rendering errors
- [ ] Monitor email delivery success rates
- [ ] Track performance metrics for template system
- [ ] Set up security monitoring for attempted XSS

### Success Validation

- [ ] Verify 0 XSS vulnerabilities in production
- [ ] Confirm 100% test pass rate maintained
- [ ] Validate performance within acceptable bounds
- [ ] Check email client compatibility preserved

### Documentation Updates

- [ ] Update security runbook with XSS prevention
- [ ] Document incident response for security issues
- [ ] Create developer guidelines for secure template coding
- [ ] Update architecture documentation with simplifications

## Emergency Rollback Plan

### Rollback Triggers
- [ ] Any XSS vulnerability discovered in production
- [ ] Email delivery failure rate >5%
- [ ] Performance degradation >20%
- [ ] Template rendering errors >1%

### Rollback Procedure
1. [ ] Immediately revert to previous version
2. [ ] Notify security team of rollback reason
3. [ ] Investigate root cause in staging environment
4. [ ] Fix issues before attempting re-deployment
5. [ ] Document lessons learned and improve process