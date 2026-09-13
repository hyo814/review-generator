"""DB 모델.

설계 결정: 번역은 별도 테이블 분리하지 않고 같은 row에 컬럼으로 보관.
이유: (1) 번역은 후기당 최대 4개 언어로 고정, (2) JOIN 없이 단일 쿼리로 끝, (3) 단순성.
번역 컬럼이 많아지거나 버전 관리가 필요해지면 그때 분리 테이블로 정규화.
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # ── 입력값 ──
    header_category: Mapped[str] = mapped_column(String(200))
    store_name: Mapped[str] = mapped_column(String(100), index=True)
    region: Mapped[str] = mapped_column(String(50))
    series_name: Mapped[str] = mapped_column(String(50))
    episode_number: Mapped[str] = mapped_column(String(20))
    visit_memo: Mapped[str] = mapped_column(Text)
    business_hours: Mapped[str] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    search_query: Mapped[str] = mapped_column(String(200))
    # ratings: JSON으로 보관 (taste, service, location, facility, revisit)
    ratings: Mapped[dict] = mapped_column(JSON)

    # ── 결과 ──
    korean_output: Mapped[str] = mapped_column(Text)
    en_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    ja_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    zh_output: Mapped[str | None] = mapped_column(Text, nullable=True)
