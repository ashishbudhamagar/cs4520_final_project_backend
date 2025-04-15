import sqlite3



def validateToken(user_id: int, token: str) -> bool:
    try:
        connection = sqlite3.connect('CapRank.db')
        cursor = connection.cursor()
        cursor.execute("SELECT token FROM User WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if result is None:
            return False
        return result[0] == token
    
    finally:
        connection.close()