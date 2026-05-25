#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

fail() {
  echo "❌ FAIL: $1"
  exit 1
}

pass() {
  echo "✅ PASS: $1"
}

[ -f ".env" ] || fail ".env file exists"

required_vars=(
  INTERNAL_API_KEY
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  POSTGRES_HOST
  POSTGRES_PORT
  UPLOAD_DIR
  EXPORT_DIR
  BIDREADY_AUTO_CREATE_TABLES
)

for key in "${required_vars[@]}"; do
  if ! grep -q "^${key}=" .env; then
    fail ".env contains ${key}"
  fi

  value="$(grep "^${key}=" .env | tail -1 | cut -d= -f2-)"
  if [ -z "$value" ]; then
    fail ".env ${key} is not empty"
  fi
done

pass ".env required values are present"

if docker compose config 2> /tmp/bidready_compose_config_stderr.txt > /tmp/bidready_compose_config_stdout.txt; then
  if grep -q "variable is not set" /tmp/bidready_compose_config_stderr.txt; then
    cat /tmp/bidready_compose_config_stderr.txt
    fail "docker compose config has unset variable warnings"
  fi
  pass "docker compose config has no unset variable warnings"
else
  cat /tmp/bidready_compose_config_stderr.txt
  fail "docker compose config failed"
fi

if grep -q "POSTGRES_DB: ${POSTGRES_DB}" docker-compose.yml; then
  fail "docker-compose.yml still has raw POSTGRES_DB interpolation without default"
fi

pass "docker-compose postgres defaults are hardened"

echo
echo "Config preflight passed."
