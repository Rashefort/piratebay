# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from config import WINDOWFLAGS
from config import CAPTCHA_TEXT
from config import INFORMATION
from config import CRITICAL
from config import WARNING



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
