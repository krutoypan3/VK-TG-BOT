import datetime
import json
import os
import re
import threading
import time
import requests
import vk_api
import SQL_DB
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import Dict
from googletrans import Translator

API_GROUP_KEY = "ccbc9abae2f2a2cd3ade51c6f018c4f4ae36222ab438d484e4f730d5037df411d5a294300d24a1d865b95"
API_SERVICE_KEY = "df8dbcb4df8dbcb4df8dbcb474dffe6b17ddf8ddf8dbcb480d4dd8c2633bc61379a4b76"
client_secret = "UpBtMcA3OMvYpL04RIYs"
vk_app_id = 7591843

print("Бот работает...")
group_id = '198599965'  # Указываем id сообщества
threads = list()
eventhr = []
kolpot = -1
group_sob = "@198599965"  # Указываем короткое имя бота (если нет то id)
group_name = "Братик"  # Указываем название сообщества
translator = Translator()

# Авторизация под именем сообщества
vk_session = vk_api.VkApi(token=API_GROUP_KEY)
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()


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

    def translate(text, lang):
        try:
            result = translator.translate(str(text), dest=lang).text
            return result
        except Exception as error:
            print(Exception)

    def Covid(event):
        words = event.message.text.lower().split()
        if len(words) > 1:
            if words[1] == 'америка':
                country = 'USA'
            else:
                country = translate(words[1], 'en')
        else:
            country = 'Russia'
        url = "https://covid-193.p.rapidapi.com/statistics"

        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "5a42fd676cmsh120861aa5715a2cp16f89ejsn6269c9e5abc8"
        }

        response = requests.request("GET", url, headers=headers)
        data = response.json()['response']
        a = False
        for i in range(len(data)):
            if data[i]['country'] == country:
                send_msg(event.message.peer_id, '&#9763;' + translate(str(data[i]['country']), 'ru') +
                         ' - информация по коронавирусу на ' +
                         data[i]['day'] + '&#9763;' +
                         '\n&#128106;Население страны: ' + str(data[i]['population']) +
                         '\n\n&#128554;Заболевших сегодня: ' + str(data[i]['cases']['new']) +
                         '\n&#128567;Болеющих данный момент: ' + str(data[i]['cases']['active']) +
                         '\n&#128583;Выздоровело: ' + str(data[i]['cases']['recovered']) +
                         '\n\n&#128565;Умерло: ' +
                         '\n&#128534;-сегодня: ' + str(data[i]['deaths']['new']) +
                         '\n&#128555;-всего: ' + str(data[i]['deaths']['total']) +
                         '\n\n&#9762;Всего: ' + str(data[i]['cases']['total']) + '&#9762;' +
                         '\n\nДля получения информации о конкретной стране, напишите "коронавирус (страна)"' +
                         '\nАктуальные данные предоставлены сайтом https://rapidapi.com/')
                a = True
        if not a:
            send_msg(event.message.peer_id, 'Извините, но информация о ситуации в данной стране мне неизвестна')

    # Авторизация
    def autorize(event):
        timer = time.time()
        error = 0
        UserName = ''
        send_msg(event.message.peer_id, 'Введите логин:')
        for event_login in longpoll.listen():  # Постоянный листинг сообщений
            if event_login.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if (timer + 180) > time.time():
                    UserName = event_login.message.text.split()[0]
                else:
                    error = 1
                break
        if error:
            send_msg(event.message.peer_id, 'Время авторизации истекло!')
        else:
            send_msg(event.message.peer_id, 'Введите пароль:')
            for event_register in longpoll.listen():  # Постоянный листинг сообщений
                if event_register.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                    if (timer + 180) > time.time():
                        Password = event_register.message.text.split()[0]
                        if SQL_DB.sql_fetch_user(SQL_DB.con, 'Password', UserName) == Password:
                            send_msg(event.message.peer_id, 'Вы авторизовались под пользователем: ' + UserName + '!')
                            SQL_DB.sql_update(SQL_DB.con, 'vk_id', event.message.from_id)
                        else:
                            send_msg(event.message.peer_id, 'Неверная связка логин/пароль')
                        break
                    else:
                        error = 1
                        break
            if error:
                send_msg(event.message.peer_id, 'Время авторизации истекло!')

    # Выход из аккаунта
    def logout(event):
        UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event.message.from_id)
        send_msg(event.message.peer_id, 'Вы вышли из аккаунта ' + UserName + '!')
        SQL_DB.sql_update(SQL_DB.con, 'vk_id', None)
        main_keyboard(event)

    # Проверка на вход в аккаунт
    def user_in_db(user_id):
        UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', user_id)
        if UserName is not None:
            return UserName
        else:
            return None

    # Регистрация нового аккаунта
    def register(event):
        vk_id = event.message.from_id
        timer = time.time()
        error = 0
        UserName = '0'
        Password = '0'
        send_msg(event.message.peer_id, 'Введите логин (не менее 4 и не более 16 символов):')
        for event_register in longpoll.listen():  # Постоянный листинг сообщений
            if event_register.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if (timer + 180) > time.time():
                    UserName = event_register.message.text.split()[0]
                    if UserName == sumbol_windows(UserName):
                        if SQL_DB.sql_fetch_user(SQL_DB.con, 'UserName', UserName) == UserName:
                            send_msg(event.message.peer_id, 'Пользователь с таким логином уже зарегистрирован'
                                                            ': регистрация отменена')
                            error = 2
                        if 16 > len(UserName) < 3:
                            error = 1
                        break
                    else:
                        send_msg(event.message.peer_id, 'Имя пользователя содержит недопустимые символы'
                                                        ': регистрация отменена')
                        error = 2
                else:
                    error = 1
                    break
        if error != 2:
            if error:
                send_msg(event.message.peer_id, 'Ваш логин содержит менее 4 или более 16 символов: '
                                                'регистрация отменена')
            else:
                send_msg(event.message.peer_id, 'Введите пароль (не менее 4 и не более 16 символов):')
                for event_register in longpoll.listen():  # Постоянный листинг сообщений
                    if event_register.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                        if (timer + 180) > time.time():
                            Password = event_register.message.text.split()[0]
                            if 16 > len(Password) < 3:
                                error = 1
                            break
                        else:
                            error = 1
                            break
                if error:
                    send_msg(event.message.peer_id,
                             'Ваш пароль содержит менее 4 или более 16 символов: регистрация отменена')
                else:
                    entities = UserName, Password, vk_id, None
                    SQL_DB.sql_insert(SQL_DB.con, entities)
                    send_msg(event.message.peer_id, 'Регистрация прошла успешно!\nЛогин: ' + UserName +
                             '\nПароль: ' + Password)
                    main_keyboard(event)

    # Отправка сообщения пользователю
    def send_msg(peerid, ms_g):
        vk.messages.send(peer_id=peerid, random_id=0, message=ms_g)

    # Курс евро и доллара
    def curs_value(*args):
        peer_id = args[0].message.peer_id
        link = "https://www.cbr-xml-daily.ru/daily_json.js"
        data = requests.get(link)
        USD = data.json()['Valute']["USD"]["Previous"]
        EUR = data.json()['Valute']["EUR"]["Previous"]
        forex = 'Курс валюты на утро ' + str(datetime.datetime.now().date()) + '\n\n' + \
                '&#128181; 1 USD = ' + str(USD) + ' Российских рублей\n' + \
                '&#128182; 1 EUR = ' + str(EUR) + ' Российский рублей'
        send_msg(peer_id, forex)


    # Личка или беседа
    def lich_or_beseda(my_peer):
        try:
            response = vk.messages.getConversationMembers(peer_id=my_peer)
            if response['count'] <= 2:
                return 1  # Личка
            else:
                return 0  # Беседа
        except vk_api.exceptions.ApiError:
            return 0  # Беседа, но нет прав у бота

    # Ввод города для определения погоды
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

    # Погода
    def weather(event_func):
        s_city = weather_city(event_func)
        appid = 'a8051039c6443539398bac146ab24206'
        city_id = 0
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
            data = res.json()
            city_id = data['list'][0]['id']
        except Exception as error:
            print("Exception (find):", error)
            pass
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
            data = res.json()
            Osadki = data['weather'][0]['description']
            Temp = data['main']['temp']
            Temp_fel = data['main']['feels_like']
            Wind_speed = data['wind']['speed']
            Wind_deg = data['wind']['deg']
            sunrise = time.ctime(data['sys']['sunrise']).split()[3]  # Восход
            sunset = time.ctime(data['sys']['sunset']).split()[3]  # Закат
            print(data)
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
            send_msg(event_func.message.peer_id, '&#127961;Погода в ' + str(data['name']) + '\n' +
                         '&#9925;Осадки: ' + str(Osadki) + '\n&#127777;Температура: ' + str(Temp) + '°C\n' +
                         '&#128583;ощущается как: ' + str(Temp_fel) + '°C\n&#127788;ветер: ' + Wind_deg + ' ' +
                     str(Wind_speed) + ' м/с' + '\n&#127749;рассвет: ' + str(sunrise) + '\n&#127748;закат: ' + str(sunset))
        except Exception as error:
            print("Exception (weather):", error)
            send_msg(event_func.message.peer_id, 'Извините, но я не знаю о таком месте...')
            pass

    # Главная клавиатура
    def main_keyboard(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            keyboard = VkKeyboard(one_time=False)
            # keyboard.add_button('аниме(в разработке)', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_button('Валюта', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Мои файлы', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()  # Отступ строки
            keyboard.add_button('Погода', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()  # Отступ строки
            if user_in_db(event_func.message.from_id):
                keyboard.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
            else:
                keyboard.add_button('Войти', color=VkKeyboardColor.POSITIVE)
                keyboard.add_button('Регистрация', color=VkKeyboardColor.POSITIVE)
            vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                             keyboard=keyboard.get_keyboard(), message='Выберите команду:')

    # Клавиатура с файлами
    def my_files_keyboard(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event_func.message.from_id)
            if UserName is not None:
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

    # Клавиатура с выбранным типом файлов
    def my_files_keyboard_content(event_func):
        my_peer = event_func.message.peer_id
        if lich_or_beseda(my_peer):
            UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event_func.message.from_id)
            if UserName is None:
                send_msg(event_func.message.from_id, 'Вы не авторизированы!')
            else:
                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button('как скачать?', color=VkKeyboardColor.PRIMARY)
                keyboard.add_button('как отправить?', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()  # Отступ строки
                keyboard.add_button('мои файлы', color=VkKeyboardColor.NEGATIVE)
                vk.messages.send(peer_id=my_peer, random_id=get_random_id(),
                                 keyboard=keyboard.get_keyboard(), message='Выберите команду:')

    # Ин-фа о том, как скачать
    def how_download(event_func):
        send_msg(event_func.message.peer_id, 'Команда для загрузки файлов:\n"скачать тип/номер"'
                                             '\nНапример: скачать photo/3')

    # Ин-фа о том, как загрузить
    def how_unload(event_func):
        send_msg(event_func.message.peer_id, 'Просто отправьте документ боту и он сохранит его')

    # Проверка на наличие запрещенных символов
    def sumbol_windows(what):
        return re.sub(r'[:*?"/<|>]', "", what)

    # Сохранение файлов в боте
    def save_file(event_func, count_attach):
        UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event_func.message.from_id)
        if UserName is None:
            send_msg(event_func.message.from_id, 'Вы не авторизированы!')
        else:
            for i in range(count_attach):  # Пробег по всем вложениям
                content_type = event_func.message["attachments"][i]["type"]  # Определение типа контента
                try:  # Если папка нет, то она появится
                    os.makedirs(r'content/users/' + str(UserName) + '/' + content_type + '/')
                except FileExistsError:  # Если есть - то есть
                    pass

                def func_save_mess(func_file_type, photo, func_content_name, func_content_type):
                    send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + " тип - " + func_file_type)
                    if photo == 1:
                        url = event_func.message["attachments"][i]["photo"]
                        url = url["sizes"][len(url["sizes"]) - 1]["url"]
                    elif photo == 2:
                        url = event_func.message["attachments"][i][func_content_type]['link_mp3']
                    else:
                        url = event_func.message["attachments"][i][func_content_type]["url"]
                    f = open(
                        r'content/users/' + str(UserName) + '/' + func_content_type + '/' +
                        func_content_name, "wb")
                    ufr = requests.get(url)  # делаем запрос
                    f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                    f.close()
                    send_msg(event_func.message["peer_id"], "Файл №" + str(i + 1) + ' - ' +
                             func_content_name + " успешно сохранен")

                if content_type == "doc":
                    func_save_mess('документ', 0, str(event_func.message["attachments"][i][content_type]["title"]),
                                   content_type)
                elif content_type == "audio":
                    audio = event_func.message["attachments"][i]["audio"]
                    func_save_mess('музыка', 0, str(sumbol_windows(audio["artist"])) + ' — '
                                   + str(sumbol_windows(audio["title"])) + '.mp3', content_type)
                elif content_type == "photo":
                    func_save_mess('фотография', 1, str(time.time()) + '.png', content_type)
                elif content_type == "graffiti":
                    func_save_mess('граффити', 0, str(event_func.message["attachments"][i]["graffiti"]["id"]),
                                   content_type)
                elif content_type == 'audio_message':
                    func_save_mess('голосовое сообщение', 2, str(time.time()) + '.mp3', content_type)
                elif content_type == "video":  # Если это фото
                    send_msg(event_func.message["peer_id"], 'Отправьте пожалуйста видео как документ')

    # Вывод списка файлов пользователя
    def my_files_list(folder, event_func):
        try:
            UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event_func.message.from_id)
            if UserName is None:
                send_msg(event_func.message.from_id, 'Вы не авторизированы!')
            else:
                files = os.listdir("./content/users/" + str(UserName) + '/' + folder)
                if folder == '':
                    smile = '/'
                    smile_2 = '&#128194;'
                else:
                    smile = '/&#128194;'
                    smile_2 = '&#128193;'
                msg = '&#128193;users/' + smile_2 + str(UserName) + smile + folder + '\n\n'
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

    # Выгрузка файлов из бота
    def download_my_file(folder, number, event_func):
        try:
            UserName = SQL_DB.sql_fetch(SQL_DB.con, 'UserName', event_func.message.from_id)
            if UserName is None:
                send_msg(event_func.message.from_id, 'Вы не авторизированы!')
            else:
                if folder == 'photo/':
                    file = (os.listdir("./content/users/" + str(UserName) + '/' + folder))[int(number)]
                    send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                    upload = vk_api.VkUpload(vk)
                    photo = upload.photo_messages("./content/users/" + str(UserName) + '/' + folder + file)
                    owner_id = photo[0]['owner_id']
                    photo_id = photo[0]['id']
                    access_key = photo[0]['access_key']
                    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                    vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
                elif folder == 'doc/':
                    file = (os.listdir("./content/users/" + str(UserName) + '/' + folder))[int(number)]
                    send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                    c = vk.docs.getMessagesUploadServer(type='doc', peer_id=event_func.message.peer_id)
                    b = requests.post(c['upload_url'], files={
                        'file': open("./content/users/" + str(UserName) + '/' + str(folder) +
                                     str(file), 'rb')})
                    result = json.loads(b.text)["file"]
                    js = vk.docs.save(file=result, title=file)
                    attachment = f'doc{js["doc"]["owner_id"]}_{js["doc"]["id"]}'
                    vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
                elif folder == 'graffiti/':
                    file = (os.listdir("./content/users/" + str(UserName) + '/' + folder))[int(number)]
                    send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                    c = vk.docs.getMessagesUploadServer(type='doc', peer_id=event_func.message.peer_id)
                    b = requests.post(c['upload_url'], files={
                        'file': open("./content/users/" + str(UserName) + '/' + str(folder) +
                                     str(file) + '.png', 'rb')})
                    result = json.loads(b.text)["file"]
                    js = vk.docs.save(file=result, title=file)
                    attachment = f'graffiti{js["graffiti"]["owner_id"]}_{js["graffiti"]["id"]}'
                    vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=attachment)
                elif folder == 'audio/':
                    file = (os.listdir("./content/users/" + str(UserName) + '/' + folder))[int(number)]
                    send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                    upload_url = vk.docs.getMessagesUploadServer(
                        type="audio_message", peer_id=event_func.message.peer_id, v="5.103")['upload_url']
                    request = requests.post(upload_url, files={
                        'file': open("./content/users/" + str(UserName) +
                                     '/' + folder + file, 'rb')}).json()
                    save = vk.docs.save(file=request['file'])['audio_message']
                    d = 'doc' + str(save['owner_id']) + '_' + str(save['id'])
                    vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, message=file, attachment=d)
                elif folder == 'audio_message/':
                    file = (os.listdir("./content/users/" + str(UserName) + '/' + folder))[int(number)]
                    send_msg(event_func.message.peer_id, 'Выгружаем файл...')
                    upload_url = vk.docs.getMessagesUploadServer(
                        type="audio_message", peer_id=event_func.message.peer_id, v="5.103")['upload_url']
                    request = requests.post(upload_url, files={
                        'file': open("./content/users/" + str(UserName) +
                                     '/' + folder + file, 'rb')}).json()
                    save = vk.docs.save(file=request['file'])['audio_message']
                    d = 'doc' + str(save['owner_id']) + '_' + str(save['id'])
                    vk.messages.send(peer_id=event_func.message.peer_id, random_id=0, attachment=d)
        except IndexError:
            send_msg(event_func.message.peer_id, 'Файл с таким номером не был найден...')

except Exception as e:
    print("Возникла ошибка: " + str(e))
