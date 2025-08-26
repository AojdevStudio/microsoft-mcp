# Developer Checklist: Microsoft MCP Server API Consolidation

**PRD Reference:** [API Consolidation PRD](../prds/api-consolidation-comprehensive.md)
**Issue ID:** MSFT-API-CONSOLIDATION
**Priority:** High
**Estimated Time:** 80 Hours / 2 Development Sprints

## Pre-Development Setup

- [ ] Review PRD and understand all consolidation requirements
- [ ] Set up development branch: `feature/MSFT-API-CONSOLIDATION`
- [ ] Review existing code patterns in `src/microsoft_mcp/tools.py`
- [ ] Understand Microsoft Graph API patterns in `src/microsoft_mcp/graph.py`
- [ ] Analyze current test patterns in `tests/email-framework/test_mcp_integration.py`
- [ ] Map dependencies between existing tools and identify consolidation opportunities
- [ ] Set up performance testing environment with baseline measurements

## Phase 1: Foundation Implementation (Weeks 1-2)

### Backend Development - Unified Search Tool

- [ ] **Create unified search tool** in `src/microsoft_mcp/tools.py`
  - [ ] Implement `search()` function with comprehensive parameters
  - [ ] Add scope parameter handling: ["emails", "files", "contacts", "sharepoint", "all"]
  - [ ] Implement intelligent query routing based on scope
  - [ ] Add consistent response format with SearchResults class
  - [ ] Implement filters parameter for service-specific filtering
  - [ ] Add sorting options: "relevance", "date", "author"
  - [ ] Handle pagination and result limits (1-100 range validation)

- [ ] **Create enhanced file listing tool** in `src/microsoft_mcp/tools.py`
  - [ ] Implement `list_files()` with comprehensive filtering
  - [ ] Add filter_type parameter: "all", "recent", "shared", "owned"
  - [ ] Implement file_types filtering for specific extensions
  - [ ] Add modified_since date filtering (ISO 8601 format)
  - [ ] Implement sorting: "modified", "name", "size", "created"
  - [ ] Add sort_order: "asc", "desc"
  - [ ] Handle folder_path navigation

- [ ] **Create unified attachment management tool** in `src/microsoft_mcp/tools.py`
  - [ ] Implement `manage_email_attachment()` with action parameter
  - [ ] Add action handling: "upload", "download", "list", "delete"
  - [ ] Implement file upload with content validation
  - [ ] Add download functionality with proper file handling
  - [ ] Implement attachment listing for messages
  - [ ] Add attachment deletion capability
  - [ ] Handle file size limits and chunked uploads (>3MB)

- [ ] **Create consolidated email context tool** in `src/microsoft_mcp/tools.py`
  - [ ] Implement `get_email_context()` with flexible scope
  - [ ] Add context_type parameter: "thread", "conversation", "related"
  - [ ] Implement depth control for context retrieval
  - [ ] Add include_attachments option
  - [ ] Unified response format for all context types
  - [ ] Performance optimization for large conversation threads

- [ ] **Update out of office management** in `src/microsoft_mcp/tools.py`
  - [ ] Merge `set_out_of_office_message` and `clear_out_of_office_message`
  - [ ] Create `update_out_of_office()` tool with action parameter
  - [ ] Handle both setting and clearing operations
  - [ ] Maintain `get_out_of_office_settings()` as separate tool
  - [ ] Add message content validation and formatting

### Data Structure and Response Format Design

- [ ] **Create unified response classes** in appropriate module
  - [ ] Define SearchResults class with categorized results
  - [ ] Create FileListResults class with metadata
  - [ ] Design AttachmentResult class for attachment operations
  - [ ] Implement EmailContextResult class for context operations
  - [ ] Add consistent error response formatting
  - [ ] Include metadata fields: total_count, next_page_token, etc.

- [ ] **Remove business logic tools** from `src/microsoft_mcp/tools.py`
  - [ ] Identify all healthcare/dental template tools for removal
  - [ ] Document template schemas for client-side migration
  - [ ] Create template JSON examples in migration documentation
  - [ ] Remove: `create_healthcare_email_template`
  - [ ] Remove: `create_dental_appointment_template`
  - [ ] Remove: `create_patient_reminder_template`
  - [ ] Remove: `create_practice_report_template`

## Phase 2: Validation & Testing (Weeks 3-4)

### Unit Tests

- [ ] **Test unified search tool** in `tests/test_tools.py`
  - [ ] Test all scope combinations with mock responses
  - [ ] Validate parameter validation and error handling
  - [ ] Test query routing logic for different scopes
  - [ ] Verify response format consistency
  - [ ] Test filter combinations and edge cases
  - [ ] Validate sorting and pagination logic
  - [ ] Achieve minimum 90% code coverage

- [ ] **Test enhanced file listing** in `tests/test_tools.py`
  - [ ] Test all filter_type options with appropriate responses
  - [ ] Validate file_types filtering logic
  - [ ] Test date filtering with various ISO 8601 formats
  - [ ] Verify sorting functionality across all options
  - [ ] Test folder navigation and path handling
  - [ ] Test edge cases: empty results, large file lists
  - [ ] Validate error handling for invalid parameters

