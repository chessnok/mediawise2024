from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field, validator
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_gigachat.chat_models.gigachat import GigaChat



class Photo(BaseModel):
    """Информация о фото"""

    content: str = Field(..., description="Что изображено на фото? 1-3 слова")
    description: str = Field(..., description="Опиши детальнее фото")



def _get_messages_from_url(url: str):
    return {
        "history": [
            HumanMessage(content="", additional_kwargs={"attachments": [url]}),
        ]
    }


def get_img_description(img_path, parser):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            #"Определи содержимое на фото. Ответь на запрос пользователя в формате JSON. Schema Information: \n{format_instructions}",
            "Тебе дан график. Опиши основную информацию, которую он несет в себе. Если изображение не несет в себе релевантной информации ответь 'НЕТ ГРАФИКА'",
        ),
        MessagesPlaceholder("history"),
    ]
    ).partial(format_instructions=parser.get_format_instructions())

    chain = RunnableLambda(_get_messages_from_url) | prompt | llm
    img = llm.upload_file(open(img_path, "rb"))
    return chain.batch([img.id_])[0].content

if __name__ == "__main__":
    
    llm = GigaChat(
    credentials="MTEwMzY1YmEtMzYzMy00YWQ1LThmMTQtNWEzODM0NzUwN2IwOjU2ZDlkOGY1LWU0MDUtNDQ2Ni1hNTQyLWU5N2M4MzJmY2FmOA==",
    verify_ssl_certs=False,
    timeout=6000,
    model="GigaChat-Pro-preview",
    base_url="https://gigachat-preview.devices.sberbank.ru/api/v1")

    parser = PydanticOutputParser(pydantic_object=Photo)
    print(get_img_description('D:\MediaWise\output_images\image_4_image_1.png.png', parser))