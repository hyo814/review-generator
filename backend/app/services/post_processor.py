"""LLM 출력 후처리.

JSX 버전의 cleanMarkdown + enforceLanguageRules를 그대로 옮김.
LLM은 확률적이라 프롬프트 규칙을 가끔 무시함. 그 안전망 역할.
"""
import re
from typing import Callable


# ── 마크다운 패턴들 (사전 컴파일로 성능 ↑) ──
_RE_BOLD_DOUBLE_STAR = re.compile(r"\*\*([^*]+?)\*\*")
_RE_BOLD_DOUBLE_UNDER = re.compile(r"__([^_]+?)__")
# *italic* — 별표가 단일이고 앞뒤로 다른 별표가 없는 경우만
_RE_ITALIC_STAR = re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)")
_RE_INLINE_CODE = re.compile(r"`([^`]+?)`")
_RE_TRIPLE_NEWLINE = re.compile(r"\n{3,}")


def clean_markdown(text: str) -> str:
    """마크다운 강조 문법 제거. 별점 🌟(이모지)는 별표가 아니라 영향 없음."""
    text = _RE_BOLD_DOUBLE_STAR.sub(r"\1", text)
    text = _RE_BOLD_DOUBLE_UNDER.sub(r"\1", text)
    text = _RE_ITALIC_STAR.sub(r"\1", text)
    text = _RE_INLINE_CODE.sub(r"\1", text)
    return text


# ── 언어별 보정 정규식 ──
# region/series_name이 동적으로 바뀌면서 시리즈명 음역 강제 변환은 프롬프트에 위임.
# 여기서는 어느 지역에서도 통하는 일반 규칙만 남겨둠 (도입구 제거, 중국어 회차 표기 통일 등).
_RE_ZH_EPISODE_WRONG = re.compile(r"第(\d+)期")
_RE_ZH_INTRO = re.compile(r"[为给]大家介绍一下[!！]?\s*")

_RE_JA_INTRO_1 = re.compile(r"皆さんに紹介します[!！]?\s*")
_RE_JA_INTRO_2 = re.compile(r"今日は.*?を紹介します[!！]?\s*")

_RE_EN_INTRO_1 = re.compile(r"Let me introduce[^.\n]*[.!]?\s*", re.IGNORECASE)
_RE_EN_INTRO_2 = re.compile(r"Today I('ll|m)?[^.\n]*introduce[^.\n]*[.!]?\s*", re.IGNORECASE)


def _enforce_zh(text: str) -> str:
    text = _RE_ZH_EPISODE_WRONG.sub(r"\1篇", text)
    text = _RE_ZH_INTRO.sub("", text)
    return text


def _enforce_ja(text: str) -> str:
    text = _RE_JA_INTRO_1.sub("", text)
    text = _RE_JA_INTRO_2.sub("", text)
    return text


def _enforce_en(text: str) -> str:
    text = _RE_EN_INTRO_1.sub("", text)
    text = _RE_EN_INTRO_2.sub("", text)
    return text


# 객체 lookup 패턴 — if/elif 체인보다 깔끔하고 확장성 ↑
_LANG_ENFORCERS: dict[str, Callable[[str], str]] = {
    "zh": _enforce_zh,
    "ja": _enforce_ja,
    "en": _enforce_en,
}


def enforce_language_rules(text: str, lang: str) -> str:
    """마크다운 제거 + 언어별 보정. 한국어는 마크다운 제거만."""
    text = clean_markdown(text)

    enforcer = _LANG_ENFORCERS.get(lang)
    if enforcer:
        text = enforcer(text)

    # 빈 줄 3개 이상 → 2개로 (제거 후 누적되는 경우 정리)
    text = _RE_TRIPLE_NEWLINE.sub("\n\n", text)
    return text.strip()
