# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from config import COLOR_VETERANS
from config import COLOR_RECRUITS
from config import COLOR_RENAMED
from config import FRIENDS_LABEL
from config import LETTERS_LABEL
from config import SONGS_LABEL
from config import DB_FRIENDS
from config import DB_ADDFRIENDS
from config import DB_RENFRIENDS
from config import DB_DELFRIENDS
from config import CAPTCHA_TEXT
from config import NOSELECTION
from config import SELECTROWS
from config import SELECTION
from config import WINDOWFLAGS
from config import INFORMATION
from config import CRITICAL
from config import WARNING
from config import STRETCH
from config import RESIZE



#-------------------------------------------------------------------------------
# Один "пункт" QStandardItem
#-------------------------------------------------------------------------------
class Item(QtGui.QStandardItem):
     def __init__(self, id, name, loot=None, color=COLOR_VETERANS):
        QtGui.QStandardItem.__init__(self)

        # Для "буквы" списка id вычисляется, как -1 * ord(буква)
        self.id = id if id else -ord(name[0])
        self.name = name
        self.loot = loot

        self.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        self.setEditable(False)
        self.setText(self.name)


#-------------------------------------------------------------------------------
# Один "пункт" QStandardItem
#-------------------------------------------------------------------------------
class Song(QtGui.QStandardItem):
    def __init__(self, name, checkable=False, color=COLOR_VETERANS):
        QtGui.QStandardItem.__init__(self)
        self.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        self.setCheckable(checkable)
        self.setEditable(False)
        self.setText(name)


#-------------------------------------------------------------------------------
# Левая панель в главном окне
#-------------------------------------------------------------------------------
class Friends(QtWidgets.QTreeView):
    def __init__(self):
        QtWidgets.QTreeView.__init__(self)
        self.model = QtGui.QStandardItemModel()
        self.root = self.model.invisibleRootItem()
        self.setModel(self.model)


    #---------------------------------------------------------------------------
    # Добавить в self.team (список отображаемых пользователей)
    #---------------------------------------------------------------------------
    def __add(self, id, name, loot, color):
        letter = name[0].upper()

        try:
            self.team[letter].append([id, name, loot, color])

        except KeyError:
            self.team[letter] = [[id, name, loot, color]]

        finally:
            self.users.append([id, name])


    #---------------------------------------------------------------------------
    # Переименовать в self.team
    #---------------------------------------------------------------------------
    def __ren(self, id, name):
        for letter in self.team:
            for i in range(len(self.team[letter])):
                if self.team[letter][i][0] == id:
                    self.team[letter][i][1] = name
                    self.team[letter][i][3] = COLOR_RENAMED
                    return


    #---------------------------------------------------------------------------
    # Удалить из self.team
    #---------------------------------------------------------------------------
    def __del(self, id, name):
        letter = name[0].upper()

        for i in range(len(self.team[letter])):
            if self.team[letter][i][0] == id:
                del self.team[letter][i]
                return


    #---------------------------------------------------------------------------
    # "Старые друзья"
    #---------------------------------------------------------------------------
    def veterans(self, friends):
        self.team = dict()
        self.users = list()

        for friend in friends:
            self.__add(*friend, COLOR_VETERANS)


    #---------------------------------------------------------------------------
    # "Новые друзья"
    #---------------------------------------------------------------------------
    def recruits(self, master, items):
        modify = {DB_ADDFRIENDS: [], DB_RENFRIENDS: [], DB_DELFRIENDS: []}
        veterans = [user[0] for user in self.users]

        for item in items:
            name = f'{item["first_name"]} {item["last_name"]}'
            id = item['id']

            if id not in veterans and 'deactivated' not in item:
                modify[DB_ADDFRIENDS].append([id, name, None, master])
                self.__add(id, name, None, COLOR_RECRUITS)

            elif id in veterans and [id, name] not in self.users:
                modify[DB_RENFRIENDS].append([name, id])
                self.__ren(id, name)

            elif id in veterans and 'deactivated' in item:
                modify[DB_DELFRIENDS].append([id])
                self.__del(id, name)

        modify.update({DB_FRIENDS: [[i[0]] for i in modify[DB_ADDFRIENDS]]})

        return modify


    #---------------------------------------------------------------------------
    # "Друзья"
    #---------------------------------------------------------------------------
    def show(self):
        # Сортировка словаря по ключу
        self.team = dict(sorted(self.team.items(), key=lambda x: x[0]))
        total_friends = 0

        # Сортировка по значению (имя) в каждом ключе
        for letter in self.team.keys():
            self.team[letter].sort(key=lambda x: x[1])
            total_friends += len(self.team[letter])

        # Создание списка "друзей"
        self.model.setHorizontalHeaderLabels([FRIENDS_LABEL % total_friends])

        for letter in self.team:
            name = f'{letter} - {len(self.team[letter])}'
            color = COLOR_VETERANS

            if any([i[3] == COLOR_RENAMED for i in self.team[letter]]):
                color = COLOR_RENAMED

            if any([i[3] == COLOR_RECRUITS for i in self.team[letter]]):
                color = COLOR_RECRUITS

            parent = Item(None, name, None, color)
            self.root.appendRow(parent)

            for friend in self.team[letter]:
                item = Item(*friend)
                parent.appendRow(item)


