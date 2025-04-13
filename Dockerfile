FROM python:3.11-slim

COPY ./backend /app
WORKDIR /app


RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

# Sobe a API e, em paralelo, roda o import_data.py
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python import_data.py"]

