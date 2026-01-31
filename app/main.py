from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers import items, auth

app = FastAPI(
    title="Python API Backend",
    description="""
A RESTful API backend with authentication and item management.

## Features

* **Authentication** - JWT-based auth with access and refresh tokens
* **User Management** - Register, login, and manage user accounts
* **Items** - CRUD operations for items

## Authentication

This API uses OAuth2 with JWT tokens. To authenticate:

1. Register a new account via `/api/v1/auth/register`
2. Login via `/api/v1/auth/login` to get access and refresh tokens
3. Include the access token in the `Authorization` header: `Bearer <token>`
4. Use `/api/v1/auth/refresh` to get a new access token when it expires
""",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints for monitoring and load balancers.",
        },
        {
            "name": "auth",
            "description": "Authentication operations including registration, login, and token management.",
        },
        {
            "name": "items",
            "description": "CRUD operations for managing items.",
        },
    ],
)

app.include_router(items.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get(
    "/",
    tags=["health"],
    summary="Root endpoint",
    description="Returns a welcome message. Use this to verify the API is running.",
    response_description="Welcome message",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {"message": "Welcome to the API"}
                }
            },
        }
    },
)
def root():
    return {"message": "Welcome to the API"}


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns the health status of the API. Use this for load balancer health checks and monitoring.",
    response_description="Health status",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"}
                }
            },
        }
    },
)
def health_check():
    return {"status": "healthy"}
