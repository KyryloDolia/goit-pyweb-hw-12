from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr, Field


# Contact schema
class ContactBase(BaseModel):
    first_name: constr(max_length=50)
    last_name: constr(max_length=50)
    email: EmailStr
    phone: Optional[constr(max_length=30)] = None
    birthday: Optional[date] = None

    class Config:
        orm_mode = True

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[constr(max_length=50)]
    last_name: Optional[constr(max_length=50)]
    email: Optional[EmailStr]
    phone: Optional[constr(max_length=30)] = None
    birthday: Optional[date] = None

    class Config:
        orm_mode = True

class ContactResponse(ContactBase):
    id: int
    created_at: datetime


# User schema
class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"