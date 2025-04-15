from litestar import Controller, get,patch, status_codes, delete
from litestar.exceptions import HTTPException
import  sqlite3

from modules.data_types import DT_UserUpdate, DT_UserDelete

from litestar.params import Body
import os, uuid
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
PROFILE_FOLDER = "profile_images"



class Controller_User(Controller):
    path = '/users'

    @get('/{userId:int}', status_code=status_codes.HTTP_200_OK)
    async def getUser(self, userId: int) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, username, name, profilePicture, created_at
                FROM User
                WHERE id = ?
            """, (userId,))

            queriedUser = cursor.fetchone()
            connection.close()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"No user with id: {userId} exists")

            return {
                'status': 'green',
                'message': 'User exists and queried',
                'data': queriedUser
            }
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
        
    

    @get('/', status_code=status_codes.HTTP_200_OK)
    async def getAllUsers(self) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, username, name, profilePicture, created_at
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
    async def updateUser(self, data: DT_UserUpdate = Body(media_type="multipart/form-data")) -> dict:
        try:
            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and password = ?
            """, (data.userId, data.currentPassword))
            queriedUser = cursor.fetchone()

            if queriedUser is None:
                raise HTTPException( status_code=status_codes.HTTP_404_NOT_FOUND, detail="Password is incorrect")



            updateValues = []
            updateFields = []

            if data.newUsername:
                updateValues.append(data.newUsername)
                updateFields.append("username = ?")

            if data.newName:
                updateValues.append(data.newName)
                updateFields.append("name = ?")

            if data.newPassword:
                updateValues.append(data.newPassword)
                updateFields.append("password = ?")

            if data.newProfilePicture:

                fileExtension = os.path.splitext(data.newProfilePicture.filename)[1]
                file_Name = f"user_{data.userId}_{uuid.uuid4().hex}{fileExtension}"


                profilePicPath = os.path.join(PROFILE_FOLDER, file_Name)

                full_save_path = os.path.join(BASE_DIR, PROFILE_FOLDER, file_Name)
                with open(full_save_path, "wb") as f:
                    f.write(await data.newProfilePicture.read())

                updateValues.append(profilePicPath)
                updateFields.append("profilePicture = ?")

            if not updateFields:
                raise HTTPException( status_code=status_codes.HTTP_400_BAD_REQUEST, detail="No update field given")

            updateValues.append(data.userId)

            commandUpdateUser = f"""
                UPDATE User
                SET {', '.join(updateFields)}
                WHERE id = ?
            """

            cursor.execute(commandUpdateUser, updateValues)

            cursor.execute("""
                SELECT id, username, name, profilePicture, created_at
                FROM User
                WHERE id = ?
            """, (data.userId,))
            updatedUser = cursor.fetchone()

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'User updated',
                'data': updatedUser
            }

        except Exception as e:
            raise HTTPException(
                status_code=status_codes.HTTP_404_NOT_FOUND, 
                detail=f"ERROR: {e}"
            )


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
                DELETE FROM User
                WHERE id = ?
            """, (data.userId,))


            connection.commit()
            connection.close()


            return {
                'status': 'green',
                'message': 'User deleted',
            }
    
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")