FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml alembic.ini ./
COPY backend ./backend
COPY alembic ./alembic
COPY scripts ./scripts
COPY ["Mitologia grega.drawio", "./Mitologia grega.drawio"]

RUN pip install --no-cache-dir .

CMD ["sh", "-c", "alembic upgrade head && python scripts/bootstrap_database.py && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
