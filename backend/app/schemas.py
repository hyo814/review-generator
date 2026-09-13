"""Pydantic 스키마.

API 요청·응답 검증과 직렬화 담당. SQLAlchemy 모델과 분리해서 둠.
이유: ORM 모델은 DB 구조, Pydantic 스키마는 API 계약. 두 관심사 분리해야
나중에 DB 스키마 바뀌어도 API 호환성 유지하기 쉬움.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


# ─────────────────── 입력 ───────────────────

class Ratings(BaseModel):
    """별점 5개 항목 (1~5)."""
    taste: int = Field(ge=1, le=5)
    service: int = Field(ge=1, le=5)
    location: int = Field(ge=1, le=5)
    facility: int = Field(ge=1, le=5)
    revisit: int = Field(ge=1, le=5)


class ReviewGenerateRequest(BaseModel):
    """후기 생성 요청."""
    header_category: str = Field(min_length=1, max_length=200)
    store_name: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=50)
    series_name: str = Field(min_length=1, max_length=50)
    episode_number: str = Field(default="1", max_length=20)
    visit_memo: str = Field(min_length=1)
    business_hours: str = ""
    address: Optional[str] = Field(default=None, max_length=300)
    search_query: str = Field(min_length=1, max_length=200)
    ratings: Ratings


class TranslateRequest(BaseModel):
    lang: Literal["en", "ja", "zh"]


# ─────────────────── 출력 ───────────────────

class ReviewSummary(BaseModel):
    """히스토리 리스트용 요약 정보."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    store_name: str
    region: str


class ReviewFull(BaseModel):
    """단건 조회용 전체 정보."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    header_category: str
    store_name: str
    region: str
    series_name: str
    episode_number: str
    visit_memo: str
    business_hours: str
    address: Optional[str]
    search_query: str
    ratings: dict
    korean_output: str
    en_output: Optional[str]
    ja_output: Optional[str]
    zh_output: Optional[str]


class GenerateResponse(BaseModel):
    id: int
    korean: str


class TranslateResponse(BaseModel):
    id: int
    lang: str
    translated: str
