from litestar import get,patch, Controller, status_codes, delete
from litestar.exceptions import HTTPException
import sqlite3

from modules.data_types import Model_User


class Controller_User(Controller):
    path = "/users"

    @get('/')
    async def getAllUsers(self) -> dict:

        try:

            connection = sqlite3.connect('CapRank.db')
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            command = """
                SELECT * FROM User
            """

            cursor.execute(command)
            result = cursor.fetchall()
            connection.close()
            usersWithoutPassword = [[elm[1],elm[2], elm[4]] for elm in result]

            return {
                'status': 'green',
                'message': 'Queried all users',
                'data': usersWithoutPassword

                }

        except Exception as e:

            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=f"Error: {e}"
            )



    @get("/{username:str}")
    async def getUser(self, username: dict) -> dict:
        try:
            connection = sqlite3.connect('CapRank.db')
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            command ="""
                SELECT * FROM User
                WHERE username = ?
            """

            cursor.execute(command, (username,))
            result = cursor.fetchone()
            connection.close()

            if result:
                return {
                    'status': 'green',
                    'message': 'Successfully queried a user',
                    'data': {
                        'username': result[1],
                        'name': result[2],
                        'profilePicture': result[4]
                    }
                }
            return {
                'status': 'red',
                'message': 'No user with that username found'
            }


        except Exception as e:

            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=f"Error: {e}"
            )
    


    @patch('/', status_code=status_codes.HTTP_200_OK)
    async def updateUser(self, updatedData: dict) -> dict:

        try:
            command = """
                UPDATE User
                Set username = ?, name = ?, password = ?, profilePicture = ?
                WHERE id = ? and password = ?
            """

            connection = sqlite3.connect('CapRank.db')
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()

            cursor.execute(command, (updatedData.username, updatedData.name, updatedData.password, updatedData.profilePicture, updatedData.id, updatedData.password))
            connection.commit()
            connection.close()

            return {
                    'status': 'green',
                    'message': 'Updated user',

                    }

        except Exception as e:
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=f"ERROR: {e}"
            )






    @delete('/', status_code=status_codes.HTTP_200_OK)
    async def deleteUser(self, deleteUser: dict) -> dict:

        try:
            command = """
                DELETE FROM User
                WHERE id = ? and password ?
            """
            connection = sqlite3.connect('CapRank.db')
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()
            cursor.execute(command, (deleteUser.id, deleteUser.password))
            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Deleted user',
            }


        except Exception as e:
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=f"ERROR: {e}"
            )




