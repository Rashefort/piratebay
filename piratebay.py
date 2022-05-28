# -*- coding: utf-8 -*-
import queue
import sys

from PyQt5 import QtWinExtras
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from vkontakte import VKontakte
from database import Database
from windows import *
from config import *


#-------------------------------------------------------------------------------
# class Pirate - Главное окно GUI
#-------------------------------------------------------------------------------
class Pirate(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.buttons = list()       # Кнопки toolbar'а
        self.loot = 0               # Отмеченная "музыка"

        self.vk = self.create_stream(VKontakte, self.handler)
        self.db = self.create_stream(Database, self.handler)


    #---------------------------------------------------------------------------
    # Создать объект класса и запустить его в потоке
    #---------------------------------------------------------------------------
    @staticmethod
    def create_stream(_class, _func, _queue=QtCore.Qt.QueuedConnection):
        pipe = queue.Queue()
        obj = _class(pipe)
        obj.signal.connect(_func, _queue)
        obj.start()

        return {'self': obj, 'pipe': pipe}


    #---------------------------------------------------------------------------
    # Создать "кнопку" для тулбара и добавить в self.buttons
    #---------------------------------------------------------------------------
    def create_button(self, name, info):
        icon = QtGui.QIcon(str(TEMPORARY / f'{name}.png'))

        tbIcon = QtWidgets.QAction(self)
        tbIcon.setIcon(QtGui.QIcon(icon))
        tbIcon.hovered.connect(
            lambda info=info: self.statusBar.showMessage(info, 1500))

        self.buttons.append(tbIcon)

        return tbIcon


    #---------------------------------------------------------------------------
    # Активация/Деактивация кнопок тулбара
    #---------------------------------------------------------------------------
    def switch_toolbar(self, disable=True):
        self.setCursor(WAITCURSOR if disable else ARROWCURSOR)
        for button in self.buttons:
            button.setDisabled(disable)


    #---------------------------------------------------------------------------
    # Главное окно
    #---------------------------------------------------------------------------
    def initUI(self, geometry, splitter, title):
        self.setWindowTitle(title)
        self.resize(550, 300)

        icon = QtGui.QIcon(str(TEMPORARY / 'icon.png'))
        self.setWindowIcon(QtGui.QIcon(icon))

        toolBar = QtWidgets.QToolBar('Pirate ToolBar')
        toolBar.setMovable(False)

        tbTeam = self.create_button('team', INFO_RELOAD_FRIENDS)
        tbSave = self.create_button('chest', INFO_SAVE_SELECTED)
        tbPump = self.create_button('sword', INFO_DOWNLOAD_MUSIC)

        tbInfo = self.create_button('skipper', INFO_AUTHORIZATION)
        tbInfo.triggered.connect(self.credentials)

        tbHelp = self.create_button('hook', INFO_HELP)

        for button in self.buttons[:-1]:
            toolBar.addAction(button)

        spacer = QtWidgets.QWidget(self)
        spacer.setSizePolicy(QtWidgets.QSizePolicy(EXPANDING, PREFERRED))
        toolBar.addWidget(spacer)
        toolBar.addAction(self.buttons[-1])

        self.friends = Friends()
        self.details = Details()

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.friends)
        self.splitter.addWidget(self.details)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        splitter_layout = QtWidgets.QVBoxLayout()
        splitter_layout.setContentsMargins(0, 0, 0, 0)
        splitter_layout.addWidget(self.splitter)

        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(splitter_layout)
        self.setCentralWidget(central_widget)

        if geometry:
            self.restoreGeometry(geometry)
            self.splitter.restoreState(splitter)

        self.statusBar = self.statusBar()
        self.statusBar.setSizeGripEnabled(False)

        self.lbUser = QtWidgets.QLabel(CONNECT_TEXT)
        self.lbUser.setMinimumSize(50, 20)
        self.lbUser.setFrameStyle(STYLEDPANEL | PLAIN)
        self.statusBar.addWidget(self.lbUser, stretch=1)

        self.lbLoot = QtWidgets.QLabel(TAGGED_TEXT % self.loot)
        self.lbLoot.setMinimumSize(50, 20)
        self.lbLoot.setFrameStyle(STYLEDPANEL | PLAIN)
        self.statusBar.addPermanentWidget(self.lbLoot)

        self.addToolBar(QtCore.Qt.TopToolBarArea, toolBar)


    #---------------------------------------------------------------------------
    # Ввод телефона и пароля
    #---------------------------------------------------------------------------
    def credentials(self):
        statusbar_text = self.lbUser.text()
        phone = self.vk_phone
        password = self.vk_password

        self.switch_toolbar(disable=True)
        self.lbUser.setText(CONNECT_TEXT)

        window = Account(self.vk_phone, self.vk_password, self)
        result = window.exec()

        if result == ACCEPTED:
            phone = window.phone.text().strip()
            password = window.password.text()

        if not phone or not password:
            Message(CRITICAL, ERROR_EMPTYPASSWORD, parent=self)
            self.lbUser.setText(statusbar_text)
            self.switch_toolbar(disable=False)

        elif [phone, password] == [self.vk_phone, self.vk_password]:
            Message(WARNING, OLDPASSWORD_TEXT, parent=self)
            self.lbUser.setText(statusbar_text)
            self.switch_toolbar(disable=False)

        else:
            Message(WARNING, NEWPASSWORD_TEXT, parent=self)
            self.vk_phone, self.vk_password = phone, password
            self.vk['pipe'].put(Data(VK_AUTHORIZATION, [phone, password]))


    #---------------------------------------------------------------------------
    # Ввод капчи
    #---------------------------------------------------------------------------
    def read_captcha(self, captcha):
        window = Captcha(captcha.get_image(), parent=self)
        result = window.exec()

        if result == ACCEPTED:
            captcha.text = window.captcha.text().strip()
        else:
            captcha.text = None

        return captcha


    #---------------------------------------------------------------------------
    # Обработчик сигналов Database и VKontakte
    #---------------------------------------------------------------------------
    def handler(self, data):
        # В data.items - [geometry, splitter, title, phone, password]
        if data.id == CREATE_WINDOW:
            self.initUI(*data.items[:3])

            # Выводим splash
            self.vk_phone, self.vk_password = data.items[3:]

            image = QtGui.QPixmap(str(TEMPORARY / 'splash.jpg'))
            self.splash = QtWidgets.QSplashScreen(image)

            align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom
            color = QtCore.Qt.white

            if self.vk_phone and self.vk_password:
                self.splash.showMessage(SPLASH_TEXT, align, color)
                self.splash.show()
            else:
                self.show()

            self.vk['pipe'].put(Data(VK_AUTHORIZATION, data.item[:2]))


        # В data.items - [id, fullname]
        elif data.id == VK_AUTHORIZATION:
            if self.splash.isVisible():
                self.splash.finish(self)
                self.show()

            self.vk_id, self.vk_name = data.items
            self.lbUser.setText(self.vk_name)
            self.switch_toolbar(disable=False)


        # В data.items - [vk_api.exceptions.Captcha]
        elif data.id == VK_CAPTCHA:
            captcha = self.read_captcha(data.item)
            data = [self.vk_phone, self.vk_password, captcha]
            self.vk['pipe'].put(Data(VK_AUTHORIZATION, data))


        # В data.items - ["текст ошибки"]
        elif data.id == VK_FAILURE:
            Message(CRITICAL, data.item, parent=self)
            self.lbUser.setText(FAILURE_TEXT)
            self.switch_toolbar(disable=False)


    #---------------------------------------------------------------------------
    # closeEvent()
    #---------------------------------------------------------------------------
    def closeEvent(self, event):
        self.vk['pipe'].put(Data(TERMINATE, None))
        self.db['pipe'].put(Data(TERMINATE, None))
        event.accept()


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    # https://ru.stackoverflow.com/questions/1128075/pyqt5-иконка-для-приложения
    QtWinExtras.QtWin.setCurrentProcessExplicitAppUserModelID('PirateBay')
    app = QtWidgets.QApplication(sys.argv)
    pirate = Pirate()
    sys.exit(app.exec())