- [ ] **Test attachment management** in `tests/test_tools.py`
  - [ ] Test all action types: upload, download, list, delete
  - [ ] Validate file size handling and chunked uploads
  - [ ] Test various file types and content validation
  - [ ] Verify error handling for invalid message/attachment IDs
  - [ ] Test base64 encoding/decoding for file content
  - [ ] Validate attachment metadata retrieval

- [ ] **Test email context tool** in `tests/test_tools.py`
  - [ ] Test all context_type options with realistic data
  - [ ] Validate depth control and result limiting
  - [ ] Test include_attachments functionality
  - [ ] Verify thread reconstruction logic
  - [ ] Test conversation history accuracy
  - [ ] Validate related email identification

### Integration Tests

- [ ] **Update Microsoft Graph integration tests** in `tests/email-framework/test_mcp_integration.py`
  - [ ] Test unified search against real Microsoft Graph API
  - [ ] Validate enhanced file listing with real OneDrive data
  - [ ] Test attachment operations with real email messages
  - [ ] Verify email context retrieval with live email threads
  - [ ] Test multi-account scenarios for all consolidated tools
  - [ ] Validate error handling with actual API errors (401, 403, 429, 404)

- [ ] **Performance testing** in `tests/performance/`
  - [ ] Create performance benchmarks for all consolidated tools
  - [ ] Compare response times with original separate tools
  - [ ] Test with realistic data volumes (1000+ emails, files)
  - [ ] Measure memory usage and resource consumption
  - [ ] Validate ≤5% regression requirement
  - [ ] Test concurrent usage patterns

- [ ] **Migration compatibility testing** in `tests/migration/`
  - [ ] Test backward compatibility during transition period
  - [ ] Validate deprecation warnings display correctly
  - [ ] Test side-by-side operation of old and new tools
  - [ ] Verify response format equivalence where applicable
  - [ ] Test migration scenarios with sample client code

### End-to-End Testing

- [ ] **Real-world scenario testing** with complete workflows
  - [ ] Test unified search across multiple Microsoft 365 services
  - [ ] Verify file management workflows with enhanced listing
  - [ ] Test complete email workflows with attachment handling
  - [ ] Validate email context scenarios with thread management
  - [ ] Test multi-user scenarios with proper account isolation
  - [ ] Verify error recovery and retry logic

## Phase 3: Migration Preparation (Weeks 5-6)

### Documentation Tasks

- [ ] **Create migration guide** in `docs/migration/api-consolidation-guide.md`
  - [ ] Document all tool changes with before/after examples
  - [ ] Provide code migration examples for each consolidated tool
  - [ ] Create template migration guide for business logic removal
  - [ ] Include performance comparison data
  - [ ] Add troubleshooting section for common migration issues
  - [ ] Provide timeline for deprecation and removal

- [ ] **Update API documentation** in `README.md`
  - [ ] Update tool list with new consolidated tools
  - [ ] Add usage examples for all new tools
  - [ ] Document new parameter options and response formats
  - [ ] Update authentication and setup instructions
  - [ ] Add migration notice and timeline
  - [ ] Include performance characteristics and limitations

- [ ] **Create template migration resources**
  - [ ] Extract template schemas to JSON files in `templates/schemas/`
  - [ ] Create client-side helper library examples
  - [ ] Document template customization patterns
  - [ ] Provide migration examples for common template use cases
  - [ ] Create validation scripts for template data

### Deprecation Implementation

- [ ] **Add deprecation warnings** to existing tools in `src/microsoft_mcp/tools.py`
  - [ ] Add warning messages to all tools being replaced
  - [ ] Include migration instructions in warning text
  - [ ] Add deprecation dates and removal timeline
  - [ ] Log deprecation usage for monitoring
  - [ ] Point users to migration guide and new tool equivalents

- [ ] **Update tool descriptions** for deprecated tools
  - [ ] Mark tools as deprecated in docstrings
  - [ ] Add "DEPRECATED" prefix to tool names/descriptions
  - [ ] Include replacement tool recommendations
  - [ ] Update parameter documentation with migration notes

## Phase 4: Deployment and Validation (Weeks 7-12)

### Deployment Tasks

- [ ] **Staging deployment** for validation
  - [ ] Deploy consolidated tools to staging environment
  - [ ] Configure feature flags for gradual rollout
  - [ ] Set up monitoring for new tool usage and performance
  - [ ] Test authentication and multi-account scenarios
  - [ ] Validate Microsoft Graph API integrations

- [ ] **Production preparation**
  - [ ] Create deployment checklist and rollback procedures
  - [ ] Set up monitoring dashboards for new tools
  - [ ] Configure alerting for performance regressions
  - [ ] Prepare communication plan for users
  - [ ] Schedule maintenance windows if needed

### Monitoring and Validation

