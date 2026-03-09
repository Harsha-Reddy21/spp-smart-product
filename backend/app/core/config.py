from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Scoring constants — mirrors scoring_service.py
    mandatory_threshold: float = 0.6
    static_penalty: float = 0.15
    default_mandatory_confidence: float = 0.3
    default_confidence: float = 0.5

    # LLM limits
    agent_max_tokens: int = 600
    score_max_tokens: int = 500
    polish_max_tokens: int = 350
    coverage_max_tokens: int = 300
    topic_max_tokens: int = 200


settings = Settings()
