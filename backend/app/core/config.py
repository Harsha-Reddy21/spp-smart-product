from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cortex_client_id: str = ""
    cortex_client_secret: str = ""
    cortex_tenant_id: str = ""
    cortex_api_url: str = "https://gateway.apim-dev.lilly.com/cortex/model/ask"
    cortex_model: str = "speqe-small-embedding"

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
