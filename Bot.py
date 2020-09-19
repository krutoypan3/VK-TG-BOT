import os
import time
import Dict
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
                        text = event_main.message.text.lower()  # Что написал
                        words = text.split()
                        count_attach = len(event_main.message["attachments"])  # Кол-во вложений
                        # print(event_main)
                        if count_attach > 0:  # Есть ли вложения
                            Func.save_file(event_main, count_attach)
                        if text in Dict.func_answer:
                            Func.thread_start(Dict.func_answer[text], event_main)
                        if text in Dict.keyboard:
                            Func.thread_start(Dict.keyboard[text], event_main)
                        if text in Dict.file_answer:
                            Func.my_files_list(Dict.file_answer[text], event_main)
                        if 'скачать' in words:
                            number = ''
                            folder = ''
                            for i in range(len(words[1])):
                                if '0' <= words[1][i] <= '9':
                                    number += words[1][i]
                                else:
                                    folder += words[1][i]
                            Func.download_my_file(folder, number, event_main)

                    Func.thread_start(main, event)



    except ValueError:
        print(ValueError)
