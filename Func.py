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

print("Бот работает...")
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


    def curs_value(*args):
        peer_id = args[0].message.peer_id
        link = "https://www.cbr-xml-daily.ru/daily_json.js"
        data = requests.get(link)
        USD = data.json()['Valute']["USD"]["Previous"]
        EUR = data.json()['Valute']["EUR"]["Previous"]
        forex = 'Курс валюты на утро ' + str(datetime.datetime.now().date()) + '\n\n' + \
                'Курс 1 USD = ' + str(USD) + ' Российских рублей\n' + \
                'Курс 1 EUR = ' + str(EUR) + ' Российский рублей'
        send_msg(peer_id, forex)

        # Личная диалог или беседа
    def lich_or_beseda(my_peer):
        try:
            response = vk.messages.getConversationMembers(peer_id=my_peer)
            if response['count'] <= 2:
                return 1  # Личка
            else:
                return 0  # Беседа
        except vk_api.exceptions.ApiError:
            return 0  # Беседа, но нет прав у бота

    def weather_city(event_func):
        timer = time.time()
        send_msg(event_func.message.peer_id, 'Введите название города:')
        for event_weather in longpoll.listen():  # Постоянный листинг сообщений
            if event_weather.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if (timer + 60) > time.time():
                    if event_weather.message.from_id == event_func.message.from_id:  # Проверка на бота
                        return event_weather.message.text
                else:
                    break

    def weather(event_func):
        s_city = weather_city(event_func)
        appid = 'a8051039c6443539398bac146ab24206'
        city_id = 0
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
            data = res.json()
            city_id = data['list'][0]['id']
        except Exception as e:
            print("Exception (find):", e)
            pass
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
            data = res.json()
            Osadki = data['weather'][0]['description']
            Temp = data['main']['temp']
            Temp_min = data['main']['temp_min']
            Temp_max = data['main']['temp_max']
            Temp_fel = data['main']['feels_like']
            send_msg(event_func.message.peer_id, 'Температура в ' + str(s_city) + '\n' +
                     'Осадки: ' + str(Osadki) + '\nТемпература:\nминимальная: ' + str(Temp_min) + '°C\n'
                     'сейчас: ' + str(Temp) + '°C\nмаксимальная: ' + str(Temp_max) + '°C\n' +
                     'ощущается как: ' + str(Temp_fel) + '°C')
        except Exception as e:
            print("Exception (weather):", e)
            pass

    def main_keyboard(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            keyboard = VkKeyboard(one_time=False)
            # keyboard.add_button('аниме(в разработке)', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_button('Валюта', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Моё', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('Погода', color=VkKeyboardColor.PRIMARY)
            vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Выберите команду:')

    def sumbol_windows(what):
        return re.sub(r'[:*?"<|>]', "", what)

    def save_file(event_func, count_attach):
        for i in range(count_attach):  # Пробег по всем вложениям
            content_type = event_func.message["attachments"][i]["type"]  # Определение типа контента
            try:  # Если папка нет, то она появится
                os.makedirs(r'content/users/' + str(event_func.message.from_id) + '/' + content_type + '/')
            except FileExistsError:  # Если есть - то есть
                pass
            if content_type == "doc":  # Если это видео
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " тип - документ")
                url = vk_polzovat.docs.getById(docs=
                                               str(event_func.message["attachments"][i]["doc"]["owner_id"]) + '_' +
                                               str(event_func.message["attachments"][i]["doc"]["id"]) + '_' +
                                               str(event_func.message["attachments"][i]["doc"]["access_key"]))[0]["url"]
                f = open(r'content/users/' + str(event_func.message.from_id) + '/doc/' +
                         sumbol_windows(str(event_func.message["attachments"][i]["doc"]["title"])), "wb")
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + ' - ' +
                         str(event_func.message["attachments"][i]["doc"]["title"]) + " успешно сохранен")

            elif content_type == "audio":  # Если это музыка
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " тип - музыка")
                url = event_func.message["attachments"][i]["audio"]["url"]
                artist = sumbol_windows(event_func.message["attachments"][i]["audio"]["artist"])
                title = sumbol_windows(event_func.message["attachments"][i]["audio"]["title"])
                f = open(r'content/users/' + str(event_func.message.from_id) + '/audio/' + str(artist) + ' — '
                         + str(title) + '.mp3', "wb")
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " успешно сохранен")

            elif content_type == "photo":  # Если это фото
                send_msg(event_func.message["peer_id"],
                         "Файл №" + str(i + 1) + " тип - фотография")
                url = vk_polzovat.photos.getById(
                    photos=str(event_func.message["attachments"][i]["photo"]["owner_id"]) + '_' +
                    str(event_func.message["attachments"][i]["photo"]["id"]) + '_' +
                    str(event_func.message["attachments"][i]["photo"]["access_key"])
                )[0]["sizes"][6]["url"]
                f = open(r'' + str('content/users/' + str(event_func.message.from_id) + '/photo/' +
                                   str(time.time()) + '.png'), "wb")
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл
                f.close()
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " успешно сохранен")

            elif content_type == "video":  # Если это фото
                send_msg(event_func.message["peer_id"], 'Отправьте пожалуйста видео как документ')

            elif content_type == "graffiti":
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " тип - граффити")
                url = vk_polzovat.docs.getById(docs=
                                               str(event_func.message["attachments"][i]["graffiti"]["owner_id"]) + '_' +
                                               str(event_func.message["attachments"][i]["graffiti"]["id"]) + '_' +
                                               str(event_func.message["attachments"][i]["graffiti"]["access_key"])
                                               )[0]["url"]
                f = open(r'content/users/' + str(event_func.message.from_id) + '/graffiti/' +
                         sumbol_windows(str(event_func.message["attachments"][i]["graffiti"]["id"])) + '.png', "wb")
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + ' - ' +
                         str(event_func.message["attachments"][i]["graffiti"]["id"]) + " успешно сохранен")


    def my_files_list(folder, event_func):
        files = os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder)
        msg = 'users/' + str(event_func.message.from_id) + '/' + folder + '\n'
        for i in range(len(files)):
            msg += folder + str(i) + ' — ' + files[i] + '\n'
        send_msg(event_func.message.peer_id, msg)

    def download_my_file(folder, number, event_func):
        if folder == 'photo/':
            file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
            upload = vk_api.VkUpload(vk)
            photo = upload.photo_messages("./content/users/" + str(event_func.message.from_id) + '/' + folder + file)
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
        elif folder == 'doc/':
            file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
            c = vk.docs.getMessagesUploadServer(type='doc', peer_id=event_func.message.peer_id)
            b = requests.post(c['upload_url'], files={
                'file': open("./content/users/" + str(event_func.message.from_id) + '/' + str(folder) + str(file), 'rb')})
            result = json.loads(b.text)["file"]
            js = vk.docs.save(file=result, title='Документ')
            attachment = f'doc{js["doc"]["owner_id"]}_{js["doc"]["id"]}'
            vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)

except ValueError:
    print(ValueError)
