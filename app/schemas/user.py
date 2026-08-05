from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str

    email: EmailStr

    password: str


class UserResponse(BaseModel):
    id: int

    username: str

    email: EmailStr

    role: str

    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str
