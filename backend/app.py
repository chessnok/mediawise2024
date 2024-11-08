import uuid

import streamlit as st
import time
from datetime import datetime
from psycopg2.extras import RealDictCursor
from config import get_db_connection

# Инициализация состояния приложения
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if 'chats' not in st.session_state:
    st.session_state.chats = {"Main Chat": [{"sender": "assistant", "message": "How can I help you?"}]}

if 'selected_chat' not in st.session_state:
    st.session_state.selected_chat = ""


# Функция для обработки чата
def chatbot_response(user_message):
    # Простая имитация ответа чата
    return f"Ответ бота на сообщение: {user_message}"


def create_chat(chat_name):
    chat_id = str(uuid.uuid4())  # Преобразуем UUID в строку
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chats (id, name) VALUES (%s, %s)",
                (chat_id, chat_name)
            )
    conn.close()
    return chat_id


# Функция для получения списка чатов
def get_chats():
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM chats ORDER BY timestamp DESC")
            chats = cur.fetchall()
    conn.close()
    return chats


# Функция для добавления сообщения в историю чата
def add_chat_message(chat_id, sender, message):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (sender, message, chat_id) VALUES (%s, %s, %s)",
                (sender, message, chat_id)
            )
    conn.close()


# Функция для получения истории чата по chat_id
def get_chat_history(chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT sender, message, timestamp FROM messages WHERE chat_id = %s ORDER BY timestamp",
                (chat_id,)
            )
            chat_history = cur.fetchall()
    conn.close()
    return chat_history


# Функция для добавления файла в базу данных
def add_file_to_db(file, group_name):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            # Получение ID группы
            cur.execute("SELECT id FROM file_groups WHERE group_name = %s", (group_name,))
            group = cur.fetchone()
            if not group:
                raise ValueError("Группа не найдена")
            group_id = group[0]

            # Добавление файла
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
                    file.getvalue()
                )
            )
    conn.close()


# Функция для создания новой группы файлов
def create_file_group(group_name):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO file_groups (group_name) VALUES (%s) ON CONFLICT DO NOTHING", (group_name,))
    conn.close()


# Функция для получения групп файлов
def get_file_groups():
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT group_name FROM file_groups")
            groups = [row['group_name'] for row in cur.fetchall()]
    conn.close()
    return groups


# Функция для получения файлов по группе
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


# Основной интерфейс приложения
st.title("Приложение с чатом и библиотекой файлов")

tab1, tab2 = st.tabs(["Чат", "Библиотека"])

# Вкладка чата
with tab1:
    st.title("💬 Chatbot")

    # Загрузка списка чатов из базы данных
    with st.sidebar:
        st.title("Ваши чаты")

        # Поле для ввода имени нового чата
        new_chat_name = st.text_input("Введите название нового чата", key="new_chat_name")

        # Кнопка добавления нового чата
        if st.button("Создать чат"):
            if new_chat_name:
                chat_id = create_chat(new_chat_name)  # Создаем чат и получаем его chat_id
                st.session_state.chats[chat_id] = new_chat_name
                st.session_state.selected_chat_id = chat_id

        # Загрузка чатов и отображение в selectbox
        chats = get_chats()
        chat_options = {chat['id']: chat['name'] for chat in chats}
        selected_chat_id = st.selectbox("Выберите чат", options=list(chat_options.keys()), format_func=lambda x: chat_options[x])
        st.session_state.selected_chat_id = selected_chat_id

    st.caption("🚀 A chatbot powered by DeepTech")

    # Загрузка истории сообщений для выбранного чата
    if selected_chat_id:
        chat_messages = get_chat_history(selected_chat_id)
    else:
        chat_messages = []

    # Создание контейнера для чата и отображение истории сообщений
    chat_container = st.container()
    with chat_container:
        for msg in chat_messages:
            st.chat_message(msg["sender"]).write(msg["message"])

    # Позиционирование строки ввода под контейнером сообщений
    prompt = st.chat_input("Your message...")

    # Обработка ответа от пользователя
    if prompt:
        if not selected_chat_id:
            st.error("Выберите чат!")
        else:
            # Добавление сообщения от пользователя
            add_chat_message(selected_chat_id, "user", prompt)
            with chat_container:
                st.chat_message("user").write(prompt)

            # Получение и отображение ответа чатбота
            response = chatbot_response(prompt)
            add_chat_message(selected_chat_id, "assistant", response)
            with chat_container:
                st.chat_message("assistant").write(response)

# Вкладка библиотеки
with tab2:
    st.header("Библиотека файлов")

    # Получение списка групп из базы данных
    group_names = get_file_groups()
    selected_group = st.selectbox("Выберите группу для просмотра:", group_names, key="selected_group")

    # Показ файлов из выбранной группы
    if selected_group:
        st.subheader(f"Файлы в группе: {selected_group}")
        files = get_files_by_group(selected_group)
        for file in files:
            st.write(f"Имя файла: {file['file_name']}")
            st.write(f"Тип файла: {file['file_type']}")
            st.write(f"Время загрузки: {file['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            with st.expander("Посмотреть файл"):
                st.text(file['content'].decode("utf-8") if file['file_type'] == "txt" else "PDF просмотр недоступен")

    # Создание новой группы
    new_group = st.text_input("Введите название новой группы для файлов:")
    if st.button("Создать группу"):
        if new_group:
            create_file_group(new_group)
            st.success(f"Группа '{new_group}' создана!")

    # Загрузка файла в группу
    uploaded_file = st.file_uploader("Загрузить файл (txt или pdf):", type=["txt", "pdf"])
    if uploaded_file and selected_group:
        start_time = time.time()
        add_file_to_db(uploaded_file, selected_group)
        st.success(f"Файл '{uploaded_file.name}' загружен в группу '{selected_group}'")
        st.write(f"Время загрузки: {time.time() - start_time:.2f} секунд")
