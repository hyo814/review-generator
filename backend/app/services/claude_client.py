"""Claude API 클라이언트 래퍼.

Anthropic Python SDK 사용. 비동기 클라이언트로 FastAPI와 자연스럽게 통합.
- 후기 생성: web_search 도구 포함 호출
- 번역: 도구 없이 호출 (검색 불필요)

content 블록 파싱은 type 기반 — server_tool_use / web_search_tool_result / text 가
섞여서 옴. 순서 의존(content[0])하면 안 됨.
"""
from anthropic import AsyncAnthropic

from app.config import settings


_client = AsyncAnthropic(api_key=settings.anthropic_api_key)


def _extract_text(content: list) -> str:
    """응답의 content 배열에서 text 블록만 골라 합침."""
    texts = []
    for block in content or []:
        # SDK는 객체로 줌 → .type / .text 속성 접근
        if getattr(block, "type", None) == "text":
            texts.append(getattr(block, "text", ""))
    return "\n".join(texts).strip()


async def generate_review_text(prompt: str) -> str:
    """후기 생성 — web_search 도구 포함."""
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )
    text = _extract_text(response.content)
    if not text:
        raise ValueError("LLM이 빈 응답을 반환했습니다.")
    return text


async def translate_text(prompt: str) -> str:
    """번역 — 도구 없이 호출."""
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = _extract_text(response.content)
    if not text:
        raise ValueError("LLM이 빈 번역 응답을 반환했습니다.")
    return text
