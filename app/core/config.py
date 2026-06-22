# core/config.py
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str | None = None
    ia_model: str = "llama-3.1-8b-instant"
    ia_temperature: float = 0.0
    smmlv_2026: int = 1_305_000
    modo_offline: bool = False  # <- Lo añadimos aquí
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # <- Ignora variables extra en .env
    )

settings = Settings()
