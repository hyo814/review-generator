# SNS 후기 자동 생성기

> 📚 **학습용 개인 프로젝트입니다.** FastAPI·React·LLM API 연동과 Docker 배포를 공부하며 만들었습니다.

국내·해외 가게 SNS 후기를 폼 입력만으로 자동 생성하는 풀스택 웹 앱입니다.
Claude API + 웹 검색을 활용해 다른 후기들의 공통 특징을 자동 분석하고, 한국어/영어/일본어/중국어 4개 언어로 번역까지 해줍니다. 지역(홍대·강남·부산 해운대·Tokyo Shibuya 등)은 자유 입력이며, LLM이 각 언어 표기로 자동 음역합니다.

## 기능

- **폼 기반 후기 생성**: 가게 정보·방문 메모·별점 입력 → AI가 검색 + 후기 작성
- **4개 언어 번역**: 한국어 / 영어 / 일본어 / 중국어 (각 언어 SNS 컨벤션에 맞게 변환)
- **번역 캐싱**: 한 번 번역한 언어는 DB에 저장돼 재호출 안 함 (비용·속도)
- **히스토리**: 생성한 후기 자동 저장, 다시 불러오기 가능
- **자동 후처리**: 마크다운 별표 제거, 언어별 도입구·표기 보정 (지역명 음역은 프롬프트에서 LLM에 위임)

## 아키텍처

```
┌──────────────┐   /api/*    ┌──────────────┐   API     ┌─────────────┐
│  Browser     │ ─────────→  │  nginx :80   │ ────────→ │ FastAPI     │
│  (React SPA) │   같은 origin │  (프론트엔드) │  내부망    │  :8000      │
└──────────────┘             │  + 정적자산  │           │  + SQLite   │
                             └──────────────┘           └─────────────┘
```

- **프론트**: React 18 + Vite + Lucide 아이콘 (vanilla CSS, Tailwind 없음)
- **백엔드**: FastAPI + SQLAlchemy 2.0 + Anthropic SDK
- **DB**: SQLite (단일 서버 운영 기준 적합. 다중 인스턴스로 가게 되면 PostgreSQL로 교체)
- **배포**: Docker Compose (프론트엔드 nginx 컨테이너 + 백엔드 컨테이너)

### 핵심 설계 결정

1. **API 키는 백엔드에만**: 프론트는 백엔드 API만 호출. 키는 절대 프론트로 안 나감.
2. **단일 origin 운영**: nginx가 프론트 정적 파일 + `/api` 프록시 둘 다 처리해서 CORS 이슈 자체를 없앰.
3. **번역 결과를 DB row 컬럼으로 보관**: 별도 테이블 정규화 안 함. 후기당 최대 4개로 고정이고 JOIN 없이 단일 쿼리로 끝나서.
4. **이중 안전망**: LLM 출력은 프롬프트로 1차 통제 + 정규식 후처리로 2차 통제.

## 빠른 시작 (Docker Compose)

가장 권장하는 실행 방법입니다.

