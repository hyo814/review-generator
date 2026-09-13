FROM python:3.12-slim

WORKDIR /app

# 의존성 먼저 복사 → Docker layer cache 활용 (코드 바뀌어도 의존성 layer 재사용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# 데이터 디렉토리 (SQLite 파일 위치). 볼륨으로 마운트할 예정
RUN mkdir -p /app/data

EXPOSE 8000

# uvicorn 기본 설정. 프로덕션에서는 --workers 늘리거나 gunicorn 앞에 둘 수도 있음
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
