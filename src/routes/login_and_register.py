from litestar import Controller, get, post, status_codes
from litestar.exceptions import HTTPException
import sqlite3

from src.modules.data_types import DT_UserRegister, DT_UserLogin




class Controller_LoginAndRegister(Controller):



    # @post('/register', status_code=status_codes.HTTP_201_CREATED)
    @post('/register')
    async def register(userData: DT_UserCreate) -> dict:

        # validate it if pydantic doesnt

        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("""
                SELECT *
                FROM User
                WHERE username = ?
            """, (userData.username,))
            
            userQueried = cursor.fetchone()

            if userQueried is None:
                raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail="Username already choosen, choose a different one")

            cursor.execute("""
                INSET INTO
                User (username, name, password, profilePicture)
                    VALUES(?,?,?,?)
            """, (userData.username, userData.name, userData.password, userData.profilePicture))

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User successfully created'
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_406_NOT_ACCEPTABLE, detail=f"ERROR: {e}")







    @post('/login')
    async def login(userData: DT_UserLogin) -> dict:

        try:
            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM User
                WHERE username = ? and password = ?
            """, (userData.username, userData.password))

            userQueried = cursor.fetchone()
            connection.close()


            if userQueried is None:
                raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail="Username or password incorrect")


            return {
                'status': 'green',
                'message': 'User successfully created',
                'data': {
                    'username': userQueried[1],
                    'name': userQueried[2],
                    'profilePicture': userQueried[4],
                    'created_at': userQueried[5]
                }
            }
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_400_BAD_REQUEST, detail=f"ERROR: {e}")

        
