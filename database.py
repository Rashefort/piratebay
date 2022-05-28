# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5 import QtSql

from config import TEMPORARY
from config import DATABASE

from config import CREATE_WINDOW
from config import TERMINATE
from config import Data


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Database(QtCore.QThread):
    signal = QtCore.pyqtSignal(Data)

    SQL = {
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
    def __make(self, command, data):
        self.query.prepare(command)
        for item in data:
            self.query.addBindValue(item)

        self.query.exec_()


    #---------------------------------------------------------------------------
    def select(self, command, items):
        self.__make(Database.SQL[command], items)
        data = self.__prepare()

        self.signal.emit(Data(command, data))


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
        for table in ['Window', 'Text']:
            self.query.prepare(f'SELECT * FROM {table}')
            self.query.exec_()
            data += self.__prepare()[0]

        # Пароли и геометрия в основной поток
        self.signal.emit(Data(CREATE_WINDOW, data))


        while (data := self.pipe.get()).id != TERMINATE:
            pass


    #---------------------------------------------------------------------------
    def __del__(self):
        self.base.close()



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('piratebay database')
