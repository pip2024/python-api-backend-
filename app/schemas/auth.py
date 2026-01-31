from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the account",
        json_schema_extra={"example": "johndoe"},
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        json_schema_extra={"example": "securepassword123"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "johndoe",
                    "password": "securepassword123",
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(
        ...,
        description="Username",
        json_schema_extra={"example": "johndoe"},
    )
    password: str = Field(
        ...,
        description="Password",
        json_schema_extra={"example": "securepassword123"},
    )


class UserResponse(BaseModel):
    """Schema for user information in responses."""

    id: int = Field(
        ...,
        description="Unique user identifier",
        json_schema_extra={"example": 1},
    )
    email: str = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    username: str = Field(
        ...,
        description="Username",
        json_schema_extra={"example": "johndoe"},
    )
    is_active: bool = Field(
        ...,
        description="Whether the user account is active",
        json_schema_extra={"example": True},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "is_active": True,
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(
        ...,
        description="JWT access token for API authentication",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token for obtaining new access tokens",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        json_schema_extra={"example": "bearer"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                }
            ]
        }
    }


class TokenRefresh(BaseModel):
    """Schema for refreshing access token."""

    refresh_token: str = Field(
        ...,
        description="The refresh token obtained from login",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )


class PasswordChange(BaseModel):
    """Schema for changing user password."""

    current_password: str = Field(
        ...,
        description="Current password for verification",
        json_schema_extra={"example": "oldpassword123"},
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)",
        json_schema_extra={"example": "newpassword456"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "oldpassword123",
                    "new_password": "newpassword456",
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str = Field(
        ...,
        description="Response message",
        json_schema_extra={"example": "Operation completed successfully"},
    )
