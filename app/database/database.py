import json
import sqlite3

from dotenv import load_dotenv

load_dotenv()

with open('data/nvidia.json', 'r') as file:
    data = json.load(file)

gpus = []
for gpu in data['gpus']:
    name = gpu['name']
    release_date = gpu['release_date']
    vram = gpu['vram']
    series = gpu['series']
    picture = gpu['picture']
    gpus.append((name, release_date, vram, series, picture))
try:

    conn = sqlite3.connect('database/werk.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nvidia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            release_date TEXT NOT NULL,
            vram TEXT NOT NULL,
            series TEXT NOT NULL,
            picture TEXT NOT NULL
        )
        ''')

    cursor.executemany('INSERT INTO nvidia (name, release_date, vram, series, picture ) VALUES (?, ?, ?, ?, ?)',
                       gpus)

    conn.commit()
    conn.close()
    print('Data inserted successfully')

except Exception as e:
    print(e)
