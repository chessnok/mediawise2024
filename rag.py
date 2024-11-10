from sys import maxsize

import chromadb
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
import os
embeddings = GigaChatEmbeddings(credentials="MTEwMzY1YmEtMzYzMy00YWQ1LThmMTQtNWEzODM0NzUwN2IwOjU2ZDlkOGY1LWU0MDUtNDQ2Ni1hNTQyLWU5N2M4MzJmY2FmOA==", verify_ssl_certs=False, max_tokens=4000, max_length=4000)

# Создаем клиент ChromaDB
client = chromadb.PersistentClient(path=".")


def giga_embend_(text):
    result = embeddings.embed_documents(texts=[text], maxsize=2000)
    return result[0]

def giga_embend(text):
    result = embeddings.embed_documents(texts=[text])
    return result[0]

def add_embedding(collection_name, text, file_name, page):
    collection = client.get_or_create_collection(name=collection_name)
    embedding = giga_embend(text)
    document_id = f"{file_name}_{page}"

    # Add the document with embedding and metadata
    collection.add(
        ids=[document_id],
        embeddings=[embedding],
        metadatas=[{"file_name": "pdf/"+file_name+".pdf", "page": page}],
        documents=[text]
    )

def get_embedding(collection_name, text):
    collection = client.get_collection(name=collection_name)
    embedding = giga_embend(text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=5
    )
    return results

def process_text_files(collection_name, folder_path="md"):
    collection = client.get_collection(name=collection_name)
    # Get all .txt files in the folder
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    import random
    # Перемешать массив txt_files
    random.shuffle(txt_files)

    for file_name in txt_files:
        document_id = file_name.split('.')[0]
        print(document_id)

        result = collection.get(ids=[document_id])

        if result and len(result.get("documents", [])) > 0:  # Assuming documents are in a 'documents' key
            print(f"Document {document_id} already exists in the collection")
            continue


        with open(os.path.join(folder_path, file_name), "r", encoding='utf-8') as f:
            text = f.read()
            if len(text) > 1200:
                text = text[:1200]
            file_name, page = document_id.split('_')
            add_embedding("main", text, file_name, page)

            print(f"Adding document {document_id} to the collection")

if __name__ == "__main__":

    #process_text_files("main")
    r = get_embedding("main", "Wedia is a Digital Asset Management solution for global brands.")
    print(r)
    #add_embedding("main", "Пасется корова на лугу", "666", 6)
    #add_embedding("main", "Кукарекает петух", "file1", 2)
    #add_embedding("main", "Едет машина", "file1", 3)
    #add_embedding("main", "Летает самолет", "file1", 4)
    #add_embedding("main", "hello", [1, 2, 3])