FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --system --create-home --home-dir /app expo

COPY requirements-online.txt /app/requirements-online.txt
RUN pip install --no-cache-dir -r /app/requirements-online.txt

COPY . /app

RUN mkdir -p /app/uploads && chown -R expo:expo /app

USER expo

EXPOSE 8000

CMD ["python", "server.py"]
