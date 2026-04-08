FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir openenv openai uvicorn fastapi

EXPOSE 8000

CMD ["python", "-m", "server.app"]