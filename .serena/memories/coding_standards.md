# Coding Standards & Conventions

## General Principles
- **Clarity over cleverness** - Write code that is easy to understand
- **Explicit over implicit** - Be clear about intentions
- **Consistency** - Follow established patterns in the codebase
- **Type safety** - Use type hints everywhere

## Code Formatting
- **Formatter**: Ruff (line length: 88 characters)
- **Import sorting**: Ruff with single-line imports
- **Indentation**: 4 spaces (no tabs)
- **Target version**: Python 3.12+

## Naming Conventions

### Variables and Functions
- Variables: `snake_case`
- Functions: `snake_case` with verb prefixes
- Private functions: `_snake_case` (leading underscore)

### Classes
- Classes: `PascalCase`
- Pydantic models: End with `Params` or `Response`
- Constants: `UPPER_SNAKE_CASE`

### Type Hints
- Required everywhere for function signatures
- Use `Optional[T]` for nullable types
- Use `Union[A, B]` or `A | B` for multiple types
- Define type aliases for complex types

## Error Handling
- Use specific exceptions over generic ones
- Provide context in error messages
- Consistent error response format with status, action, error_type, message, details, timestamp

## Async Patterns
- Always use async/await for I/O operations
- Use asyncio.gather for concurrent operations
- Proper exception handling in async code

## Security Guidelines
- Always validate user input with Pydantic
- Never hardcode secrets or credentials
- Use environment variables for configuration
- Don't leak sensitive information in error messages
- Use parameterized queries and sanitize data

## Documentation
- Docstrings required for public functions
- Use Google-style docstrings with Args, Returns, Raises sections
- Include examples in docstrings when helpful
- Inline comments only for non-obvious logic