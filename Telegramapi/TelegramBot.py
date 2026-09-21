import json
from dotenv import load_dotenv
import os
from requests import post, get

class TelegramBot:
    def __init__(self, TOKEN):
        self.main_url = f"https://api.telegram.org/bot{TOKEN}/"

    def getMe(self):
        return get(f"{self.main_url}getMe")

    def get_messages(self):
        return get(f"{self.main_url}GetUpdates", params="message").json()

    def get_last_message_from_user_by_id(self, user_id):
        response = get(f"{self.main_url}GetUpdates", params="message").json()
        for index in range(len(response["result"])-1, 0, -1):
            if user_id == response["result"][index]["message"]["from"]["id"]:
                return response["result"][index]["message"]
        return "No messages"

    def send_text_message_to_user_by_id(self, message_text, user_id):
        parameters = {
            "text": message_text,
            "chat_id": user_id
        }
        return post(f"{self.main_url}sendMessage", params=parameters)

    def send_picture_to_user_by_id(self, photo, user_id, caption = ""):
        parameters = {
            "photo": photo,
            "chat_id": user_id,
            "caption": caption
        }
        return post(f"{self.main_url}sendPhoto", params=parameters)

load_dotenv()
TOKEN = os.getenv('TOKEN')
tg_bot = TelegramBot(TOKEN)
print(tg_bot.getMe())
# print(json.dumps(tg_bot.get_messages(), indent=4))
print(json.dumps(tg_bot.get_last_message_from_user_by_id(994917029)))
print(tg_bot.send_text_message_to_user_by_id("hello world", 994917029))
