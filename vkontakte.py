# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from requests.exceptions import ConnectionError
from vk_api.exceptions import LoginRequired
from vk_api.exceptions import PasswordRequired
from vk_api.exceptions import BadPassword
from vk_api.exceptions import Captcha
from vk_api import audio
import vk_api

from config import VK_AUTHORIZATION
from config import VK_CAPTCHA
from config import VK_FAILURE
from config import VK_FRIENDS
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

            except ConnectionError as error:
                # 'Connection aborted.', RemoteDisconnected('Remote end closed connection without response'
                # HTTPSConnectionPool(host='vk.com', port=443): Max retries exceeded with url: /feed2.php (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x0000000003938C40>: Failed to establish a new connection: [Errno 11004] getaddrinfo failed'))
                print(f'ConnectionError -> {error}')

            except Exception as error:
                print(f'Exception -> {error}')

            else:
                self.account = self.session.get_api()
                self.audio = audio.VkAudio(vk=self.session)

                my = self.account.users.get()[0]
                data = [my['id'], f'{my["first_name"]} {my["last_name"]}']

                self.signal.emit(Data(VK_AUTHORIZATION, data))

        else:
            self.signal.emit(Data(VK_FAILURE, [ERROR_EMPTYPASSWORD]))


    #---------------------------------------------------------------------------
    # Вернуть список друзей в ВК
    #---------------------------------------------------------------------------
    def get_friends(self):
        friends_ids = self.account.friends.get(user_id=14314571)['items']
        friends_str = ','.join(list(map(str, friends_ids)))
        info = self.account.users.get(user_ids=friends_str)#[:10] # <---------------------------------

        self.signal.emit(Data(VK_FRIENDS, info))


    #---------------------------------------------------------------------------
    # QThread.run()
    #---------------------------------------------------------------------------
    def run(self):
        while (data := self.pipe.get()).id != TERMINATE:
            if data.id == VK_AUTHORIZATION:
                self.authorization(*data.items)

            elif data.id == VK_FRIENDS:
                self.get_friends()



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    print('module vkontakte')
