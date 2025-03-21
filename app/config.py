import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
