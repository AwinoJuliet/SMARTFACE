import sqlite3

DB_FILE = 'users.db'

def reset_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS UserDetails")

    # Recreate the tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE UserDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT NOT NULL,
            full_name TEXT NOT NULL,
            year_of_registration TEXT NOT NULL,
            face_image_path TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database reset successfully!")

# Run it
reset_database()
