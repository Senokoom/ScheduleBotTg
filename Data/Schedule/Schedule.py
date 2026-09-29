from Data.Schedule.Task import Task

class Schedule:
    def __init__(self, user_id):
        self.user_id = user_id
        self.tasks : list[Task] = []

    @classmethod
    def create_from_dict(cls, schedule_dict):
        user_id = schedule_dict["user_id"]
        _tasks = []
        for task in schedule_dict["tasks"]:
            _tasks.append(Task.from_dict(task))
        result = cls(user_id)
        result.tasks = _tasks
        return result

    def get_empty_task_id(self):
        taken_ids = {task.task_id for task in self.tasks}
        i = 0
        while i in taken_ids:
            i += 1
        return i

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if str(task.task_id) == str(task_id):
                return task
        return None



    def create_task(self, taskid, text="", start_time="", date=None, reminds=1, picture=None, location=None):
        self.tasks.append(Task(task_id=taskid, text=text, date=date, start_time=start_time, reminds=reminds, picture=picture, location=location))

    def get_all_tasks(self):
        return self.tasks

    def get_all_current_tasks(self, time):
        result = []
        for task in self.tasks:
            if task.start_time <= time and task.is_active():
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