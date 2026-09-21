from Data.DataManager import DataManager
from Data.Language.PhraseGiver import PhraseGiver
from Data.Schedule.Schedule import Schedule
from Data.User import User
from Telegramapi.TelegramAPIBot import TelegramAPIBot
import json
from dotenv import load_dotenv
import os
import pathlib

class ScheduleTgBot:
    def __init__(self, datamanager, telegrambot, phrasegiver):
        self.data_manager : DataManager = datamanager
        self.telegram_bot : TelegramAPIBot = telegrambot
        self.phrases = phrasegiver
        self.command_list = [
            "/start",
            "/language",
            "/create"
        ]
        self.state_list = [
            "waiting_for_language",
            "waiting_task_name",
            "waiting_task_date",
            "waiting_task_time"
        ]


    def getUpdate(self):
        all_messages = self.telegram_bot.get_messages()
        # print(json.dumps(all_messages, indent=4))
        if not (messages_list := all_messages.get("result", [])):
            return
        for update in messages_list[::-1]:
            msg = update.get("message")
            if not msg:
                continue
            from_user = msg.get("from")
            if not from_user:
                continue
            user_id = from_user["id"]
            username = from_user.get("username", '-')
            msg_id = msg["message_id"]

            user_data = self.data_manager.get_user_data_by_id(user_id)

            if not user_data:
                current_user = User(*(self.data_manager.save_new_user([user_id, username, msg_id])))
                self.handle_messages(current_user, msg)
                return
            else:
                current_user = User(*(user_data))
                if str(msg_id) != str(current_user.last_message_id):
                    if current_user.state and current_user.state in self.state_list:
                        self.state_switch(current_user, msg)
                    current_user.last_message_id = msg_id
                    self.data_manager.update_user_data(current_user.to_list())
                    self.handle_messages(current_user, msg)
                    return
                else:
                    return

    def state_switch(self, user, msg):
        match user.state:
            case "waiting_for_language":
                self.language_state(user, msg)
            case "waiting_task_name":
                self.task_name_state(user, msg)
            case _:
                self.default_response(user)


    def command_switch(self, user, msg):
        match msg["text"]:
            case "/start":
                self.start(user)
            case "/language":
                # print("Я ТУТА ПОШЕЛ В ЛАНГУАГЕ")
                self.language(user)
            case "/create":
                self.create_task(user)
            case _:
                self.default_response(user)


    def start(self, user):
        #создаю или ищу расписание этого чела
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["welcome_text"][user.language], user.user_id)




    def task_date_state(self, user, msg):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_date"][user.language], user.user_id)
        if msg["text"]:
            #PARSE INTO DATE. SOMEHOW IDK. WTF MTF
            pass




    def task_name_state(self, user, msg):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_name"][user.language], user.user_id)
        if msg["text"]:
            if msg["text"] in "/exit":
                user.state = None
                self.data_manager.update_user_data(user)
                return
            else:
                schedule = self.create_or_get_schedule(user)
                schedule.create_task(schedule.get_empty_task_id(), msg["text"])
                user.state = "waiting_task_date"
                self.data_manager.update_user_data(user.to_list())
                self.data_manager.update_or_save_schedule_data(schedule.to_dict())
                self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_date"][user.language], user.user_id)
                return


    def create_task(self, user):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_name"][user.language], user.user_id)
        user.state = "waiting_task_name"
        self.data_manager.update_user_data(user.to_list())
        return


    def language_state(self, user, msg):
        if msg["text"] in "ru":
            user.language = "ru"
            user.state = None
            self.data_manager.update_user_data(user.to_list())
            self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["language_changed"][user.language], user.user_id)
            return
        elif msg["text"] in "en":
            user.language = "en"
            user.state = None
            self.data_manager.update_user_data(user.to_list())
            self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["language_changed"][user.language], user.user_id)
            return
        elif msg["text"] in "/exit":
            user.state = None
            self.data_manager.update_user_data(user.to_list())
            self.start(user)
        else:
            self.language(user)
        return

    def language(self, user):
        # print("IN LANGUAGE")
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["language_question"][user.language], user.user_id)
        user.state = "waiting_for_language"
        self.data_manager.update_user_data(user.to_list())
        return

    def default_response(self, user):
        self.telegram_bot.send_text_message_to_user_by_id("Не могу обработать эту команду, сорри", user.user_id)


    def create_or_get_schedule(self, user):
        schedule = self.data_manager.get_schedule_data_by_user_id(user.user_id)
        if not schedule:
            result = Schedule(user.user_id)
            self.data_manager.update_or_save_schedule_data(schedule.to_dict())
            return result
        else:
            result = Schedule.create_from_dict(schedule)
            return result

    def handle_messages(self, current_user, message, first_time=False):
        print("_----------------------------------------_")
        print(f"current_user: {current_user.to_list()}")
        print(f"Message text: {message["text"]}")
        print(first_time)
        print(f"current user state: {current_user.state}")
        print("__________________________________________")
        if message["text"] in self.command_list:
            self.command_switch(current_user, message)






load_dotenv()
TOKEN = os.getenv('TOKEN')
tg_bot = TelegramAPIBot(TOKEN)

project_data_dir = pathlib.Path(__file__).resolve().parent

a = ScheduleTgBot(DataManager(project_data_dir / "Data/user.csv", project_data_dir / "Data/schedules.yaml"), TelegramAPIBot(TOKEN), PhraseGiver(project_data_dir / "Data/Language/en_ru.yaml"))


from time import sleep
while True:
    print("scanned")
    a.getUpdate()
    sleep(1)