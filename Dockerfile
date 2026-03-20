FROM python:3.11-slim AS builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --no-cache -r requirements.txt

FROM python:3.11-slim

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser . ./

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8501
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
