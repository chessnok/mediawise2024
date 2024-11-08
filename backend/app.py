import streamlit as st
import time
from datetime import datetime
from psycopg2.extras import RealDictCursor
from config import get_db_connection

# Инициализация состояния приложения
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Функция для обработки чата
def chatbot_response(user_message):
    # Простая имитация ответа чата
    return f"Ответ бота на сообщение: {user_message}"

# Функция для добавления сообщения в историю чата
def add_chat_message(sender, message):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_history (sender, message) VALUES (%s, %s)",
                (sender, message)
            )
    conn.close()

# Функция для получения истории чата
def get_chat_history():
    conn = get_db_connection()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT sender, message FROM chat_history ORDER BY id")
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
    st.header("Чат с ботом")
    user_input = st.text_input("Введите ваше сообщение:", key="user_input")

    if st.button("Отправить"):
        if user_input:
            # Добавление сообщения в базу данных
            add_chat_message("Вы", user_input)
            response = chatbot_response(user_input)
            add_chat_message("Бот", response)
            st.session_state.user_input = ""  # Очистка ввода после отправки

    # Отображение истории чата
    chat_history = get_chat_history()
    for message in chat_history:
        st.write(f"{message['sender']}: {message['message']}")

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
