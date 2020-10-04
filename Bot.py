import time

import Dict
import Func
from Func import longpoll
from vk_api.bot_longpoll import VkBotEventType
'''
import requests #импортируем модуль
f=open(r'D:\file_bdseo.zip',"wb") #открываем файл для записи, в режиме wb
ufr = requests.get("http://site.ru/file.zip") #делаем запрос
f.write(ufr.content) #записываем содержимое в файл; как видите - content запроса
f.close()'''



if __name__ == '__main__':
    try:
        last_messages = []
        reg_or_log = []
        for event in longpoll.listen():  # Постоянный листинг сообщений
            if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if event.message.from_id > 0:  # Проверка на бота
                    def main(event_main):
                        if event.message.from_id in last_messages:  # Если id в списке то завершаем функцию
                            return True
                        else:
                            last_messages.append(event_main.message.from_id)  # Если нет в списке - добавляем
                        text = event_main.message.text.lower()  # Что написал
                        words = text.split()
                        count_attach = len(event_main.message["attachments"])  # Кол-во вложений
                        # print(event_main)
                        if count_attach > 0:  # Есть ли вложения
                            Func.save_file(event_main, count_attach)
                        if text in Dict.func_answer:
                            Func.thread_start(Dict.func_answer[text], event_main)
                        if text in Dict.file_answer:
                            Func.my_files_list(Dict.file_answer[text], event_main)
                        if text in Dict.keyboard:
                            Func.thread_start(Dict.keyboard[text], event_main)
                        if 'скачать' in words:
                            number = ''
                            folder = ''
                            for i in range(len(words[1])):
                                if '0' <= words[1][i] <= '9':
                                    number += words[1][i]
                                else:
                                    folder += words[1][i]
                            Func.download_my_file(folder, number, event_main)
                        if text == 'регистрация':
                            if event_main.message.from_id not in reg_or_log:
                                reg_or_log.append(event_main.message.from_id)
                                if Func.user_in_db(event_main.message.from_id) is None:
                                    Func.register(event_main)
                                else:
                                    Func.send_msg(event_main.message.peer_id, 'У вас уже выполнен вход '
                                                                              'под другим пользователем!')
                                reg_or_log.remove(event_main.message.from_id)
                        if text == 'войти':
                            if event_main.message.from_id not in reg_or_log:
                                reg_or_log.append(event_main.message.from_id)
                                if Func.user_in_db(event_main.message.from_id) is None:
                                    Func.autorize(event_main)
                                else:
                                    Func.send_msg(event_main.message.peer_id, 'У вас уже выполнен вход '
                                                                          'под другим пользователем!')
                                reg_or_log.remove(event_main.message.from_id)
                        if text == 'выйти':
                            if event_main.message.from_id not in reg_or_log:
                                reg_or_log.append(event_main.message.from_id)
                                if Func.user_in_db(event_main.message.from_id):
                                    Func.logout(event_main)
                                reg_or_log.remove(event_main.message.from_id)
                        if len(words) > 0:
                            Func.thread_start(Dict.func_answer_more_word[words[0]], event_main)
                        time.sleep(2)
                        try:
                            last_messages.remove(event_main.message.from_id)
                        except AttributeError:
                            pass
                    Func.thread_start(main, event)


    except ValueError:
        print(ValueError)
