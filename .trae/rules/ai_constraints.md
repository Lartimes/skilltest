# AI Code Generation Constraints

These rules restrict how AI tools generate code.


AI Must

- Generate type hints
- Generate docstrings
- Follow project architecture
- Add error handling
- Follow naming conventions


AI Must NOT

- Generate functions longer than 50 lines
- Generate classes longer than 500 lines
- Duplicate code
- Use print for logging
- Hardcode configuration


Security Restrictions

Forbidden functions

eval()
exec()


Unsafe operations

pickle.load(untrusted_input)


Configuration

Configuration must come from

- environment variables
- configuration files

Never hardcode secrets.