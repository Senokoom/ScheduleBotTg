from Data.DataManager import DataManager
from Data.Schedule.Schedule import Schedule
from Data.User import User
from Telegramapi.TelegramAPIBot import TelegramAPIBot
import dateparser

class ScheduleTgBot:
    def __init__(self, datamanager, telegrambot, phrasegiver, admin_id, greeting_users_ids, greeting_file_path):
        self.data_manager: DataManager = datamanager
        self.telegram_bot: TelegramAPIBot = telegrambot
        self.phrases = phrasegiver
        self.admin_id = admin_id  # <-- ДОБАВЬ ЭТО
        self.greeting_users_ids = greeting_users_ids  # <-- ДОБАВЬ ЭТО
        self.greeting_file_path = greeting_file_path  # <-- ДОБАВЬ ЭТО
        self.last_greeting_date = None  # <-- ДОБАВЬ ЭТО
        self.last_report_date = None  # <-- ДОБАВЬ ЭТО

            # ... остальной код
        self.command_list = [
            "/start",
            "/language",
            "/create",
            "/tasks",
            "/delete",
            "/cat"
        ]
        self.state_list = [
            "waiting_for_language",
            "waiting_task_name",
            "waiting_task_date",
            "waiting_task_time",
            "waiting_for_delete_id"
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
                current_user = User(*[user_id, username, msg_id])
                self.data_manager.save_new_user(current_user.to_list())

                # Проверяем тип сообщения
                if "location" in msg:
                    self.handle_location(current_user, msg)
                else:
                    self.handle_messages(current_user, msg)
                continue
            else:
                current_user = User(*user_data)
                if int(msg_id) > int(current_user.last_message_id):
                    current_user.last_message_id = msg_id
                    self.data_manager.update_user_data(current_user.to_list())

                    # Проверяем тип сообщения
                    if "location" in msg:
                        self.handle_location(current_user, msg)
                    else:
                        self.handle_messages(current_user, msg)
                    continue
                else:
                    continue

    def check_scheduled_tasks(self):
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        today = now.date()

        # 8:00 UTC = 11:00 MSK
        if now.hour == 8 and now.minute == 0 and self.last_greeting_date != today:
            self.send_morning_greeting()
            self.last_greeting_date = today

        # 23:55 UTC = 02:55 MSK следующего дня
        if now.hour == 23 and now.minute == 55 and self.last_report_date != today:
            self.send_daily_report()
            self.last_report_date = today

    def send_morning_greeting(self):
        try:
            with open(self.greeting_file_path, 'r', encoding='utf-8') as f:
                greeting_text = f.read()

            for user_id in self.greeting_users_ids:
                self.telegram_bot.send_text_message_to_user_by_id(greeting_text, user_id)

            self.data_manager.log_action("morning_greeting", "system", f"Sent to {len(self.greeting_users_ids)} users")
        except Exception as e:
            print(f"Ошибка отправки приветствия: {e}")

    def send_daily_report(self):
        try:
            report_text = self.data_manager.generate_report()

            # Сохраняем отчет во временный файл
            report_file = "daily_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)

            # Отправляем файл админу
            self.telegram_bot.send_document_to_user_by_id(report_file, self.admin_id)

            self.data_manager.log_action("daily_report", "system", "Sent to admin")
        except Exception as e:
            print(f"Ошибка отправки отчета: {e}")

    def handle_location(self, user, msg):
        location = msg.get("location")
        if location:
            latitude = location["latitude"]
            longitude = location["longitude"]

            # Получаем адрес
            address = self.telegram_bot.get_address_from_coordinates(latitude, longitude)

            if address:
                response_text = self.phrases.text_dict["location_received"][user.language].format(
                    address=address
                )
                self.telegram_bot.send_text_message_to_user_by_id(response_text, user.user_id)
            else:
                self.telegram_bot.send_text_message_to_user_by_id(
                    self.phrases.text_dict["location_error"][user.language],
                    user.user_id
                )


    def state_switch(self, user, msg):
        match user.state:
            case "waiting_for_language":
                self.language_state(user, msg)
            case "waiting_task_name":
                self.task_name_state(user, msg)
            case "waiting_task_date":
                self.task_date_state(user, msg)
            case "waiting_task_time":
                self.task_time_state(user, msg)
            case "waiting_for_delete_id":  # <-- ДОБАВЬ ЭТО
                self.delete_id_state(user, msg)
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
            case "/tasks":
                self.get_all_tasks(user)
            case "/delete":  # <-- ДОБАВЬ ЭТО
                self.delete_task_command(user)
            case "/cat":
                self.send_cat(user)
            case _:
                self.default_response(user)

    def start(self, user):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["welcome_text"][user.language], user.user_id)

    def get_all_tasks(self, user):
        schedule = self.create_or_get_schedule(user)
        if not schedule.tasks:
            self.telegram_bot.send_text_message_to_user_by_id(
                self.phrases.text_dict["no_tasks"][user.language],
                user.user_id
            )
            return

        final_str = self.phrases.text_dict["task_show"][user.language] + "\n"
        for task in schedule.tasks:
            # Безопасно форматируем время
            if task.start_time and hasattr(task.start_time, 'strftime'):
                time_str = task.start_time.strftime("%H:%M")
            else:
                time_str = "--:--"

            # Безопасно форматируем дату
            if task.date and hasattr(task.date, 'strftime'):
                date_str = task.date.strftime("%d/%m/%Y")
            else:
                date_str = "не указана"

            final_str += f"{task.task_id} {task.text}\n   {self.phrases.text_dict['task_show_time'][user.language]} {time_str}  {self.phrases.text_dict['task_show_date'][user.language]} {date_str}\n"

        self.telegram_bot.send_text_message_to_user_by_id(final_str, user.user_id)




    def send_cat(self, user):
        cat_url = self.telegram_bot.get_random_cat()
        if cat_url:
            self.telegram_bot.send_picture_to_user_by_id(cat_url, user.user_id)
        else:
            self.telegram_bot.send_text_message_to_user_by_id(
                "Failed to get a cat picture 😿",
                user.user_id
            )

    def check_reminders(self):
        from datetime import datetime

        now = datetime.now()
        # print(f"[REMINDERS] Проверка в {now}")

        for schedule_dict in self.data_manager.schedule_data:
            schedule = Schedule.create_from_dict(schedule_dict)
            user_id = schedule.user_id

            user_data = self.data_manager.get_user_data_by_id(user_id)
            if not user_data:
                continue
            user = User(*user_data)

            updated = False

            for task in schedule.tasks:
                # print(f"[REMINDERS] Задача {task.task_id}:")
                # print(f"  is_active: {task.is_active} (type: {type(task.is_active)})")
                # print(f"  date: {task.date} (type: {type(task.date)})")
                # print(f"  start_time: {task.start_time} (type: {type(task.start_time)})")

                if not task.is_active:
                    # print("  -> Пропуск: неактивна")
                    continue

                if not task.start_time:
                    # print("  -> Пропуск: нет времени")
                    continue

                try:
                    if hasattr(task.start_time, 'hour'):
                        task_time = task.start_time
                    else:
                        # print(f"  -> Пропуск: start_time не time объект: {type(task.start_time)}")
                        continue

                    if task.date:
                        if hasattr(task.date, 'date'):
                            task_date = task.date.date()
                        elif hasattr(task.date, 'year'):
                            task_date = task.date
                        else:
                            # print(f"  -> Пропуск: date не date объект: {type(task.date)}")
                            continue

                        task_datetime = datetime.combine(task_date, task_time)
                        # print(f"  -> task_datetime: {task_datetime}")
                        # print(f"  -> now >= task_datetime: {now >= task_datetime}")

                        if now >= task_datetime:
                            reminder_text = self.phrases.text_dict["reminder_text"][user.language].format(
                                task_text=task.text
                            )
                            self.telegram_bot.send_text_message_to_user_by_id(reminder_text, user_id)
                            # print(f"  -> Напоминание отправлено!")

                            task.is_active = False
                            updated = True

                    else:
                        # Ежедневное напоминание
                        if now.hour == task_time.hour and now.minute == task_time.minute:
                            last_remind_key = f"last_remind_{task.task_id}"
                            today_str = now.strftime("%Y-%m-%d")

                            if not hasattr(self, '_last_remind_dates'):
                                self._last_remind_dates = {}

                            if self._last_remind_dates.get(last_remind_key) != today_str:
                                reminder_text = self.phrases.text_dict["reminder_text"][user.language].format(
                                    task_text=task.text
                                )
                                self.telegram_bot.send_text_message_to_user_by_id(reminder_text, user_id)
                                self._last_remind_dates[last_remind_key] = today_str
                                # print(f"  -> Ежедневное напоминание отправлено!")

                except Exception as e:
                    print(f"  -> ОШИБКА: {e}")
                    continue

            if updated:
                self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user_id)



    def delete_task_command(self, user):
        schedule = self.create_or_get_schedule(user)

        if not schedule.tasks:
            self.telegram_bot.send_text_message_to_user_by_id(
                self.phrases.text_dict["no_tasks"][user.language],
                user.user_id
            )
            return

        # Показываем список задач
        final_str = self.phrases.text_dict["task_show"][user.language] + "\n"
        for task in schedule.tasks:
            if task.start_time and hasattr(task.start_time, 'strftime'):
                time_str = task.start_time.strftime("%H:%M")
            else:
                time_str = "--:--"

            if task.date and hasattr(task.date, 'strftime'):
                date_str = task.date.strftime("%d/%m/%Y")  # <-- Заменил точки на слеши
            else:
                date_str = "не указана"

            final_str += f"ID {task.task_id} {task.text}\n   {self.phrases.text_dict['task_show_time'][user.language]} {time_str}  {self.phrases.text_dict['task_show_date'][user.language]} {date_str}\n"

        final_str += "\n" + self.phrases.text_dict["delete_task"][user.language]
        print(final_str)
        print(self.telegram_bot.send_text_message_to_user_by_id(final_str, user.user_id).json())
        user.state = "waiting_for_delete_id"
        self.data_manager.update_user_data(user.to_list())

    def delete_id_state(self, user, msg):
        if msg.get("text"):
            if msg["text"] == "/exit":
                user.state = None
                self.data_manager.update_user_data(user.to_list())
                self.start(user)
                return

            try:
                task_id = int(msg["text"])
                schedule = self.create_or_get_schedule(user)

                task_found = False
                for task in schedule.tasks:
                    if task.task_id == task_id:
                        schedule.delete_task(task_id)
                        task_found = True
                        break

                if task_found:
                    self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user.user_id)
                    self.telegram_bot.send_text_message_to_user_by_id(
                        self.phrases.text_dict["task_deleted"][user.language],
                        user.user_id
                    )
                    self.data_manager.log_action("delete_task", user.user_id, f"Task ID: {task_id}")  # <-- ДОБАВЬ ЭТО
                else:
                    self.telegram_bot.send_text_message_to_user_by_id(
                        self.phrases.text_dict["task_not_found"][user.language],
                        user.user_id
                    )

                user.state = None
                self.data_manager.update_user_data(user.to_list())

            except ValueError:
                self.telegram_bot.send_text_message_to_user_by_id(
                    self.phrases.text_dict["delete_task"][user.language],
                    user.user_id
                )



    def delete_task_and_clear_user(self, user, task_id):
        schedule = self.create_or_get_schedule(user)
        schedule.delete_task(task_id)
        user.state = None
        user.current_task_id = None
        # print("ОЧИСТИЛИ КОРАШГУЩРАЖЩГУЫЦРАГЩШЖЦЫУ РААТЖЛОЦУЫГ РИТАУЦЫОЛЖЫД ЩЭРКИатоуЦЫЛЖЩ ЭХЖРГКаЩУОЦЫЛЬЛЩ ЭХРШГКАЩУВШЦДЛ ШРОЩКА+уЫЭЦОШЗ Г*()РХЩ")
        self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user.user_id)
        self.data_manager.update_user_data(user.to_list())
        return


    def task_time_state(self, user : User, msg):
        if msg.get("text", None):
            if msg["text"] == "/exit":
                self.delete_task_and_clear_user(user, user.current_task_id)
                self.start(user)
                return
            time = dateparser.parse(msg["text"])
            if time:
                time = time.time()
                schedule = self.create_or_get_schedule(user)
                current_task_id = user.current_task_id
                current_task = schedule.get_task_by_id(current_task_id)
                current_task.start_time = time
                user.state = None
                user.current_task_id = None
                self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user.user_id)
                self.data_manager.update_user_data(user.to_list())
                self.start(user)
                return
        self.task_time(user)


    def task_time(self, user):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_time"][user.language],
                                                          user.user_id)
        user.state = "waiting_task_time"
        self.data_manager.update_user_data(user.to_list())
        return


    def task_date_state(self, user : User, msg):
        if msg.get("text", None):
            user = User(*self.data_manager.get_user_data_by_id(user.user_id))
            if msg["text"] == "/exit":
                self.delete_task_and_clear_user(user, user.current_task_id)
                self.start(user)
                return
            date = dateparser.parse(msg["text"])
            if date:
                date = date.date()
                schedule = self.create_or_get_schedule(user)
                # print(f"ВОТ ЭТО СКЕДУЛЕ В ДАТЕ {schedule.to_dict()}")
                # print(f"ЭТО ЮЗЕР В ДАТЕ {user.to_list()}")
                # print(f"ЭТО ТАСКА КЮРРЕНТ В ДАТЕ {schedule.get_task_by_id(user.current_task_id)}")
                current_task_id = user.current_task_id
                current_task = schedule.get_task_by_id(current_task_id)
                current_task.date = date
                user.state = "waiting_task_time"
                self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user.user_id)
                self.data_manager.update_user_data(user.to_list())
                self.task_time(user)
                return
        self.task_date(user)

    def task_date(self, user):
        print(self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_date"][user.language],
                                                          user.user_id).json())
        user.state = "waiting_task_date"
        self.data_manager.update_user_data(user.to_list())
        return

    def task_name_state(self, user, msg):
        if msg.get("text", None):
            if msg["text"] == "/exit":
                user.state = None
                self.data_manager.update_user_data(user.to_list())
                self.start(user)
                return
            else:
                schedule = self.create_or_get_schedule(user)
                current_task_id = schedule.get_empty_task_id()
                user.current_task_id = current_task_id
                schedule.create_task(current_task_id, msg["text"])
                user.state = "waiting_task_date"
                self.data_manager.update_user_data(user.to_list())
                self.data_manager.update_schedule_data_by_id(schedule.to_dict(), user.user_id)
                self.data_manager.log_action("create_task", user.user_id,
                                             f"Task ID: {current_task_id}, Name: {msg['text']}")  # <-- ДОБАВЬ ЭТО
                self.task_date(user)
                return
        self.create_task(user)
        return

    def create_task(self, user):
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["task_name"][user.language],
                                                          user.user_id)
        user.state = "waiting_task_name"
        self.data_manager.update_user_data(user.to_list())
        self.data_manager.log_action("start_create_task", user.user_id)  # <-- ДОБАВЬ ЭТО
        return

    def language_state(self, user, msg):
        if msg["text"] == "ru":
            user.language = "ru"
            user.state = None
            self.data_manager.update_user_data(user.to_list())
            self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["language_changed"][user.language], user.user_id)
            return
        elif msg["text"] == "en":
            user.language = "en"
            user.state = None
            self.data_manager.update_user_data(user.to_list())
            self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["language_changed"][user.language], user.user_id)
            return
        elif msg["text"] == "/exit":
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
        self.telegram_bot.send_text_message_to_user_by_id(self.phrases.text_dict["default_response"][user.language], user.user_id)


    def create_or_get_schedule(self, user):
        schedule = self.data_manager.get_schedule_data_by_user_id(user.user_id)
        if not schedule:
            result = Schedule(user.user_id)
            self.data_manager.save_schedule_data(result.to_dict())
            return result
        else:
            result = Schedule.create_from_dict(schedule)
            return result

    def save(self):
        return self.data_manager.update_all_rom_data()

    def handle_messages(self, current_user, message):
        print("_----------------------------------------_")
        print(f"current_user: {current_user.to_list()}")
        print(f"Message text: {message.get('text', message.get('location', 'location'))}")
        print(f"current user state: {current_user.state}")
        print("__________________________________________")

        # Проверяем, является ли сообщение командой
        msg_text = message.get("text", "")

        # Если это команда - обрабатываем её, игнорируя состояние
        if msg_text in self.command_list:
            # Сбрасываем состояние при получении команды
            if current_user.state:
                current_user.state = None
                current_user.current_task_id = None
                self.data_manager.update_user_data(current_user.to_list())
            self.command_switch(current_user, message)
        # Если есть активное состояние - обрабатываем через state_switch
        elif current_user.state and current_user.state in self.state_list:
            self.state_switch(current_user, message)
        else:
            self.telegram_bot.send_text_message_to_user_by_id(
                self.phrases.text_dict["default_response"][current_user.language],
                current_user.user_id
            )



#
# load_dotenv()
# TOKEN = os.getenv('TOKEN')
# ADMIN_ID = os.getenv('ADMIN_ID')  # Замени на свой ID
# GREETING_USERS = [int(uid) for uid in os.getenv('GREETING_USERS', '').split(',') if uid]  # Список ID через запятую
#
# project_data_dir = pathlib.Path(__file__).resolve().parent
#
# a = ScheduleTgBot(
#     DataManager(project_data_dir / "Data/user.csv", project_data_dir / "Data/schedules.yaml"),
#     TelegramAPIBot(TOKEN),
#     PhraseGiver(project_data_dir / "Data/Language/en_ru.yaml"),
#     ADMIN_ID,
#     GREETING_USERS,
#     project_data_dir / "morning_greeting.txt"
# )
#
# counter = 0
# from time import sleep
# while True:
#     counter += 1
#     print("scanned")
#     if counter >= 5:
#         counter = 0
#         print("SAVED in ROM")
#         a.save()
#     a.getUpdate()
#     a.check_reminders()
#     a.check_scheduled_tasks()  # <-- ДОБАВЬ ЭТО
#     sleep(1)