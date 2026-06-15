import spotipy, requests
import sqlite3 as db


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

sqlstring = """
    CREATE TABLE tblStudent(
    Name TEXT,
    Amount INTEGER, 
    URIS TEXT,
    SongNames TEXT
    )
"""

runsql(sqlstring)

def add_playlist_db(name, amount, uris, songNames):
    sqlstring = """INSERT INTO tblPlaylist(Name, Amount, URIS, SongNames)
                    VALUES (?,?,?,?)"""
    values = (name, amount, uris, songNames)
    runsql(sqlstring, values)


add_playlist_db("TEST1", "30", "etc", "HELLO")