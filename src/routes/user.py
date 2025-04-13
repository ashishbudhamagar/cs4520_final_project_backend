from litestar import Controller, get,patch, status_codes, delete
from litestar.exceptions import HTTPException
import  sqlite3

from modules.data_types import DT_UserUpdate, DT_UserDelete


class Controller_User(Controller):
    path = '/users'


    @get('/{userId:int}', status_code=status_codes.HTTP_200_OK)
    async def getUser(self, userId: int) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("""
                SELECT username, name, profilePicture, created_at
                FROM User
                WHERE id = ?
            """, (userId,))

            queriedUser = cursor.fetchone()
            connection.close()

            if queriedUser == None:
                print(5)
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"No user with id: {userId} exists")

            return {
                'status': 'green',
                'message': 'User exists and queried',
                'data': {
                    'username': queriedUser[0],
                    'name': queriedUser[1],
                    'profilePicture': queriedUser[2],
                    'created_at': queriedUser[3],
                }
            }
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
        
    

    @get('/', status_code=status_codes.HTTP_200_OK)
    async def getAllUsers(self) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT username, name, profilePicture, created_at
                FROM User
            """)

            allQueriedUsers = cursor.fetchall()
            connection.close()

            return {
                'status': 'green',
                'message': 'User exists and queried',
                'data': allQueriedUsers
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
        


    
    @patch('/', status_code=status_codes.HTTP_200_OK)
    async def updateUser(self, data: DT_UserUpdate ) -> str:
        print("HERE")
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and password = ?
            """, (data.userId, data.password))

            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Password is incorrect")
            

            updatValues = []
            updateFields = []

            if data.newUsername:
                updatValues.append(data.newUsername)
                updateFields.append("username = ?")
            if data.newName:
                updatValues.append(data.newName)
                updateFields.append("name = ?")
            if data.newPassword:
                updatValues.append(data.newPassword)
                updateFields.append("password = ?")
            if data.newProfilePicture:
                updatValues.append(data.newProfilePicture)
                updateFields.append("profilePicture = ?")

            updatValues.append(data.userId)
            commandUpdateUser = f"""
                Update User
                SET {', '.join(updateFields)}
                WHERE id = ?
            """
            cursor.execute(commandUpdateUser, updatValues)

            cursor.execute("""
                SELECT username, name, profilePicture, created_at
                FROM User
                WHERE id = ?
            """, (data.userId))
            
            updatedUser = cursor.fetchone()
            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User updated',
                'data': updatedUser
            }
        
        except Exception as e:
            print("Eeor:", e)
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
        



    @delete('/', status_code=status_codes.HTTP_200_OK)
    async def deleteUser(self, data: DT_UserDelete) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and password = ?
            """, (data.userId, data.password))

            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Password is incorrect")
            
            cursor.execute("""
                DELETE User
                WHERE id = ?
            """, (data.userId,))

            deletedUser = cursor.fetchone()
            print("delted", deletedUser)

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User deleted',
            }
    
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
