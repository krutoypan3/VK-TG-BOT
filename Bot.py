import os
import Func
from Func import longpoll
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

load_dotenv()
API_GROUP_KEY = os.environ.get("API_GROUP_KEY")
API_USER_KEY = os.environ.get("API_USER_KEY")
API_SERVICE_KEY = os.environ.get("API_SERVICE_KEY")
client_secret = os.environ.get("client_secret")
vk_app_id = int(os.environ.get("vk_app_id"))


if __name__ == '__main__':
    try:
        for event in longpoll.listen():  # Постоянный листинг сообщений
            if event.type == VkBotEventType.MESSAGE_NEW:  # Проверка на приход сообщения
                if event.message.from_id > 0:  # Проверка на бота
                    def main(event_main):
                        pass
                    
                    Func.thread_start(main, event)



    except ValueError:
        print(ValueError)

