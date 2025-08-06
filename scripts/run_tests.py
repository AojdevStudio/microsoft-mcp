#!/usr/bin/env python3
"""Test runner script for Microsoft MCP server.

This script provides a unified interface for running different types of tests
with appropriate configurations for local development and CI/CD environments.

Usage:
    python scripts/run_tests.py [options]
    
Examples:
    python scripts/run_tests.py --unit                    # Run unit tests only
    python scripts/run_tests.py --integration             # Run integration tests only
    python scripts/run_tests.py --all                     # Run all tests except E2E
    python scripts/run_tests.py --e2e                     # Run E2E tests (requires auth)
    python scripts/run_tests.py --coverage                # Run with coverage
    python scripts/run_tests.py --fast                    # Run fast tests only
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for Microsoft MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Categories:
  unit         - Fast unit tests with all external dependencies mocked
  integration  - Integration tests with internal component testing
  e2e          - End-to-end tests with real Microsoft Graph API (requires auth)
  email        - Email framework specific tests
  
Examples:
  python scripts/run_tests.py --unit --coverage
  python scripts/run_tests.py --all --html-report
  python scripts/run_tests.py --e2e  # Requires: export RUN_E2E_TESTS=true
"""
    )
    
    # Test selection options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--unit", 
        action="store_true", 
        help="Run unit tests only (fast, no external dependencies)"
    )
    test_group.add_argument(
        "--integration", 
        action="store_true", 
        help="Run integration tests only (medium speed, mocked externals)"
    )
    test_group.add_argument(
        "--e2e", 
        action="store_true", 
        help="Run E2E tests only (slow, requires real authentication)"
    )
    test_group.add_argument(
        "--email", 
        action="store_true", 
        help="Run email framework tests only"
    )
    test_group.add_argument(
        "--all", 
        action="store_true", 
        help="Run all tests except E2E (default for CI)"
    )
    
    # Output options
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "--html-report", 
        action="store_true", 
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Skip slow tests"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--failfast", "-x", 
        action="store_true", 
        help="Stop on first failure"
    )
    parser.add_argument(
        "--parallel", "-n", 
        type=int, 
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    # Default to --all if no specific test type is selected
    if not any([args.unit, args.integration, args.e2e, args.email]):
        args.all = True
    
    # Validate E2E test requirements
    if args.e2e and os.getenv("RUN_E2E_TESTS", "false").lower() != "true":
        print("ERROR: E2E tests require RUN_E2E_TESTS=true environment variable")
        print("Set it with: export RUN_E2E_TESTS=true")
        print("Also ensure you've authenticated with: uv run python authenticate.py")
        return 1
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("ERROR: Must be run from the project root directory")
        return 1
    
    # Build base command
    cmd = ["uv", "run", "pytest"]
    
    # Add test selection
    if args.unit:
        cmd.extend(["tests/unit/"])
        description = "Unit Tests"
    elif args.integration:
        cmd.extend(["tests/integration/"])
        description = "Integration Tests"
    elif args.e2e:
        cmd.extend(["tests/test_integration_e2e.py", "-m", "e2e"])
        description = "End-to-End Tests"
    elif args.email:
        cmd.extend(["-m", "email_framework"])
        description = "Email Framework Tests"
    elif args.all:
        cmd.extend(["tests/", "-m", "not e2e"])
        description = "All Tests (except E2E)"
    
    # Add output options
    if args.verbose:
        cmd.append("-v")
    
    if args.failfast:
        cmd.append("-x")
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage options
    if args.coverage or args.html_report:
        cmd.extend(["--cov=microsoft_mcp"])
        
        if args.html_report:
            cmd.extend(["--cov-report=html"])
        else:
            cmd.extend(["--cov-report=term-missing"])
        
        # Set coverage failure threshold
        cmd.extend(["--cov-fail-under=80"])
    
    # Add standard options for better output
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--strict-config"
    ])
    
    # Run the tests
    exit_code = run_command(cmd, description)
    
    # Print summary
    if exit_code == 0:
        print(f"\n✅ {description} passed successfully!")
        if args.html_report:
            print("📊 HTML coverage report generated: htmlcov/index.html")
    else:
        print(f"\n❌ {description} failed with exit code {exit_code}")
    
    # Additional suggestions
    if exit_code != 0:
        print("\n💡 Troubleshooting tips:")
        if "No accounts found" in str(exit_code):
            print("   - Tests requiring authentication should use mocks")
            print("   - Check that external dependencies are properly mocked")
        print("   - Run with --verbose for more detailed output")
        print("   - Run specific test files to isolate issues")
        print("   - Check tests/README.md for testing strategy")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
