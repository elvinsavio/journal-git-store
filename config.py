import hashlib

class Config:   
    LOGIN_KEY = "Elvin@1234"
    HASHED_LOGIN_KEY = hashlib.sha256(LOGIN_KEY.encode()).hexdigest()
    TIMEZONE = "Asia/Kolkata"