FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY .env .
COPY config.py .
COPY main.py .
COPY backend /app/backend
COPY frontend /app/frontend

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]