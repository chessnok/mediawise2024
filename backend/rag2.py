import chromadb
from langchain_community.embeddings.gigachat import GigaChatEmbeddings

# Создаем объект GigaChatEmbeddings для получения эмбеддингов (представлений) текста
# Указываем необходимые учетные данные и отключаем проверку SSL-сертификатов
embeddings = GigaChatEmbeddings(credentials="MTEwMzY1YmEtMzYzMy00YWQ1LThmMTQtNWEzODM0NzUwN2IwOjU2ZDlkOGY1LWU0MDUtNDQ2Ni1hNTQyLWU5N2M4MzJmY2FmOA==", verify_ssl_certs=False)

# Создаем клиент ChromaDB с постоянным хранилищем данных в указанной директории
client = chromadb.PersistentClient(path=".")


def giga_embend(text):
    # Получаем эмбеддинг для переданного текста
    result = embeddings.embed_documents(texts=[text])
    return result[0]  # Возвращаем первый (и единственный) эмбеддинг


def add_embedding(collection_name, text, file_name, page):
    # Получаем или создаем коллекцию по имени
    collection = client.get_or_create_collection(name=collection_name)
    # Генерируем эмбеддинг для текста
    embedding = giga_embend(text)
    # Создаем уникальный идентификатор документа, используя имя файла и номер страницы
    document_id = f"{file_name}_{page}"

    # Добавляем документ в коллекцию с эмбеддингом и метаданными (имя файла и страница)
    collection.add(
        ids=[document_id],
        embeddings=[embedding],
        metadatas=[{"file_name": file_name, "page": page}],
        documents=[text]
    )


def get_embedding(collection_name, text):
    # Получаем коллекцию по имени
    collection = client.get_collection(name=collection_name)
    # Генерируем эмбеддинг для запроса (текста)
    embedding = giga_embend(text)
    # Выполняем запрос к коллекции для поиска похожих эмбеддингов
    results = collection.query(
        query_embeddings=[embedding],
        n_results=5  # Ограничиваем количество возвращаемых результатов до 5
    )
    return results  # Возвращаем результаты запроса
