# Architecture Rules

The project must follow a layered architecture.

Directory Structure

project/

app/
  api/
  service/
  repository/
  model/
  utils/

tests/


Layer Responsibilities


API Layer

Responsibilities

- Receive HTTP request
- Validate parameters
- Call service layer

Must NOT

- Contain business logic
- Contain database queries


Service Layer

Responsibilities

- Business logic
- Transaction orchestration
- Workflow coordination

Must NOT

- Write SQL directly


Repository Layer

Responsibilities

- Database access
- ORM operations
- SQL queries


Model Layer

Responsibilities

- Data models
- DTO objects
- ORM models


Utils Layer

Responsibilities

- Shared helper functions