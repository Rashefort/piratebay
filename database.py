# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5 import QtSql

from config import TEMPORARY
from config import DATABASE

from config import CREATE_WINDOW
from config import DB_GETFRIENDS
from config import DB_ADDFRIENDS
from config import DB_RENFRIENDS
from config import DB_DELFRIENDS
from config import DB_PASSWORD
from config import DB_GEOMETRY
from config import DB_ADDSONG
from config import DB_GETLOOT
from config import DB_MASTERS
from config import DB_FRIENDS
from config import TERMINATE
from config import Data


#-------------------------------------------------------------------------------
# Работа с базой sqlite
#-------------------------------------------------------------------------------
class Database(QtCore.QThread):
    signal = QtCore.pyqtSignal(Data)

    SQL = {
        DB_GETFRIENDS: 'SELECT id, name, loot FROM Teams WHERE master=?',
        DB_GETLOOT:    'SELECT * FROM Audio WHERE id=?',
        DB_MASTERS:    'INSERT OR IGNORE INTO Masters VALUES(?)',
        DB_FRIENDS:    'INSERT OR IGNORE INTO Friends VALUES(?)',
        DB_ADDSONG:    'INSERT OR IGNORE INTO Audios VALUES(?, ?, ?, ?, ?)',
        DB_ADDFRIENDS: 'INSERT OR IGNORE INTO Teams VALUES (?, ?, ?, ?)',
        DB_RENFRIENDS: 'UPDATE Teams SET name=? WHERE id=?',
        DB_PASSWORD:   'UPDATE Strings SET phone=?, password=?',
        DB_GEOMETRY:   'UPDATE Window SET geometry=?, splitter=?',
        DB_DELFRIENDS: 'DELETE FROM Friends WHERE id=?',
    }


    #---------------------------------------------------------------------------
    def __init__(self, pipe, base=DATABASE, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.base = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.base.setDatabaseName(base)
        self.base.open()

        self.query = QtSql.QSqlQuery()
        self.pipe = pipe


    #---------------------------------------------------------------------------
    def __prepare(self):
        count = self.query.record().count()
        data = list()

        self.query.first()
        while self.query.isValid():
            data.append([self.query.value(i) for i in range(count)])
            self.query.next()

        return data


    #---------------------------------------------------------------------------
    def __make(self, command, items):
        self.query.prepare(command)
        for item in items:
            self.query.addBindValue(item)

        self.query.exec_()


    #---------------------------------------------------------------------------
    def select(self, command, items):
        self.__make(Database.SQL[command], items)
        data = self.__prepare()

        self.signal.emit(Data(command, data))


    #---------------------------------------------------------------------------
    def modify(self, command, items):
        for item in items:
            self.__make(Database.SQL[command], item)


    #---------------------------------------------------------------------------
    def run(self):
        # Вытаскиваем из базы иконки, пароли, геометрию и положение окна.
        self.query.prepare('SELECT * FROM Images')
        self.query.exec_()

        # Иконки сохраняются в %Temp%
        for name, data in self.__prepare():
            with open(TEMPORARY / name, 'wb') as file:
                file.write(data)

        # Пароли и геометрия в data
        data = []
        for table in ['Window', 'Strings']:
            self.query.prepare(f'SELECT * FROM {table}')
            self.query.exec_()
            data += self.__prepare()[0]

        # Пароли и геометрия в основной поток
        self.signal.emit(Data(CREATE_WINDOW, data))


        # Основной цикл обработки сигналов
        while (data := self.pipe.get()).id != TERMINATE:
            self.base.transaction()

            if data.id <= DB_GETLOOT:
                self.select(data.id, data.item)

            else:
                self.modify(data.id, data.items)

            self.base.commit()


    #---------------------------------------------------------------------------
    def __del__(self):
        self.base.close()



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('piratebay database')
