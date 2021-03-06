# -*- coding: utf-8 -*-
from pathlib import Path
import sqlite3


if __name__ == '__main__':
    if not Path('piratebay.db').is_file():
        connection = sqlite3.connect('piratebay.db')
        cursor = connection.cursor()


        cursor.execute("CREATE TABLE Strings (title TEXT, phone TEXT, password TEXT)")
        cursor.execute("INSERT INTO Strings VALUES (?, ?, ?)", ('На абордаж!', '', ''))


        cursor.execute("CREATE TABLE Window (geometry BLOB, splitter BLOB)")
        cursor.execute("INSERT INTO Window VALUES (?, ?)", (None, None))


        cursor.execute("CREATE TABLE Images (name TEXT, file BLOB)")
        for icon in ['icon', 'team', 'chest', 'sword', 'skipper', 'hook', 'red', 'yellow', 'green']:
            with open(f'{icon}.png', 'rb') as file:
                blob = file.read()
                cursor.execute("INSERT INTO Images VALUES (?, ?)", (f'{icon}.png', blob))

        with open(f'splash.jpg', 'rb') as file:
            blob = file.read()
            cursor.execute("INSERT INTO Images VALUES (?, ?)", (f'splash.jpg', blob))


        cursor.execute("CREATE TABLE Masters (id INTEGER PRIMARY KEY)")


        cursor.execute("""
            CREATE TABLE Teams (id INTEGER, name TEXT, loot INTEGER, master INTEGER,
            FOREIGN KEY(master) REFERENCES Masters(id))
        """)


        cursor.execute("CREATE TABLE Friends (id INTEGER PRIMARY KEY)")


        cursor.execute("""
            CREATE TABLE Audios (artist TEXT, title TEXT, duration INTEGER, url TEXT, friend INTEGER,
            FOREIGN KEY(friend) REFERENCES Friends(id))
        """)


        connection.commit()
        connection.close()

    else:
        print(f'Файл \'piratebay.db\' уже существует.')
