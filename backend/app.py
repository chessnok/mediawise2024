import os
import uuid
import streamlit as st
import time
from datetime import datetime
from psycopg2.extras import RealDictCursor
from config import get_db_connection
from streamlit_cookies_manager import CookieManager

# Инициализация менеджера кук
cookies = CookieManager()

if not cookies.ready():
    # Ожидаем загрузки кук
    st.stop()


if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if 'chats' not in st.session_state:
    st.session_state.chats = {"Main Chat": [
        {"sender": "assistant", "message": "How can I help you?"}]}

if 'selected_chat' not in st.session_state:
    st.session_state.selected_chat = ""

if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

if not os.path.exists("/files"):
    os.makedirs("/files")


# Функции для чата и работы с файлами
def chatbot_response(user_message):
    return f"Ответ бота на сообщение: {user_message}"


def create_chat(chat_name):
    user_id = str(cookies.get('Authorization'))
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


def get_chats():
    user_id = str(cookies.get('Authorization'))
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
            file_path = os.path.join("/files", file.name)  # Путь для сохранения файла
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
            cur.execute("SELECT group_name FROM file_groups ORDER BY timestamp DESC")
            groups = [row['group_name'] for row in cur.fetchall()]
    conn.close()
    return groups


# Проверка и создание user_id
user_id = cookies.get('Authorization')
if not user_id:
    user_id = str(uuid.uuid4())
    cookies['Authorization'] = user_id
    create_chat('Первый чат')
    st.session_state.chats = get_chats()[0]['id']


# Основной интерфейс приложения
st.title("Приложение с чатом и библиотекой файлов")

tab1, tab2 = st.tabs(["Чат", "Библиотека"])


# Вкладка чата
with tab1:
    st.title("💬 Chatbot")

    with st.sidebar:
        new_chat_name = st.text_input("Введите название нового чата",
                                      key="new_chat_name")

        if st.button("Создать чат"):
            if new_chat_name:
                chat_id = create_chat(new_chat_name)
                st.session_state.chats[chat_id] = new_chat_name
                st.session_state.selected_chat_id = chat_id

        chats = get_chats()
        chat_options = {chat['id']: chat['name'] for chat in chats}
        selected_chat_id = st.selectbox("Выберите чат",
                                        options=list(chat_options.keys()),
                                        format_func=lambda x: chat_options[x])
        st.session_state.selected_chat_id = selected_chat_id

    st.caption("🚀 A chatbot powered by DeepTech")

    if selected_chat_id:
        chat_messages = get_chat_history(selected_chat_id)
    else:
        chat_messages = []

    chat_container = st.container()
    with chat_container:
        for msg in chat_messages:
            st.chat_message(msg["sender"]).write(msg["message"])

    prompt = st.chat_input("Your message...")

    if prompt:
        if not selected_chat_id:
            st.error("Выберите чат!")
        else:
            add_chat_message(selected_chat_id, "user", prompt)
            with chat_container:
                st.chat_message("user").write(prompt)

            response = chatbot_response(prompt)
            add_chat_message(selected_chat_id, "assistant", response)
            with chat_container:
                st.chat_message("assistant").write(response)


# Вкладка библиотеки
with tab2:
    st.header("Библиотека файлов")

    new_group_name = st.text_input("Введите название новой группы для файлов:",
                                   key="new_group_name")

    if st.button("Создать группу"):
        if new_group_name:
            create_file_group(new_group_name)
            st.success(f"Группа '{new_group_name}' создана!")

    selected_group = st.selectbox("Выберите группу для просмотра:", get_groups())
    st.session_state.selected_group = selected_group

    files_container = st.empty()

    def display_files():
        with files_container.container():
            st.subheader(f"Файлы в группе: {selected_group}")
            files = get_files_by_group(selected_group)
            if files:
                for file in files:
                    with st.expander(file['file_name']):
                        st.write(f"Имя файла: {file['file_name']}")
                        st.write(f"Тип файла: {file['file_type']}")
                        st.write(
                            f"Время загрузки: {file['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                        if file['file_type'] == "txt":
                            st.text(file['content'].decode("utf-8"))
                        elif file['file_type'] == "pdf":
                            # Ссылка для просмотра PDF файла
                            file_url = f"/files/{file['file_name']}"
                            st.markdown(f'<embed src="{file_url}" width="100%" height="500px" type="application/pdf" >',
                                        unsafe_allow_html=True)
            else:
                st.write("В этой группе пока нет файлов!")

    if selected_group:
        display_files()

    uploaded_file = st.file_uploader("Загрузить файл (txt или pdf):",
                                     type=["txt", "pdf"])

    # Загрузка файла
    if uploaded_file:
        if st.button("Загрузить файл") and selected_group:
            if uploaded_file.name in map(lambda x: x['file_name'], get_files_by_group(selected_group)):
                st.error(f"Файл '{uploaded_file.name}' уже загружен в группу '{selected_group}'")
            else:
                start_time = time.time()
                add_file_to_db(uploaded_file, selected_group)
                st.success(f"Файл '{uploaded_file.name}' загружен в группу '{selected_group}'")
                st.write(f"Время загрузки: {time.time() - start_time:.2f} секунд")

                files_container.empty()
                display_files()

