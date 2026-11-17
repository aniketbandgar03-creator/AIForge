from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "aiforge_db"
    MODEL_NAME: str = "gemini-3.6-flash"
    TEMPERATURE: float = 0.2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()