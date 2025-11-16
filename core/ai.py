from config import config


class AI:
    def __init__(self, api) -> None:
        self.api_key = config.GEMINI_KEY
