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
        self.vk = self.create_stream(VKontakte, self.handler)
        self.db = self.create_stream(Database, self.handler)
        self.selected = None


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
    # Создать "кнопку" для тулбара
    #---------------------------------------------------------------------------
    def create_button(self, name, info):
        icon = QtGui.QIcon(str(TEMPORARY / f'{name}.png'))

        button = QtWidgets.QAction(self)
        button.setIcon(QtGui.QIcon(icon))
        button.hovered.connect(
            lambda info=info: self.statusBar.showMessage(info, 1500))

        return button


    #---------------------------------------------------------------------------
    # "Светофор" в статусбаре
    #---------------------------------------------------------------------------
    def traffic_light(self, light, text):
        self.master_light = light
        self.light.setPixmap(QtGui.QPixmap(light))
        self.master.setText(text)


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

        # self.tbTeam = self.create_button('team', INFO_RELOAD_FRIENDS)
        # toolBar.addAction(button)

        self.tbCheck = self.create_button('chest', INFO_CHECK_SELECTED)
        self.tbCheck.triggered.connect(self.audiorecords)
        self.tbCheck.setEnabled(False)
        toolBar.addAction(self.tbCheck)

        # self.tbPump = self.create_button('sword', INFO_DOWNLOAD_MUSIC)

        self.tbInfo = self.create_button('skipper', INFO_AUTHORIZATION)
        self.tbInfo.triggered.connect(self.credentials)
        toolBar.addAction(self.tbInfo)

        spacer = QtWidgets.QWidget(self)
        spacer.setSizePolicy(QtWidgets.QSizePolicy(EXPANDING, PREFERRED))
        toolBar.addWidget(spacer)

        self.tbHelp = self.create_button('hook', INFO_HELP)
        toolBar.addAction(self.tbHelp)

        self.friends = Friends()
        self.friends.clicked.connect(self.single_click)
        self.friends.doubleClicked.connect(self.double_click)

        self.details = Details()
        self.details.clicked.connect(self.single_click)
        self.details.doubleClicked.connect(self.double_click)

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
        self.statusBar.setStyleSheet('QStatusBar::item {border: None;}')

        self.status = QtWidgets.QLabel(self)
        self.light = QtWidgets.QLabel(self)
        self.light.setPixmap(QtGui.QPixmap(TRAFFIC_RED))
        self.light.setMinimumSize(16, 16)
        self.master = QtWidgets.QLabel(MASTER_TEXT)

        self.statusBar.addWidget(self.status, stretch=1)
        self.statusBar.addPermanentWidget(self.master)
        self.statusBar.addPermanentWidget(self.light)

        self.addToolBar(QtCore.Qt.TopToolBarArea, toolBar)


    #---------------------------------------------------------------------------
    # Проверить аудиозаписи "друга"
    #---------------------------------------------------------------------------
    def audiorecords(self):
        if Question(CHECKAUDIO_TEXT, self).ask():
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.vk['pipe'].put(Data(VK_AUDIO, [self.selected]))
            self.setEnabled(False)


    #---------------------------------------------------------------------------
    # Ввод телефона и пароля
    #---------------------------------------------------------------------------
    def credentials(self):
        master_light = self.master_light
        master_text = self.master.text()
        phone = self.vk_phone
        password = self.vk_password

        self.traffic_light(TRAFFIC_YELLOW, CONNECT_TEXT)

        window = Account(self.vk_phone, self.vk_password, self)
        result = window.exec()

        if result == ACCEPTED:
            phone = window.phone.text().strip()
            password = window.password.text()

        if not phone or not password:
            Message(CRITICAL, ERROR_EMPTYPASSWORD, parent=self)
            self.traffic_light(master_light, master_text)

        elif [phone, password] == [self.vk_phone, self.vk_password]:
            Message(WARNING, OLDPASSWORD_TEXT, parent=self)
            self.traffic_light(master_light, master_text)

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

            self.vk['pipe'].put(Data(VK_AUTHORIZATION, data.item[3:]))


        # В data.items - [id, fullname]
        elif data.id == VK_AUTHORIZATION:
            if self.splash.isVisible():
                self.splash.finish(self)
                self.show()

            self.vk_id, self.vk_name = data.items
            self.db['pipe'].put(Data(DB_MASTERS, [[self.vk_id]]))
            self.db['pipe'].put(Data(DB_GETFRIENDS, [[self.vk_id]]))

            self.traffic_light(TRAFFIC_GREEN, self.vk_name)


        # В data.items - [vk_api.exceptions.Captcha]
        elif data.id == VK_CAPTCHA:
            captcha = self.read_captcha(data.item)
            data = [self.vk_phone, self.vk_password, captcha]
            self.vk['pipe'].put(Data(VK_AUTHORIZATION, data))


        # В data.items - ["текст ошибки"]
        elif data.id == VK_FAILURE:
            Message(CRITICAL, data.item, parent=self)
            self.traffic_light(TRAFFIC_RED, FAILURE_TEXT)


        # В data.items - ["текст ошибки"]
        elif data.id == VK_DENIED:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            Message(CRITICAL, data.item, parent=self)
            self.setEnabled(True)


        # В data.items - [[id, name, loot], ...]
        elif data.id == DB_GETFRIENDS:
            self.vk['pipe'].put(Data(VK_FRIENDS, None))
            self.friends.veterans(data.items)


        # В data.items - [{id, first_name, last_name, ...}, ...]
        elif data.id == VK_FRIENDS:
            data = self.friends.recruits(self.vk_id, data.items)

            for key in data:
                if data[key]:
                    self.db['pipe'].put(Data(key, data[key]))

            if not self.friends.team:
                Message(CRITICAL, NOFRIENDS_TEXT, parent=self)
            else:
                self.friends.show()


        # В data.items - [{id, first_name, last_name, ...}, ...]
        elif data.id == DB_GETLOOT:
            print(data.items)


        # В data.items - []
        elif data.id == VK_AUDIO:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

            songs = []
            for item in data.items:
                songs.append([
                    item['artist'],
                    item['title'],
                    str(item['duration']),
                    item['url'],
                    str(item['owner_id']),
                ])

            self.details.songs(songs)
            self.setEnabled(True)


    #---------------------------------------------------------------------------
    # Обработчик кликов мышки.
    #---------------------------------------------------------------------------
    def single_click(self, index):
        self.click = [SINGLE_CLICK, index]
        QtCore.QTimer.singleShot(DOUBLECLICK_INTERVAL, self.accept_click)


    def double_click(self, index):
        self.click = [DOUBLE_CLICK, index]


    def accept_click(self):
        # По количеству столбцов определяем в каком виджете был click
        columns = self.click[1].model().columnCount()
        widget = self.friends if columns == 1 else self.details

        if widget.selectionModel().hasSelection():
            item = widget.selectedIndexes()[0]
            data = item.model().itemFromIndex(self.click[1])

            self.tbCheck.setEnabled(data.id > 0)
            self.selected = data.id

            if self.click[0] == SINGLE_CLICK:
                if columns == 1:
                    letter = self.friends.team[data.name[0].upper()]
                    self.details.letters(letter)

                elif columns == 2:
                    row = self.details.currentIndex().row()
                    self.details.selectRow(row)

            else:
                if data.id > 0: # Переписать этот блок
                    if data.loot and data.loot > 0:
                        self.db['pipe'].put(Data(DB_GETLOOT, [data.id]))

                    elif data.loot == '':
                        Message(WARNING, NODATABASE_TEXT, parent=self)

                    else:
                        Message(WARNING, NOMUSIC_TEXT, parent=self)


    #---------------------------------------------------------------------------
    # closeEvent()
    #---------------------------------------------------------------------------
    def closeEvent(self, event):
        data = [[self.vk_phone, self.vk_password]]
        self.db['pipe'].put(Data(DB_PASSWORD, data))

        data = [[self.saveGeometry(), self.splitter.saveState()]]
        self.db['pipe'].put(Data(DB_GEOMETRY, data))

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
