FROM python:3.13-slim

RUN mkdir /api

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.prod.sh

ENTRYPOINT ["/api/entrypoint.prod.sh"]
