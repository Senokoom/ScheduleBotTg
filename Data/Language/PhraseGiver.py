import yaml

class PhraseGiver:
    def __init__(self, language_file):
        with open(language_file, mode='r', encoding='utf-8') as phrases_yaml:
            phrases = yaml.safe_load(phrases_yaml)
        self.text_dict = phrases
# PhraseGiver()