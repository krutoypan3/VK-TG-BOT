import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
database_key = os.environ.get("database_key")
user_key = os.environ.get("user_key")
password_key = os.environ.get("password_key")
host_key = os.environ.get("host_key")
port_key = os.environ.get("port_key")


# Соединение с БД
def sql_connection():
    conc = psycopg2.connect(
        database=database_key,  # Название базы данных
        user=user_key,  # Имя пользователя
        password=password_key,  # Пароль пользователя
        host=host_key,  # Хост
        port=port_key  # Порт
    )
    return conc


con = sql_connection()  # Создание соединения с БД
