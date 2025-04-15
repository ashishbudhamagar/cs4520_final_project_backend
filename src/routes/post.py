from litestar import Controller, get, status_codes, post, patch,delete
from litestar.exceptions import HTTPException
from litestar.params import Body
import sqlite3

import uuid
import os

from modules.data_types import DT_PostGet, DT_PostCreate

postImageFolder = '../src/user_post_images'


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



    @post('/', status_codes=status_codes.HTTP_201_CREATED)
    async def createPost(self, data: DT_PostCreate = Body(media_type="multipart/form-data")) -> dict:
        try:

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            cursor.execute("""
                SELECT *
                FROM User
                WHERE id = ? and password = ?
            """, (data.userId, data.password))

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


    # /post/postId_userId_password
    @delete('/{postIdUserIdPassword:str}', status_code=status_codes.HTTP_200_OK)
    async def deletePost(self, postIdUserIdPassword: str) -> dict:

        try:

            postIdUserIdPassword = postIdUserIdPassword.split("_")


            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM User WHERE id = ? and password = ? ", (postIdUserIdPassword[1], postIdUserIdPassword[2]))
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete")
            
            
            cursor.execute("SELECT * FROM Post WHERE id = ? and userId = ? ", (postIdUserIdPassword[0], postIdUserIdPassword[1]))
            queriedPost = cursor.fetchone() 

            if queriedPost == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete someone else post")
            

            cursor.execute("DELETE FROM Post WHERE id = ?", (postIdUserIdPassword[0],))
            connection.commit()
            connection.close()
            

            return {
                'status': 'green',
                'message': 'Post deleted',
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")
    



    # /post/postId_userId_password
    @patch('/{postIdUserIdPassword: str}', status_code=status_codes.HTTP_200_OK)
    async def updatePost(self, postIdUserIdPassword: str) -> dict:

        try:

            postIdUserIdPassword = postIdUserIdPassword.split("_")

            connection = sqlite3.connect('CapRank.db')
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM User WHERE id = ? and password = ? ", (postIdUserIdPassword[1], postIdUserIdPassword[2]))
            queriedUser = cursor.fetchone()

            if queriedUser == None:
                raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"Unathorized to delete")
            

            cursor.execute('SELECT * FROM UserLikedPosts where userId = ? and postId = ?', (postIdUserIdPassword[1], postIdUserIdPassword[0]))
            queriedUserLiked = cursor.fetchone()


            if queriedUserLiked == None:
                
                print("BERE")
                cursor.execute("""
                    UPDATE Post
                    SET likes = likes + 1
                    WHERE id = ?
                """, (postIdUserIdPassword[0],))

                cursor.execute("""
                    INSERT INTO
                    UserLikedPosts (userId, postId)
                        Values(?,?)
                """, (postIdUserIdPassword[1], postIdUserIdPassword[0]))

            else:
                cursor.execute("""
                    UPDATE Post
                    SET likes = likes - 1
                    WHERE id = ?
                """, (postIdUserIdPassword[0],))

                cursor.execute("""
                    DELETE FROM UserLikedPosts
                    WHERE userId = ? and postId = ?
                """, (postIdUserIdPassword[1], postIdUserIdPassword[0]))


            connection.commit()
            connection.close()

            return {
                'status': 'green',
                'message': 'Post like updated',
            }
        
        except Exception as e:
            raise HTTPException(status_code=status_codes.HTTP_404_NOT_FOUND, detail=f"ERROR: {e}")