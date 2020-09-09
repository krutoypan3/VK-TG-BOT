import json
import os
import socket
import threading
import random
import time
import urllib3
import vk_api
import SQL_DB
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv


load_dotenv()

API_GROUP_KEY = os.environ.get("API_GROUP_KEY")
API_USER_KEY = os.environ.get("API_USER_KEY")
API_SERVICE_KEY = os.environ.get("API_SERVICE_KEY")
client_secret = os.environ.get("client_secret")
vk_app_id = int(os.environ.get("vk_app_id"))

print("Бот запускается...")
group_id = '196288744'  # Указываем id сообщества
threads = list()
eventhr = []
kolpot = -1
group_sob = "@bratikbot"  # Указываем короткое имя бота (если нет то id)
group_name = "Братик"  # Указываем название сообщества

# Авторизация под именем сообщества
vk_session = vk_api.VkApi(token=API_GROUP_KEY)
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()

# Авторизация под именем пользователя
vk_session_user = vk_api.VkApi(token=API_USER_KEY)
vk_polzovat = vk_session_user.get_api()

# Авторизация сервисным токеном
vk_session_SERVISE = vk_api.VkApi(app_id=vk_app_id, token=API_SERVICE_KEY, client_secret=client_secret)
vk_session_SERVISE.server_auth()
vk_SERVISE = vk_session_SERVISE.get_api()
vk_session_SERVISE.token = {'access_token': API_SERVICE_KEY, 'expires_in': 0}

try:
    # Запуск потока с одним аргрументом
    def thread_start(Func, *args):
        global kolpot
        x = threading.Thread(target=Func, args=args)
        threads.append(x)
        kolpot += 1
        eventhr.append(kolpot)
        x.start()

except ValueError:
    print(ValueError)

