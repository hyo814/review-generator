"""후기 관련 API 라우터.

엔드포인트:
- POST /api/reviews/generate          : 새 후기 생성 + DB 저장
- POST /api/reviews/{id}/translate    : 특정 후기 번역 (DB에 캐시)
- GET  /api/reviews/history           : 최근 히스토리 (요약)
- GET  /api/reviews/{id}              : 단건 전체 조회
- DELETE /api/reviews/{id}            : 삭제

DB-캐싱 전략: 한 번 번역한 언어는 row의 컬럼에 저장. 같은 언어 재요청 시
LLM 호출 안 하고 DB에서 즉시 반환. 비용·속도 모두 이득.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Review
from app.schemas import (
    ReviewGenerateRequest,
    TranslateRequest,
    ReviewSummary,
    ReviewFull,
    GenerateResponse,
    TranslateResponse,
)
from app.services import claude_client
from app.services.prompts import build_generation_prompt, build_translation_prompt
from app.services.post_processor import enforce_language_rules

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_review(
    payload: ReviewGenerateRequest,
    db: Session = Depends(get_db),
):
    """후기 생성 → 마크다운 후처리 → DB 저장 → 응답."""
    prompt = build_generation_prompt(payload)

    try:
        raw_text = await claude_client.generate_review_text(prompt)
    except Exception as e:
        # 외부 API 장애는 502로 표현 (Bad Gateway 의미상 적절)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Claude API 호출 실패: {str(e)}",
        )

    # 한국어는 마크다운 제거만 (언어별 보정은 외국어에만 의미 있음)
    cleaned = enforce_language_rules(raw_text, lang="ko")

    review = Review(
        header_category=payload.header_category,
        store_name=payload.store_name,
        region=payload.region,
        series_name=payload.series_name,
        episode_number=payload.episode_number,
        visit_memo=payload.visit_memo,
        business_hours=payload.business_hours,
        address=payload.address,
        search_query=payload.search_query,
        ratings=payload.ratings.model_dump(),
        korean_output=cleaned,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return GenerateResponse(id=review.id, korean=cleaned)


@router.post("/{review_id}/translate", response_model=TranslateResponse)
async def translate_review(
    review_id: int,
    payload: TranslateRequest,
    db: Session = Depends(get_db),
):
    """번역 — DB 캐시 hit이면 LLM 호출 생략."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="후기를 찾을 수 없습니다.")

    # 캐시 hit 검사 (해당 언어 컬럼에 값 있으면 그대로 반환)
    cached = getattr(review, f"{payload.lang}_output")
    if cached:
        return TranslateResponse(id=review.id, lang=payload.lang, translated=cached)

    prompt = build_translation_prompt(
        lang=payload.lang,
        korean_text=review.korean_output,
        series_name=review.series_name,
        episode_number=review.episode_number,
        store_name=review.store_name,
        region=review.region,
        address=review.address,
    )

    try:
        raw_translated = await claude_client.translate_text(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"번역 API 호출 실패: {str(e)}",
        )

    cleaned = enforce_language_rules(raw_translated, lang=payload.lang)

    # DB에 캐싱 (다음 요청부터 즉시 반환)
    setattr(review, f"{payload.lang}_output", cleaned)
    db.commit()

    return TranslateResponse(id=review.id, lang=payload.lang, translated=cleaned)


@router.get("/history", response_model=list[ReviewSummary])
def list_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """최근 후기 히스토리 (요약).

    페이지네이션:
    - limit: 페이지당 건수 (기본 20, 최대 100)
    - offset: 건너뛸 건수 (load-more 패턴, 0부터)
    프론트는 응답 길이가 limit 미만이면 마지막 페이지로 판단.
    """
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    reviews = (
        db.query(Review)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/{review_id}", response_model=ReviewFull)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """단건 전체 조회 (모든 입력값 + 한국어 + 번역 캐시)."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="후기를 찾을 수 없습니다.")
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """후기 삭제."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="후기를 찾을 수 없습니다.")
    db.delete(review)
    db.commit()
    return None
