from typing import TypedDict, List, Optional


class Retrieval(TypedDict):
    type: str  # Тип контента: text или image
    content: str  # Текст, либо ссылка на картинку в локальном хранилище
    source: str  # Ссылка на источник данных: txt или pdf
    relevance: float  # Чем больше, тем больше вероятность, что это релевантный контент
    page: int  # Номер страницы в pdf-файле, если это pdf


# Точный вид сообщений может поменяться, т.к. будут ещё картинки, но они обычно просто ссылками передаются
class Message(TypedDict):
    role: str  # Роль отправителя: assistant или user
    content: str
    attachments: List[str]  # Список контента, в формате uuid


example_request: List[Message] = [
    {
        "role": "user",
        "content": "Привет, пришли любой график",
        "attachments": [
            "4b3b3b3b-3b3b-3b3b-3b3b-3b3b3b3b3b3b",
        ]
    }
]


def get_response(thread: List[Message]) -> str:
    if len(thread) == 1:
        return "Привет! вот рандомный график"
    if len(thread) == 3:
        return "Эти графики описывают уровень ожирения в мире"
    return "Эти еще какие-то графики"


def add_file_to_rag(file_path: str) -> None:
    pass


def get_retrievals_from_rag(content: str) -> List[Retrieval]:
    pass

from typing import List, Optional, Dict, Any

class ResponseItem:
    def __init__(
        self,
        item_id: str,
        embedding: Optional[List[float]],
        document: Optional[str],
        url: Optional[str],
        data: Optional[Any],
        metadata: Optional[Dict[str, Any]],
        distance: float
    ):
        self.id = item_id
        self.embedding = embedding
        self.document = document
        self.url = url
        self.data = data
        self.metadata = metadata
        self.distance = distance

    def __repr__(self):
        return f"ResponseItem(id={self.id}, distance={self.distance})"


class ResponseProcessor:
    def __init__(self, response: Dict[str, Any]):
        self.items = self._parse_response(response)

    def _parse_response(self, response: Dict[str, Any]) -> List[ResponseItem]:
        ids = response.get('ids', [[]])[0]
        embeddings = response.get('embeddings')
        documents = response.get('documents', [[]])[0]
        uris = response.get('uris', [None])[0]
        data = response.get('data')
        metadatas = response.get('metadatas', [[]])[0]
        distances = response.get('distances', [[]])[0]

        items = []
        for i in range(len(ids)):
            item = ResponseItem(
                item_id=ids[i],
                embedding=embeddings[i] if embeddings else None,
                document=documents[i] if i < len(documents) else None,
                url=uris[i] if uris and i < len(uris) else None,
                data=data,
                metadata=metadatas[i] if i < len(metadatas) else None,
                distance=distances[i] if i < len(distances) else float('inf')
            )
            items.append(item)
        return items

    def get_sorted_items_by_distance(self) -> List[ResponseItem]:
        return sorted(self.items, key=lambda item: item.distance)

# Пример использования
response_data = {
    'ids': [['file1_1', 'file1_3', 'file1_4', 'file1_2']],
    'embeddings': None,
    'documents': [['Пасется корова на лугу', 'Едет машина', 'Летает самолет', 'Кукарекает петух']],
    'uris': None,
    'data': None,
    'metadatas': [
        [{'file_name': 'file1', 'page': 1}, {'file_name': 'file1', 'page': 3},
         {'file_name': 'file1', 'page': 4}, {'file_name': 'file1', 'page': 2}]
    ],
    'distances': [[209.41722178978537, 341.28294906182595, 359.67542279595773, 367.7899129907945]]
}

processor = ResponseProcessor(response_data)
sorted_items = processor.get_sorted_items_by_distance()

# Вывод отсортированного списка
for item in sorted_items:
    print(item)
