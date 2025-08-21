# GitHub Actions CI/CD Pipeline

This directory contains comprehensive GitHub Actions workflows for the Microsoft MCP project, providing automated testing, security scanning, releases, and maintenance.

## 🚀 Workflow Overview

### Core Workflows

#### 1. **CI Pipeline** (`ci.yml`)
**Triggers**: Push to main/develop/feature branches, Pull Requests
**Duration**: ~15-20 minutes
**Purpose**: Comprehensive testing and quality assurance

**Jobs**:
- **Code Quality & Security**: Linting (ruff), formatting, type checking (mypy), security audit
- **Tests**: Multi-platform testing (Ubuntu, macOS, Windows) with Python 3.12/3.13
- **Email Framework Tests**: Specialized testing for email template system
- **Build**: Package building and validation
- **Deployment Check**: Version bump validation for main branch

**Key Features**:
- ✅ Multi-OS and multi-Python version testing
- ✅ Comprehensive caching strategy for dependencies
- ✅ Security scanning with pip-audit
- ✅ Code coverage reporting with Codecov integration
- ✅ Artifact uploads for debugging and analysis

#### 2. **Release Pipeline** (`release.yml`)
**Triggers**: Git tags (`v*.*.*`), Manual dispatch
**Duration**: ~20-30 minutes
**Purpose**: Automated version releases and publishing

**Jobs**:
- **Validate Release**: Version format and conditions validation
- **Pre-Release Tests**: Full CI pipeline execution before release
- **Build Release**: Package building with changelog generation
- **GitHub Release**: Automated GitHub release creation
- **PyPI Publishing**: Automated package publishing to PyPI
- **Post-Release**: Development version preparation and notifications

**Key Features**:
- ✅ Semantic version validation
- ✅ Automated changelog generation
- ✅ PyPI publishing with trusted publishing (OIDC)
- ✅ Pre-release vs stable release handling
- ✅ Automatic development version bumping

#### 3. **Security Scanning** (`security.yml`)
**Triggers**: Daily schedule, Push to main, Pull Requests, Manual
**Duration**: ~15-25 minutes
**Purpose**: Comprehensive security analysis

**Jobs**:
- **Dependency Scan**: pip-audit and Safety vulnerability checking
- **SAST Analysis**: Bandit security linting and Semgrep analysis
- **CodeQL Analysis**: GitHub's semantic code analysis
- **Secret Scanning**: TruffleHog and gitleaks secret detection
- **License Check**: License compatibility verification
- **Security Summary**: Consolidated security status reporting

**Key Features**:
- ✅ Multiple security scanning tools integration
- ✅ SARIF report uploads for GitHub Security tab
- ✅ License compliance checking
- ✅ Automated vulnerability reporting

#### 4. **Maintenance & Updates** (`maintenance.yml`)
**Triggers**: Weekly schedule (Sunday 3 AM UTC), Manual dispatch
**Duration**: ~10-20 minutes
**Purpose**: Automated repository maintenance

**Jobs**:
- **Dependency Updates**: Automated dependency version updates
- **Actions Updates**: GitHub Actions version updates
- **Cache Cleanup**: Old cache cleanup for storage optimization
- **Health Check**: Repository health assessment and metrics

**Key Features**:
- ✅ Automated PR creation for updates
- ✅ Compatibility testing before updates
- ✅ Repository health monitoring
- ✅ Maintenance recommendations

### Specialized Workflows

#### 5. **Pull Request Validation** (`pr-validation.yml`)
**Triggers**: Pull Request events
**Duration**: ~10-15 minutes
**Purpose**: PR quality validation and automation

**Features**:
- ✅ PR structure validation (title format, description quality)
- ✅ Changed files analysis and categorization
- ✅ Automated labeling and size assessment
- ✅ Code quality quick checks
- ✅ Breaking changes detection
- ✅ Security quick scan for potential secrets

#### 6. **Notifications & Status** (`notifications.yml`)
**Triggers**: Workflow completions, Issues, PRs, Releases
**Duration**: ~2-5 minutes
**Purpose**: Status tracking and notifications

**Features**:
- ✅ Workflow status notifications
- ✅ PR lifecycle tracking
- ✅ Issue auto-triaging and labeling
- ✅ Release announcements
- ✅ Daily status summaries

## 🔧 Configuration Details

### Environment Variables
```yaml
PYTHON_VERSION: "3.12"        # Primary Python version
CACHE_VERSION: "v1"           # Cache invalidation control
```

### Required Secrets
```yaml
# GitHub (automatically provided)
GITHUB_TOKEN: <automatic>     # Repository access

# PyPI Publishing (for releases)
# Configure at: https://pypi.org/manage/account/publishing/
# Uses OIDC trusted publishing - no manual token needed

# Optional: External integrations
SLACK_WEBHOOK_URL: <optional> # Slack notifications
CODECOV_TOKEN: <optional>     # Enhanced Codecov integration
```

### Cache Strategy
The workflows implement a sophisticated caching strategy:

