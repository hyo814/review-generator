"""프롬프트 빌더.

JSX 버전의 buildPrompt + LANG_RULES를 그대로 옮긴 것.
프롬프트는 LLM 출력의 80%를 좌우하는 핵심 자산이라 별도 모듈로 분리.
나중에 A/B 테스트나 버전 관리 도입할 때 여기만 손보면 됨.
"""
from app.config import settings
from app.schemas import ReviewGenerateRequest, Ratings


def stars(n: int) -> str:
    """별점 숫자 → 🌟 반복."""
    n = max(0, min(5, n))
    return "🌟" * n


def build_generation_prompt(req: ReviewGenerateRequest) -> str:
    """한국어 후기 생성용 프롬프트."""
    r = req.ratings
    return f"""당신은 한국어 SNS 후기 작성 전문가입니다.

먼저 web_search 도구로 "{req.search_query}"를 검색해서 다른 방문자들의 리뷰에서 공통적으로 언급되는 특징(분위기, 시그니처 메뉴, 웨이팅 패턴, 위치 특성 등)을 파악해주세요. 검색 결과 요약은 별도로 보여주지 말고, 후기 본문에 자연스럽게 녹여주세요.

[작성 형식 — 아래 구조를 정확히 따라주세요]

.{req.header_category}
#{req.store_name} 소개해드리겠습니다.
#{req.series_name} {req.episode_number}편💚

✅️ [본문 1] 상호 스토리/특징 + 검색에서 공통적으로 언급되는 포인트를 자연스럽게 녹임

✅️ [본문 2] 메뉴/가격/맛 경험 (아래 방문 메모 기반으로 1인칭 후기처럼)

✅️ [본문 3] 영업시간 안내 — 첫 줄에 "🕐 영업시간 참고하세요!" 도입문을 시계 이모지와 함께 붙이고, 그 아래에 입력된 영업시간을 줄바꿈 그대로 단순하게 표시 (줄글로 풀지 말 것)

<별점후기>
맛: {stars(r.taste)} - [한줄 코멘트]
서비스: {stars(r.service)} - [한줄 코멘트]
위치: {stars(r.location)} - [한줄 코멘트]
시설: {stars(r.facility)} - [한줄 코멘트]
재방문의사: {stars(r.revisit)} - [한줄 코멘트]

[별점 뒤 코멘트 작성 지침]
- 각 항목 별점 뒤에 짧은 한줄 코멘트를 자동 생성
- 방문 메모 + 검색에서 파악한 가게 특성을 종합해서 그 항목과 어울리는 핵심 인상을 한 줄로 요약
- 톤: 짧고 캐주얼하게 (예: "김치가 진짜 미쳤어요!", "웨이팅 있지만 충분히 가치 있음", "골목 안이지만 찾기 어렵진 않아요")
- 별점 점수와 코멘트 톤을 일치시킬 것
- 길이: 한 항목당 15자 내외, 최대 25자 이내
- 구분자는 모두 " - "로 통일

해시태그 8~10개 (지역+카테고리, 지역+상호명 조합 위주)

[입력 정보]
- 상호명: {req.store_name}
- 지역: {req.region}
- 방문 메모: {req.visit_memo}
- 영업시간: {req.business_hours}

[작성 톤]
- 친근한 구어체 사용 (~하더라고요, ~느낌이에요, ~좋았어요 등)
- 직접 다녀온 1인칭 후기 톤
- 후기글 본문만 출력 (앞뒤 안내 문구·메타 코멘트 없이 바로 시작)

[이모지 사용 가이드]
- 본문 ✅️ 3개 항목 안에 분위기에 어울리는 이모지를 3~4개 정도 자연스럽게 섞어서 사용 가능
- 하트 이모지는 가능하면 초록색 하트(💚) 사용 (빨간 하트 대신)
- 메뉴/음식 관련 이모지(☕🍞🍰🍜🥟 등), 분위기 이모지(✨🌿🪴 등) 활용

[출력 형식 — 매우 중요]
- 마크다운 문법 절대 사용 금지: **굵게**, *기울임*, __밑줄__, `코드`, # 헤더 등 모든 마크다운 기호 쓰지 말 것
- 가게 이름이나 메뉴명을 강조하고 싶어도 별표(*)나 백틱으로 감싸지 말고 일반 텍스트 그대로 출력
- 출력은 SNS에 그대로 붙여넣기 가능한 평문(plain text)이어야 함"""


# ─────────────────── 언어별 번역 규칙 ───────────────────

