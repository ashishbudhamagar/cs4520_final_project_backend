from litestar import Controller, post, status_codes
from litestar.exceptions import HTTPException
from modules.data_types import Model_Login, Model_UserRegister
import sqlite3


databaseName = 'CapRank.db'

class Controller_LoginAndRegister(Controller):

    @post('/register')
    async def register(self, data: Model_UserRegister) -> dict:

        try:
            command = """
                INSERT INTO
                    User (username, name, password, profilePicture)
                    Values (?,?,?,?)
                """

            connection = sqlite3.connect(databaseName)
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            cursor.execute(command, (data.username, data.name, data.password, data.profilePicture))
            connection.commit()
            connection.close()

            return {
                "status": "green",
                "message": "User successfully registered"
            }

        except Exception as e:
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )



    @post('/login')
    async def login(self, data: Model_Login) -> dict:
        try:
            connection = sqlite3.connect(databaseName)
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            command = """
                SELECT * FROM User
                WHERE username = ? and password = ?
            """

            cursor.execute(command, (data.username, data.password))
            result = cursor.fetchall()

            if len(result) == 1:
                return {
                    "status": 'green',
                    'message': 'Correct username and password'
                }

            return {
                'status': 'red',
                'message': 'Incorrect username or password'
            }
        
        except Exception as e:
            print("ERROR: ",e)

            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=f"Error: {e}"
            )