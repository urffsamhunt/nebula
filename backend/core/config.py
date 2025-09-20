from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Loads environment variables from the .env file."""
    GOOGLE_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()