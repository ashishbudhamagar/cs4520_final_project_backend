from pydantic import BaseModel
from typing import Optional


class Model_User(BaseModel):
    username: str
    name: str
    password: str
    profilePicture: Optional[str] = None

class Model_Login(BaseModel):
    username: str
    password: str



# class Model_Post(BaseModel):
#     id: int


#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#     userId INTEGER NOT NULL,
#     image TEXT NOT NULL,
#     caption TEXT,
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#     likes INTEGER DEFAULT 0,
#     topCaptionId INTEGER,
    
#     FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
#     FOREIGN KEY (topCaptionId) REFERENCES Caption(id) ON DELETE SET NULL