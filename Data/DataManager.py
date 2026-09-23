import csv
import yaml
import os


class DataManager:
    def __init__(self, user_data_path, schedule_data_path):
        self.user_data_path = user_data_path
        self.schedule_data_path = schedule_data_path

        self.user_data = []
        self.schedule_data = []
        self.action_log = []
        self.update_all_ram_data()

    def log_action(self, action_type, user_id, details=""):
        from datetime import datetime
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "user_id": user_id,
            "details": details
        }
        self.action_log.append(log_entry)

    def get_today_logs(self):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_logs = []
        for log in self.action_log:
            log_date = datetime.fromisoformat(log["timestamp"]).date()
            if log_date == today:
                today_logs.append(log)
        return today_logs

    def generate_report(self):
        from datetime import datetime
        today_logs = self.get_today_logs()

        report_lines = [f"Отчет за {datetime.now().strftime('%d.%m.%Y')}\n"]
        report_lines.append(f"Всего действий: {len(today_logs)}\n\n")

        # Группируем по типам действий
        actions_count = {}
        for log in today_logs:
            action = log["action"]
            actions_count[action] = actions_count.get(action, 0) + 1

        report_lines.append("Статистика действий:\n")
        for action, count in actions_count.items():
            report_lines.append(f"  {action}: {count}\n")

        report_lines.append("\nДетали:\n")
        for log in today_logs:
            report_lines.append(f"[{log['timestamp']}] {log['action']} - User {log['user_id']} - {log['details']}\n")

        return "".join(report_lines)





    def update_all_ram_data(self):
        self.update_ram_user_data()
        self.update_ram_schedule_data()

    def update_ram_user_data(self):
        # Создаем файл, если его нет, чтобы не было ошибки
        if not os.path.exists(self.user_data_path):
            open(self.user_data_path, 'w').close()

        with open(self.user_data_path, mode="r", newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            self.user_data = list(reader)

    def update_ram_schedule_data(self):
        if not os.path.exists(self.schedule_data_path):
            self.schedule_data = []
            return

        with open(self.schedule_data_path, mode="r", encoding="utf-8") as yamlfile:
            yaml_list = yaml.safe_load(yamlfile)
            # ЗАЩИТА: если файл пустой, yaml вернет None. Делаем его пустым списком.
            self.schedule_data = yaml_list if yaml_list else []

    def update_rom_user_data(self):
        with open(self.user_data_path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.user_data)

    def update_rom_schedule_data(self):
        with open(self.schedule_data_path, mode="w", encoding='utf-8') as yamlfile:
            yaml.safe_dump(self.schedule_data, yamlfile, allow_unicode=True, default_flow_style=False)

    def update_all_rom_data(self):
        try:
            self.update_rom_user_data()
            self.update_rom_schedule_data()
            return True
        except Exception as e:
            print(f"Ошибка сохранения в ROM: {e}")
            return False

    def get_user_data_by_id(self, user_id):
        for user in self.user_data:
            if str(user[0]) == str(user_id):
                return user
        return None  # Вернули None вместо False для корректной проверки "if not user_data"

    def save_new_user(self, user_data_list):
        if not self.get_user_data_by_id(user_data_list[0]):
            self.user_data.append(user_data_list)

    def delete_user_by_id(self, user_id):
        for user in self.user_data:
            if str(user[0]) == str(user_id):
                self.user_data.remove(user)
                return True
        return False

    def update_user_data(self, new_user_data):
        user_id = new_user_data[0]
        for i in range(len(self.user_data)):
            if str(self.user_data[i][0]) == str(user_id):
                self.user_data[i] = new_user_data
                return True
        return False

    def get_schedule_data_by_user_id(self, user_id):
        for schedule in self.schedule_data:
            if str(schedule.get("user_id")) == str(user_id):
                return schedule
        return None

    def update_schedule_data_by_id(self, schedule_data, uid):
        # ИСПРАВЛЕННЫЙ ЦИКЛ: убрали "- 1", теперь проверяются ВСЕ элементы
        for i in range(len(self.schedule_data)):
            if str(self.schedule_data[i].get('user_id')) == str(uid):
                self.schedule_data[i] = schedule_data
                return True

        # Если не нашли, добавляем как новый (на всякий случай)
        self.schedule_data.append(schedule_data)
        return True

    def save_schedule_data(self, schedule_data):
        if not self.get_schedule_data_by_user_id(schedule_data["user_id"]):
            self.schedule_data.append(schedule_data)
            return True
        return False