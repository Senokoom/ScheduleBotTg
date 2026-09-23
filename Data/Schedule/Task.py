class Task:
    def __init__(self, task_id, text="", date='', start_time="", repeat=False, picture=None, reminds=1, location=None, is_active=True):
        self.task_id = task_id
        self.reminds = reminds
        self.picture = picture
        self.repeat = repeat
        self.text = text
        self.start_time = start_time
        self.date = date
        self.is_active = is_active
        self.location = location

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'reminds': self.reminds,
            'picture': self.picture,
            'text': self.text,
            'start_time': self.start_time,
            'date': self.date,
            'location': self.location,
            'is_active': self.is_active
        }