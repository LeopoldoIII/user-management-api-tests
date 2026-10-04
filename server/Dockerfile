# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py db.py validators.py ./

# Non-root user for security
RUN useradd -m -u 1001 apiuser && chown -R apiuser:apiuser /app
USER apiuser

EXPOSE 3000

# Use Gunicorn with 4 workers for production — replace Flask dev server
# --timeout 30: kill stuck workers after 30s (important for load tests)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:3000", "--timeout", "30", "--access-logfile", "-", "app:app"]
