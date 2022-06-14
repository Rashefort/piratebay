# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from config import COLOR_VETERANS
from config import COLOR_RECRUITS
from config import COLOR_RENAMED
from config import DB_ADDFRIENDS
from config import DB_RENFRIENDS
from config import DB_DELFRIENDS
from config import CAPTCHA_TEXT
from config import WINDOWFLAGS
from config import INFORMATION
from config import CRITICAL
from config import WARNING



#-------------------------------------------------------------------------------
# "Друг" (или "буква") списка "друзей"
#-------------------------------------------------------------------------------
class Amigo(QtGui.QStandardItem):
     def __init__(self, id, name, color):
        QtGui.QStandardItem.__init__(self)

        # Для "буквы" списка id вычисляется, как -1 * ord(буква)
        self.id = id if id else -ord(name[0])
        self.name = name

        self.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        self.setEditable(False)
        self.setText(self.name)


#-------------------------------------------------------------------------------
# Левая панель в главном окне
#-------------------------------------------------------------------------------
class Friends(QtWidgets.QTreeView):
    def __init__(self):
        QtWidgets.QTreeView.__init__(self)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Друзья'])
        self.root = self.model.invisibleRootItem()

        self.setModel(self.model)


    #---------------------------------------------------------------------------
    # Добавить в self.friends (список отображаемых пользователей)
    #---------------------------------------------------------------------------
    def __add(self, id, name, loot, color):
        letter = name[0].upper()

        try:
            self.friends[letter].append([id, name, loot, color])

        except KeyError:
            self.friends[letter] = [[id, name, loot, color]]

        finally:
            self.users.append([id, name])


    #---------------------------------------------------------------------------
    # Переименовать в self.friends
    #---------------------------------------------------------------------------
    def __ren(self, id, name):
        for letter in self.friends:
            for i in range(len(self.friends[letter])):
                if self.friends[letter][i][0] == id:
                    self.friends[letter][i][1] = name
                    self.friends[letter][i][3] = COLOR_RENAMED
                    return


    #---------------------------------------------------------------------------
    # Удалить из self.friends
    #---------------------------------------------------------------------------
    def __del(self, id, name):
        letter = name[0].upper()

        for i in range(len(self.friends[letter])):
            if self.friends[letter][i][0] == id:
                del self.friends[letter][i]
                return


    #---------------------------------------------------------------------------
    # "Старые друзья"
    #---------------------------------------------------------------------------
    def veterans(self, friends):
        self.friends = dict()
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
                modify[DB_ADDFRIENDS].append([id, name, 0, master])
                self.__add(id, name, 0, COLOR_RECRUITS)

            elif id in veterans and [id, name] not in self.users:
                modify[DB_RENFRIENDS].append([name, id])
                self.__ren(id, name)

            elif id in veterans and 'deactivated' in item:
                modify[DB_DELFRIENDS].append([id])
                self.__del(id, name)

        return modify


    #---------------------------------------------------------------------------
    # "Новые друзья"
    #---------------------------------------------------------------------------
    def show(self):
        # Сортировка словаря по ключу
        self.friends = dict(sorted(self.friends.items(), key=lambda x: x[0]))

        # Сортировка по значению (имя) в каждом ключе
        for letter in self.friends.keys():
            self.friends[letter].sort(key=lambda x: x[1])

        # Создание списка "друзей"
        for letter in self.friends:
            name = f'{letter} - {len(self.friends[letter])}'
            color = COLOR_VETERANS

            if any([i[3] == COLOR_RENAMED for i in self.friends[letter]]):
                color = COLOR_RENAMED

            if any([i[3] == COLOR_RECRUITS for i in self.friends[letter]]):
                color = COLOR_RECRUITS

            parent = Amigo(None, name, color)
            self.root.appendRow(parent)

            for friend in self.friends[letter]:
                item = Amigo(friend[0], friend[1], friend[3])
                parent.appendRow(item)


#-------------------------------------------------------------------------------
# Правая панель в главном окне
#-------------------------------------------------------------------------------
class Details(QtWidgets.QTreeView):
    def __init__(self):
        QtWidgets.QTreeView.__init__(self)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Детали'])
        self.root = self.model.invisibleRootItem()
        self.setModel(self.model)


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
        self.setIcon(icon)
        self.setWindowTitle(Message.title[icon])
        self.setText(text)
        self.exec()


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
