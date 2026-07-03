#!/usr/bin/env bash
set -euo pipefail

railway variable set RAILPACK_START_CMD --stdin \
  --service mitologia-backend \
  --environment production \
  --skip-deploys \
  --json <<'START_COMMAND'
PYTHONPATH=/app/.railway-packages python -c "from alembic.config import main; main()" upgrade head && PYTHONPATH=/app/.railway-packages python scripts/bootstrap_database.py && PYTHONPATH=/app/.railway-packages python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
START_COMMAND

railway variable set RAILPACK_INSTALL_CMD --stdin \
  --service mitologia-backend \
  --environment production \
  --skip-deploys \
  --json <<'INSTALL_COMMAND'
pip install --target ./.railway-packages .
INSTALL_COMMAND
