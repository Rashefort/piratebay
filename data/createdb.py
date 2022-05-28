# -*- coding: utf-8 -*-
from pathlib import Path
import sqlite3


if __name__ == '__main__':
    if not Path('piratebay.db').is_file():
        connection = sqlite3.connect('piratebay.db')
        cursor = connection.cursor()


        cursor.execute("CREATE TABLE Text (title TEXT, phone TEXT, password TEXT)")
        cursor.execute("INSERT INTO Text VALUES (?, ?, ?)", ('На абордаж!', '', ''))


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

        connection.commit()
        connection.close()

    else:
        print(f'Файл \'piratebay.db\' уже существует.')