### 1) 사전 준비
- [Docker](https://docs.docker.com/get-docker/) 및 Docker Compose 설치
- [Anthropic API 키](https://console.anthropic.com/) 발급

### 2) 환경변수 파일 생성

```bash
cp backend/.env.example backend/.env
```

`backend/.env` 열어서 `ANTHROPIC_API_KEY`만 본인 키로 교체:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

프로젝트 루트에 `.env` 만들어서 접속용 Basic Auth 계정 설정 (없으면 `docker compose`가 실행 안 됨):

```env
BASIC_AUTH_USER=원하는아이디
BASIC_AUTH_PASSWORD=길고-랜덤한-비밀번호
```

(선택) 폼 기본값·시리즈명 변환 규칙은 env로 설정: `cp frontend/.env.example frontend/.env` 후 `VITE_DEFAULT_*` 입력, 시리즈명 접미사는 `backend/.env`의 `SERIES_SUFFIX_*`.

> nginx가 IP당 요청 제한도 겁니다: 전체 10회/초, 후기 생성·번역은 5회/분. 초과하면 429.

### 3) 빌드 & 실행

```bash
docker compose up -d --build
```

처음엔 이미지 빌드로 2~3분 정도 걸립니다.

### 4) 접속

브라우저에서 [http://localhost:8080](http://localhost:8080)

다른 포트 쓰고 싶으면:
```bash
FRONTEND_PORT=9000 docker compose up -d
```

### 종료

```bash
docker compose down
```

## 로컬 개발 (Docker 없이)

코드 자주 수정하면서 개발할 때 유용합니다.

### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # ANTHROPIC_API_KEY 입력
uvicorn app.main:app --reload
```
→ `http://localhost:8000/docs` 에서 Swagger UI 자동 생성됨 (FastAPI 기본 제공)

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```
→ `http://localhost:5173`

Vite dev 서버가 `/api` 요청을 자동으로 8000으로 프록시합니다 (`vite.config.js` 참고).

## 배포 (단일 서버 + Docker)

EC2/Lightsail/Vultr 같은 단일 VPS에 배포하는 가장 단순한 방식입니다.

### 1) 서버에 코드 클론

```bash
git clone <your-repo-url> review-generator
cd review-generator
```

### 2) 환경변수 설정

```bash
cp backend/.env.example backend/.env
# 에디터로 ANTHROPIC_API_KEY 입력
nano backend/.env
```

루트 `.env`에 `BASIC_AUTH_USER` / `BASIC_AUTH_PASSWORD`도 꼭 설정 (빠른 시작 2단계 참고). 비밀번호는 `openssl rand -base64 24` 같은 랜덤 값 권장.

**프로덕션에서 CORS 도메인 설정 잊지 말 것**: 단일 origin 운영이라 사실 영향 없지만, 다른 도메인에서 호출할 일이 생기면 `CORS_ORIGINS`에 추가.

### 3) 실행

```bash
docker compose up -d --build
```

### 4) (권장) HTTPS — Caddy 또는 Cloudflare

도메인 있으면 nginx 앞에 Caddy/Cloudflare Tunnel 두면 인증서 자동 발급. 또는 docker-compose에 `traefik` 서비스 추가하는 방식도 있어요. 운영 들어가면 별도 가이드.

### 백업

SQLite 파일 하나만 백업하면 됩니다:
```bash
# 호스트의 ./data/reviews.db 가 컨테이너의 /app/data/reviews.db 로 마운트되어 있음
cp data/reviews.db data/reviews.db.bak.$(date +%Y%m%d)
```

## 주요 API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST   | `/api/reviews/generate` | 후기 생성 |
| POST   | `/api/reviews/{id}/translate` | 번역 (DB 캐시 hit이면 즉시 반환) |
| GET    | `/api/reviews/history?limit=20` | 최근 히스토리 |
| GET    | `/api/reviews/{id}` | 단건 전체 조회 |
| DELETE | `/api/reviews/{id}` | 삭제 |
| GET    | `/health` | 헬스체크 |

전체 스펙은 백엔드 실행 후 `/docs` 에서 확인 (FastAPI 자동 문서).

## 프로젝트 구조

```
review-generator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 진입점
│   │   ├── config.py            # 환경변수 (pydantic-settings)
│   │   ├── database.py          # DB 연결 + 세션
│   │   ├── models.py            # SQLAlchemy 모델
│   │   ├── schemas.py           # Pydantic 스키마 (API 계약)
│   │   ├── routers/
│   │   │   └── reviews.py       # /api/reviews/* 라우트
│   │   └── services/
│   │       ├── claude_client.py # Anthropic SDK 래퍼
│   │       ├── prompts.py       # 프롬프트 빌더 (생성/번역)
│   │       └── post_processor.py# 마크다운 제거 + 언어별 보정
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # 메인 오케스트레이션
│   │   ├── main.jsx             # 진입점
│   │   ├── styles.css           # CSS 토큰 + 스타일
│   │   ├── components/          # 폼·출력·언어탭·히스토리·별점
│   │   └── api/client.js        # fetch 래퍼
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js           # /api 프록시 설정
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 자주 막히는 부분

### "Claude API 호출 실패: ..."
- `backend/.env` 의 `ANTHROPIC_API_KEY` 확인
- 키가 활성화 됐는지 [console.anthropic.com](https://console.anthropic.com/) 에서 확인
- 크레딧 소진됐는지 확인

### Docker 빌드 실패
```bash
docker compose down -v           # 볼륨까지 정리
docker compose build --no-cache  # 캐시 없이 재빌드
docker compose up -d
```

### 번역 결과가 이상함
LLM 출력은 확률적이라 가끔 규칙을 무시합니다. `backend/app/services/post_processor.py` 의 정규식이 자동 보정하지만, 새 패턴이 자주 발견되면 거기에 추가하시면 됩니다.

### DB 초기화하고 싶을 때
```bash
docker compose down
rm data/reviews.db
docker compose up -d
```

## 라이선스

MIT (자유롭게 수정·사용)
