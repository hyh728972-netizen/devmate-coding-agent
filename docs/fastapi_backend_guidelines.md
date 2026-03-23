# FastAPI Backend Guidelines

- All APIs should follow RESTful conventions.
- Use async endpoints for database or network operations.
- Use Pydantic models for request validation.
- Keep routes under `/api/v1`.
- Logging should use Python logging module instead of print.