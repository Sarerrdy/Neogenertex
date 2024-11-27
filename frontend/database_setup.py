import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('tether_menu_users.db')

# Create a cursor object
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        expiry_time TEXT,
        duration INTEGER
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
