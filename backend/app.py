import os
import uuid
import streamlit as st
import time
from db import get_chats, add_chat_message, add_image_message, get_chat_history, get_files_by_group, create_file_group, \
    get_groups, add_file_to_db, create_chat
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
def chatbot_response(user_message) -> (str, str, int):
    message = f"Ответ бота на сообщение: {user_message}"
    src = "test.pdf"
    page_num = 3
    return message, src, page_num


# def chatbot_response(chatid):
#     context = get_chat_history(chatid)
#     context = [{"role": msg["sender"], "content": msg["message"]} for msg in
#                context]
#     # TODO: implement rag
#     context = [{"role": "system", "content": "Ты — ассистент базы знаний компании. Твоя задача, сопровождать выдачу информации по запросу пользователя. Тебе будут предоставлены данные, полученные из базы знаний по результатам запроса пользователя: текстовые данные будут выделены тегами \"<rag>\" и \"</rag>\" — всю информацию внутри тегов считай информацией из базы знаний, входное изображение также воспринимай, как источник из базы знаний. Твой ответ должен следовать следующим принципам: 1) Если запрос пользователя — вопросительный, то нужно ответить на вопрос. 2) Если запрос пользователя — поисковый (в нём нет вопросительной интонации), то нужно кратко описать, что находится на изображении или в тексте из базы знаний. 3) Если ты считаешь, что предоставленные данные из базы знаний не релевантны запросу пользователя — написать, что ты не можешь ответить на данный вопрос по причине отсутствия достоверных данных. Ответ должен содержать только текст, без дополнительной стилизации и комментариев."}] + context
#     resp = ask(context)
#     return resp


# Проверка и создание user_id
user_id = cookies.get('Authorization')
if not user_id:
    user_id = str(uuid.uuid4())
    cookies['Authorization'] = user_id
    create_chat('Первый чат', user_id)
    st.session_state.chats = get_chats(user_id)[0]['id']

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
                user_id = str(cookies.get('Authorization'))
                chat_id = create_chat(new_chat_name, user_id)
                st.session_state.chats[chat_id] = new_chat_name
                st.session_state.selected_chat_id = chat_id

        user_id = str(cookies.get('Authorization'))
        chats = get_chats(user_id)
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
            if not msg["is_pdf_page"]:
                st.chat_message(msg["sender"]).write(msg["message"])
            else:
                try:
                    page_num = msg["page_num"]
                    src = msg["message"]
                    st.markdown(
                        f'<embed src="/files/{src}#page={str(page_num)}" width="100%" height="500px" type="application/pdf">',
                        unsafe_allow_html=True
                    )

                except:
                    st.chat_message(msg["sender"]).image("not_found.jpg", caption="Файл не найден")

    prompt = st.chat_input("Your message...")

    if prompt:
        if not selected_chat_id:
            st.error("Выберите чат!")
        else:
            add_chat_message(selected_chat_id, "user", prompt)
            with chat_container:
                st.chat_message("user").write(prompt)
            response, src, page_num = chatbot_response(prompt)
            #response = chatbot_response(selected_chat_id)
            add_chat_message(selected_chat_id, "assistant", response)
            add_image_message(selected_chat_id, "assistant", src, page_num)
            with chat_container:
                st.chat_message("assistant").write(response)
                st.chat_message("assistant").markdown(
                    f'<embed src="/files/{src}#page={str(page_num)}" width="100%" height="500px" type="application/pdf">',
                    unsafe_allow_html=True
                )

# Вкладка библиотеки
with tab2:
    st.header("Библиотека файлов")

    new_group_name = st.text_input("Введите название новой группы для файлов:",
                                   key="new_group_name")

    if st.button("Создать группу"):
        if new_group_name:
            create_file_group(new_group_name)
            st.success(f"Группа '{new_group_name}' создана!")

    selected_group = st.selectbox("Выберите группу для просмотра:",
                                  get_groups())
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
                            try:
                                # Преобразуем memoryview в bytes, а затем декодируем в строку
                                content = file['content'].tobytes().decode(
                                    "utf-8")
                                # Ограничиваем высоту контейнера с прокруткой
                                st.markdown(
                                    f"""
                                    <div style="height:400px; overflow-y:scroll; border:1px solid #ccc; padding:10px; white-space:pre-wrap;">
                                        {content}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            except UnicodeDecodeError:
                                st.error(
                                    "Не удалось декодировать содержимое файла.")

                        elif file['file_type'] == "pdf":
                            # Ссылка для просмотра PDF файла
                            file_url = f"/files/{file['file_name']}"
                            st.markdown(
                                 f'<embed src="{file_url}" width="100%" height="500px" type="application/pdf">',
                                 unsafe_allow_html=True
                            )
            else:
                st.write("В этой группе пока нет файлов!")


    if selected_group:
        display_files()

    uploaded_file = st.file_uploader("Загрузить файл (txt или pdf):",
                                     type=["txt", "pdf"])

    # Загрузка файла
    if uploaded_file:
        if st.button("Загрузить файл") and selected_group:
            if uploaded_file.name in map(lambda x: x['file_name'],
                                         get_files_by_group(selected_group)):
                st.error(
                    f"Файл '{uploaded_file.name}' уже загружен в группу '{selected_group}'")
            else:
                start_time = time.time()
                add_file_to_db(uploaded_file, selected_group)
                st.success(
                    f"Файл '{uploaded_file.name}' загружен в группу '{selected_group}'")
                st.write(
                    f"Время загрузки: {time.time() - start_time:.2f} секунд")

                files_container.empty()
                display_files()
