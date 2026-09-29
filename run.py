from Data.DataManager import DataManager
from Data.Language.PhraseGiver import PhraseGiver
from Data.ScheduleTgBot import ScheduleTgBot
from Telegramapi.TelegramAPIBot import TelegramAPIBot
from dotenv import load_dotenv
import os
import pathlib
from time import sleep

# Загружаем переменные окружения
load_dotenv()

# Получаем настройки из .env
TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Замени на свой ID
GREETING_USERS = [int(uid) for uid in os.getenv('GREETING_USERS').split(',') if uid]

# Определяем пути
project_data_dir = pathlib.Path(__file__).resolve().parent

# Инициализируем бота
bot = ScheduleTgBot(
    DataManager(
        project_data_dir / "Data/user.csv",
        project_data_dir / "Data/schedules.yaml"
    ),
    TelegramAPIBot(TOKEN),
    PhraseGiver(project_data_dir / "Data/Language/en_ru.yaml"),
    ADMIN_ID,
    GREETING_USERS,
    project_data_dir / "morning_greeting.txt"
)

# Основной цикл
counter = 0
print("Бот запущен...")

while True:
    counter += 1
    print("scanned")

    # Сохраняем данные каждые 5 секунд
    if counter >= 5:
        counter = 0
        print("SAVED in ROM")
        bot.save()

    # Обрабатываем входящие сообщения
    bot.getUpdate()

    # Проверяем напоминания
    bot.check_reminders()

    # Проверяем запланированные задачи (приветствие и отчет)
    bot.check_scheduled_tasks()

    sleep(1)