#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

SERVICE="${SERVICE:-api}"
COMMAND="${1:-upgrade}"

case "$COMMAND" in
  upgrade)
    docker compose exec -T "$SERVICE" alembic -c alembic.ini upgrade head
    ;;
  current)
    docker compose exec -T "$SERVICE" alembic -c alembic.ini current
    ;;
  history)
    docker compose exec -T "$SERVICE" alembic -c alembic.ini history
    ;;
  check)
    docker compose exec -T "$SERVICE" alembic -c alembic.ini check
    ;;
  *)
    echo "Usage: scripts/db_migrate.sh [upgrade|current|history|check]"
    exit 1
    ;;
esac
