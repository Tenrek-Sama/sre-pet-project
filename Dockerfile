# ============ STAGE 1: BUILD ============
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============ STAGE 2: RUNTIME ============
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Копируем зависимости из builder
COPY --from=builder /root/.local /home/app/.local

# Копируем код (ДО переключения пользователя, чтобы chown сработал)
COPY . .

# Добавляем PYTHONPATH — чтобы Python видел модули в текущей директории
ENV PYTHONPATH=/app
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Меняем владельца на app
RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
