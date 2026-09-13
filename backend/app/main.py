"""FastAPI 진입점.

- 앱 시작 시 DB 초기화
- CORS 미들웨어 등록 (프론트와 분리 운영)
- 라우터 마운트
- 헬스체크 엔드포인트
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 1회 실행되는 초기화 훅. 종료 시 정리 작업도 여기에."""
    init_db()
    yield
    # (앱 종료 시 추가 정리 필요해지면 여기에 작성)


app = FastAPI(
    title="SNS Review Generator API",
    description="국내·해외 가게 SNS 후기 자동 생성·번역 서비스 (한국어 → 영/일/중)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 프론트엔드 origin만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reviews.router)


@app.get("/health")
def health_check():
    """헬스체크. Docker healthcheck나 모니터링에서 사용."""
    return {"status": "ok"}
