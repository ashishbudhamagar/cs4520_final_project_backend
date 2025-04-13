from litestar import get, post, put, delete, Controller, status_codes
from litestar.exceptions import HTTPException
import sqlite3



class Controller_Post(Controller):
    path = "/post"

    @get('/')
    async def getPost(postId: int) -> dict:


        connection = sqlite3.connect('CapRank.db')
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()

        command = """
            SELECT * 
            FROM Post
            WHERE id = ?
        """

        cursor.execute(command, (postId,))

        result = cursor.fetchone()

        if result:
            return {
                'status': 'green',
                'message': 'Successfully post queired',
                'data': result
            }
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=f"ERROR: {e}"
        )
    
