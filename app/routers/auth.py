from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory storage for demo purposes
users_db: dict[str, User] = {}
current_id = 0

http_bearer = HTTPBearer()


def get_current_user(credentials = Depends(http_bearer)) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception

    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password. The username and email must be unique.",
    response_description="The created user information",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "johndoe",
                        "is_active": True,
                    }
                }
            },
        },
        400: {
            "description": "Registration failed",
            "content": {
                "application/json": {
                    "examples": {
                        "username_taken": {
                            "summary": "Username already exists",
                            "value": {"detail": "Username already registered"},
                        },
                        "email_taken": {
                            "summary": "Email already exists",
                            "value": {"detail": "Email already registered"},
                        },
                    }
                }
            },
        },
    },
)
def register(user_data: UserCreate):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **username**: Unique username (3-50 characters)
    - **password**: Password (minimum 8 characters)
    """
    global current_id

    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    for user in users_db.values():
        if user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    current_id += 1
    user = User(
        id=current_id,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    users_db[user_data.username] = user

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get tokens",
    description="Authenticate with username and password to receive access and refresh tokens. Use the access token in the Authorization header for protected endpoints.",
    response_description="Access and refresh tokens",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Inactive user",
            "content": {
                "application/json": {
                    "example": {"detail": "Inactive user"}
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        },
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate and receive JWT tokens.

    This endpoint uses OAuth2 password flow. Send credentials as form data:
    - **username**: Your username
    - **password**: Your password

    Returns access and refresh tokens on successful authentication.
    """
    user = users_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Use a valid refresh token to obtain a new access token and refresh token pair. The old refresh token will be invalidated.",
    response_description="New access and refresh tokens",
    responses={
        200: {
            "description": "Tokens refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid refresh token"},
                        },
                        "user_not_found": {
                            "summary": "User not found",
                            "value": {"detail": "User not found"},
                        },
                    }
                }
            },
        },
    },
)
def refresh_token(token_data: TokenRefresh):
    """
    Refresh authentication tokens.

    - **refresh_token**: Valid refresh token from previous login or refresh
    """
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    username = payload.get("sub")
    user = users_db.get(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the profile information of the currently authenticated user. Requires a valid access token.",
    response_description="Current user information",
    responses={
        200: {
            "description": "User information retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "johndoe",
                        "is_active": True,
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
    },
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Requires authentication via Bearer token in the Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the password for the currently authenticated user. Requires the current password for verification.",
    response_description="Password change confirmation",
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Password updated successfully"}
                }
            },
        },
        400: {
            "description": "Current password incorrect",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect current password"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
    },
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
):
    """
    Change the current user's password.

    - **current_password**: Your current password for verification
    - **new_password**: New password (minimum 8 characters)

    Requires authentication via Bearer token.
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    current_user.hashed_password = hash_password(password_data.new_password)
    return MessageResponse(message="Password updated successfully")


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Logout the current user. In a production environment, this would invalidate the user's tokens.",
    response_description="Logout confirmation",
    responses={
        200: {
            "description": "Logged out successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            },
        },
    },
)
def logout():
    """
    Logout the current user.

    Note: In this demo implementation, tokens are not invalidated server-side.
    In production, you would add the token to a blacklist or use a token store.
    """
    return MessageResponse(message="Successfully logged out")
