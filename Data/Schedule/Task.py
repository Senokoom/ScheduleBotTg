from datetime import datetime, date, time


class Task:
    def __init__(self, task_id, text="", date=None, start_time=None, repeat=False, picture=None, reminds=1,
                 location=None, is_active=True):
        self.task_id = task_id
        self.reminds = reminds
        self.picture = picture
        self.repeat = repeat
        self.text = text
        self.start_time = start_time  # datetime.time или None
        self.date = date  # datetime.date или None
        self.is_active = is_active
        self.location = location

    def to_dict(self):
        # Конвертируем date в ISO строку
        if self.date:
            if hasattr(self.date, 'isoformat'):
                date_str = self.date.isoformat()
            else:
                date_str = str(self.date)
        else:
            date_str = None

        # Конвертируем start_time в ISO строку
        if self.start_time:
            if hasattr(self.start_time, 'isoformat'):
                time_str = self.start_time.isoformat()
            else:
                time_str = str(self.start_time)
        else:
            time_str = None

        return {
            'task_id': self.task_id,
            'reminds': self.reminds,
            'picture': self.picture,
            'repeat': self.repeat,
            'text': self.text,
            'start_time': time_str,
            'date': date_str,
            'location': self.location,
            'is_active': self.is_active
        }


    @classmethod
    def from_dict(cls, task_dict):
        # Парсим date обратно в datetime.date
        date_val = task_dict.get('date')
        if date_val and isinstance(date_val, str) and date_val.strip():
            try:
                date_val = date.fromisoformat(date_val)
            except (ValueError, TypeError):
                date_val = None
        else:
            date_val = None

        # Парсим start_time обратно в datetime.time
        time_val = task_dict.get('start_time')
        if time_val and isinstance(time_val, str) and time_val.strip():
            try:
                time_val = time.fromisoformat(time_val)
                # print("time_val:", time_val)
            except (ValueError, TypeError):
                time_val = None
        else:
            time_val = None

        return cls(
            task_id=task_dict.get('task_id'),
            text=task_dict.get('text', ''),
            date=date_val,
            start_time=time_val,
            repeat=task_dict.get('repeat', False),
            picture=task_dict.get('picture'),
            reminds=task_dict.get('reminds', 1),
            location=task_dict.get('location'),
            is_active=task_dict.get('is_active', True)
        )