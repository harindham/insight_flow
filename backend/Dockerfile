FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

COPY backend/requirements.txt /srv/backend/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /srv/backend/requirements.txt

COPY backend /srv/backend

WORKDIR /srv/backend/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
