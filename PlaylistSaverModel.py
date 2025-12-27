import spotipy, requests
import sqlite3 as db

def setup_database():
    def runsql(*args):
        conn = db.connect("PlaylistSaver.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        if len(args) == 1:
            cursor.execute(args[0])
        else:
            cursor.execute(args[0], args[1])
        conn.commit()
        return cursor.fetchall()