import sqlite3

with sqlite3.connect('room.db') as connection:
    c = connection.cursor()
    #c.execute('DROP TABLE room')
    c.execute('CREATE TABLE room(name TEXT,latitude INTEGER, longitude INTEGER,capacity INT, picture TEXT, description TEXT)')