#-------------------------------------------------------------------------------
# Правая панель в главном окне
#-------------------------------------------------------------------------------
class Details(QtWidgets.QTableView):
    def __init__(self):
        QtWidgets.QTableView.__init__(self)
        self.model = QtGui.QStandardItemModel()
        self.setSelectionBehavior(SELECTROWS)
        self.setModel(self.model)


    #---------------------------------------------------------------------------
    # Список "друзей" на выбранную букву
    #---------------------------------------------------------------------------
    def letters(self, data):
        self.model.clear()
        self.model.setRowCount(len(data))
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(LETTERS_LABEL)
        self.setSelectionMode(SELECTION)

        for i in range(0, len(data)):
            item = Item(*data[i])
            self.model.setItem(i, 0, item)

            name = str(data[i][2]) if data[i][2] else 'хз'
            item = Item(data[i][0], name)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.setItem(i, 1, item)

        self.setModel(self.model)

        self.header = self.horizontalHeader()
        self.header.setSectionResizeMode(0, STRETCH)
        self.header.setSectionResizeMode(1, RESIZE)


    #---------------------------------------------------------------------------
    # Аудио список "друга"
    #---------------------------------------------------------------------------
    def songs(self, data):
        self.model.clear()
        self.model.setRowCount(len(data))
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(SONGS_LABEL)
        self.setSelectionMode(NOSELECTION)

        for i in range(0, len(data)):
            for j in range(0, 2):
                item = Song(data[i][j], checkable=not j)
                self.model.setItem(i, j, item)

            item = Song(data[i][2])
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.setItem(i, 2, item)

        self.setModel(self.model)

        self.header = self.horizontalHeader()
        self.header.setSectionResizeMode(0, RESIZE)
        self.header.setSectionResizeMode(1, STRETCH)
        self.header.setSectionResizeMode(2, RESIZE)


#-------------------------------------------------------------------------------
# Окна сообщений MessageBox
#-------------------------------------------------------------------------------
class Message(QtWidgets.QMessageBox):
    title = {
        INFORMATION: 'Уведомление',
        WARNING: 'Предупреждение',
        CRITICAL: 'Ошибка',
    }

    def __init__(self, icon, text, parent=None):
        QtWidgets.QMessageBox.__init__(self, parent)
        self.setWindowTitle(Message.title[icon])
        self.setIcon(icon)
        self.setText(text)
        self.exec()


#-------------------------------------------------------------------------------
# Окно вопроса
#-------------------------------------------------------------------------------
class Question(QtWidgets.QMessageBox):
    def __init__(self, text, parent=None):
        QtWidgets.QMessageBox.__init__(self, parent)
        self.setIcon(QtWidgets.QMessageBox.Question)
        self.addButton(QtWidgets.QMessageBox.Yes)
        self.addButton(QtWidgets.QMessageBox.No)
        self.setDefaultButton(QtWidgets.QMessageBox.No)
        self.setWindowTitle('Вопрос')
        self.setText(text)


    #---------------------------------------------------------------------------
    def ask(self):
        return self.exec() == QtWidgets.QMessageBox.Yes


#-------------------------------------------------------------------------------
# Окно ввода телефона и пароля
#-------------------------------------------------------------------------------
class Account(QtWidgets.QDialog):
    def __init__(self, phone, password, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle('Authorization')
        self.setWindowFlags(WINDOWFLAGS)

        lbPhone = QtWidgets.QLabel('Телефон')
        self.phone = QtWidgets.QLineEdit(phone)

        lbPassword = QtWidgets.QLabel('Пароль')
        self.password = QtWidgets.QLineEdit(password)

        btOK = QtWidgets.QPushButton("&OK")
        btOK.clicked.connect(self.accept)
        btOK.setDefault(True)

        btCancel = QtWidgets.QPushButton("&Cancel")
        btCancel.clicked.connect(self.reject)

        hboxButton = QtWidgets.QHBoxLayout()
        hboxButton.addWidget(btOK)
        hboxButton.addWidget(btCancel)

        authBox = QtWidgets.QVBoxLayout()
        authBox.addWidget(lbPhone)
        authBox.addWidget(self.phone)
        authBox.addWidget(lbPassword)
        authBox.addWidget(self.password)
        authBox.addSpacing(10)
        authBox.addLayout(hboxButton)

        self.setLayout(authBox)


#-------------------------------------------------------------------------------
# Окно ввода капчи
#-------------------------------------------------------------------------------
class Captcha(QtWidgets.QDialog):
    def __init__(self, image, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle('Captcha')
        self.setWindowFlags(WINDOWFLAGS)

        lbText = QtWidgets.QLabel(CAPTCHA_TEXT)
        self.captcha = QtWidgets.QLineEdit()
        vboxInput = QtWidgets.QVBoxLayout()
        vboxInput.addWidget(lbText)
        vboxInput.addWidget(self.captcha)

        captcha = QtGui.QPixmap()
        captcha.loadFromData(image, "JPG")
        lbCaptcha = QtWidgets.QLabel(self)
        lbCaptcha.setPixmap(captcha)
        hboxImage = QtWidgets.QHBoxLayout()
        hboxImage.addWidget(lbCaptcha)
        hboxImage.addLayout(vboxInput)

        btOK = QtWidgets.QPushButton("&OK")
        btOK.clicked.connect(self.accept)

        btCancel = QtWidgets.QPushButton("&Cancel")
        btCancel.clicked.connect(self.reject)

        hboxButton = QtWidgets.QHBoxLayout()
        hboxButton.addWidget(btOK)
        hboxButton.addWidget(btCancel)

        captchaBox = QtWidgets.QVBoxLayout()
        captchaBox.addLayout(hboxImage)
        captchaBox.addSpacing(10)
        captchaBox.addLayout(hboxButton)

        self.setLayout(captchaBox)



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('module windows')
