import os
import time

import requests
import Func
from Func import longpoll
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import datetime
'''
import requests #импортируем модуль
f=open(r'D:\file_bdseo.zip',"wb") #открываем файл для записи, в режиме wb
ufr = requests.get("http://site.ru/file.zip") #делаем запрос
f.write(ufr.content) #записываем содержимое в файл; как видите - content запроса
f.close()'''



if __name__ == '__main__':
    try:
        for event in longpoll.listen():  # Постоянный листинг сообщений
            if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if event.message.from_id > 0:  # Проверка на бота
                    def main(event_main):
                        count_attach = len(event_main.message["attachments"])  # Кол-во вложений
                        print(event_main)
                        if count_attach > 0:  # Есть ли вложения
                            for i in range(count_attach):  # Пробег по всем вложениям
                                content_type = event_main.message["attachments"][i]["type"]  # Определение типа контента
                                if content_type == "video":  # Если это видео
                                    Func.send_msg(event_main.message["peer_id"], "Вы прислали видео")

                                if content_type == "photo":  # Если это фото
                                    Func.send_msg(event_main.message["peer_id"], "Вы прислали фото")
                                    url = Func.vk_polzovat.photos.getById(
                                        photos=
                                        str(event_main.message["attachments"][i]["photo"]["owner_id"]) + '_' +
                                        str(event_main.message["attachments"][i]["photo"]["id"]) + '_' +
                                        str(event_main.message["attachments"][i]["photo"]["access_key"])
                                    )[0]["sizes"][6]["url"]
                                    try:  # Если папка нет, то она появится
                                        os.makedirs(r'content/users/' + str(event_main.message.from_id) + '/' +
                                                    str(datetime.datetime.now().date()) + '/')
                                    except FileExistsError:  # Если есть - то есть
                                        pass
                                    f = open(r'content/users/' + str(event_main.message.from_id) + '/' +
                                             str(datetime.datetime.now().date()) + '/' + str(time.time()) +
                                             '.jpg', "wb")  # открываем файл для записи, в режиме wb
                                    ufr = requests.get(url)  # делаем запрос
                                    f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
                                    f.close()
                                    Func.send_msg(event_main.message["peer_id"], "Фото успешно сохранено")


                    Func.thread_start(main, event)



    except ValueError:
        print(ValueError)
