from typing import TypedDict, Dict, Any, List, Optional, Type
from uuid import uuid4


# Точный вид сообщений может поменяться, т.к. будут ещё картинки, но они обычно просто ссылками передаются
class Message(TypedDict):
    role: str  # Роль отправителя: assistant или user
    content: str


class Retrieval(TypedDict):
    type: str  # Тип контента: text или image
    content: str  # Текст, либо ссылка на картинку в локальном хранилище
    source: str  # Ссылка на источник данных: txt или pdf
    relevance: float  # Чем больше, тем больше вероятность, что это релевантный контент
    page: Optional[int]  # Номер страницы в pdf-файле, если это pdf


class LLMRequest(TypedDict):
    messages: List[Message]
    retrievals: List[Retrieval]  # Список контента, от RAG

example_request: LLMRequest = {
    "messages": [
        {
            "role": "user",
            "content": "Привет, пришли любой график",
        },
        {
            "role": "assistant",
            "content": "Эти графики описывают уровень ожирения в мире",
        },
        {
            "role": "user",
            "content": "Спасибо, а что по поводу статей на эту тему?",
        },
    ],
    "retrievals": [
        {
            "type": "text",
            "content": "важная часть текста про ожирение",
            "source": "/files/lol.txt",
            "relevance": 0.9
        },
        {
            "type": "image",
            "content": "/files/image_part.jpeg",
            "source": "/files/lol2.pdf",
            "relevance": 0.95
        },
        {
            "type": "image",
            "content": "/files/image_part.jpeg",
            "source": "/files/lol2.pdf",
            "relevance": 0.5
        }
    ]
}

def get_response(thread: LLMRequest) -> str:
    if len(thread["messages"]) == 1:
        return "Привет! вот рандомный график"
    if len(thread["messages"]) == 3:
        return "Эти графики описывают уровень ожирения в мире"
    return "Эти еще какие-то графики"



def add_file_to_rag(file_path: str) -> None:
    pass


def get_retrievals_from_rag(content: str) -> List[Retrieval]:
    pass
