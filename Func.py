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
import Dict
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
            print(data)
            Osadki = data['weather'][0]['description']
            Temp = data['main']['temp']
            Temp_min = data['main']['temp_min']
            Temp_max = data['main']['temp_max']
            Temp_fel = data['main']['feels_like']
            Wind_speed = data['wind']['speed']
            Wind_deg = data['wind']['deg']
            print(Wind_deg)
            if 0 <= Wind_deg <= 22:
                Wind_deg = 'северный'
            elif 23 <= Wind_deg <= 66:
                Wind_deg = 'северо-восточный'
            elif 67 <= Wind_deg <= 112:
                Wind_deg = 'восточный'
            elif 113 <= Wind_deg <= 158:
                Wind_deg = 'юго-восточный'
            elif 159 <= Wind_deg <= 203:
                Wind_deg = 'южный'
            elif 204 <= Wind_deg <= 248:
                Wind_deg = 'юго-западный'
            elif 249 <= Wind_deg <= 293:
                Wind_deg = 'западный'
            elif 294 <= Wind_deg <= 338:
                Wind_deg = 'северо-западный'
            elif 339 <= Wind_deg <= 360:
                Wind_deg = 'северный'
            print(Wind_deg)

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
            keyboard.add_button('Мои файлы', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('Погода', color=VkKeyboardColor.PRIMARY)
            vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Выберите команду:')

    def my_files_keyboard(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            keyboard = VkKeyboard(one_time=False)
            # keyboard.add_button('аниме(в разработке)', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_button('аудио', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('фото', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('видео', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('документы', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('гс', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('граффити', color=VkKeyboardColor.POSITIVE)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('главная', color=VkKeyboardColor.NEGATIVE)
            vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Выберите команду:')

    def my_files_keyboard_content(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button('как скачать?', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('как отправить?', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('мои файлы', color=VkKeyboardColor.NEGATIVE)
            vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Выберите команду:')
    def how_download(event_func):
        send_msg(event_func.message.peer_id, 'Команда для загрузки файлов:\n"скачать тип/номер"'
                                             '\nНапример: скачать photo/3')
    def how_unload(event_func):
        send_msg(event_func.message.peer_id, 'Просто отправьте документ боту и он сохранит его')

    def sumbol_windows(what):
        return re.sub(r'[:*?"<|>]', "", what)

    def save_file(event_func, count_attach):
        for i in range(count_attach):  # Пробег по всем вложениям
            content_type = event_func.message["attachments"][i]["type"]  # Определение типа контента
            try:  # Если папка нет, то она появится
                os.makedirs(r'content/users/' + str(event_func.message.from_id) + '/' + content_type + '/')
            except FileExistsError:  # Если есть - то есть
                pass

            def func_save_mess(func_file_type, photo, func_content_name, func_content_type):
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " тип - " + func_file_type)
                if photo:
                    url = event_func.message["attachments"][i]["photo"]
                    url = url["sizes"][len(url["sizes"]) - 1]["url"]
                else:
                    url = event_func.message["attachments"][i][func_content_type]["url"]
                f = open(
                    r'content/users/' + str(event_func.message.from_id) + '/' + func_content_type + '/' +
                    func_content_name, "wb")
                ufr = requests.get(url)  # делаем запрос
                f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                f.close()
                send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + ' - ' +
                         func_content_name + " успешно сохранен")

            if content_type == "doc":
                func_save_mess('документ', 0, str(event_func.message["attachments"][i][content_type]["title"]), content_type)
            elif content_type == "audio":
                audio = event_func.message["attachments"][i]["audio"]
                func_save_mess('музыка', 0, str(sumbol_windows(audio["artist"])) + ' — '
                               + str(sumbol_windows(audio["title"])) + '.mp3', content_type)
            elif content_type == "photo":
                func_save_mess('фотография', 1, str(time.time()) + '.png', content_type)
            elif content_type == "graffiti":
                func_save_mess('граффити', 0, str(event_func.message["attachments"][i]["graffiti"]["id"]), content_type)
            elif content_type == 'audio_message':
                func_save_mess('голосовое сообщение', 0, str(time.time()) + '.mp3', content_type)
            elif content_type == "video":  # Если это фото
                send_msg(event_func.message["peer_id"], 'Отправьте пожалуйста видео как документ')



    def my_files_list(folder, event_func):
        try:
            files = os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder)
            if folder == '':
                smile = '/'
                smile_2 = '&#128194;'
            else:
                smile = '/&#128194;'
                smile_2 = '&#128193;'
            msg = '&#128193;users/' + smile_2 + str(event_func.message.from_id) + smile + folder + '\n\n'
            smile_3 = Dict.smile_list[folder]
            for i in range(len(files)):
                if len(files[i]) > 27:
                    new = ''
                    for j in range(len(files[i])):
                        if j < 16:
                            new += files[i][j]
                        elif j == 17:
                            new += '...'
                        elif (j + 7) > len(files[i]):
                            new += files[i][j]
                    files[i] = new
                msg += smile_3 + ' ' + folder + str(i) + ' — ' + files[i] + '\n'
            send_msg(event_func.message.peer_id, msg)
        except FileNotFoundError:
            send_msg(event_func.message.peer_id, 'У вас нет файлов')
            how_unload(event_func)

    def download_my_file(folder, number, event_func):
        try:
            if folder == 'photo/':
                file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
                send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                upload = vk_api.VkUpload(vk)
                photo = upload.photo_messages("./content/users/" + str(event_func.message.from_id) +
                                              '/' + folder + file)
                owner_id = photo[0]['owner_id']
                photo_id = photo[0]['id']
                access_key = photo[0]['access_key']
                attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
            elif folder == 'doc/':
                file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
                send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                c = vk.docs.getMessagesUploadServer(type='doc', peer_id=event_func.message.peer_id)
                b = requests.post(c['upload_url'], files={
                    'file': open("./content/users/" + str(event_func.message.from_id) + '/' + str(folder) +
                                 str(file), 'rb')})
                result = json.loads(b.text)["file"]
                js = vk.docs.save(file=result, title=file)
                attachment = f'doc{js["doc"]["owner_id"]}_{js["doc"]["id"]}'
                vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
            elif folder == 'graffiti/':
                file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
                send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                c = vk.docs.getMessagesUploadServer(type='doc', peer_id=event_func.message.peer_id)
                b = requests.post(c['upload_url'], files={
                    'file': open("./content/users/" + str(event_func.message.from_id) + '/' + str(folder) +
                                 str(file), 'rb')})
                result = json.loads(b.text)["file"]
                js = vk.docs.save(file=result, title=file)
                attachment = f'graffiti{js["graffiti"]["owner_id"]}_{js["graffiti"]["id"]}'
                vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
            elif folder == 'audio/':
                file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
                send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                upload_url = vk.docs.getMessagesUploadServer(type="audio_message", peer_id=event_func.message.peer_id,
                                                v="5.103")['upload_url']
                request = requests.post(upload_url, files={
                    'file': open("./content/users/" + str(event_func.message.from_id) +
                                 '/' + folder + file, 'rb')}).json()
                save = vk.docs.save(file=request['file'])['audio_message']
                d = 'doc' + str(save['owner_id']) + '_' + str(save['id'])
                vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, message=file, attachment=d)
            elif folder == 'audio_message/':
                file = (os.listdir("./content/users/" + str(event_func.message.from_id) + '/' + folder))[int(number)]
                send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                upload_url = vk.docs.getMessagesUploadServer(type="audio_message", peer_id=event_func.message.peer_id,
                                                             v="5.103")['upload_url']
                request = requests.post(upload_url, files={
                    'file': open("./content/users/" + str(event_func.message.from_id) +
                                 '/' + folder + file, 'rb')}).json()
                save = vk.docs.save(file=request['file'])['audio_message']
                d = 'doc' + str(save['owner_id']) + '_' + str(save['id'])
                vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=d)
        except IndexError:
            send_msg(event_func.message.peer_id, 'Файл с таким номером не был найден...')

except ValueError:
    print(ValueError)
