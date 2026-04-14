FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" appuser

COPY . .

EXPOSE 3000

USER appuser

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "1", "--limit-max-requests", "500"]
