import streamlit as st
import os

def display_files(folder, mime_type):
    files = os.listdir(folder)
    if files:
        for file in files:
            file_path = os.path.join(folder, file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📄 {file}",
                    data=f,
                    file_name=file,
                    mime=mime_type
                )
    else:
        st.write(f"Нет загруженных файлов в папке {folder}.")


st.title("Библиотека")

# Директории для сохранения файлов
pdf_folder = 'pdf'
txt_folder = 'txt'

# Создаем директории, если их нет
for folder in [pdf_folder, txt_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Форма для загрузки файлов
uploaded_file = st.file_uploader("Выберите файл для загрузки (PDF или TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    file_details = {"Имя файла": uploaded_file.name, "Тип файла": uploaded_file.type}
    st.write(file_details)

    # Определяем папку сохранения по MIME-типу
    file_type = uploaded_file.type
    if file_type == 'application/pdf':
        save_folder = pdf_folder
    elif file_type == 'text/plain':
        save_folder = txt_folder
    else:
        st.error("Неподдерживаемый тип файла.")

    save_path = os.path.join(save_folder, uploaded_file.name)
    # Проверяем, существует ли файл с таким именем
    if os.path.exists(save_path):
        # Если да, добавляем суффикс к имени файла
        name, ext = os.path.splitext(uploaded_file.name)
        i = 1
        while os.path.exists(os.path.join(save_folder, f"{name}_{i}{ext}")):
            i += 1
        save_path = os.path.join(save_folder, f"{name}_{i}{ext}")

    # Сохраняем файл локально
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Файл успешно сохранен как {os.path.basename(save_path)}")

# Отображаем список всех загруженных файлов во вкладках
st.header("Загруженные файлы")

# Создаем вкладки для PDF и TXT файлов
tab_pdf, tab_txt = st.tabs(["PDF", "TXT"])

with tab_pdf:
    display_files(pdf_folder, 'application/pdf')

with tab_txt:
    display_files(txt_folder, 'text/plain')



