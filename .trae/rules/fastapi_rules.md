# FastAPI Development Rules

These rules apply when building APIs using FastAPI.


Basic API Structure

Example

from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}



API Design Rules

- Use RESTful endpoints
- Use nouns instead of verbs
- Use plural resources

Examples

GET /users
GET /users/{id}
POST /users



Request Validation

Use Pydantic models for request validation.

Example

from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str



Dependency Injection

Use FastAPI dependency injection for shared services.



Separation of Concerns

API layer must only

- Validate input
- Call service layer
- Return response

Business logic must stay in service layer.