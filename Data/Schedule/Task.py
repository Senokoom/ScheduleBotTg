class Task:
    def __init__(self, task_id, text, start_time, picture=None, reminds=1, end_time=None):
        self.task_id = task_id
        self.reminds = reminds
        self.picture = picture
        self.text = text
        self.start_time = start_time
        self.end_time = end_time if end_time is not None else start_time

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'reminds': self.reminds,
            'picture': self.picture,
            'text': self.text,
            'start_time': self.start_time,
            'end_time': self.end_time
        }