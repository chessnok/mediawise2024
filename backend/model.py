from typing import TypedDict, Dict, Any, List, Optional, Type
from uuid import uuid4


# Точный вид сообщений может поменяться, т.к. будут ещё картинки, но они обычно просто ссылками передаются
class Message(TypedDict):
    role: str
    content: str


class Thread(TypedDict):
    id: str
    messages: List[Message]


class Retrieval(TypedDict):
    type: str  # Тип контента: text или image
    content: str  # Текст, либо ссылка на картинку в локальном хранилище
    source: str  # Ссылка на источник данных: txt или pdf
    relevance: float  # Чем больше, тем больше вероятность, что это релевантный контент


class ModelResponse(TypedDict):
    message: str  # Сообщение, которое нужно отправить пользователю
    retrievals: List[Retrieval]


def get_response(thread: Thread) -> ModelResponse:
    if len(thread["messages"]) == 0:
        return {
            "message": "Привет! Чем могу помочь?",
            "retrievals": []
        }
    if len(thread["messages"]) == 1:
        return {
            "message": "Какой-то текст",
            "retrievals": []
        }
    if len(thread["messages"]) == 2:
        return {
            "message": "Ну тут вот такой текст",
            "retrievals": [
                {
                    "type": "text",
                    "content": "Текст",
                    "source": "txt",
                    "relevance": 0.9
                },
            ]
        }
    return {
        "message": "Идеи закончились",
        "retrievals": [
            {
                "type": "text",
                "content": "Текст",
                "source": "txt",
                "relevance": 0.9
            },
            {
                "type": "image",
                "content": "https://drive.google.com/uc?export=download&id=1SqlpHn6FKBwNHEIKziqqT9s00O1E8LJr",
                "source": "pdf",
                "relevance": 0.7
            }
        ]
    }