def _en_rules(
    series_name: str,
    episode_number: str,
    store_name: str,
    region: str,
    address: str | None,
) -> str:
    location_block = (
        f"- Add this exact line right after the business hours block:\n  ✅️ Location: {address}\n  Keep address in original Korean — DO NOT translate it."
        if address
        else "- No address provided, skip the location line."
    )
    ko, en = settings.series_suffix_ko, settings.series_suffix_en
    series_rule = (
        f'- If it follows the "{{지역}}{ko}" pattern, output "{{Region}}{en}" (e.g. 홍대{ko} → Hongdae{en}, 부산{ko} → Busan{en}).\n'
        if ko and en
        else ""
    )
    return f"""

⚠️ ENGLISH (Instagram/TikTok) — STRICT TRANSFORMATION RULES ⚠️

📌 TRANSFORMATION PATTERNS:

INPUT:  #{series_name} {episode_number}편💚
OUTPUT: #<series_name in Latin script> Ep.{episode_number} 💚
- Romanize the Korean series name into CamelCase, no spaces.
{series_rule}- If series_name is already in Latin/English, keep it as-is (just strip spaces/CamelCase if needed).
- NEVER leave Korean characters in this hashtag.

INPUT:  #{store_name} 소개해드리겠습니다.
OUTPUT: #{store_name} (drop "소개해드리겠습니다" entirely — DO NOT replace with "Let me introduce..." or any filler)

INPUT:  #{region}맛집 / #{region} / #{region}관광
OUTPUT: #<Region>Food / #<Region> / #<Region>Travel
- Romanize the region using the standard/widely-known Latin form:
  • Korean places: 홍대→Hongdae, 강남→Gangnam, 이태원→Itaewon, 한남동→Hannam, 연남동→Yeonnam, 명동→Myeongdong, 종로→Jongno, 부산 해운대→BusanHaeundae, 제주→Jeju, 강릉→Gangneung, 분당→Bundang, 판교→Pangyo.
  • Drop the "동/구/시" suffix when it makes the tag feel clunky (연남동→Yeonnam, not Yeonnamdong); keep it when it reads naturally (명동→Myeongdong).
  • Compound/two-word regions: join into CamelCase (해운대 → Haeundae; 부산 해운대 → BusanHaeundae).
- Overseas regions already in Latin script (Tokyo, Shibuya, Bangkok, Bali, NYC, Paris, …): keep verbatim, just CamelCase if multi-word.
- Overseas regions written in CJK (e.g. 渋谷, 上海): use the standard English/Latin form (Shibuya, Shanghai).

🚫 FORBIDDEN:
- Adding intro phrases like "Let me introduce", "Today I'll show you", etc.
- Leaving Korean characters in any hashtag.
- Generic-only hashtags (#food, #restaurant alone).

✅ REQUIRED HASHTAGS (must include all 4, customized to actual cuisine):
- #<Region>Food (or #<Region>Restaurant)
- #<Region>
- #<Region>Travel
- #<Region>[CUISINE] — match actual menu (e.g. #YeonnamCafe, #HongdaeBBQ, #BusanSashimi, #TokyoRamen)

📍 LOCATION:
{location_block}

Total hashtags: 8~10"""


def _ja_rules(
    series_name: str,
    episode_number: str,
    store_name: str,
    region: str,
    address: str | None,
) -> str:
    location_block = (
        f"- 営業時間ブロックの直後にこの行を追加:\n  ✅️ 場所：{address}\n  住所は韓国語のまま — 翻訳禁止。"
        if address
        else "- 住所未入力のため場所の行は追加しない。"
    )
    ko, ja = settings.series_suffix_ko, settings.series_suffix_ja
    series_rule = (
        f"- 「{{地域}}{ko}」パターンなら「{{地域漢字}}{ja}」に変換 (例: 홍대{ko}→弘大{ja}, 부산{ko}→釜山{ja})。\n"
        if ko and ja
        else ""
    )
    return f"""

⚠️ 日本語 (Instagram) — 厳守変換ルール ⚠️

📌 変換パターン:

入力: #{series_name} {episode_number}편💚
出力: #<series_name を日本語表記に変換> {episode_number}話💚
{series_rule}- 地域名に正式漢字表記がある韓国地名はそれを使用。なければ片仮名音写。
- series_name が既に日本語/ローマ字なら表記をそのまま維持。

入力: #{store_name} 소개해드리겠습니다。
出力: #{store_name} ("소개해드리겠습니다" 全部削除 — 「皆さんに紹介します」のような代替フレーズも追加禁止)

入力: #{region}맛집 / #{region} / #{region}관광
出力: #<地域>グルメ / #<地域> / #<地域>観光
- 韓国の地名は漢字表記を優先 (홍대→弘大, 강남→江南, 이태원→梨泰院, 한남동→漢南洞, 연남동→延南洞, 명동→明洞, 종로→鍾路, 부산→釜山, 해운대→海雲台, 제주→済州, 강릉→江陵, 분당→盆唐, 판교→板橋)。
- 漢字表記が一般的でない場合のみ片仮名 (例: ある複合地名)。
- 海外地名は現地語/日本語慣用表記をそのまま使用 (Tokyo→東京, Shibuya→渋谷, Bangkok→バンコク, Paris→パリ, NYC→ニューヨーク)。

🚫 絶対禁止:
- 原文にない導入フレーズ追加 (「皆さんに紹介します!」「今日はこちら」等)
- ハッシュタグに韓国語(ハングル)を残すこと (必ず日本語表記に変換)
- 広すぎる一般タグ単独使用 (#グルメ, #カフェ 単独など)

✅ 必須ハッシュタグ (4つ全て含める、実際の料理に合わせる):
- #<地域>グルメ
- #<地域>
- #<地域>観光
- #<地域>[料理ジャンル] — 実際メニューに合わせる (例: #延南洞カフェ, #弘大焼肉, #釜山刺身, #東京ラーメン)

📍 場所:
{location_block}

ハッシュタグ合計: 8~10個"""


