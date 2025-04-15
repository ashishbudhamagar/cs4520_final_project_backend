from litestar import Controller, get, status_codes, post, patch, delete
from litestar.exceptions import HTTPException

from modules.data_types import DT_CaptionCreate

import sqlite3





class Controller_Caption(Controller):

    path = '/caption'



    @get("/{captionId:int}", status_code=status_codes.HTTP_200_OK)
    async def getCaption(self, captionId: int) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM Caption
                WHERE id = ?
            """, (captionId,))


            queriedCaption = cursor.fetchone()
            connection.close()

            if queriedCaption == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"No caption with id: {captionId}")
            
            return {
                'status': 'green',
                'message': 'Caption queried successfully',
                'data': queriedCaption
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')



    @get("/post/{postId:int}", status_code=status_codes.HTTP_200_OK)
    async def getCaptionsByPost(self, postId: int) -> dict:
        try:
            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM Caption
                WHERE postId = ?
                ORDER BY likes DESC, created_at ASC
            """, (postId,))

            queriedCaptions = cursor.fetchall()
            connection.close()
            
            return {
                'status': 'green',
                'message': 'Captions for post queried successfully',
                'data': queriedCaptions
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')


    @get("/", status_code=status_codes.HTTP_200_OK)
    async def getAllCaptions(self) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM Caption
                ORDER BY created_at DESC
            """)

            queriedCaptions = cursor.fetchall()
            connection.close()
            
            return {
                'status': 'green',
                'message': 'All captions queried successfully',
                'data': queriedCaptions
            }
        

        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')




    @post('/', status_code=status_codes.HTTP_201_CREATED)
    async def createCaption(self, data: DT_CaptionCreate) -> dict:
        try:


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            

            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? AND password = ?
            """, (data.userId, data.password))


            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unauthorized to make caption")
            

            cursor.execute("""
                SELECT *
                FROM Post
                WHERE id = ?
            """, (data.postId,))

            queriedPost = cursor.fetchone()

            if queriedPost == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"No post with id: {data.postId}")
            

            
            cursor.execute("""
                INSERT INTO
                Caption (postId, userId, text, likes)
                VALUES (?, ?, ?, ?)
            """, (data.postId, data.userId, data.text, 0))


            
            cursor.execute("""
                SELECT *
                FROM Caption
                WHERE userId = ? and postId = ?
            """, (data.userId, data.postId))


            newCaption = cursor.fetchone()

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Caption created successfully',
                'data': newCaption
            }
        
        except Exception as e:
            print("ERROR:", e)
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')



    # /caption/captionId_userId_password
    @delete('/{captionIdUserIdPassword:str}', status_code=status_codes.HTTP_200_OK)
    async def deleteCaption(self, captionIdUserIdPassword: str) -> dict:
        try:


            captionIdUserIdPassword = captionIdUserIdPassword.split("_")
            captionId = captionIdUserIdPassword[0]
            userId = captionIdUserIdPassword[1]
            password = captionIdUserIdPassword[2]

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")


            cursor.execute("""
                SELECT * 
                FROM User 
                WHERE id = ? AND password = ? 
            """, (userId, password))
            
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unauthorized to delete caption")
            
            
            cursor.execute("""
                SELECT * 
                FROM Caption 
                WHERE id = ? AND userId = ? 
            """, (captionId, userId))
            
            queriedCaption = cursor.fetchone()

            if queriedCaption is None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unable to delete someone else caption")
            
            cursor.execute("""
                SELECT postId 
                FROM Caption 
                WHERE id = ?
            """, (captionId,))
            
            postId = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT topCaptionId 
                FROM Post 
                WHERE id = ?
            """, (postId,))
            
            topCaptionId = cursor.fetchone()[0]

            cursor.execute("""
                DELETE FROM Caption 
                WHERE id = ?
            """, (captionId,))
            
            if str(topCaptionId) == captionId:


                cursor.execute("""
                    SELECT id 
                    FROM Caption 
                    WHERE postId = ? 
                    ORDER BY likes DESC 
                    LIMIT 1
                """, (postId,))
                
                newTopCaption = cursor.fetchone()

                
                if newTopCaption is None:
                    cursor.execute("""
                        UPDATE Post 
                        SET topCaptionId = NULL 
                        WHERE id = ?
                    """, (postId,))
                else:
                    cursor.execute("""
                        UPDATE Post 
                        SET topCaptionId = ? 
                        WHERE id = ?
                    """, (newTopCaption[0], postId))

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Caption deleted successfully'
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")




    # /caption/captionId_userId_password
    @patch('/{captionIdUserIdPassword:str}', status_code=status_codes.HTTP_200_OK)
    async def updateCaptionLikes(self, captionIdUserIdPassword: str) -> dict:

        try:
            captionIdUserIdPassword = captionIdUserIdPassword.split('_')

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")



            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and password = ?
            """, (captionIdUserIdPassword[1], captionIdUserIdPassword[2]))

            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unauthorized to delete caption")
                
            
            cursor.execute("""
                SELECT *
                FROM Caption
                WHERE id = ?
            """, (captionIdUserIdPassword[0],))

            queriedCaption = cursor.fetchone()

            if queriedCaption == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="no caption with that id")
                

            cursor.execute("""
                SELECT *
                FROM UserLikedCaptions
                WHERE userId = ? and captionId = ?
            """, (captionIdUserIdPassword[1], captionIdUserIdPassword[0]))



            queriedLikedCaptions = cursor.fetchone()

            if queriedLikedCaptions == None:
                
                cursor.execute("""
                    UPDATE Caption
                    SET likes = likes + 1
                    WHERE id = ?
                """, (captionIdUserIdPassword[0],))

                cursor.execute("""
                    INSERT INTO
                    UserLikedCaptions (userId, captionId)
                        Values(?,?)
                """, (captionIdUserIdPassword[1], captionIdUserIdPassword[0]))


            else:
                cursor.execute("""
                    UPDATE Caption
                    SET likes = likes - 1
                    WHERE id = ?
                """, (captionIdUserIdPassword[0],))

                cursor.execute("""
                    DELETE FROM UserLikedCaptions
                    WHERE userId = ? and postId = ?
                """, (captionIdUserIdPassword[1], captionIdUserIdPassword[0]))


            cursor.execute("SELECT *  FROM Caption where postId = ?", (queriedCaption[1],))
            queriedPost = cursor.fetchone()


            cursor.execute("SELECT id FROM Caption WHERE postId + ? Order by likes DESC LIMIT 1", (queriedCaption[1]))

            highestLikedCaptionId = cursor.fetchone()

            if highestLikedCaptionId == captionIdUserIdPassword[0] and queriedPost[5] != highestLikedCaptionId:
                cursor.execute("Update Post SET topCaptionId = ? Where id = ?", (queriedCaption[0], queriedCaption[1]))


            connection.commit()
            connection.close()


            return {
                'status': 'green',
                'message': 'Caption updated successfully'
            }
        

        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")



