
# =========================
# Stage 1: Builder
# =========================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.12-slim AS runtime

# Update Debian OS packages to reduce known vulnerabilities
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create a non-root user
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# =========================
# Stage 3: Test
# =========================
FROM runtime AS test

USER root

RUN pip install --no-cache-dir pytest==8.3.5 httpx==0.28.1

COPY tests/ ./tests/

RUN chown -R appuser:appuser /app

USER appuser

CMD ["pytest", "-q"]
