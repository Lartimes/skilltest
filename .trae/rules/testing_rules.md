# Testing Rules

Testing must use pytest.


Directory Structure

tests/

test_user_service.py
test_order_service.py


Test Naming

Use pattern

test_<module>_<behavior>

Examples

test_user_create_success
test_user_create_invalid_email


Example Test

def test_add():
    assert 1 + 1 == 2


Coverage Requirements

Minimum coverage

Service Layer ≥ 80%


Best Practices

- Use fixtures
- Avoid shared global state
- Tests must be deterministic