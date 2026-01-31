from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
