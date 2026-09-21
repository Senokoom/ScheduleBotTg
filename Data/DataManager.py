import csv
import yaml

class DataManager:
    def __init__(self, user_data_path, schedule_data_path):
        self.user_data_path = user_data_path
        self.schedule_data_path = schedule_data_path

    def save_new_user(self, user_data_list):
        with open(self.user_data_path, mode="a", newline='', encoding="utf-8") as csvfile:
            if not self.get_user_data_by_id(user_data_list[0]):
                writer = csv.writer(csvfile)
                writer.writerow(user_data_list)
                return user_data_list
        return False

    def delete_user_by_id(self, user_id):
        with open(self.user_data_path, mode='r',newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            for row in rows:
                if row[0] == str(user_id):
                    rows.remove(row)
        with open(self.user_data_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
            # print("deleted")
        return

    def update_user_data(self, new_user_data):
        self.delete_user_by_id(new_user_data[0])
        self.save_new_user(new_user_data)
        return

    def get_user_data_by_id(self, user_id):
        with open(self.user_data_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == str(user_id):
                    return row
        return False

    def get_schedule_data_by_user_id(self, user_id):
        with open(self.schedule_data_path, mode='r', encoding='utf-8') as yamlfile:
            yaml_schedule = yaml.safe_load(yamlfile)
            if yaml_schedule:
                for schedule in yaml_schedule:
                    if schedule["id"] == user_id:
                        return schedule
            return False

    def update_or_save_schedule_data(self, schedule_data):
        with open(self.schedule_data_path, mode='r', encoding='utf-8') as yamlfile:
            yaml_dict = yaml.safe_load(yamlfile)
            yaml_dict.update(schedule_data)
        with open(self.schedule_data_path, mode='w', encoding='utf-8') as yamlfile:
            yaml.safe_dump(yaml_dict, yamlfile, allow_unicode=True, default_flow_style=False)
        return schedule_data

# import pathlib
# project_data_dir = pathlib.Path(__file__).resolve().parent.parent
# d = DataManager(project_data_dir / "Data/user.csv", project_data_dir / "Data/schedules.yaml")
# d.delete_user_by_id("994917029")