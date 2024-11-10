import chromadb
from langchain_community.embeddings.gigachat import GigaChatEmbeddings

embeddings = GigaChatEmbeddings(credentials="MTEwMzY1YmEtMzYzMy00YWQ1LThmMTQtNWEzODM0NzUwN2IwOjU2ZDlkOGY1LWU0MDUtNDQ2Ni1hNTQyLWU5N2M4MzJmY2FmOA==", verify_ssl_certs=False)

# Создаем клиент ChromaDB
client = chromadb.PersistentClient(path=".")


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
        metadatas=[{"file_name": file_name, "page": page}],
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

if __name__ == "__main__":
    r = get_embedding("main", "корова")
    print(r)
    #add_embedding("main", "Пасется корова на лугу", "file1", 1)
    #add_embedding("main", "Кукарекает петух", "file1", 2)
    #add_embedding("main", "Едет машина", "file1", 3)
    #add_embedding("main", "Летает самолет", "file1", 4)
    #add_embedding("main", "hello", [1, 2, 3])