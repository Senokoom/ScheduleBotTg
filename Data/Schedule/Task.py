class Task:
    def __init__(self, task_id, text="", start_time="", repeat=False, picture=None, reminds=1, location=None, is_active=False):
        self.task_id = task_id
        self.reminds = reminds
        self.picture = picture
        self.repeat = repeat
        self.text = text
        self.start_time = start_time
        self.is_active = is_active
        self.location = location

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'reminds': self.reminds,
            'picture': self.picture,
            'text': self.text,
            'start_time': self.start_time,
            'location': self.location
        }