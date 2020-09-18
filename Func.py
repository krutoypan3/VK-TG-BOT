import datetime
import json
import os
import re
import socket
import threading
import random
import time

import requests
import urllib3
import vk_api
# import SQL_DB
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
group_id = '198599965'  # Указываем id сообщества
threads = list()
eventhr = []
kolpot = -1
group_sob = "@198599965"  # Указываем короткое имя бота (если нет то id)
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


    def send_msg(peerid, ms_g):
        vk.messages.send(peer_id=peerid, random_id=0, message=ms_g)


    def save_file(event_func, count_attach):
        try:  # Если папка нет, то она появится
            os.makedirs(r'content/users/' + str(event_func.message.from_id) + '/' +
                        str(datetime.datetime.now().date()) + '/')
        except FileExistsError:  # Если есть - то есть
            pass
        for i in range(count_attach):  # Пробег по всем вложениям
            content_type = event_func.message["attachments"][i]["type"]  # Определение типа контента
            if content_type == "doc":  # Если это видео
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " тип - документ")
                url = vk_polzovat.docs.getById(
                    docs=
                    str(event_func.message["attachments"][i]["doc"]["owner_id"]) + '_' +
                    str(event_func.message["attachments"][i]["doc"]["id"]) + '_' +
                    str(event_func.message["attachments"][i]["doc"]["access_key"])
                )[0]["url"]
                f = open(r'content/users/' + str(event_func.message.from_id) + '/' +
                         str(datetime.datetime.now().date()) + '/' + str(time.time()) +
                         '.' + str(event_func.message["attachments"][i]["doc"]["ext"]),
                         "wb")  # открываем файл для записи, в режиме wb
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " успешно сохранен")

            elif content_type == "audio":  # Если это музыка
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " тип - музыка")
                url = event_func.message["attachments"][i]["audio"]["url"]
                artist = re.sub(r'[:*?"<|>]', "", event_func.message["attachments"][i]["audio"]["artist"])
                title = re.sub(r'[:*?"<|>]', "", event_func.message["attachments"][i]["audio"]["title"])
                f = open(r'content/users/' + str(event_func.message.from_id) + '/' +
                         str(datetime.datetime.now().date()) + '/' + str(artist) + ' — ' + str(title) +
                         '.mp3',
                         "wb")  # открываем файл для записи, в режиме wb
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " успешно сохранен")

            elif content_type == "photo":  # Если это фото
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " тип - фотография")
                url = vk_polzovat.photos.getById(
                    photos=
                    str(event_func.message["attachments"][i]["photo"]["owner_id"]) + '_' +
                    str(event_func.message["attachments"][i]["photo"]["id"]) + '_' +
                    str(event_func.message["attachments"][i]["photo"]["access_key"])
                )[0]["sizes"][6]["url"]
                f = open(r'' + str('content/users/' + str(event_func.message.from_id) + '/' +
                         str(datetime.datetime.now().date()) + '/' + str(time.time()) +
                         '.png'), "wb")  # открываем файл для записи, в режиме wb
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " успешно сохранен")

except ValueError:
    print(ValueError)