def _zh_rules(
    series_name: str,
    episode_number: str,
    store_name: str,
    region: str,
    address: str | None,
) -> str:
    location_block = (
        f"- 영업시간 블록 바로 아래에 이 줄을 추가:\n  ✅️ 位置：{address}\n  주소는 한국어 그대로 — 번역 금지."
        if address
        else "- 주소 미입력 시 위치 줄 생략."
    )
    ko, zh = settings.series_suffix_ko, settings.series_suffix_zh
    series_rule = (
        f'- "{{지역}}{ko}" 패턴이면 "{{지역 简体중국어}}{zh}"로 변환 (예: 홍대{ko}→弘大{zh}, 부산{ko}→釜山{zh})\n'
        if ko and zh
        else ""
    )
    return f"""

⚠️ 中文(샤오홍슈) — 엄격한 변환 규칙 ⚠️

📌 변환 패턴:

입력: #{series_name} {episode_number}편💚
출력: #<series_name 중국어 표기>{episode_number}篇💚
- "편 → 篇" (절대 "第X期"로 쓰지 말 것)
{series_rule}- series_name이 이미 중국어/영문이면 그대로 유지

입력: #{store_name} 소개해드리겠습니다.
출력: #{store_name} ("소개해드리겠습니다" 통째로 삭제 — "为大家介绍一下" "给大家介绍一下" 같은 대체 문구 추가도 절대 금지)

입력: #{region}맛집 / #{region} / #{region}관광
출력: #<지역>美食店 / #<지역> / #<지역>旅游
- 한국 지명은 정식 简体중국어 한자 표기 사용 (홍대→弘大, 강남→江南, 이태원→梨泰院, 한남동→汉南洞, 연남동→延南洞, 명동→明洞, 종로→钟路, 부산→釜山, 해운대→海云台, 제주→济州, 강릉→江陵, 분당→盆唐, 판교→板桥).
- 절대 잘못된 음역 만들지 말 것 (예: 红大 ❌ → 弘大 ✅).
- 해외 지명은 중국어 통용 표기 사용 (Tokyo→东京, Shibuya→涩谷, Bangkok→曼谷, Paris→巴黎, NYC→纽约).

🚫 절대 금지:
- "为大家介绍一下" / "给大家介绍一下" 등 도입 문구 추가
- "第X期" 형식 (반드시 "X篇")
- 한국어(한글) 해시태그 그대로 유지 (반드시 중국어로 변환)
- 일반 카테고리 태그(#酒馆, #西餐 단독)

✅ 필수 해시태그 (4개 모두 포함, 실제 요리에 맞게):
- #<지역>美食店
- #<지역>
- #<지역>旅游
- #<지역>[요리종류] — 실제 메뉴에 맞게 (예: #延南洞咖啡店, #弘大烤肉店, #釜山生鱼片, #东京拉面)

📍 위치:
{location_block}

해시태그 총: 8~10개"""


_LANG_LABEL = {"en": "English", "ja": "日本語", "zh": "中文"}


def build_translation_prompt(
    *,
    lang: str,
    korean_text: str,
    series_name: str,
    episode_number: str,
    store_name: str,
    region: str,
    address: str | None,
) -> str:
    """번역용 프롬프트."""
    label = _LANG_LABEL.get(lang, lang)

    rules_fn = {"en": _en_rules, "ja": _ja_rules, "zh": _zh_rules}.get(lang)
    lang_rules = (
        rules_fn(series_name, episode_number, store_name, region, address) if rules_fn else ""
    )

    return f"""다음 한국어 SNS 후기를 {label}로 번역해주세요.{lang_rules}

[기본 번역 지침]
- 친근한 SNS 후기 톤 유지 (해당 언어의 자연스러운 SNS 어투로)
- ✅️, 🌟, 🕐, 💚 같은 이모지/마커는 그대로 유지
- 별점 🌟 개수 그대로 유지
- 영업시간 형식과 줄바꿈 그대로 유지
- 가게 고유명사는 원어 유지 + 필요 시 음역 병기
- 마크다운 문법(**굵게**, *기울임*, `코드` 등) 절대 사용 금지
- 번역문만 출력 (앞뒤 설명 없이)

[원문]
{korean_text}"""
