# Python Development Rules

These rules define how AI should generate Python code in this repository.

General Principles

- Follow PEP8 coding standards
- Prefer Python standard library
- Use type hints for all functions
- Functions should be ≤ 50 lines
- Classes should be ≤ 500 lines
- Avoid duplicated logic
- Ensure code readability and maintainability


Naming Conventions

Variables

Use snake_case

Examples
user_id
order_price
max_retry_count


Classes

Use PascalCase

Examples
UserService
OrderRepository


Constants

Use UPPER_CASE

Examples
MAX_RETRY = 3
DEFAULT_TIMEOUT = 30


Function Guidelines

Functions must

- Have type hints
- Have docstrings
- Be single responsibility
- Avoid complex nesting

Example

def calculate_total_price(price: float, tax: float) -> float:
    """Return total price including tax."""
    return price * (1 + tax)


Logging

Do not use print for production logging.

Use logging module.

Example

import logging

logger = logging.getLogger(__name__)
logger.info("User login success")


Exception Handling

Never swallow exceptions.

Bad

try:
    run()
except:
    pass


Good

try:
    run()
except ValueError as e:
    logger.error("Invalid value %s", e)
    raise


Performance

Prefer

- list comprehension
- dict lookup
- set lookup

Avoid

- O(n^2) nested loops