import csv
import yaml

class DataManager:
    def __init__(self, user_data_path, schedule_data_path):
        self.user_data_path = user_data_path
        self.schedule_data_path = schedule_data_path

    def save_new_user(self, user_data_list):
        if not self.get_schedule_data_by_user_id(user_data_list[0]):
            with open(self.user_data_path, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(user_data_list)
            return user_data_list
        return "User already exists"

    def get_user_data_by_id(self, user_id):
        with open(self.user_data_path, mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == str(user_id):
                    return row
        return "User Does Not Exist"

    def get_schedule_data_by_user_id(self, user_id):
        with open(self.schedule_data_path, mode='r', newline='') as yaml_file:
            yaml_schedule = yaml.safe_load(yaml_file)
            for schedule in yaml_schedule:
                if schedule["id"] == user_id:
                    return schedule
        return "Schedule Does Not Exist"

    def save_schedule_data(self, schedule_data):
        with open(self.schedule_data_path, mode='a', newline='') as yaml_file:
            file = yaml.safe_load(yaml_file)
            file.update(schedule_data)
        return schedule_data


d = DataManager(user_data_path='user.csv', schedule_data_path='schedule_data.csv')
print(d.get_user_data_by_id(1))