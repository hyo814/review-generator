"""DB 연결 및 세션 관리.

SQLAlchemy 2.0 스타일. SQLite 사용 시 connect_args에 check_same_thread=False 필요.
프로덕션에서 PostgreSQL로 갈아끼우려면 DATABASE_URL만 바꾸면 됨.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# SQLite는 멀티스레드 환경(FastAPI 기본)에서 check_same_thread=False 필요
# 다른 DB 사용 시 이 옵션 빼야 함
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,  # 디버깅 시 True로
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """모든 모델의 베이스 클래스."""
    pass


def init_db() -> None:
    """앱 시작 시 호출. 데이터 폴더 생성 + 테이블 생성."""
    # SQLite 파일 경로의 디렉토리 자동 생성
    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    # 모델 import 후 테이블 생성 (순환 import 방지를 위해 함수 안에서)
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI 의존성 주입용 DB 세션 제너레이터."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
