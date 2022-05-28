# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from vk_api.exceptions import LoginRequired
from vk_api.exceptions import PasswordRequired
from vk_api.exceptions import BadPassword
from vk_api.exceptions import Captcha
from vk_api import audio
import vk_api

from config import VK_AUTHORIZATION
from config import VK_CAPTCHA
from config import VK_FAILURE
from config import ERROR_EMPTYPASSWORD
from config import ERROR_BADPASSWORD
from config import TERMINATE
from config import Data


#-------------------------------------------------------------------------------
# class VKontakte - API ВКонтакте
#-------------------------------------------------------------------------------
class VKontakte(QtCore.QThread):
    signal = QtCore.pyqtSignal(Data)

    def __init__(self, pipe, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.pipe = pipe


    #---------------------------------------------------------------------------
    # Авторизация
    #---------------------------------------------------------------------------
    def authorization(self, login, password, captcha=None):
        if login and password:
            try:
                if captcha is None:
                    self.session = vk_api.VkApi(login=login, password=password)
                    self.session.auth()

                else:
                    captcha.try_again(captcha.text)

            except Captcha as captcha:
                self.signal.emit(Data(VK_CAPTCHA, [captcha]))

            except BadPassword:
                self.signal.emit(Data(VK_FAILURE, [ERROR_BADPASSWORD]))

            else:
                self.account = self.session.get_api()
                self.audio = audio.VkAudio(vk=self.session)

                my = self.account.users.get()[0]
                data = [my['id'], f'{my["first_name"]} {my["last_name"]}']

                self.signal.emit(Data(VK_AUTHORIZATION, data))

        else:
            self.signal.emit(Data(VK_FAILURE, [ERROR_EMPTYPASSWORD]))


    #---------------------------------------------------------------------------
    # QThread.run()
    #---------------------------------------------------------------------------
    def run(self):
        while (data := self.pipe.get()).id != TERMINATE:
            if data.id == VK_AUTHORIZATION:
                self.authorization(*data.items)



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('module vkontakte')
