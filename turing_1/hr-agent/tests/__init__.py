"""
Tests Package - Unit and Integration Tests

This package contains all tests for the HR Agent System.

Test Modules:
- test_auth.py              # JWT authentication tests
- test_leave.py             # Leave balance function tests
- test_capex.py            # Team capex function tests
- test_org.py              # Organization structure function tests

Test Structure:
Each test module follows pytest conventions:
- Test classes group related tests
- Test functions start with "test_"
- Clear docstrings explain what is tested

Running Tests:
    pytest tests/                    # Run all tests
    pytest tests/test_auth.py -v    # Run specific module with verbose output
    pytest tests/ -v --tb=short     # All tests with short tracebacks
    pytest tests/ --cov=app          # With code coverage

Test Philosophy:
- Each test should be independent
- Tests should be fast and deterministic
- Clear assertions with descriptive messages
- Test both happy path and error cases
- Aim for high code coverage

Author: HR Agent Development Team
"""
