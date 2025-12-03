FROM python:3.12-slim

WORKDIR /app

# API용 가벼운 requirements만 사용
COPY requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
