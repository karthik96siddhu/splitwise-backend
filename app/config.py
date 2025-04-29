# config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file

class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
