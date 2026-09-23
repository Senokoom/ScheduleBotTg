import json
from dotenv import load_dotenv
import os
from requests import post, get


class TelegramAPIBot:
    def __init__(self, TOKEN):
        self.main_url = f"https://api.telegram.org/bot{TOKEN}/"
        # КРИТИЧЕСКИ ВАЖНО: храним ID последнего прочитанного апдейта
        self.last_update_id = 0

    def send_document_to_user_by_id(self, file_path, user_id, caption=""):
        parameters = {
            "chat_id": user_id,
            "caption": caption
        }
        with open(file_path, 'rb') as file:
            files = {"document": file}
            return post(f"{self.main_url}sendDocument", data=parameters, files=files)

    def get_address_from_coordinates(self, latitude, longitude):
        headers = {
            "User-Agent": "ScheduleTgBot/1.0 (leva.kochin@gmail.com)"  # Замени на свой email или любое другое
        }
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "ru"
        }

        try:
            response = get("https://nominatim.openstreetmap.org/reverse", params=params, headers=headers)

            # Проверяем статус ответа
            if response.status_code != 200:
                print(f"Nominatim API error: {response.status_code} - {response.text}")
                return None

            data = response.json()
            if "display_name" in data:
                return data["display_name"]
            return None

        except Exception as e:
            print(f"Ошибка при получении адреса: {e}")
            return None

    def get_random_cat(self):
        response = get("https://api.thecatapi.com/v1/images/search")
        data = response.json()
        if data and len(data) > 0:
            return data[0]["url"]
        return None

    def getMe(self):
        return get(f"{self.main_url}getMe").json()

    def get_messages(self):
        # 1. Передаем offset, чтобы Телеграм отдавал только НОВЫЕ сообщения
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 1  # Короткий long-polling, чтобы не долбить API впустую
        }
        response = get(f"{self.main_url}getUpdates", params=params)
        data = response.json()

        # 2. Если получили новые сообщения, обновляем last_update_id
        if data.get('ok') and data.get('result'):
            updates = data['result']
            if updates:
                self.last_update_id = updates[-1]['update_id']

        return data

    def get_last_message_from_user_by_id(self, user_id):
        # Убрали сломанный params="message". Получаем все и фильтруем в Python.
        response = get(f"{self.main_url}getUpdates").json()
        if not response.get("result"):
            return None

        # Идем с конца списка, чтобы найти последнее сообщение
        for update in reversed(response["result"]):
            msg = update.get("message")
            if msg and msg.get("from", {}).get("id") == user_id:
                return msg
        return None

    def send_text_message_to_user_by_id(self, message_text, user_id):
        parameters = {
            "text": message_text,
            "chat_id": user_id,
            "parse_mode": "MarkdownV2"
            # Убедись, что в тексте нет неоэкранированных символов _ * [ ] ( ) ~ ` > # + - = | { } . !, иначе Телеграм вернет ошибку 400
        }
        # ИСПРАВЛЕНО: используем json= вместо params= для POST запросов
        return post(f"{self.main_url}sendMessage", json=parameters)

    def send_picture_to_user_by_id(self, photo, user_id, caption=""):
        parameters = {
            "chat_id": user_id,
            "caption": caption
        }
        # Для отправки файлов лучше использовать files=, но если photo это file_id, то json= сработает
        if isinstance(photo, str) and photo.startswith("http") or len(photo) < 100:  # file_id обычно короткий
            parameters["photo"] = photo
            return post(f"{self.main_url}sendPhoto", json=parameters)
        else:
            # Если это путь к файлу или байты
            files = {"photo": open(photo, "rb") if isinstance(photo, str) else photo}
            return post(f"{self.main_url}sendPhoto", data=parameters, files=files)