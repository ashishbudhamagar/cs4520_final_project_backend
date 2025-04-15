from litestar import Controller, get, status_codes, post, patch,delete
from litestar.exceptions import HTTPException
from litestar.params import Body
import sqlite3

import uuid
import os

from modules.data_types import DT_PostCreate, DT_PostDeleteAndUpdate

from modules.functions import validateToken

postImageFolder = "user_post_images"


class Controller_Post(Controller):

    path = '/post'


    @get("/{postId:int}", status_code=status_codes.HTTP_200_OK)
    async def getPost(self, postId: int) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM Post
                WHERE id = ?
            """, (postId,))

            queriedPost = cursor.fetchone()

            if queriedPost == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"No post with id: {postId} found")
            
            return {
                'status': 'green',
                'message': 'Post queried successfully',
                'data': queriedPost
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')



    @get("/", status_code=status_codes.HTTP_200_OK)
    async def getAllPosts(self) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM Post
            """)

            queriedPosts = cursor.fetchall()

            return {
                'status': 'green',
                'message': 'Post queried successfully',
                'data': queriedPosts
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')



    @post('/', status_code=status_codes.HTTP_201_CREATED)
    async def createPost(self, data: DT_PostCreate = Body(media_type="multipart/form-data")) -> dict:
        try:

            if not validateToken(data.userId, data.token):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED, detail="Invalid token")


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and token = ?
            """, (data.userId, data.token))

            queriedPost = cursor.fetchone()

            if queriedPost == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unauthorized to post")
            


            fileExtension = os.path.splitext(data.image.filename)[1]
            fileName = f"{data.userId}_{uuid.uuid4().hex}{fileExtension}"

            imagePath = os.path.join(postImageFolder, fileName)

            with open(imagePath, 'wb') as f:
                f.write( await data.image.read())



            cursor.execute("""
                INSERT INTO
                Post (userId, imageName, likes, topCaptionId)
                    VALUES (?, ?, ?, ?)
            """, (data.userId, fileName, 0, None))

            newPostId = cursor.lastrowid


            if data.userCaptionText != None:
                cursor.execute("""
                    INSERT INTO
                    Caption (postId, userId, text, likes)
                        Values(?,?,?,?)
                """, (newPostId, data.userId, data.userCaptionText, 0))

                newCaptionId = cursor.lastrowid

                cursor.execute("""
                    UPDATE Post 
                        SET topCaptionId = ? 
                        WHERE id = ?
                """, (newCaptionId, newPostId))
            
            
            cursor.execute("""
                SELECT *
                FROM Post
                WHERE id = ?
            """, (newPostId,))

            newPostData = cursor.fetchone()

            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Post made successfully',
                'data': newPostData
            }
        
        except Exception as e:
            print("ERROR:",e)
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f'ERROR: {e}')


    @delete('/', status_code=status_codes.HTTP_200_OK)
    async def deletePost(self, data: DT_PostDeleteAndUpdate ) -> dict:

        try:

            if not validateToken(data.userId, data.token):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM User WHERE id = ? and token = ? ", (data.userId, data.token))
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete")
            
            
            cursor.execute("SELECT * FROM Post WHERE id = ? and userId = ? ", (data.postId, data.userId))
            queriedPost = cursor.fetchone() 

            if queriedPost == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete someone else post")
            

            cursor.execute("DELETE FROM Post WHERE id = ?", (data.postId))
            connection.commit()
            connection.close()
            

            return {
                'status': 'green',
                'message': 'Post deleted'
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
    



    @patch('/', status_code=status_codes.HTTP_200_OK)
    async def updatePost(self, data: DT_PostDeleteAndUpdate) -> dict:

        try:

            if not validateToken(data.userId, data.token):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED, detail="Invalid token")


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM User WHERE id = ? and token = ? ",(data.userId, data.token))
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete")
            

            cursor.execute('SELECT * FROM UserLikedPosts where userId = ? and postId = ?', (data.userId, data.postId))
            queriedUserLiked = cursor.fetchone()


            if queriedUserLiked == None:
                
                cursor.execute("""
                    UPDATE Post
                    SET likes = likes + 1
                    WHERE id = ?
                """, (data.postId,))

                cursor.execute("""
                    INSERT INTO
                    UserLikedPosts (userId, postId)
                        Values(?,?)
                """, (data.userId, data.postId))

            else:
                cursor.execute("""
                    UPDATE Post
                    SET likes = likes - 1
                    WHERE id = ?
                """, (data.postId,))

                cursor.execute("""
                    DELETE FROM UserLikedPosts
                    WHERE userId = ? and postId = ?
                """, (data.userId, data.postId))


            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Post like updated',
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")