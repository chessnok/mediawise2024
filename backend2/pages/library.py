import streamlit as st
import os
import re
import uuid
import json
from streamlit_pdf_viewer import pdf_viewer  # Импортируем pdf_viewer


# base64 больше не нужен, поэтому его можно удалить

def sanitize_filename(filename):
    return re.sub(r'[^а-яА-Яa-zA-Z0-9_\.-]', '_', filename)


st.title("Библиотека")

# Определяем категории
categories = ['Категория 1', 'Категория 2', 'Категория 3']

# Базовая папка для загрузок
uploads_folder = 'uploads'
if not os.path.exists(uploads_folder):
    os.makedirs(uploads_folder)

# Файл метаданных для хранения связей файлов и категорий
metadata_file = 'file_metadata.json'

# Загружаем существующие метаданные
if os.path.exists(metadata_file):
    with open(metadata_file, 'r', encoding='utf-8') as f:
        file_metadata = json.load(f)
else:
    file_metadata = {}

# Создаем вкладки для загрузки и просмотра файлов
tab_upload, tab_view = st.tabs(["Загрузка файлов", "Просмотр файлов"])

with tab_upload:
    st.header("Загрузка файлов")
    # Выбор категорий (множественный выбор)
    selected_categories = st.multiselect('Выберите категории для файла', categories)

    # Загрузка файла
    uploaded_file = st.file_uploader("Выберите файл для загрузки (PDF или TXT)", type=["pdf", "txt"])

    if uploaded_file is not None and selected_categories:
        file_details = {"Имя файла": uploaded_file.name, "Тип файла": uploaded_file.type}
        st.write(file_details)

        # Проверяем расширение файла
        allowed_extensions = ['.pdf', '.txt']
        ext = os.path.splitext(uploaded_file.name)[1]
        if ext.lower() not in allowed_extensions:
            st.error("Неподдерживаемый тип файла.")
        else:
            # Санитизация имени файла
            safe_filename = sanitize_filename(uploaded_file.name)

            # Генерируем уникальный идентификатор файла
            unique_filename = f"{uuid.uuid4()}{ext}"
            save_path = os.path.join(uploads_folder, unique_filename)

            # Сохраняем файл локально
            try:
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Файл успешно сохранен как {safe_filename}")

                # Обновляем метаданные
                file_metadata[unique_filename] = {
                    'original_name': safe_filename,
                    'categories': selected_categories
                }

                # Сохраняем метаданные
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(file_metadata, f, ensure_ascii=False, indent=4)

            except Exception as e:
                st.error(f"Ошибка при сохранении файла: {e}")
    else:
        if uploaded_file is not None and not selected_categories:
            st.warning("Пожалуйста, выберите хотя бы одну категорию.")

with tab_view:
    st.header("Просмотр файлов")

    # Выбор категории
    selected_category = st.selectbox('Выберите категорию', categories)

    if selected_category:
        # Получаем файлы в выбранной категории
        files_in_category = [
            (file_id, data['original_name'])
            for file_id, data in file_metadata.items()
            if selected_category in data['categories']
        ]

        if files_in_category:
            # Разделяем файлы на PDF и TXT
            pdf_files = [
                (file_id, name) for file_id, name in files_in_category
                if os.path.splitext(name)[1].lower() == '.pdf'
            ]
            txt_files = [
                (file_id, name) for file_id, name in files_in_category
                if os.path.splitext(name)[1].lower() == '.txt'
            ]

            # Создаем вкладки для PDF и TXT файлов
            tab_pdf, tab_txt = st.tabs(["PDF файлы", "TXT файлы"])

            with tab_pdf:
                if pdf_files:
                    # Создаем словарь для выбора
                    pdf_options = {name: file_id for file_id, name in pdf_files}
                    selected_pdf_name = st.selectbox('Выберите PDF файл', list(pdf_options.keys()))

                    if selected_pdf_name:
                        selected_file_id = pdf_options[selected_pdf_name]
                        file_path = os.path.join(uploads_folder, selected_file_id)

                        # Отображаем PDF файл с использованием streamlit-pdf-viewer
                        try:
                            pdf_viewer(file_path)

                            # Кнопка для скачивания файла
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="Скачать файл",
                                    data=f.read(),
                                    file_name=selected_pdf_name,
                                    key=f"download_{selected_file_id}"
                                )
                        except Exception as e:
                            st.error(f"Ошибка при открытии файла: {e}")
                else:
                    st.write("Нет PDF файлов в выбранной категории.")

            with tab_txt:
                if txt_files:
                    # Создаем словарь для выбора
                    txt_options = {name: file_id for file_id, name in txt_files}
                    selected_txt_name = st.selectbox('Выберите TXT файл', list(txt_options.keys()))

                    if selected_txt_name:
                        selected_file_id = txt_options[selected_txt_name]
                        file_path = os.path.join(uploads_folder, selected_file_id)

                        # Отображаем TXT файл
                        try:
                            with open(file_path, "r", encoding='utf-8') as f:
                                content = f.read()
                            st.text_area("Содержимое файла", content, height=400)

                            # Кнопка для скачивания файла
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="Скачать файл",
                                    data=f.read(),
                                    file_name=selected_txt_name,
                                    key=f"download_{selected_file_id}"
                                )
                        except Exception as e:
                            st.error(f"Ошибка при открытии файла: {e}")
                else:
                    st.write("Нет TXT файлов в выбранной категории.")
        else:
            st.write("Нет файлов в выбранной категории.")
