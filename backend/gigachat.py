import os
import uuid
import requests
from typing import List

mine_types = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "tiff": "image/tiff",
}


def generate_token() -> str:
    import requests

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'RqUID': str(uuid.uuid4()),
        'Authorization': 'Bearer MTEwMzY1YmEtMzYzMy00YWQ1LThmMTQtNWEzODM0NzUwN2IwOjU2ZDlkOGY1LWU0MDUtNDQ2Ni1hNTQyLWU5N2M4MzJmY2FmOA=='
    }

    response = requests.request("POST", url, headers=headers, data=payload,
                                verify=False)
    response.raise_for_status()
    return response.json()['access_token']


def add_file(file_paths: List[str]) -> List[str]:
    url = "https://gigachat.devices.sberbank.ru/api/v1/files"
    headers = {
        'Authorization': 'Bearer ' + generate_token()
    }
    payload = {'purpose': 'general'}
    max_file_size = 15 * 1024 * 1024  # 15 МБ в байтах

    file_ids = []

    for path in file_paths:
        file_size = os.path.getsize(path)

        if file_size > max_file_size:
            print(f"Файл {path} превышает лимит в 15 МБ и не будет загружен.")
            continue

        with open(path, 'rb') as file:
            files = {'file': (
                os.path.basename(path), file, mine_types[path.split('.')[-1]])}
            response = requests.post(url, headers=headers, data=payload,
                                     files=files, verify=False)

            if response.status_code == 200:
                file_ids.append(response.json()['id'])
            else:
                print(f"Ошибка загрузки файла {path}: {response.text}")

    return file_ids


def ask(context: List[dict], temperature: float = 0.6) -> str:
    import requests
    import json

    url = "https://gigachat-preview.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
        "model": "GigaChat-Pro-preview",
        "messages": context,
        "stream": False,
        "update_interval": 0,
        "temperature": temperature
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + generate_token()
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(response.text)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


if __name__ == '__main__':
    file_paths = ['C:\\python\\mediawise2024\\chart1.jpg',
                  'C:\\python\\mediawise2024\\chart2.jpg']
    file_ids = add_file(file_paths)
    print("Загруженные файлы с ID:", file_ids)

    print(ask([
        {
            "role": "system",
            "content": "Привет, теперь ты лучший аналитик в мире!",
        },
        {
            "role": "user",
            "content": "Что на этих графиках?",
            "attachments": file_ids
        }
    ]))