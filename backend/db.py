import os
from datetime import datetime

from config import get_db_connection
import uuid
from psycopg2.extras import RealDictCursor


def create_chat(chat_name, user_id: str):
    chat_id = str(uuid.uuid4())
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chats (id, name, user_id) VALUES (%s, %s, %s)",
                (chat_id, chat_name, user_id)
            )
    conn.close()
    return chat_id


def get_chats(user_id: str):
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name FROM chats WHERE user_id = %s ORDER BY timestamp DESC",
                (user_id,))
            chats = cur.fetchall()
    conn.close()
    return chats


def add_chat_message(chat_id, sender, message):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (sender, message, chat_id) VALUES (%s, %s, %s)",
                (sender, message, chat_id)
            )
    conn.close()


def add_image_message(chat_id, sender, image: str, page_num: int):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (sender, is_pdf_page, chat_id, message, page_num) VALUES (%s, %s, %s, %s, %s)",
                (sender, True, chat_id, image, page_num)
            )
    conn.close()


def get_chat_history(chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT sender, message, timestamp, is_pdf_page, page_num FROM messages WHERE chat_id = %s ORDER BY timestamp",
                (chat_id,)
            )
            chat_history = cur.fetchall()
    conn.close()
    return chat_history


def add_file_to_db(file, group_name):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM file_groups WHERE group_name = %s",
                        (group_name,))
            group = cur.fetchone()
            if not group:
                raise ValueError("Группа не найдена")
            group_id = group[0]

            # Сохранение файла в директории /files
            file_path = os.path.join("/files",
                                     file.name)  # Путь для сохранения файла
            with open(file_path, "wb") as f:
                f.write(file.getvalue())

            cur.execute(
                """
                INSERT INTO files (group_id, file_name, file_type, timestamp, content)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    group_id,
                    file.name,
                    "pdf" if file.name.endswith(".pdf") else "txt",
                    datetime.now(),
                    file_path  # Сохраняем путь к файлу в базе данных
                )
            )
    conn.close()


def create_file_group(group_name):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO file_groups (group_name) VALUES (%s) ON CONFLICT DO NOTHING",
                (group_name,))
    conn.close()


def get_file_groups():
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT group_name FROM file_groups")
            groups = [row['group_name'] for row in cur.fetchall()]
    conn.close()
    return groups


def get_files_by_group(group_name):
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT f.file_name, f.file_type, f.timestamp, f.content
                FROM files f
                JOIN file_groups g ON f.group_id = g.id
                WHERE g.group_name = %s
                """,
                (group_name,)
            )
            files = cur.fetchall()
    conn.close()
    return files


def get_groups():
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT group_name FROM file_groups ORDER BY timestamp DESC")
            groups = [row['group_name'] for row in cur.fetchall()]
    conn.close()
    return groups
