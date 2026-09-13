#!/bin/sh
# Basic Auth 계정 파일 생성. 환경변수 없으면 컨테이너 시작 실패 (인증 없이 뜨는 것 방지)
set -e
: "${BASIC_AUTH_USER:?BASIC_AUTH_USER 필요}"
: "${BASIC_AUTH_PASSWORD:?BASIC_AUTH_PASSWORD 필요}"
printf '%s:%s\n' "$BASIC_AUTH_USER" "$(printf %s "$BASIC_AUTH_PASSWORD" | mkpasswd -m sha512 -P 0)" > /etc/nginx/.htpasswd
chmod 644 /etc/nginx/.htpasswd