- [ ] **Performance monitoring setup**
  - [ ] Track response times for all consolidated tools
  - [ ] Monitor API call patterns and rate limiting
  - [ ] Set up alerts for performance regression (>5%)
  - [ ] Track user adoption rates for new tools
  - [ ] Monitor error rates and failure patterns

- [ ] **User migration tracking**
  - [ ] Track usage of deprecated vs. new tools
  - [ ] Monitor support tickets related to migration
  - [ ] Collect user feedback on new tool experience
  - [ ] Track migration completion rates
  - [ ] Identify common migration issues

### Final Cleanup (Week 12)

- [ ] **Remove deprecated tools** after 90-day notice period
  - [ ] Confirm migration completion rate >90%
  - [ ] Remove deprecated tool implementations
  - [ ] Clean up related test code and documentation
  - [ ] Update tool count documentation (61 → 46)
  - [ ] Archive deprecated tool documentation

- [ ] **Performance validation**
  - [ ] Conduct final performance comparison
  - [ ] Document actual vs. projected improvements
  - [ ] Validate all success metrics achieved
  - [ ] Create performance report for stakeholders

## Quality Assurance Tasks

### Code Review Checklist

- [ ] **Microsoft Graph API integration review**
  - [ ] Verify correct API endpoints and versions used
  - [ ] Check proper scope requirements and permissions
  - [ ] Validate error handling for all API response codes
  - [ ] Ensure pagination support where applicable
  - [ ] Review rate limiting and retry logic

- [ ] **Tool design consistency review**
  - [ ] Verify consistent parameter naming patterns
  - [ ] Check unified response format implementation
  - [ ] Validate input parameter validation
  - [ ] Ensure meaningful return values and error messages
  - [ ] Review documentation completeness and accuracy

- [ ] **Security and authentication review**
  - [ ] Verify account isolation and multi-tenant support
  - [ ] Check token handling and refresh mechanisms
  - [ ] Validate input sanitization and validation
  - [ ] Review error message security (no sensitive data exposure)
  - [ ] Confirm proper authentication flow handling

### Final Validation Steps

- [ ] **Acceptance criteria validation**
  - [ ] Confirm 61 → 46 tool reduction achieved
  - [ ] Validate all business logic removed from API layer
  - [ ] Test unified search performance and functionality
  - [ ] Verify file listing consolidation completeness
  - [ ] Confirm attachment management consolidation
  - [ ] Validate 90-day migration period completion
  - [ ] Check API consistency improvements
  - [ ] Confirm performance requirements met (≤5% regression)
  - [ ] Verify documentation and migration guide completeness
  - [ ] Validate integration test coverage

- [ ] **Post-deployment monitoring**
  - [ ] Monitor production metrics for 30 days post-deployment
  - [ ] Track user adoption and migration success
  - [ ] Address any performance or functionality issues
  - [ ] Collect and document lessons learned
  - [ ] Update development processes based on experience

## Rollback Procedures

### Emergency Rollback Plan

- [ ] **Immediate rollback capabilities**
  - [ ] Maintain feature flags for instant tool switching
  - [ ] Keep deprecated tools available during transition
  - [ ] Prepare database rollback scripts if needed
  - [ ] Document rollback decision criteria
  - [ ] Test rollback procedures in staging environment

- [ ] **Rollback validation**
  - [ ] Verify all original functionality restored
  - [ ] Test performance returns to baseline
  - [ ] Confirm user workflows continue uninterrupted
  - [ ] Validate authentication and multi-account scenarios
  - [ ] Check integration points remain functional

## Success Metrics Validation

- [ ] **Quantitative metrics confirmation**
  - [ ] Tool count: 61 → 46 (25% reduction achieved)
  - [ ] Parameter count reduction: 40% across similar operations
  - [ ] Performance: ≤5% regression across all operations
  - [ ] Migration rate: >90% within 90-day period
  - [ ] Error rate: Maintained or improved
  - [ ] Documentation: 100% coverage for new tools

- [ ] **Qualitative metrics assessment**
  - [ ] Developer experience survey results
  - [ ] Code maintainability improvements measured
  - [ ] API consistency improvements documented
  - [ ] Integration complexity reduction validated

## Post-Implementation Tasks

- [ ] **Create post-implementation report**
  - [ ] Document actual vs. planned outcomes
  - [ ] Analyze performance improvements and any regressions
  - [ ] Report on user adoption and migration success
  - [ ] Document lessons learned and best practices
  - [ ] Recommend future API consolidation opportunities

- [ ] **Update development processes**
  - [ ] Incorporate lessons learned into development guidelines
  - [ ] Update API design review checklist
  - [ ] Enhance testing procedures based on experience
  - [ ] Update documentation standards
  - [ ] Improve migration planning processes

- [ ] **Close issue and archive artifacts**
  - [ ] Mark MSFT-API-CONSOLIDATION as complete
  - [ ] Archive migration resources and deprecated code
  - [ ] Update project status and communicate completion
  - [ ] Schedule follow-up review in 6 months
  - [ ] Document API evolution for future reference