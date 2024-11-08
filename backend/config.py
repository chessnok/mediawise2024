import psycopg2


def get_db_connection():
    """ Функция для подключения к базе данных"""
    return psycopg2.connect(
        host="db",
        database="deeptech",
        user="deeptech",
        password="deeptech"
    )
