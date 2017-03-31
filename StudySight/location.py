import sqlite3

with sqlite3.connect('locations.db') as connection:
    c = connection.cursor()
    #c.execute('DROP TABLE locations')
    c.execute('CREATE TABLE locations(name TEXT,latitude INTEGER, longitude INTEGER)')
