import sqlite3
def get_db_connection():
    conn = sqlite3.connect('C:/Users/vdaja/Documents/werk/werk/app/database/database/werk.db')
    conn.row_factory = sqlite3.Row
    return conn