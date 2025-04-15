from litestar import Controller, post, status_codes
from litestar.exceptions import HTTPException
from litestar.params import Body

import sqlite3
import uuid
import os

from pathlib import Path


from modules.data_types import DT_UserRegister, DT_UserLogin



BASE_DIR = Path(__file__).parent.parent  
DEFAULT_PROFILE_PIC = BASE_DIR / "profile_images" / "deault_profile_image.jpg"

CUSTOM_PROFILE_FOLDER = BASE_DIR / "profile_images"



class Controller_LoginAndRegister(Controller):
    

    @post('/register', status_code=status_codes.HTTP_201_CREATED)
    async def register(self, data: DT_UserRegister) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                SELECT *
                FROM User
                WHERE username = ?
            """, (data.username,))


            userQueried = cursor.fetchone()

            if userQueried != None:
                raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail="Username already exists, choose a differnet one")
            


            profile_pic_path = "profile_images/default_profile_image.jpg"
    

            cursor.execute("""
                INSERT INTO
                User (username, name, password)
                    VALUES(?,?,?)
            """, (data.username, data.name, data.password ))

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User successfully created'
            }
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail=f"ERROR: {e}")


    @post('/login', status_code=status_codes.HTTP_200_OK)
    async def login(self, data: DT_UserLogin) -> dict:
        try:


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                SELECT *
                FROM User
                WHERE username = ? and password = ?
            """, (data.username, data.password))

            userQueried = cursor.fetchone()


            if userQueried == None:
                raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail="Username or password incorrect")

            authToken = str(uuid.uuid4())

            cursor.execute("UPDATE User SET token = ? WHERE id = ?", (authToken, userQueried[0]))
            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User successfully loggedin',
                "data": {
                        "userId": userQueried[0],
                        "username": userQueried[1],
                        "name": userQueried[2],
                        "profilePicture": userQueried[4],
                        "token": authToken
                    }
            }
        

        except Exception as e:
            print(e)
            raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail=f"ERROR: {e}")

    