import os

import psycopg2


def get_db_connection():
    """ Функция для подключения к базе данных"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "deeptech"),
        user=os.getenv("DB_USER", "deeptech"),
        password=os.getenv("DB_PASSWORD", "deeptech"),
    )
