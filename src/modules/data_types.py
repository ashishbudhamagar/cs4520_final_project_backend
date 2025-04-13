from pydantic import BaseModel, Field
from typing import Optional



class DT_UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    name: str = Field(..., min_length=1, max_length=30)
    password: str = Field(..., min_length=3, max_length=20)
    profilePicture: Optional[str] = None


class DT_UserLogin(BaseModel):
    username: str = Field(...)
    password: str = Field(...)