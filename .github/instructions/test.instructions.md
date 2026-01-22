---
applyTo: "**/tests/**"
description: "Testing conventions and patterns for this codebase"
---

# Testing Instructions

Always use pytest fixtures for test setup and teardown. This ensures proper resource management and test isolation.

## Test Structure
- Organize tests in a `tests/` directory mirroring the source structure
- Use descriptive test function names prefixed with `test_`
- Group related tests in test classes prefixed with `Test`

## Fixtures
- Define reusable fixtures in `conftest.py`
- Use appropriate fixture scopes: function, class, module, session
- Clean up resources in fixture teardown

## Assertions
- Use pytest's assert statement with clear comparison messages
- Prefer pytest's built-in assertions over unittest-style assertions

## Async Tests
- Mark async tests with `@pytest.mark.asyncio`
- Use `pytest-asyncio` for async test support
- Clean up async resources properly

## Best Practices
- Keep tests isolated and independent
- Mock external dependencies
- Use parametrize for testing multiple scenarios
- Aim for high test coverage of critical paths
