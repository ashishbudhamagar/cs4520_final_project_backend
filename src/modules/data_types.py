from pydantic import BaseModel, Field, ConfigDict
from litestar.datastructures import UploadFile

from typing import Optional, Annotated


class DT_UserRegister(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: Annotated[str, Field(min_length=3, max_length=30)]
    name: Annotated[str, Field(min_length=1, max_length=30)]
    password: Annotated[str, Field(min_length=3, max_length=30)]
    profilePicture: Optional[UploadFile] = None


class DT_UserLogin(BaseModel):
    username: Annotated[str, Field(min_length=1)]
    password: Annotated[str, Field(min_length=1)]


class DT_UserUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    userId: Annotated[int, Field(ge=1)]
    currentPassword: Annotated[str, Field(min_length=1)]

    newUsername: Optional[Annotated[str, Field(min_length=3, max_length=30)]] = None
    newName: Optional[Annotated[str, Field(min_length=1, max_length=30)]] = None
    newPassword: Optional[Annotated[str, Field(min_length=3, max_length=30)]] = None
    newProfilePicture: Optional[UploadFile] = None


class DT_UserDelete(BaseModel):
    userId: Annotated[int, Field(ge=1)]
    password: Annotated[str, Field(min_length=1)]




class DT_PostCreate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    userId: Annotated[int, Field(ge=1)]
    token: Annotated[str, Field(min_length=1)]
    image: UploadFile
    userCaptionText: Optional[Annotated[str, Field(min_length=1, max_length=300)]] = None


class DT_CaptionCreate(BaseModel):
    postId: Annotated[int, Field(ge=1)]
    userId: Annotated[int, Field(ge=1)]
    token: Annotated[str, Field(min_length=1)]
    text: Annotated[str, Field(min_length=1)]


class DT_PostDeleteAndUpdate(BaseModel):
    postId: Annotated[int, Field(ge=1)]
    userId: Annotated[int, Field(ge=1)]
    token: Annotated[str, Field(min_length=1)]


class DT_CaptionDeleteAndUpdate(BaseModel):
    captionId: Annotated[int, Field(ge=1)]
    userId: Annotated[int, Field(ge=1)]
    token: Annotated[str, Field(min_length=1)]




