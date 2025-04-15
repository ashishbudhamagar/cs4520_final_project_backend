from litestar import Controller, get, status_codes, post, patch, delete
from litestar.exceptions import HTTPException

from modules.data_types import DT_CaptionCreate, DT_CaptionDeleteAndUpdate

import sqlite3
from modules.functions import validateToken





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
                WHERE id = ? AND token = ?
            """, (data.userId, data.token))


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
                WHERE id = ?
            """, (cursor.lastrowid,))


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



    @delete('/', status_code=status_codes.HTTP_200_OK)
    async def deleteCaption(self, data: DT_CaptionDeleteAndUpdate) -> dict:
        try:

            if not validateToken(data.userId, data.token):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED, detail="Invalid token")


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")


            cursor.execute("""
                SELECT * 
                FROM User 
                WHERE id = ? AND token = ? 
            """, (data.userId, data.token))
            
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unauthorized to delete caption")
            
            
            cursor.execute("""
                SELECT * 
                FROM Caption 
                WHERE id = ? AND userId = ? 
            """, (data.captionId, data.userId))
            
            queriedCaption = cursor.fetchone()

            if queriedCaption is None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unable to delete someone else caption")
            
            cursor.execute("""
                SELECT postId 
                FROM Caption 
                WHERE id = ?
            """, (data.captionId,))
            
            postId = cursor.fetchone()[1]
            
            cursor.execute("""
                SELECT topCaptionId 
                FROM Post 
                WHERE id = ?
            """, (postId,))
            
            topCaptionId = cursor.fetchone()

            cursor.execute("""
                DELETE FROM Caption 
                WHERE id = ?
            """, (data.captionId,))
            
            if str(topCaptionId) == data.captionId:


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




    @patch('/', status_code=status_codes.HTTP_200_OK)
    async def updateCaptionLikes(self, data: DT_CaptionDeleteAndUpdate) -> dict:
        try:


            if not validateToken(data.userId, data.token):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED, detail="Invalid token")

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                SELECT id
                FROM User
                WHERE id = ? AND token = ?
            """, (data.userId, data.token))

            queriedUser = cursor.fetchone()

            if queriedUser is None:
                raise HTTPException( status_code=status_codes.HTTP_404_NOT_FOUND, detail="Unauthorized to toggle caption likes")
            

            cursor.execute("""
                SELECT id, postId, likes
                FROM Caption
                WHERE id = ?
            """, (data.captionId,))

            queriedCaption = cursor.fetchone()

            if queriedCaption is None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail="No caption with that id")

            captionId = queriedCaption[0]
            postId = queriedCaption[1]

            cursor.execute("""
                SELECT *
                FROM UserLikedCaptions
                WHERE userId = ? AND captionId = ?
            """, (data.userId, captionId))
            likedAlready = cursor.fetchone()

            if likedAlready is None:
                cursor.execute("""
                    UPDATE Caption
                    SET likes = likes + 1
                    WHERE id = ?
                """, (captionId,))

                cursor.execute("""
                    INSERT INTO UserLikedCaptions (userId, captionId)
                    VALUES (?, ?)
                """, (data.userId, captionId))

            else:
                cursor.execute("""
                    UPDATE Caption
                    SET likes = likes - 1
                    WHERE id = ?
                """, (captionId,))

                cursor.execute("""
                    DELETE FROM UserLikedCaptions
                    WHERE userId = ? AND captionId = ?
                """, (data.userId, captionId))


            cursor.execute(
                """
                SELECT id
                FROM Caption
                WHERE postId = ?
                ORDER BY likes DESC, created_at ASC
                LIMIT 1
                """,
                (postId,)
            )
            newTop = cursor.fetchone()



            if newTop is not None:
                newTopCaptionId = newTop[0]
                cursor.execute("""
                    UPDATE Post
                    SET topCaptionId = ?
                    WHERE id = ?
                """, (newTopCaptionId, postId))
            else:
                cursor.execute("""
                    UPDATE Post
                    SET topCaptionId = NULL
                    WHERE id = ?
                """, (postId,))

            connection.commit()
            connection.close()



            return {
                'status': 'green',
                'message': 'Caption like/unlike successfully'
            }

        except Exception as e:
            raise HTTPException(
                status_code=status_codes.HTTP_404_NOT_FOUND, 
                detail=f"ERROR: {e}"
            )