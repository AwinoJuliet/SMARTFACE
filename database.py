import sqlite3

# Connect to the SQLite database
def connect_db():
    return sqlite3.connect("smartface.db")

# Create necessary tables (Users table)
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create table for user details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_no TEXT NOT NULL,
            year TEXT,
            image_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Optional: Insert new user (helper function)
def insert_user(name, reg_no, year, image_path):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, reg_no, year, image_path)
        VALUES (?, ?, ?, ?)
    ''', (name, reg_no, year, image_path))
    conn.commit()
    conn.close()

# Optional: Fetch user by name (for checking registered faces)
def get_user_by_name(name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    return result
