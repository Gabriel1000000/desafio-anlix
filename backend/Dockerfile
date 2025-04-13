FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Executa a importação antes de iniciar a API
RUN python import_data.py

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
