import sqlite3


def setupDatabase():
    databaseName = 'CapRank.db'
    connection = sqlite3.connect(databaseName)
    connection.execute("PRAGMA foreign_keys = ON;")
    cursor = connection.cursor()

    schemaCommand = """

    CREATE TABLE IF NOT EXISTS 
        User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            profilePicture TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

    CREATE TABLE IF NOT EXISTS 
        Post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            image TEXT NOT NULL,
            caption TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            topCaptionId INTEGER,
            
            FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
            FOREIGN KEY (topCaptionId) REFERENCES Caption(id) ON DELETE SET NULL
        );

    CREATE TABLE IF NOT EXISTS 
        Caption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postId INTEGER NOT NULL,
            userId INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,

            FOREIGN KEY (postId) REFERENCES Post(id) ON DELETE CASCADE,
            FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE
        );
    """

    cursor.executescript(schemaCommand)
    connection.commit()
    connection.close()