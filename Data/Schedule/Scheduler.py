from Task import Task

class Scheduler:
    def __init__(self, user_id):
        self.user_id = user_id
        self.tasks = []

    def create_task(self, taskid, text, start_time,  end_time=None, reminds=1, picture=None):
        self.tasks.append(Task(task_id=taskid, text=text, start_time=start_time, end_time=end_time, reminds=reminds, picture=picture))

    def get_all_tasks(self):
        return self.tasks

    def get_all_current_tasks(self, time):
        result = []
        for task in self.tasks:
            if task.start_time <= time <= task.end_time:
                result.append(task)
        return result

    def delete_task(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                self.tasks.remove(task)
        return

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'tasks': [task.to_dict() for task in self.tasks]
        }