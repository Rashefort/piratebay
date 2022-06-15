# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore



WINDOWFLAGS = QtCore.Qt.Window | QtCore.Qt.MSWindowsFixedSizeDialogHint
WAITCURSOR  = QtCore.Qt.WaitCursor
ARROWCURSOR = QtCore.Qt.ArrowCursor
INFORMATION = QtWidgets.QMessageBox.Information
CRITICAL    = QtWidgets.QMessageBox.Critical
WARNING     = QtWidgets.QMessageBox.Warning
ACCEPTED    = QtWidgets.QDialog.Accepted
EXPANDING   = QtWidgets.QSizePolicy.Expanding
PREFERRED   = QtWidgets.QSizePolicy.Preferred
STYLEDPANEL = QtWidgets.QFrame.StyledPanel
PLAIN       = QtWidgets.QFrame.Plain

DATABASE    = 'piratebay.db'
TEMPORARY   = Path(os.environ['TEMP'])

DOUBLECLICK_INTERVAL: int = 250
SINGLE_CLICK:         int = 1
DOUBLE_CLICK:         int = 2

CREATE_WINDOW:        int = 100

VK_AUTHORIZATION:     int = 200
VK_CAPTCHA:           int = 210
VK_FAILURE:           int = 220
VK_FRIENDS:           int = 230

DB_GETFRIENDS:        int = 300
DB_ADDFRIENDS:        int = 310
DB_MASTERS:           int = 320
DB_PASSWORD:          int = 330
DB_RENFRIENDS:        int = 340
DB_GEOMETRY:          int = 350
DB_DELFRIENDS:        int = 360

TERMINATE:            int = 999

SPLASH_TEXT:          str = 'Загрузка данных...'
CONNECT_TEXT:         str = 'Подключение к ВК...'
CAPTCHA_TEXT:         str = 'Введите текст на картинке'
TAGGED_TEXT:          str = ' Выбрано %d'
FAILURE_TEXT:         str = 'Связь с VK не установлена'
NEWPASSWORD_TEXT:     str = 'Данные успешно изменены'
OLDPASSWORD_TEXT:     str = 'Данные остались прежними'

ERROR_EMPTYPASSWORD:  str = 'Не задан телефон или пароль'
ERROR_BADPASSWORD:    str = 'Неверный телефон или пароль'

INFO_RELOAD_FRIENDS:  str = 'Обновить список друзей'
INFO_SAVE_SELECTED:   str = 'Сохранить отмеченное'
INFO_DOWNLOAD_MUSIC:  str = 'Скачать выбранные треки'
INFO_AUTHORIZATION:   str = 'Настройки учетной записи'
INFO_HELP:            str = 'Помощь'

TRAFFIC_RED:          str = str(TEMPORARY / 'red.png')
TRAFFIC_YELLOW:       str = str(TEMPORARY / 'yellow.png')
TRAFFIC_GREEN:        str = str(TEMPORARY / 'green.png')

COLOR_VETERANS:       str = '#000000'
COLOR_RECRUITS:       str = '#E65100'
COLOR_RENAMED:        str = '#AA00FF'


# Класс для передачи данных между потоками
@dataclass
class Data:
    __slots__ = ('_id', '_items')
    _id: int
    _items: list

    @property
    def id(self):
        return self._id

    @property
    def items(self):
        return self._items

    @property
    def item(self):
        return self._items if len(self._items) != 1 else self._items[0]



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('module config')
