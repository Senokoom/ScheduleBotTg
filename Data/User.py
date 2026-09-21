class User:
    def __init__(self, user_id, name, last_message_id):
        self.user_id = user_id
        self.name = name
        self.last_message_id = last_message_id

    def to_list(self):
        return [self.user_id, self.name, self.last_message_id]