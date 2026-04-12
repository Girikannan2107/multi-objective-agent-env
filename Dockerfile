FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir openenv openai uvicorn fastapi
RUN pip install openenv-core fastapi uvicorn

EXPOSE 8000

CMD ["python", "-m", "server.app"]