- **UV Dependencies**: Cached by OS, Python version, and lock file hash
- **Multi-level Cache Keys**: Primary + fallback restore keys
- **Job-specific Caches**: Different cache keys for build, test, security jobs
- **Automatic Cleanup**: Weekly cache cleanup to optimize storage

### Security Measures
- **Minimal Permissions**: Each workflow uses least-privilege permissions
- **Token Security**: OIDC trusted publishing for PyPI (no long-lived tokens)
- **Secret Scanning**: Multiple tools for detecting leaked credentials
- **SARIF Integration**: Security results integrate with GitHub Security tab
- **Dependency Auditing**: Regular vulnerability scanning

## 📊 Monitoring & Insights

### Status Badges
Add these badges to your README for visibility:

```markdown
[![CI Pipeline](https://github.com/elyxlz/microsoft-mcp/workflows/CI%20Pipeline/badge.svg)](https://github.com/elyxlz/microsoft-mcp/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/elyxlz/microsoft-mcp/workflows/Security%20Scanning/badge.svg)](https://github.com/elyxlz/microsoft-mcp/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/elyxlz/microsoft-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/elyxlz/microsoft-mcp)
```

### Workflow Analytics
- **Actions Usage**: Monitor workflow run times and costs
- **Success Rates**: Track workflow reliability
- **Security Alerts**: Review security tab regularly
- **Artifact Storage**: Monitor artifact storage usage

## 🚦 Workflow Triggers Summary

| Workflow | Push | PR | Schedule | Manual | Tags |
|----------|------|----|---------|---------|----- |
| CI Pipeline | ✅ | ✅ | ❌ | ✅ | ❌ |
| Release | ❌ | ❌ | ❌ | ✅ | ✅ |
| Security | Main only | ✅ | Daily | ✅ | ❌ |
| Maintenance | ❌ | ❌ | Weekly | ✅ | ❌ |
| PR Validation | ❌ | ✅ | ❌ | ❌ | ❌ |
| Notifications | Via workflow_run | ✅ | ❌ | ❌ | ❌ |

## 🔄 Release Process

### Automated Release (Recommended)
1. **Merge to main**: All changes go through PR validation
2. **Version bump**: Update version in `pyproject.toml`
3. **Create tag**: `git tag v1.2.3 && git push origin v1.2.3`
4. **Automated pipeline**: Release workflow handles the rest

### Manual Release
1. Go to **Actions** → **Release Pipeline**
2. Click **Run workflow**
3. Enter version number (e.g., `1.2.3`)
4. Choose if it's a pre-release
5. Click **Run workflow**

### Release Artifacts
- **GitHub Release**: Changelog and source archives
- **PyPI Package**: Installable wheel and source distribution
- **Artifacts**: Build artifacts for debugging

## 🛠️ Development Workflow

### For Contributors
1. **Fork & Branch**: Create feature branch
2. **Local Testing**: Run `uv run pytest` locally
3. **Create PR**: Automated validation runs
4. **Address Feedback**: Respond to reviews and checks
5. **Merge**: Maintainer merges after approval

### For Maintainers
1. **Review PRs**: Use automated validation insights
2. **Security Review**: Check security scan results weekly
3. **Dependencies**: Review automated dependency update PRs
4. **Releases**: Tag releases when ready
5. **Monitoring**: Review workflow analytics monthly

## 🔧 Customization

### Adding New Workflows
1. Create new `.yml` file in `.github/workflows/`
2. Follow existing patterns for structure
3. Add appropriate permissions and timeouts
4. Test thoroughly on feature branch

### Modifying Existing Workflows
1. **Test Changes**: Always test on feature branch first
2. **Documentation**: Update this README if needed
3. **Permissions**: Review security implications
4. **Notifications**: Consider impact on team notifications

### Environment-Specific Configuration
- **Development**: Use feature branch testing
- **Staging**: Main branch represents staging environment
- **Production**: Tags trigger production releases

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [UV Package Manager](https://docs.astral.sh/uv/)
- [Ruff Linter Configuration](https://docs.astral.sh/ruff/)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Codecov Integration](https://docs.codecov.com/docs)

## 🆘 Troubleshooting

### Common Issues

**Workflow fails on dependency installation**
- Check UV cache configuration
- Verify `pyproject.toml` syntax
- Review dependency conflicts

**Security scans reporting false positives**
- Review `.github/workflows/security.yml` configuration
- Add exceptions to Bandit configuration in `pyproject.toml`
- Update security tool versions

**Release workflow fails**
- Verify version format (must be semantic versioning)
- Check PyPI trusted publishing configuration
- Review release permissions

**Tests fail in CI but pass locally**
- Check environment variable configuration
- Review OS-specific test conditions
- Verify test isolation

### Getting Help
1. **Check workflow logs**: Detailed error information
2. **Review this documentation**: Common solutions
3. **Search existing issues**: Similar problems may be documented
4. **Create new issue**: Use issue templates for bug reports

---

*This CI/CD pipeline is designed to be robust, secure, and maintainable. Regular reviews and updates ensure it continues to serve the project's needs effectively.*