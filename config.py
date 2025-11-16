import hashlib
import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent reinitialization
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        load_dotenv()

        # load from env
        self.LOGIN_KEY: str = self.__get_key("LOGIN_KEY")
        self.TIMEZONE: str = self.__get_key("TIMEZONE")
        self.GEMINI_KEY: str = self.__get_key("GEMINI_KEY")

        # in app
        self.HASHED_LOGIN_KEY = hashlib.sha256(self.LOGIN_KEY.encode()).hexdigest()

    @staticmethod
    def __get_key(name: str, default: Optional[str] = None):
        value = os.getenv(name)

        # If found, return it
        if value is not None:
            return value

        # Missing → check default handling
        if default is None:
            raise KeyError(f"Environment variable '{name}' is required but not set")

        return default


config = Config()
__all__ = ["config"]
