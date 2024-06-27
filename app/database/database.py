import json
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv

load_dotenv()

with open('data/character.json', 'r') as file:
    data = json.load(file)




characters = []
for character in data['data']['results']:
    char_id = character['id']
    name = character['name']
    description = character['description']
    characters.append((char_id, name, description))
try:

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heroes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    cursor.executemany('INSERT INTO heroes (id, name, bio) VALUES (%s, %s, %s)', characters)

    cursor.execute('''
                CREATE TABLE IF NOT EXISTS hero_list (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    rating INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                )
            ''')

    conn.commit()
    conn.close()

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")
