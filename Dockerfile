FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY chat_adapter/requirements.txt /app/chat_adapter/requirements.txt
RUN pip install --no-cache-dir -r /app/chat_adapter/requirements.txt

COPY finance_ai_agent /app/finance_ai_agent
COPY chat_adapter /app/chat_adapter

CMD ["uvicorn", "chat_adapter.main:app", "--host", "0.0.0.0", "--port", "8080"]
