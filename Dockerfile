FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir openenv-core

CMD ["python", "inference.py"]