class User:
    def __init__(self, user_id, name, last_message_id, language="ru", state=None, current_task_id=None):
        self.user_id = user_id
        self.name = name
        self.last_message_id = last_message_id
        self.language = language
        self.state = state
        self.current_task_id = current_task_id

    def to_list(self):
        return [self.user_id, self.name, self.last_message_id, self.language, self.state, self.current_task_id]