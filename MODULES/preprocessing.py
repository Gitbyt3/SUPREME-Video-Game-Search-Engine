import csv
import sqlite3
import json
import os
import pandas as pd

def create_database(games):
    path = os.path.dirname(__file__)
    db_filename = os.path.abspath(os.path.join(path, '../game-search-server/games.db'))
    print(db_filename)
    if os.path.exists(db_filename):
        print(f"Database '{db_filename}' already exists. Skipping CSV to SQLite conversion.")
        return
    
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    def format_date(x):
        # if the value is empty/null, return None
        if pd.isnull(x):
            return None
        # if it's already a Timestamp, format it
        if isinstance(x, pd.Timestamp):
            return x.strftime('%Y-%m-%d')
        # otherwise, assume it's a string and try to convert using the expected format.
        dt = pd.to_datetime(x, format='%b %d, %Y', errors='coerce')
        return dt.strftime('%Y-%m-%d') if pd.notnull(dt) else None

    games['release_date'] = games['Release_Date'].apply(format_date)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        title TEXT,
        release_date TEXT,
        developers TEXT,
        summary TEXT,
        platforms TEXT,
        genres TEXT,
        rating REAL,
        plays TEXT,
        playing TEXT,
        backlogs TEXT,
        wishlist TEXT,
        lists TEXT,
        reviews TEXT,
        ctr INTEGER DEFAULT 0
    )
    ''')

    for index, row in games.iterrows():
        # If needed, you can parse and then re-dump the JSON strings to ensure consistency
        # For example:
        # developers = json.dumps(json.loads(row['Developers']))
        # platforms = json.dumps(json.loads(row['Platforms']))
        # genres = json.dumps(json.loads(row['Genres']))
        # Here, we simply use them as-is.
        cursor.execute('''
        INSERT INTO games (
            id, title, release_date, developers, summary, platforms,
            genres, rating, plays, playing, backlogs, wishlist, lists, reviews
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            index,
            row['Title'],
            row['release_date'],
            json.dumps(row['Developers']),  # stored as JSON string (array of strings)
            row['Summary'],
            json.dumps(row['Platforms']),   # stored as JSON string (array of strings)
            json.dumps(row['Genres']),      # stored as JSON string (could be an array or object)
            float(row['Rating']),  # convert rating to a float
            row['Plays'],
            row['Playing'],
            row['Backlogs'],
            row['Wishlist'],
            row['Lists'],
            row['Reviews']
        ))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("CSV data has been successfully inserted into the SQLite database 'games.db'.")

def init(games):
    create_database(games)

def execute():
    # Placeholder for any execution logic
    pass