from pydantic import BaseModel
from typing import Optional


class Model_UserRegister(BaseModel):
    username: str
    name: str
    password: str
    profilePicture: Optional[str] = None

class Model_Login(BaseModel):
    username: str
    password: str