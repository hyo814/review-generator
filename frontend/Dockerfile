# ───── 빌드 단계 ─────
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 먼저 (package.json만 변경 안 되면 layer 재사용)
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY . .
RUN npm run build

# ───── 런타임 단계: nginx ─────
FROM nginx:alpine

# 빌드 결과물(dist)을 nginx가 서빙할 위치로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx 설정 (SPA 라우팅 + /api 백엔드 프록시)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Basic Auth 계정 생성 스크립트 (nginx 공식 이미지가 시작 시 /docker-entrypoint.d/*.sh 실행)
COPY --chmod=755 htpasswd.sh /docker-entrypoint.d/40-htpasswd.sh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
