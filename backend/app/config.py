"""애플리케이션 설정.

환경변수 기반으로 설정을 로드합니다.
- ANTHROPIC_API_KEY: Claude API 키 (필수)
- DATABASE_URL: SQLite 경로 (기본: ./data/reviews.db)
- CORS_ORIGINS: 프론트엔드 origin 목록 (콤마 구분)
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Claude API
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-20250514"

    # 시리즈명 접미사 변환 (선택). "{지역}+접미사" 형태 시리즈명을 언어별 표기로 바꾸는 규칙.
    # 하나라도 비어 있으면 해당 언어 규칙은 프롬프트에서 생략 → LLM이 일반 음역
    series_suffix_ko: str = ""
    series_suffix_en: str = ""
    series_suffix_ja: str = ""
    series_suffix_zh: str = ""

    # DB
    database_url: str = "sqlite:///./data/reviews.db"

    # CORS — 콤마 구분 문자열로 받아서 리스트로 파싱
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
